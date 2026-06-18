from __future__ import annotations

import json
from pathlib import Path

from analyzers.decision_analyzer import ALLOWED_DECISIONS, DecisionAnalyzer


def load_config():
    with Path("config/test_settings.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def _issue(priority="P1", category="capability_gap", title="需要支持批量导出交易流水"):
    return {
        "category": category,
        "title": title,
        "description": "运营和客户反馈当前只能逐账户导出交易流水，批量处理效率较低。",
        "priority": priority,
        "frequency": 4,
        "data_sources": ["tickets", "telegram"],
        "suggestions": ["增加按账户组、时间范围批量导出能力。"],
        "priority_reason": "频次达到 P1 阈值。",
    }


def test_decide_returns_structured_decision():
    analyzer = DecisionAnalyzer(load_config())
    decision = analyzer.decide(_issue())

    assert decision["decision"] in ALLOWED_DECISIONS
    assert decision["decision_label"]
    assert isinstance(decision["do_next"], list)
    assert isinstance(decision["do_not_yet"], list)
    assert isinstance(decision["evidence"], list) and decision["evidence"]
    # 证据等级必须落在允许集合内
    assert decision["evidence"][0]["level"] in {"Fact", "Assumption", "Needs validation", "Contradiction"}


def test_decide_issues_only_high_priority():
    analyzer = DecisionAnalyzer(load_config())
    issues = [_issue(priority="P1"), _issue(priority="P2", title="次要体验问题")]
    analyzer.decide_issues(issues, context="本期 VOC 整体概述")

    assert "product_decision" in issues[0]
    assert "product_decision" not in issues[1]


def test_skill_prompt_loaded_from_project_copy():
    analyzer = DecisionAnalyzer(load_config())
    # 应加载项目内 skill 副本（含 skill 标题），而非内置 fallback
    assert "Product Owner Decision" in analyzer.skill_prompt


def test_high_risk_flagged_for_fund_related_issue():
    analyzer = DecisionAnalyzer(load_config())
    decision = analyzer.decide(_issue(title="提现地址校验规则理解困难", category="concept_confusion"))
    assert decision["high_risk"] is True


def test_disabled_decision_skips_all():
    config = load_config()
    config["analysis"]["product_decision"]["enabled"] = False
    analyzer = DecisionAnalyzer(config)
    issues = [_issue(priority="P0")]
    analyzer.decide_issues(issues)
    assert "product_decision" not in issues[0]
