# VOC 自动化分析工具

定期自动收集 VOA/VOC 数据，进行 AI 分析，生成 Markdown / Excel 报告，并将 P0/P1 优先建议输出为待执行的 Phabricator task 清单。

## 目录结构

```text
voc-automation/
├── config/
│   ├── settings.json
│   ├── test_settings.json
│   └── voc-framework.json
├── collectors/
├── analyzers/
├── reporters/
├── integrations/
├── scheduler/
├── skills/voc-automation.skill/
├── tests/
├── main.py
└── requirements.txt
```

## 安装

```bash
cd /Users/yin.wang/voc-automation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

在 `.env` 中填写：

```bash
ANTHROPIC_API_KEY=your_claude_api_key
TICKET_API_TOKEN=your_ticket_api_token
TELEGRAM_BOT_TOKEN=your_tg_bot_token
LANGFUSE_API_KEY=your_langfuse_key
```

## 配置

编辑 `config/settings.json`：

- `data_sources.tickets.api_endpoint`：工单 API
- `data_sources.telegram.api_endpoint`：TG 消息 API
- `data_sources.langfuse.api_endpoint`：Langfuse 数据 API
- `output.report_dir`：报告输出目录，默认 `/Users/yin.wang/Desktop/VOC产品洞察分析工具`
- `phabricator.priority_threshold`：默认只为 P0/P1 创建待处理 task

## 手动执行

```bash
cd /Users/yin.wang/voc-automation
python main.py
```

测试配置可以这样运行：

```bash
python main.py --config config/test_settings.json
```

## Claude Code 中使用

```text
帮我执行 VOC 自动化：
1. 运行 /Users/yin.wang/voc-automation/main.py
2. 读取生成的 pending_pha_tasks.json
3. 调用 MCP 工具创建所有 Phabricator task
```

Skill 入口位于：

```text
skills/voc-automation.skill/skill.py
```

## 输出文件

运行完成后，`output.report_dir` 下会生成：

- `VOC_分析报告_YYYYMMDD.md`
- `VOC_分析结论表_YYYYMMDD.xlsx`
- `执行摘要_YYYYMMDD.txt`
- `pending_pha_tasks.json`

`pending_pha_tasks.json` 会保存类似：

```json
[
  {
    "tool": "mcp__mcp-now__pha_task_create",
    "params": {
      "title": "问题标题",
      "description": "详细描述"
    },
    "status": "pending",
    "created_at": "2026-06-14T10:00:00"
  }
]
```

## 定时执行

在 Claude Code 中创建定时任务：

```text
帮我设置一个定时任务，每周一早上 9 点运行 /Users/yin.wang/voc-automation/main.py
```

或使用 skill：

```bash
/schedule --cron "0 9 * * 1" --prompt "/voc-automation" --description "每周一早上9点执行VOC分析"
```

## 测试

```bash
pytest -q
```

测试使用 `config/test_settings.json` 和 mock 数据，不会调用真实外部 API。
