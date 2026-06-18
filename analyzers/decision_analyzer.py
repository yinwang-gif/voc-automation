from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# product-owner-decision skill 的查找顺序：项目内副本优先，其次全局安装位置。
DEFAULT_SKILL_DIRS = [
    PROJECT_ROOT / "skills" / "product-owner-decision",
    Path.home() / ".claude" / "skills" / "product-owner-decision",
]

ALLOWED_DECISIONS = ["explore", "prototype", "pilot", "enter_prd", "pause", "stop"]
ALLOWED_LEVELS = ["Fact", "Assumption", "Needs validation", "Contradiction"]


class DecisionAnalyzer:
    """对单个 VOC 问题运行 Product Owner Decision，产出结构化的产品决策。

    定位：VOC 分析负责「发现问题 + 改进建议」，本模块在其后补一步「该不该做」的
    判断——把一个问题升级成带证据的决策（explore / prototype / pilot / enter_prd /
    pause / stop）。调用方式、mock 开关与 ClaudeAnalyzer 保持一致。
    """

    def __init__(self, config: Dict[str, Any]):
        analysis_config = config.get("analysis", {})
        decision_config = analysis_config.get("product_decision", {})

        self.enabled = bool(decision_config.get("enabled", True))
        self.apply_to_priorities = decision_config.get("apply_to_priorities", ["P0", "P1"])
        self.api_key = analysis_config.get("api_key") or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = decision_config.get("claude_model") or analysis_config.get("claude_model", "claude-sonnet-4-6")
        self.max_tokens = int(decision_config.get("max_tokens", 8000))
        self.use_prompt_caching = bool(analysis_config.get("use_prompt_caching", True))
        self.mock_analysis = bool(analysis_config.get("mock_analysis", False))
        self.client = None

        self.skill_prompt = self._load_skill_prompt(decision_config.get("skill_path"))

        if not self.mock_analysis and self.enabled:
            if not self.api_key or self.api_key.startswith("YOUR_"):
                raise ValueError(
                    "未配置 ANTHROPIC_API_KEY。请在 .env 中设置，或在测试配置中启用 mock_analysis。"
                )
            try:
                from anthropic import Anthropic
            except ImportError as exc:  # pragma: no cover
                raise ImportError("缺少 anthropic SDK，请先运行: pip install -r requirements.txt") from exc
            self.client = Anthropic(api_key=self.api_key)

    # ------------------------------------------------------------------ #
    # 公开方法
    # ------------------------------------------------------------------ #
    def should_decide(self, issue: Dict[str, Any]) -> bool:
        """是否需要为该问题跑产品决策（默认只对 P0/P1）。"""
        return self.enabled and issue.get("priority") in self.apply_to_priorities

    def decide_issues(
        self, issues: List[Dict[str, Any]], context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """对满足优先级条件的问题逐个跑决策，结果原地挂到 issue['product_decision']。"""
        if not self.enabled:
            return issues
        for issue in issues:
            if self.should_decide(issue):
                issue["product_decision"] = self.decide(issue, context)
        return issues

    def decide(self, issue: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """对单个问题产出结构化决策。"""
        if self.mock_analysis:
            return self._mock_decision(issue)

        system_prompt = f"{self.skill_prompt}\n\n{self._output_instruction()}"
        system_block: Dict[str, Any] = {"type": "text", "text": system_prompt}
        if self.use_prompt_caching:
            system_block["cache_control"] = {"type": "ephemeral"}

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=[system_block],
            messages=[{"role": "user", "content": self._build_user_prompt(issue, context)}],
        )
        response_text = "\n".join(getattr(block, "text", "") for block in response.content)
        return self._parse_decision(response_text)

    # ------------------------------------------------------------------ #
    # Prompt 构建
    # ------------------------------------------------------------------ #
    def _load_skill_prompt(self, configured_path: Optional[str]) -> str:
        """加载 product-owner-decision skill 的方法论作为 system prompt。

        取 SKILL.md（工作流 + 必守门槛）加 references/contracts.md（输出契约、决策表、
        证据标准、高风险规则）。找不到 skill 时退回内置精简契约，保证模块可用。
        """
        candidates: List[Path] = []
        if configured_path:
            configured = Path(configured_path).expanduser()
            if not configured.is_absolute():
                configured = PROJECT_ROOT / configured
            candidates.append(configured)
        candidates.extend(DEFAULT_SKILL_DIRS)

        for skill_dir in candidates:
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                parts = [skill_md.read_text(encoding="utf-8")]
                contracts = skill_dir / "references" / "contracts.md"
                if contracts.exists():
                    parts.append(contracts.read_text(encoding="utf-8"))
                return "\n\n---\n\n".join(parts)

        return self._fallback_prompt()

    def _output_instruction(self) -> str:
        """约束模型针对单个 VOC 问题输出结构化 JSON。"""
        return f"""## 本次任务

你将收到一个来自 VOC（客户之声）分析的问题。请对**这一个问题**运行 Product Owner
Decision，判断它现在应该进入哪个阶段，并严格按下面的 JSON 结构输出（只输出一个 JSON，
不要输出多余文字）：

```json
{{
  "decision": "{' | '.join(ALLOWED_DECISIONS)}",
  "rationale": "为什么是这个决策，一两句话",
  "intent": "真正要解决的问题判断",
  "builder": "最小验证方案（最小可验证闭环 / MVP 边界）",
  "seller": "谁真的需要、现在怎么凑合解决的、会反对什么",
  "measurer": "怎么判断有效（成功指标 / 护栏 / kill 标准）",
  "critic": "最大的风险或反对意见、最弱的一环",
  "high_risk": true,
  "risk_domain": "若涉及资金/钱包/签名/KYC/合规/客户数据/对客 ROI 等高风险域则写明，否则空字符串",
  "do_next": ["1-3 个具体的下一步动作"],
  "do_not_yet": ["明确现在还不该做的事"],
  "evidence": [
    {{"claim": "关键论断", "level": "{' | '.join(ALLOWED_LEVELS)}", "source": "来源", "owner": "负责人或 missing"}}
  ]
}}
```

硬性约束：
- 单条客户反馈不能当成已验证的市场需求。
- 高风险域未完成评审时，decision 不得为 `pilot` 或 `enter_prd`。
- 不要声称创建了任务/文档/知识库文章——这里只产出决策建议。"""

    def _build_user_prompt(self, issue: Dict[str, Any], context: Optional[str]) -> str:
        suggestions = issue.get("suggestions") or []
        suggestion_text = "\n".join(f"- {s}" for s in suggestions) or "（无）"
        context_block = f"\n## 本期 VOC 整体概述\n{context}\n" if context else ""
        return f"""请对以下 VOC 问题做产品决策。
{context_block}
## 问题
- 标题：{issue.get('title', '')}
- VOC 分类：{issue.get('category', '')}
- 优先级：{issue.get('priority', '')}（{issue.get('priority_reason', '')}）
- 频次：{issue.get('frequency', 0)} 次
- 数据来源：{', '.join(issue.get('data_sources', []) or [])}

## 问题描述
{issue.get('description', '')}

## VOC 已给出的改进建议
{suggestion_text}

请按要求只输出一个 JSON。"""

    # ------------------------------------------------------------------ #
    # 解析与规范化
    # ------------------------------------------------------------------ #
    def _parse_decision(self, response_text: str) -> Dict[str, Any]:
        text = response_text.strip()
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if json_match:
            text = json_match.group(1).strip()
        else:
            first = text.find("{")
            last = text.rfind("}")
            if first >= 0 and last > first:
                text = text[first : last + 1]
        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            # 模型未给出可解析 JSON 时，降级为 pause，保留原文便于排查。
            return self._normalize_decision(
                {"decision": "pause", "rationale": "决策模型未返回可解析结果，需人工复核。", "intent": response_text[:500]}
            )
        return self._normalize_decision(result)

    def _normalize_decision(self, result: Dict[str, Any]) -> Dict[str, Any]:
        decision = str(result.get("decision", "explore")).strip().lower()
        if decision not in ALLOWED_DECISIONS:
            decision = "explore"

        evidence = []
        for row in result.get("evidence", []) or []:
            if not isinstance(row, dict):
                continue
            level = str(row.get("level", "Assumption")).strip()
            if level not in ALLOWED_LEVELS:
                level = "Assumption"
            evidence.append(
                {
                    "claim": row.get("claim", ""),
                    "level": level,
                    "source": row.get("source", ""),
                    "owner": row.get("owner", "missing"),
                }
            )

        return {
            "decision": decision,
            "rationale": result.get("rationale", ""),
            "intent": result.get("intent", ""),
            "builder": result.get("builder", ""),
            "seller": result.get("seller", ""),
            "measurer": result.get("measurer", ""),
            "critic": result.get("critic", ""),
            "high_risk": bool(result.get("high_risk", False)),
            "risk_domain": result.get("risk_domain", ""),
            "do_next": self._as_list(result.get("do_next")),
            "do_not_yet": self._as_list(result.get("do_not_yet")),
            "evidence": evidence,
            "decision_label": self._decision_label(decision),
        }

    @staticmethod
    def _as_list(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return [str(v) for v in value]

    @staticmethod
    def _decision_label(decision: str) -> str:
        return {
            "explore": "继续探索",
            "prototype": "做原型验证",
            "pilot": "小范围试点",
            "enter_prd": "进入 PRD",
            "pause": "暂缓",
            "stop": "不做",
        }.get(decision, decision)

    # ------------------------------------------------------------------ #
    # Fallback / Mock
    # ------------------------------------------------------------------ #
    def _fallback_prompt(self) -> str:
        """skill 目录缺失时的内置精简方法论，保证决策仍可运行。"""
        return (
            "你是产品负责人。对给定的一个 VOC 问题判断它应进入哪个阶段："
            f"{' / '.join(ALLOWED_DECISIONS)}。区分事实与假设，单条反馈不等于已验证需求；"
            "高风险域（资金/钱包/签名/KYC/合规/客户数据/对客 ROI）未评审时不得 pilot 或 enter_prd。"
        )

    def _mock_decision(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """离线/测试用的占位决策，结构与真实输出一致。"""
        category = issue.get("category", "")
        title = issue.get("title", "该问题")
        decision = {
            "concept_confusion": "prototype",
            "capability_gap": "explore",
            "product_issue": "prototype",
        }.get(category, "explore")

        text = f"{title} {issue.get('description', '')}"
        high_risk = any(k in text for k in ["资金", "提现", "地址", "签名", "钱包", "费用", "合规", "KYC"])

        return self._normalize_decision(
            {
                "decision": decision,
                "rationale": f"{issue.get('priority', '')} 问题，有低成本验证路径，先小步验证价值再决定是否立项。",
                "intent": f"围绕「{title}」，先确认问题是否真实且值得投入。",
                "builder": "搭一个最小可验证闭环（解释卡片 / 原型 / 可复用话术），不改动核心逻辑。",
                "seller": "高频反馈的客户与一线 CS；当前靠人工解释或绕过。",
                "measurer": "成功＝相关反馈/追问下降；护栏＝不引入新的误解；kill＝验证后无改善。",
                "critic": "证据主要来自反馈频次，尚未证明改动一定有效，需防止把单点反馈当普遍需求。",
                "high_risk": high_risk,
                "risk_domain": "对客资金/费用相关，措辞需评审" if high_risk else "",
                "do_next": [
                    "聚类近期相关反馈，确认问题边界",
                    "做最小原型或话术并找少量真实场景验证",
                ],
                "do_not_yet": ["不要直接进入正式 PRD", "不要对客做任何确定性承诺"],
                "evidence": [
                    {
                        "claim": f"该问题近期出现 {issue.get('frequency', 0)} 次",
                        "level": "Fact",
                        "source": ", ".join(issue.get("data_sources", []) or []) or "VOC 分析",
                        "owner": "产品负责人",
                    },
                    {
                        "claim": "改进措施能降低相关反馈",
                        "level": "Needs validation",
                        "source": "产品假设",
                        "owner": "产品负责人",
                    },
                ],
            }
        )
