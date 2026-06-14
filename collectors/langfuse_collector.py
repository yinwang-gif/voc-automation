from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests


LANGFUSE_COLUMNS = ["conversation_id", "user_query", "ai_response", "timestamp", "tags"]


class LangfuseCollector:
    def __init__(self, config: Dict[str, Any]):
        source_config = config.get("data_sources", {}).get("langfuse", {})
        self.enabled = bool(source_config.get("enabled", True))
        self.api_endpoint = source_config.get("api_endpoint", "")
        self.project_id = source_config.get("project_id", "")
        self.days_lookback = int(source_config.get("days_lookback", 8))
        self.api_key = source_config.get("api_key") or os.getenv("LANGFUSE_API_KEY", "")
        self.timeout = int(source_config.get("timeout", 30))

    def collect(self) -> pd.DataFrame:
        """收集 AI 对话数据。"""
        if not self.enabled:
            return self._empty_frame()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days_lookback)

        if self.api_endpoint.startswith("mock://"):
            return self._normalize_frame(pd.DataFrame(self._mock_payload()))

        if self.api_endpoint.startswith("file://"):
            return self._normalize_frame(self._read_file_payload(self.api_endpoint.replace("file://", "", 1)))

        if not self.api_endpoint or self.api_endpoint.startswith("YOUR_"):
            raise ValueError("LangfuseCollector 未配置有效 api_endpoint，请更新 config/settings.json 或使用 mock://langfuse。")

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        params = {
            "project_id": self.project_id,
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
            for key in ("conversations", "traces", "data", "items", "results"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [self._from_langfuse_trace(item) for item in value]
            if all(col in payload for col in ("conversation_id", "user_query")):
                return [payload]
        raise ValueError("Langfuse API 返回格式无法识别，期望 list 或包含 conversations/traces/data/items/results 的 dict。")

    def _from_langfuse_trace(self, item: Dict[str, Any]) -> Dict[str, Any]:
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        return {
            "conversation_id": item.get("conversation_id") or item.get("id") or item.get("trace_id") or "",
            "user_query": item.get("user_query") or item.get("input") or metadata.get("user_query") or "",
            "ai_response": item.get("ai_response") or item.get("output") or metadata.get("ai_response") or "",
            "timestamp": item.get("timestamp") or item.get("created_at") or item.get("createdAt") or "",
            "tags": item.get("tags") or metadata.get("tags") or [],
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
        raise ValueError(f"不支持的 Langfuse 文件格式: {path.suffix}")

    def _normalize_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return self._empty_frame()

        rename_map = {
            "id": "conversation_id",
            "query": "user_query",
            "question": "user_query",
            "answer": "ai_response",
            "response": "ai_response",
            "created_at": "timestamp",
            "createdAt": "timestamp",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        for col in LANGFUSE_COLUMNS:
            if col not in df.columns:
                df[col] = ""

        return df[LANGFUSE_COLUMNS].copy()

    def _empty_frame(self) -> pd.DataFrame:
        return pd.DataFrame(columns=LANGFUSE_COLUMNS)

    def _mock_payload(self) -> List[Dict[str, Any]]:
        now = datetime.now().isoformat()
        return [
            {
                "conversation_id": "LF-001",
                "user_query": "为什么提现地址需要 memo？",
                "ai_response": "这是链上地址识别规则，需要用户同时提供地址和 memo。",
                "timestamp": now,
                "tags": ["withdrawal", "concept_confusion"],
            },
            {
                "conversation_id": "LF-002",
                "user_query": "如何批量导出所有账户流水？",
                "ai_response": "当前后台暂不支持跨账户批量导出。",
                "timestamp": now,
                "tags": ["reporting", "capability_gap"],
            },
        ]
