from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from integrations.claude_analyzer import ClaudeAnalyzer
from .priority_ranker import PriorityRanker


class VOCAnalyzer:
    def __init__(self, config: Dict[str, Any], voc_framework: Dict[str, Any]):
        self.config = config
        self.voc_framework = voc_framework
        self.claude = ClaudeAnalyzer(config)
        self.ranker = PriorityRanker()

    def analyze(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """完整 VOC 分析流程。"""
        cleaned_data = self._preprocess(raw_data)
        analysis_result = self.claude.analyze_voc(cleaned_data, self.voc_framework)
        prioritized_issues = self._rank_by_priority(analysis_result["issues"])
        comparison = self._compare_with_history(prioritized_issues)

        return {
            "issues": prioritized_issues,
            "summary": analysis_result["summary"],
            "comparison": comparison,
            "metadata": {
                "date_range": (raw_data["start_date"], raw_data["end_date"]),
                "total_tickets": len(raw_data.get("tickets", [])),
                "total_tg_messages": len(raw_data.get("telegram", [])),
                "total_langfuse_conversations": len(raw_data.get("langfuse_summary", [])),
                "analysis_timestamp": datetime.now().isoformat(),
            },
        }

    def _preprocess(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = dict(raw_data)
        for key in ("tickets", "telegram", "langfuse_summary"):
            value = cleaned.get(key)
            if isinstance(value, pd.DataFrame):
                cleaned[key] = value.fillna("")
        return cleaned

    def _rank_by_priority(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按优先级排序。"""
        return self.ranker.rank(issues)

    def _compare_with_history(self, prioritized_issues: List[Dict[str, Any]]) -> str:
        """与历史 VOC 报告进行轻量对比。"""
        report_dir = Path(self.config.get("output", {}).get("report_dir", ".")).expanduser()
        if not report_dir.exists():
            return ""

        history_files = sorted(report_dir.glob("VOC_分析报告_*.md"))
        if not history_files:
            return ""

        previous_report = history_files[-1]
        titles = [issue.get("title", "") for issue in prioritized_issues]
        continued = []
        try:
            previous_text = previous_report.read_text(encoding="utf-8")
            continued = [title for title in titles if title and title in previous_text]
        except Exception:
            return ""

        if not continued:
            return f"本次未发现与上期报告《{previous_report.name}》标题完全一致的持续问题。"
        return "以下问题与上期标题一致，建议持续跟踪：\n" + "\n".join(f"- {title}" for title in continued)
