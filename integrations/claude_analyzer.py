from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

import pandas as pd


class ClaudeAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        analysis_config = config.get("analysis", {})
        self.api_key = analysis_config.get("api_key") or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = analysis_config.get("claude_model", "claude-sonnet-4-6")
        self.max_tokens = int(analysis_config.get("max_tokens", 16000))
        self.use_prompt_caching = bool(analysis_config.get("use_prompt_caching", True))
        self.mock_analysis = bool(analysis_config.get("mock_analysis", False))
        self.client = None

        if not self.mock_analysis:
            if not self.api_key or self.api_key.startswith("YOUR_"):
                raise ValueError("未配置 ANTHROPIC_API_KEY。请在 .env 中设置，或在测试配置中启用 mock_analysis。")
            try:
                from anthropic import Anthropic
            except ImportError as exc:
                raise ImportError("缺少 anthropic SDK，请先运行: pip install -r requirements.txt") from exc
            self.client = Anthropic(api_key=self.api_key)

    def analyze_voc(self, raw_data: Dict[str, Any], voc_framework: Dict[str, Any]) -> Dict[str, Any]:
        """使用 Claude 分析 VOC 数据。"""
        if self.mock_analysis:
            return self._mock_response(raw_data)

        system_prompt = self._build_system_prompt(voc_framework)
        user_prompt = self._build_user_prompt(raw_data)

        system_block: Dict[str, Any] = {
            "type": "text",
            "text": system_prompt,
        }
        if self.use_prompt_caching:
            system_block["cache_control"] = {"type": "ephemeral"}

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=[system_block],
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = "\n".join(getattr(block, "text", "") for block in response.content)
        return self._parse_response(response_text)

    def _build_system_prompt(self, voc_framework: Dict[str, Any]) -> str:
        """构建 system prompt，包含 VOC 框架定义。"""
        return f"""你是一个专业的 VOC（客户之声）分析专家。

你的任务是分析用户反馈数据，按照以下框架分类：

{json.dumps(voc_framework, indent=2, ensure_ascii=False)}

分析要求：
1. 将每个问题归类到：概念困扰 / 能力缺口 / 产品残留问题
2. 识别高频问题（出现 >= 3 次）
3. 评估优先级（P0/P1/P2）
4. 提供具体的改进建议
5. 交叉验证：与历史 VOC 结论对比，判断是新问题还是持续问题

输出格式要求：
- 使用 JSON 结构化输出
- 每个问题包含：category, title, description, priority, frequency, data_sources, suggestions
"""

    def _build_user_prompt(self, raw_data: Dict[str, Any]) -> str:
        """构建 user prompt，包含原始数据。"""
        tickets = raw_data.get("tickets")
        telegram = raw_data.get("telegram")
        langfuse_summary = raw_data.get("langfuse_summary")

        return f"""请分析以下用户反馈数据：

## 工单数据（{self._len_safe(tickets)} 条）
{self._to_markdown(tickets)}

## TG 消息（{self._len_safe(telegram)} 条）
{self._to_markdown(telegram)}

## AI 对话摘要
{self._to_markdown(langfuse_summary)}

请按照 VOC 框架进行分析，并输出结构化结果。
"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """解析 Claude 返回的 JSON 结果。"""
        text = response_text.strip()
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if json_match:
            text = json_match.group(1).strip()
        else:
            first = text.find("{")
            last = text.rfind("}")
            if first >= 0 and last > first:
                text = text[first : last + 1]

        result = json.loads(text)
        return self._normalize_result(result)

    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(result, list):
            result = {"summary": "", "issues": result}

        issues = result.get("issues", [])
        normalized_issues = []
        for issue in issues:
            priority = issue.get("priority", "P2")
            normalized_issues.append(
                {
                    "category": issue.get("category", "product_issue"),
                    "title": issue.get("title", "未命名问题"),
                    "description": issue.get("description", ""),
                    "priority": priority,
                    "frequency": int(issue.get("frequency", 1) or 1),
                    "data_sources": issue.get("data_sources") or [],
                    "suggestions": issue.get("suggestions") or [],
                    "emoji": issue.get("emoji") or self._emoji_for_priority(priority),
                    "priority_reason": issue.get("priority_reason", "根据频次、影响面和业务重要性综合判断。"),
                }
            )

        return {
            "summary": result.get("summary", ""),
            "issues": normalized_issues,
        }

    def _to_markdown(self, value: Any) -> str:
        if value is None:
            return "_无数据_"
        if isinstance(value, pd.DataFrame):
            if value.empty:
                return "_无数据_"
            limited = value.head(200)
            try:
                return limited.to_markdown(index=False)
            except Exception:
                return limited.to_csv(index=False)
        return str(value)

    def _len_safe(self, value: Any) -> int:
        try:
            return len(value)
        except Exception:
            return 0

    def _emoji_for_priority(self, priority: str) -> str:
        return {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(priority, "🟢")

    def _mock_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        total_tickets = self._len_safe(raw_data.get("tickets"))
        total_tg = self._len_safe(raw_data.get("telegram"))
        total_langfuse = self._len_safe(raw_data.get("langfuse_summary"))

        if total_tickets + total_tg + total_langfuse == 0:
            return {
                "summary": "本周期未收集到有效用户反馈数据，暂未识别出需跟进的问题。",
                "issues": [],
            }

        return self._normalize_result(
            {
                "summary": "本周期用户反馈主要集中在提现地址校验理解成本、交易流水批量导出能力缺口，以及交易详情页偶发加载失败三个方向。",
                "issues": [
                    {
                        "category": "concept_confusion",
                        "title": "用户对提现地址校验规则理解困难",
                        "description": "多渠道反馈显示，用户在填写提现地址和 memo/tag 时不清楚校验失败原因，影响提现核心流程。",
                        "priority": "P1",
                        "frequency": 4,
                        "data_sources": ["tickets", "telegram", "langfuse"],
                        "suggestions": [
                            "在提现地址输入区补充 memo/tag 场景说明和示例。",
                            "将校验失败提示从通用报错改为可操作的具体原因。",
                            "在帮助中心增加链和 memo/tag 对应规则说明。",
                        ],
                        "priority_reason": "频次达到 P1 阈值，且影响提现核心流程。",
                    },
                    {
                        "category": "capability_gap",
                        "title": "需要支持批量导出交易流水",
                        "description": "运营和客户反馈当前只能逐账户导出交易流水，批量处理效率较低。",
                        "priority": "P1",
                        "frequency": 3,
                        "data_sources": ["tickets", "telegram", "langfuse"],
                        "suggestions": [
                            "增加按账户组、时间范围批量导出交易流水能力。",
                            "导出任务异步化，完成后通过通知中心或邮件提示。",
                            "补充导出权限和审计日志。",
                        ],
                        "priority_reason": "频次达到 P1 阈值，并影响运营处理效率。",
                    },
                    {
                        "category": "product_issue",
                        "title": "交易详情页偶发加载失败",
                        "description": "部分用户进入交易详情页时出现卡住或加载失败，刷新后恢复，属于已有功能稳定性问题。",
                        "priority": "P2",
                        "frequency": 2,
                        "data_sources": ["tickets", "telegram"],
                        "suggestions": [
                            "补充前端错误埋点，定位失败接口和错误码。",
                            "对详情页接口增加重试和降级展示。",
                            "排查最近 15 天相关接口超时和 5xx 日志。",
                        ],
                        "priority_reason": "频次未达到 P1 阈值，但影响用户体验。",
                    },
                ],
            }
        )
