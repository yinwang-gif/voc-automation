"""
name: voc-automation
description: 自动收集 VOC 数据，分析并创建 Phabricator tasks
trigger: 定时执行或手动触发 /voc-automation
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = os.getenv("VOC_AUTOMATION_ROOT", "/Users/yin.wang/voc-automation")
sys.path.append(PROJECT_ROOT)

from scheduler.workflow_runner import WorkflowRunner  # noqa: E402


def run(args=None):
    """Skill 入口函数。"""
    config_path = os.getenv("VOC_AUTOMATION_CONFIG", f"{PROJECT_ROOT}/config/settings.json")
    runner = WorkflowRunner(config_path)
    result = runner.run()

    if result.get("success"):
        _execute_pending_pha_tasks()

    return result


def _execute_pending_pha_tasks():
    """执行待创建的 Phabricator tasks。

    这个函数会读取 pending_pha_tasks.json，
    然后在 Claude Code 中逐个调用 MCP 工具。
    """
    config_path = os.getenv("VOC_AUTOMATION_CONFIG", f"{PROJECT_ROOT}/config/settings.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    task_file = Path(config["output"]["report_dir"]) / "pending_pha_tasks.json"

    if not task_file.exists():
        return

    with task_file.open("r", encoding="utf-8") as f:
        pending_tasks = json.load(f)

    completed_tasks = []

    for task in pending_tasks:
        if task["status"] != "pending":
            continue

        print(f"[MCP_CALL] {task['tool']}")
        print(f"[MCP_PARAMS] {json.dumps(task['params'], ensure_ascii=False)}")

        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        completed_tasks.append(task)

    with task_file.open("w", encoding="utf-8") as f:
        json.dump(completed_tasks, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    run()
