# VOC 自动化分析工具

每周一 10:00 自动通过 MCP 拉取工单/Telegram/Langfuse 数据 → Claude 分析 → 生成 Excel 周报 → 创建 Phabricator Task，全程无需人工干预。

## 工作方式

```
launchctl 定时触发 (周一 10:00)
  → notify_voc_analysis.sh
    → claude -p --permission-mode bypassPermissions
      → MCP (Superset) 拉数据
      → Claude 按 VOC 框架分析
      → 生成 Excel 周报 (4 Sheet)
      → MCP (Phabricator) 创建 P0/P1 Task
```

全程通过 MCP Server (`mcp-now`)，无需配置数据源 API。

## 快速安装

```bash
git clone https://github.com/yinwang-gif/voc-automation.git
cd voc-automation
./setup.sh
```

setup.sh 自动完成：检查 Claude Code CLI → 配置 API Key → 安装 launchctl 定时任务。

## 前置条件

- Claude Code CLI 已安装 (`npm install -g @anthropic-ai/claude-code`)
- `mcp-now` MCP Server 已配置（包含 Superset + Phabricator 连接）
- API Key：`ANTHROPIC_AUTH_TOKEN` 和 `ANTHROPIC_BASE_URL` 环境变量（setup.sh 会引导填写）

## 数据源（全部通过 MCP）

| 数据源 | MCP Server | Superset Dataset | Chart |
|--------|-----------|-----------------|-------|
| 工单 | mcp-now | 2652 ([Ticket] Ticket List) | 5978 |
| TG 消息 | mcp-now | 2459 ([客户360]Telegram聊天记录) | - |
| AI 对话 | mcp-now | 2812 ([PortalAgent] Langfuse Record) | 6111, 6108 |

详细配置见 `config/settings.json`。

## 输出

每周一执行后在 `~/Desktop/VOC产品洞察分析工具/` 生成：

```
VOC_周报_YYYY-MM-DD.xlsx
```

Excel 包含 4 个 Sheet：

| Sheet | 内容 |
|-------|------|
| 数据概览 | 数据源名称、拉取数量、状态 |
| VOC 分析 | 问题分类、描述、频次、优先级、改进建议 |
| 原始依据 | 工单原文、TG 消息原文、用户原话摘录 |
| PHA Tasks | Task 编号、标题、优先级、Phabricator 链接、状态 |

## 手动测试

```bash
./notify_voc_analysis.sh
```

## 管理定时任务

```bash
# 查看状态
launchctl list | grep voc-analysis

# 停止
launchctl unload ~/Library/LaunchAgents/com.user.voc-analysis.plist

# 重新启动
launchctl load ~/Library/LaunchAgents/com.user.voc-analysis.plist
```

## 配置说明

编辑 `config/settings.json`：

- `data_sources.*.superset_dataset_id` — 各数据源对应的 Superset Dataset ID
- `data_sources.*.superset_chart_id` — 预建的 Superset Chart ID
- `analysis.voc_framework` — VOC 分析框架（概念困扰/能力缺口/产品残留问题）
- `analysis.min_frequency_for_attention` — 触发关注的最低频次阈值
- `phabricator.mcp_tool` — 创建 Task 的 MCP 工具名
- `output.report_dir` — 报告输出目录
- `schedule.cron` — 定时规则（当前：每周一 10:00）
