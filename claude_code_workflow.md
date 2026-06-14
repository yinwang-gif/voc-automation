# VOC 自动化分析 - 纯 Claude Code 工作流

## 核心思想
不需要复杂的 Python 脚本，直接在 Claude Code 中：
1. 通过 Superset MCP 拉取数据（SQL 查询）
2. 直接让 Claude 分析（利用当前对话的 Claude）
3. 通过 Phabricator MCP 创建 task

**优势：**
- ✅ 无需额外 API key（除了 Claude 自己的）
- ✅ 所有工具现成（MCP server 已连接）
- ✅ 实时交互，可随时调整
- ✅ 结果直接可见

---

## 工作流步骤

### Step 1: 拉取工单数据

```sql
-- 在 Claude Code 中说：
帮我执行 SQL 查询，拉取最近 8 天的工单数据：

SELECT 
    id,
    title,
    description,
    priority,
    status,
    product_domain,
    created_at,
    tags
FROM tickets
WHERE created_at >= NOW() - INTERVAL '15 days'
ORDER BY created_at DESC
```

使用 MCP 工具：`mcp__mcp-now__execute_sql`

---

### Step 2: 拉取 TG 消息数据

```sql
-- 在 Claude Code 中说：
帮我执行 SQL 查询，拉取最近 8 天的 TG 消息：

SELECT 
    message_id,
    text,
    sender,
    timestamp,
    thread_id
FROM telegram_messages
WHERE timestamp >= NOW() - INTERVAL '15 days'
    AND channel_id = 'YOUR_CHANNEL_ID'
ORDER BY timestamp DESC
```

使用 MCP 工具：`mcp__mcp-now__execute_sql`

---

### Step 3: 拉取 AI 对话数据（Langfuse）

```sql
-- 在 Claude Code 中说：
帮我执行 SQL 查询，拉取最近 8 天的 AI 对话摘要：

SELECT 
    conversation_id,
    user_query,
    ai_response,
    timestamp,
    tags
FROM langfuse_conversations
WHERE timestamp >= NOW() - INTERVAL '15 days'
ORDER BY timestamp DESC
LIMIT 100
```

使用 MCP 工具：`mcp__mcp-now__execute_sql`

---

### Step 4: Claude 分析（直接在对话中）

```text
请基于以上数据，按照 VOC 框架进行分析：

1. 概念困扰 - 用户反复问"为什么/怎么理解"
2. 能力缺口 - 用户需要功能，产品没提供
3. 产品残留问题 - 已有功能不好用

要求：
- 识别高频问题（出现 >= 3 次）
- 评估优先级（P0/P1/P2）
- 提供具体改进建议
- 与历史 VOC（/Users/yin.wang/Desktop/VOC产品洞察分析工具/VOC_三类问题分析结论表_20260612.xlsx）对比

输出格式：
- Markdown 报告
- 提取前 3 个 P0/P1 建议，准备创建 Phabricator task
```

**Claude 会直接分析并生成报告**（不需要额外 API 调用）

---

### Step 5: 生成 Markdown 报告

```text
请将分析结果保存为 Markdown 报告：
/Users/yin.wang/Desktop/VOC产品洞察分析工具/VOC_分析报告_{今天日期}.md
```

使用工具：`Write`

---

### Step 6: 创建 Phabricator Tasks

```text
请为以下 3 个 P0/P1 建议创建 Phabricator task：

1. [建议标题 1]
2. [建议标题 2]
3. [建议标题 3]

使用 mcp__mcp-now__pha_task_create
```

使用 MCP 工具：`mcp__mcp-now__pha_task_create`

---

## 一键执行版本（完整 Prompt）

```text
帮我执行 VOC 自动化分析：

1. 通过 Superset MCP 拉取最近 8 天的数据：
   - 工单：execute_sql 查询 tickets 表
   - TG 消息：execute_sql 查询 telegram_messages 表
   - AI 对话：execute_sql 查询 langfuse_conversations 表

2. 分析数据，按 VOC 框架分类：
   - 概念困扰 / 能力缺口 / 产品残留问题
   - 识别高频问题和优先级
   - 与历史 VOC 对比（读取 /Users/yin.wang/Desktop/VOC产品洞察分析工具/VOC_三类问题分析结论表_20260612.xlsx）

3. 生成报告：
   - 保存 Markdown 到 /Users/yin.wang/Desktop/VOC产品洞察分析工具/VOC_分析报告_{今天日期}.md

4. 创建 Phabricator Tasks：
   - 为前 3 个 P0/P1 建议创建 task
   - 使用 mcp__mcp-now__pha_task_create
   - 显示创建的 task 链接
```

---

## 优势对比

### 方案 A: Python 脚本（之前的方案）
```
Python 收集数据 → Claude API 分析 → 生成 pending_pha_tasks.json → Claude Code 执行 MCP
```
**问题：**
- 需要配置多个 API key
- 需要维护 Python 代码
- 数据收集和分析分离

### 方案 B: 纯 Claude Code（新方案）
```
Claude Code (MCP 拉数据) → Claude 分析 → Claude Code (MCP 创建 task)
```
**优势：**
- 只需要当前 Claude Code session
- 所有工具现成（MCP server）
- 实时可见、可调整
- 无需额外配置

---

## 数据库表结构（需要确认）

### 工单表
```sql
-- 需要确认实际表名和字段
SELECT * FROM tickets LIMIT 1;
-- 或
SELECT * FROM cobo_tickets LIMIT 1;
```

### TG 消息表
```sql
SELECT * FROM telegram_messages LIMIT 1;
```

### Langfuse 表
```sql
SELECT * FROM langfuse_conversations LIMIT 1;
```

**在 Claude Code 中执行：**
```
帮我列出 Superset 中所有可用的数据集：
mcp__mcp-now__list_datasets
```

---

## 定时自动化

### 方式 1: Claude Code Cron
```text
帮我创建定时任务，每周一早上 9:10 执行上面的完整 VOC 分析流程
```

### 方式 2: 手动触发
每周在 Claude Code 中说：
```
执行 VOC 分析（按照 voc-automation/claude_code_workflow.md）
```

---

## 总结

**配置需求：** 无（所有工具通过 MCP，Claude 就是当前对话）

**执行方式：** 直接在 Claude Code 中对话

**优势：** 最简单、最灵活、最透明

**适用场景：** 你已经有 MCP server 连接，且希望快速迭代调整分析逻辑
