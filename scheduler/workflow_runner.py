from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from analyzers.voc_analyzer import VOCAnalyzer
from collectors.langfuse_collector import LangfuseCollector
from collectors.telegram_collector import TelegramCollector
from collectors.ticket_collector import TicketCollector
from integrations.phabricator_client import PhabricatorClient
from reporters.excel_reporter import ExcelReporter
from reporters.markdown_reporter import MarkdownReporter


class WorkflowRunner:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path).expanduser().resolve()
        with self.config_path.open("r", encoding="utf-8") as f:
            self.config = json.load(f)

        framework_path = self.config_path.parent / "voc-framework.json"
        if not framework_path.exists():
            framework_path = Path("config/voc-framework.json")
        with framework_path.open("r", encoding="utf-8") as f:
            self.voc_framework = json.load(f)

        self.ticket_collector = TicketCollector(self.config)
        self.telegram_collector = TelegramCollector(self.config)
        self.langfuse_collector = LangfuseCollector(self.config)
        self.analyzer = VOCAnalyzer(self.config, self.voc_framework)
        self.md_reporter = MarkdownReporter(self.config)
        self.excel_reporter = ExcelReporter(self.config)
        self.pha_client = PhabricatorClient(self.config)

    def run(self) -> Dict[str, Any]:
        """执行完整工作流。"""
        print("🚀 开始 VOC 自动化分析...")

        try:
            print("📊 步骤 1/5: 收集数据...")
            raw_data = {
                "tickets": self.ticket_collector.collect(),
                "telegram": self.telegram_collector.collect(),
                "langfuse_summary": self.langfuse_collector.collect(),
                "start_date": (datetime.now() - timedelta(days=15)).isoformat(),
                "end_date": datetime.now().isoformat(),
            }
            print(f"   ✓ 工单: {len(raw_data['tickets'])} 条")
            print(f"   ✓ TG: {len(raw_data['telegram'])} 条")

            print("🤖 步骤 2/5: AI 分析中...")
            analysis_result = self.analyzer.analyze(raw_data)
            print(f"   ✓ 识别问题: {len(analysis_result['issues'])} 个")

            print("📝 步骤 3/5: 生成报告...")
            md_path = self.md_reporter.generate(analysis_result)
            excel_path = self.excel_reporter.generate(analysis_result)
            print(f"   ✓ Markdown: {md_path}")
            print(f"   ✓ Excel: {excel_path}")

            print("🎫 步骤 4/5: 创建 Phabricator tasks...")
            created_tasks = self.pha_client.create_tasks_from_issues(analysis_result["issues"])
            print(f"   ✓ 创建 {len(created_tasks)} 个 task")

            print("✅ 步骤 5/5: 生成执行摘要...")
            summary = self._generate_summary(analysis_result, created_tasks, md_path, excel_path)
            output_dir = Path(self.config.get("output", {}).get("report_dir", ".")).expanduser()
            output_dir.mkdir(parents=True, exist_ok=True)
            summary_path = output_dir / f"执行摘要_{datetime.now().strftime('%Y%m%d')}.txt"
            with summary_path.open("w", encoding="utf-8") as f:
                f.write(summary)

            print(f"\n🎉 完成！摘要: {summary_path}")
            return {
                "success": True,
                "reports": [md_path, excel_path],
                "tasks": created_tasks,
                "summary": str(summary_path),
            }
        except Exception as exc:
            print(f"❌ VOC 自动化分析失败: {exc}")
            return {"success": False, "error": str(exc)}


    def _format_task_list(self, tasks: list) -> str:
        return chr(10).join([f"- {t['issue']}: {t['task_url']}" for t in tasks])

    def _generate_summary(self, analysis: Dict[str, Any], tasks: list, md_path: str, excel_path: str) -> str:
        """生成执行摘要。"""
        return f"""VOC 自动化分析执行摘要
{'=' * 50}
执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

数据统计:
- 工单: {analysis['metadata']['total_tickets']} 条
- TG 消息: {analysis['metadata']['total_tg_messages']} 条
- 识别问题: {len(analysis['issues'])} 个
  - P0: {len([i for i in analysis['issues'] if i['priority'] == 'P0'])} 个
  - P1: {len([i for i in analysis['issues'] if i['priority'] == 'P1'])} 个
  - P2: {len([i for i in analysis['issues'] if i['priority'] == 'P2'])} 个

生成报告:
- Markdown: {md_path}
- Excel: {excel_path}

创建 Phabricator Tasks: {len(tasks)} 个
{self._format_task_list(tasks)}

下一步:
1. 查看完整报告: {md_path}
2. 在 Phabricator 中分配 task owner
3. 跟踪 task 执行进度
"""
