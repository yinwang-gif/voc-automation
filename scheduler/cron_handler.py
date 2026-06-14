from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CronHandler:
    """保存 Claude Code 定时任务所需的 prompt 信息。"""

    cron: str
    description: str
    command: str

    @classmethod
    def from_config(cls, config: Dict[str, Any], command: str) -> "CronHandler":
        schedule = config.get("schedule", {})
        return cls(
            cron=schedule.get("cron", "0 9 * * 1"),
            description=schedule.get("description", "Weekly VOC analysis"),
            command=command,
        )

    def build_claude_code_prompt(self) -> str:
        return (
            f"帮我设置一个定时任务，cron 为 {self.cron}，"
            f"执行命令：{self.command}，描述：{self.description}"
        )
