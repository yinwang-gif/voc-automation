from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests


TELEGRAM_COLUMNS = ["message_id", "text", "sender", "timestamp", "thread_id"]


class TelegramCollector:
    def __init__(self, config: Dict[str, Any]):
        source_config = config.get("data_sources", {}).get("telegram", {})
        self.enabled = bool(source_config.get("enabled", True))
        self.api_endpoint = source_config.get("api_endpoint", "")
        self.channel_id = source_config.get("channel_id", "")
        self.days_lookback = int(source_config.get("days_lookback", 15))
        self.bot_token = source_config.get("bot_token") or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.timeout = int(source_config.get("timeout", 30))

    def collect(self) -> pd.DataFrame:
        """收集 TG 消息。"""
        if not self.enabled:
            return self._empty_frame()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days_lookback)

        if self.api_endpoint.startswith("mock://"):
            return self._normalize_frame(pd.DataFrame(self._mock_payload()))

        if self.api_endpoint.startswith("file://"):
            return self._normalize_frame(self._read_file_payload(self.api_endpoint.replace("file://", "", 1)))

        if not self.api_endpoint or self.api_endpoint.startswith("YOUR_"):
            raise ValueError("TelegramCollector 未配置有效 api_endpoint，请更新 config/settings.json 或使用 mock://telegram。")

        headers = {}
        if self.bot_token:
            headers["Authorization"] = f"Bearer {self.bot_token}"

        params = {
            "channel_id": self.channel_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        response = requests.get(self.api_endpoint, headers=headers, params=params, timeout=self.timeout)
        response.raise_for_status()
        records = self._extract_records(response.json())
        return self._normalize_frame(pd.DataFrame(records))

    def _extract_records(self, payload: Any) -> List[Dict[str, Any]]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("messages", "data", "items", "results"):
                value = payload.get(key)
                if isinstance(value, list):
                    return value
            if "result" in payload and isinstance(payload["result"], list):
                return [self._from_telegram_update(update) for update in payload["result"]]
            if all(col in payload for col in ("message_id", "text")):
                return [payload]
        raise ValueError("Telegram API 返回格式无法识别，期望 list 或包含 messages/data/items/results 的 dict。")

    def _from_telegram_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        message = update.get("message") or update.get("channel_post") or {}
        sender = message.get("from") or {}
        return {
            "message_id": message.get("message_id") or update.get("update_id"),
            "text": message.get("text") or message.get("caption") or "",
            "sender": sender.get("username") or sender.get("first_name") or "",
            "timestamp": datetime.fromtimestamp(message.get("date", 0)).isoformat() if message.get("date") else "",
            "thread_id": message.get("message_thread_id", ""),
        }

    def _read_file_payload(self, file_path: str) -> pd.DataFrame:
        path = Path(file_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(path)
        suffix = path.suffix.lower()
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(path)
        if suffix == ".csv":
            return pd.read_csv(path)
        if suffix == ".json":
            return pd.read_json(path)
        raise ValueError(f"不支持的 Telegram 文件格式: {path.suffix}")

    def _normalize_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return self._empty_frame()

        rename_map = {
            "id": "message_id",
            "message": "text",
            "content": "text",
            "created_at": "timestamp",
            "created": "timestamp",
            "user": "sender",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        for col in TELEGRAM_COLUMNS:
            if col not in df.columns:
                df[col] = ""

        return df[TELEGRAM_COLUMNS].copy()

    def _empty_frame(self) -> pd.DataFrame:
        return pd.DataFrame(columns=TELEGRAM_COLUMNS)

    def _mock_payload(self) -> List[Dict[str, Any]]:
        now = datetime.now().isoformat()
        return [
            {
                "message_id": "TG-001",
                "text": "提现地址校验为什么老失败？用户不知道要填 memo，文案也看不懂。",
                "sender": "ops_a",
                "timestamp": now,
                "thread_id": "withdrawal-help",
            },
            {
                "message_id": "TG-002",
                "text": "有客户问能不能批量导出交易流水，现在一个个导出太慢。",
                "sender": "ops_b",
                "timestamp": now,
                "thread_id": "reporting",
            },
            {
                "message_id": "TG-003",
                "text": "交易详情页今天又有人反馈加载失败，刷新之后恢复。",
                "sender": "support_c",
                "timestamp": now,
                "thread_id": "transaction",
            },
        ]
