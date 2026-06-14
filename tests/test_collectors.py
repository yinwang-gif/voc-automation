from __future__ import annotations

import json
from pathlib import Path

from collectors.langfuse_collector import LangfuseCollector
from collectors.telegram_collector import TelegramCollector
from collectors.ticket_collector import TicketCollector


def load_test_config():
    with Path("config/test_settings.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def test_ticket_collector():
    collector = TicketCollector(load_test_config())
    df = collector.collect()
    assert len(df) > 0
    assert "id" in df.columns
    assert "title" in df.columns


def test_telegram_collector():
    collector = TelegramCollector(load_test_config())
    df = collector.collect()
    assert len(df) > 0
    assert "message_id" in df.columns
    assert "text" in df.columns


def test_langfuse_collector():
    collector = LangfuseCollector(load_test_config())
    df = collector.collect()
    assert len(df) > 0
    assert "conversation_id" in df.columns
    assert "user_query" in df.columns
