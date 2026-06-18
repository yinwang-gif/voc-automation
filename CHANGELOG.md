# Changelog

## 0.2.0

- 集成 product-owner-decision skill：VOC 分析后对 P0/P1 问题自动运行产品决策。
- 新增 `analyzers/decision_analyzer.py`（DecisionAnalyzer，支持 mock 与高风险守门）。
- WorkflowRunner 流程从 5 步扩展为 6 步，新增「产品决策」环节。
- Markdown / Excel 报告与 Phabricator task 描述增加产品决策内容。
- 生产路径（QUICK_START.md / notify_voc_analysis.sh）增加决策步骤与「产品决策」Sheet。
- 项目内置 skill 副本于 `skills/product-owner-decision/`；新增决策模块单元测试。

## 0.1.0

- 初始化 VOC 自动化项目结构。
- 实现工单、Telegram、Langfuse 三个数据收集器。
- 实现 Claude VOC 分析封装和 mock 分析模式。
- 实现 Markdown / Excel 报告生成。
- 实现 Phabricator MCP 待处理 task 清单生成。
- 实现 WorkflowRunner 端到端流程。
- 增加 Claude Code skill wrapper。
- 增加单元测试和集成测试。
