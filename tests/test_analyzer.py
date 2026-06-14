from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from analyzers.voc_analyzer import VOCAnalyzer
from collectors.langfuse_collector import LangfuseCollector
from collectors.telegram_collector import TelegramCollector
from collectors.ticket_collector import TicketCollector


def load_json(path: str):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def test_voc_analysis():
    config = load_json("config/test_settings.json")
    framework = load_json("config/voc-framework.json")
    raw_data = {
        "tickets": TicketCollector(config).collect(),
        "telegram": TelegramCollector(config).collect(),
        "langfuse_summary": LangfuseCollector(config).collect(),
        "start_date": (datetime.now() - timedelta(days=15)).isoformat(),
        "end_date": datetime.now().isoformat(),
    }
    analyzer = VOCAnalyzer(config, framework)
    result = analyzer.analyze(raw_data)
    assert "issues" in result
    assert len(result["issues"]) > 0
    assert result["issues"][0]["priority"] in {"P0", "P1", "P2"}
