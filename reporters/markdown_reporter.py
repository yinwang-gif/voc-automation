from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


class MarkdownReporter:
    def __init__(self, config: Dict[str, Any]):
        self.output_dir = Path(config.get("output", {}).get("report_dir", ".")).expanduser()

    def generate(self, analysis_result: Dict[str, Any]) -> str:
        """生成 Markdown 报告。"""
        timestamp = datetime.now().strftime("%Y%m%d")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.output_dir / f"VOC_分析报告_{timestamp}.md"

        with report_path.open("w", encoding="utf-8") as f:
            f.write(self._build_report(analysis_result))

        return str(report_path)

    def _build_report(self, result: Dict[str, Any]) -> str:
        """构建 Markdown 内容。"""
        metadata = result.get("metadata", {})
        date_range = metadata.get("date_range", ("", ""))
        md = f"""# VOC 用户反馈分析报告

**生成时间：** {metadata.get('analysis_timestamp', '')}
**数据时间范围：** {date_range[0]} ~ {date_range[1]}
**数据来源：** 工单{metadata.get('total_tickets', 0)}条、TG消息{metadata.get('total_tg_messages', 0)}条

---

## 一、核心发现

{result.get('summary', '')}

---

## 二、问题详情

"""
        for priority in ["P0", "P1", "P2"]:
            issues = [i for i in result.get("issues", []) if i.get("priority") == priority]
            if issues:
                md += f"\n### {priority} 优先级问题\n\n"
                for issue in issues:
                    md += self._format_issue(issue)

        if result.get("comparison"):
            md += "\n---\n\n## 三、与上期对比\n\n"
            md += result["comparison"]
            md += "\n"

        return md

    def _format_issue(self, issue: Dict[str, Any]) -> str:
        """格式化单个问题。"""
        return f"""#### {issue.get('emoji', '')} {issue.get('title', '')}

**分类：** {issue.get('category', '')}
**频次：** {issue.get('frequency', 0)} 次
**数据来源：** {', '.join(issue.get('data_sources', []))}

{issue.get('description', '')}

**建议操作：**
{self._format_suggestions(issue.get('suggestions', []))}

---

"""

    def _format_suggestions(self, suggestions: List[str]) -> str:
        """格式化建议列表。"""
        return "\n".join([f"{i + 1}. {s}" for i, s in enumerate(suggestions)])
