from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd
import requests


TICKET_COLUMNS = [
    "id",
    "title",
    "description",
    "priority",
    "status",
    "product_domain",
    "created_at",
    "tags",
]


class TicketCollector:
    def __init__(self, config: Dict[str, Any]):
        source_config = config.get("data_sources", {}).get("tickets", {})
        self.enabled = bool(source_config.get("enabled", True))
        self.api_endpoint = source_config.get("api_endpoint", "")
        self.auth_token = source_config.get("auth_token") or os.getenv("TICKET_API_TOKEN", "")
        self.days_lookback = int(source_config.get("days_lookback", 8))
        self.timeout = int(source_config.get("timeout", 30))

    def collect(self) -> pd.DataFrame:
        """收集指定时间范围内的工单数据。"""
        if not self.enabled:
            return self._empty_frame()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days_lookback)

        if self.api_endpoint.startswith("mock://"):
            return self._normalize_frame(pd.DataFrame(self._mock_payload()))

        if self.api_endpoint.startswith("file://"):
            return self._normalize_frame(self._read_file_payload(self.api_endpoint.replace("file://", "", 1)))

        if not self.api_endpoint or self.api_endpoint.startswith("YOUR_"):
            raise ValueError("TicketCollector 未配置有效 api_endpoint，请更新 config/settings.json 或使用 mock://tickets。")

        headers = {}
        if self.auth_token and self.auth_token != "YOUR_TOKEN":
            headers["Authorization"] = f"Bearer {self.auth_token}"

        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

        response = requests.get(self.api_endpoint, headers=headers, params=params, timeout=self.timeout)
        response.raise_for_status()

        tickets = self._extract_records(response.json())
        return self._normalize_frame(pd.DataFrame(tickets))

    def save_raw_data(self, output_dir: str | Path) -> str:
        """保存原始数据到文件。"""
        df = self.collect()
        timestamp = datetime.now().strftime("%Y%m%d")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        filepath = output_path / f"raw_tickets_{timestamp}.xlsx"
        df.to_excel(filepath, index=False)
        return str(filepath)

    def _extract_records(self, payload: Any) -> List[Dict[str, Any]]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("tickets", "data", "items", "results"):
                value = payload.get(key)
                if isinstance(value, list):
                    return value
            if all(col in payload for col in ("id", "title")):
                return [payload]
        raise ValueError("工单 API 返回格式无法识别，期望 list 或包含 tickets/data/items/results 的 dict。")

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
            payload = pd.read_json(path)
            return payload
        raise ValueError(f"不支持的工单文件格式: {path.suffix}")

    def _normalize_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return self._empty_frame()

        rename_map = {
            "ticket_id": "id",
            "subject": "title",
            "content": "description",
            "body": "description",
            "domain": "product_domain",
            "created": "created_at",
            "created_time": "created_at",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        for col in TICKET_COLUMNS:
            if col not in df.columns:
                df[col] = ""

        return df[TICKET_COLUMNS].copy()

    def _empty_frame(self) -> pd.DataFrame:
        return pd.DataFrame(columns=TICKET_COLUMNS)

    def _mock_payload(self) -> List[Dict[str, Any]]:
        now = datetime.now().isoformat()
        return [
            {
                "id": "TICKET-001",
                "title": "用户不理解提现地址校验规则",
                "description": "用户反馈提现地址填写后一直提示校验失败，不清楚为什么不能提交。",
                "priority": "high",
                "status": "open",
                "product_domain": "wallet",
                "created_at": now,
                "tags": ["withdrawal", "address", "confused"],
            },
            {
                "id": "TICKET-002",
                "title": "希望支持批量导出交易流水",
                "description": "运营侧需要一次性导出多个账户的交易流水，目前只能逐个操作。",
                "priority": "medium",
                "status": "open",
                "product_domain": "reporting",
                "created_at": now,
                "tags": ["export", "feature request"],
            },
            {
                "id": "TICKET-003",
                "title": "交易详情页偶发加载失败",
                "description": "用户进入交易详情时偶尔卡住，需要刷新后才恢复。",
                "priority": "medium",
                "status": "open",
                "product_domain": "transaction",
                "created_at": now,
                "tags": ["bug", "loading"],
            },
        ]
