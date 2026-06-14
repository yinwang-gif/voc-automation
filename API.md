# API 对接说明

## 工单 API

`collectors/ticket_collector.py` 期望接口返回 list，或返回包含以下任意 key 的 dict：

- `tickets`
- `data`
- `items`
- `results`

推荐字段：

| 字段 | 说明 |
|---|---|
| id | 工单 ID |
| title | 标题 |
| description | 描述 |
| priority | 优先级 |
| status | 状态 |
| product_domain | 产品域 |
| created_at | 创建时间 |
| tags | 标签 |

## Telegram API

`collectors/telegram_collector.py` 期望接口返回 list，或返回包含以下任意 key 的 dict：

- `messages`
- `data`
- `items`
- `results`

推荐字段：

| 字段 | 说明 |
|---|---|
| message_id | 消息 ID |
| text | 消息内容 |
| sender | 发送者 |
| timestamp | 时间 |
| thread_id | 线程 ID |

## Langfuse API

`collectors/langfuse_collector.py` 期望接口返回 list，或返回包含以下任意 key 的 dict：

- `conversations`
- `traces`
- `data`
- `items`
- `results`

推荐字段：

| 字段 | 说明 |
|---|---|
| conversation_id | 对话 ID |
| user_query | 用户问题 |
| ai_response | AI 回复 |
| timestamp | 时间 |
| tags | 标签 |

## 文件数据源

三个 collector 都支持 `file://`：

```json
"api_endpoint": "file:///path/to/tickets.xlsx"
```

支持 `.xlsx`、`.xls`、`.csv`、`.json`。

## Mock 数据源

用于本地测试：

```json
"api_endpoint": "mock://tickets"
```

可用值：

- `mock://tickets`
- `mock://telegram`
- `mock://langfuse`
