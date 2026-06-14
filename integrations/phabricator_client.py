from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests


class PhabricatorClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get("phabricator", {}).get("base_url", "")
        self.use_mcp = bool(config.get("phabricator", {}).get("use_mcp", True))
        self.auto_create = bool(config.get("phabricator", {}).get("auto_create_tasks", True))
        self.priority_threshold = config.get("phabricator", {}).get("priority_threshold", "P0/P1")
        self.api_token = config.get("phabricator", {}).get("api_token") or os.getenv("PHABRICATOR_API_TOKEN", "")

    def create_tasks_from_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为高优先级问题创建 task。"""
        created_tasks = []

        for issue in issues:
            if not self._should_create_task(issue):
                continue

            task_result = self.create_task(
                title=issue["title"],
                description=self._build_task_description(issue),
            )

            created_tasks.append(
                {
                    "issue": issue["title"],
                    "task_id": task_result["id"],
                    "task_url": task_result["uri"],
                }
            )

        return created_tasks

    def create_task(self, title: str, description: str) -> Dict[str, Any]:
        """创建单个 Phabricator task。

        在 Claude Code 中调用时，这个函数会被替换为直接使用 MCP 工具：
        mcp__mcp-now__pha_task_create
        """
        if self.use_mcp:
            return self._call_mcp_tool(
                tool="mcp__mcp-now__pha_task_create",
                params={
                    "title": title,
                    "description": description,
                },
            )
        return self._call_conduit_api(
            "maniphest.createtask",
            {
                "title": title,
                "description": description,
            },
        )

    def _call_mcp_tool(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用 MCP 工具（通过 Claude Code）。"""
        task_file = Path(self.config.get("output", {}).get("report_dir", ".")).expanduser() / "pending_pha_tasks.json"
        task_file.parent.mkdir(parents=True, exist_ok=True)

        if task_file.exists():
            with task_file.open("r", encoding="utf-8") as f:
                pending_tasks = json.load(f)
        else:
            pending_tasks = []

        pending_tasks.append(
            {
                "tool": tool,
                "params": params,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            }
        )

        with task_file.open("w", encoding="utf-8") as f:
            json.dump(pending_tasks, f, indent=2, ensure_ascii=False)

        return {
            "id": f"pending_{len(pending_tasks)}",
            "uri": f"{self.base_url}/T<待创建>",
            "status": "pending",
        }

    def _call_conduit_api(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.base_url or not self.api_token:
            raise ValueError("直接调用 Phabricator API 需要配置 phabricator.base_url 和 PHABRICATOR_API_TOKEN。")

        endpoint = f"{self.base_url.rstrip('/')}/api/{method}"
        response = requests.post(endpoint, data={"api.token": self.api_token, **params}, timeout=30)
        response.raise_for_status()
        payload = response.json()
        if payload.get("error_code"):
            raise RuntimeError(f"Phabricator API 调用失败: {payload.get('error_info')}")
        result = payload.get("result", {})
        task_id = result.get("id") or result.get("object", {}).get("id")
        uri = result.get("uri") or f"{self.base_url}/T{task_id}"
        return {"id": task_id, "uri": uri, "status": "created"}

    def _build_task_description(self, issue: Dict[str, Any]) -> str:
        """构建 task 描述。"""
        return f"""## 问题背景
根据 VOC 用户反馈分析报告，该问题被标记为 {issue.get('emoji', '')} {issue.get('priority', '')} 优先级。

## 用户反馈
{issue.get('description', '')}

## 数据来源
- 频次：{issue.get('frequency', 0)} 次
- 数据源：{', '.join(issue.get('data_sources', []))}

## VOC 框架分类
- 类型：**{issue.get('category', '')}**

## 建议操作
{chr(10).join([f'{i + 1}. {s}' for i, s in enumerate(issue.get('suggestions', []))])}

## 优先级理由
{issue.get('priority_reason', '根据频次、影响面和业务重要性综合判断。')}

---
**数据来源：** VOC 自动化分析工具
**分析时间：** {datetime.now().strftime('%Y-%m-%d')}
"""

    def _should_create_task(self, issue: Dict[str, Any]) -> bool:
        """判断是否应该创建 task。"""
        if not self.auto_create:
            return False

        if self.priority_threshold == "P0/P1":
            return issue.get("priority") in ["P0", "P1"]
        if self.priority_threshold == "P0":
            return issue.get("priority") == "P0"
        return True
