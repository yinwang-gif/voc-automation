"""
name: voc-automation
description: VOC 自动化分析 — MCP 拉数据 → Claude 分析 → 生成 Excel → 创建 PHA Task
trigger: /voc-automation 或定时触发
"""

from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(args=None):
    """Skill 入口 — 直接通过 claude -p 执行完整分析流程，MCP 创建 Task。"""
    config_path = os.path.join(PROJECT_ROOT, "config", "settings.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    print(f"📊 VOC 自动化分析启动")
    print(f"   项目路径: {PROJECT_ROOT}")
    print(f"   输出目录: {config['output']['report_dir']}")
    print(f"   数据源: {list(config['data_sources'].keys())}")
    print()
    print("请使用以下指令执行分析：")
    print(f"  claude -p --permission-mode bypassPermissions '读取 {PROJECT_ROOT}/QUICK_START.md 并执行完整 VOC 分析流程'")

    return {"success": True, "project_root": PROJECT_ROOT}


if __name__ == "__main__":
    run()
