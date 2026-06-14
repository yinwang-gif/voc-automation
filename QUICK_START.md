# VOC 分析快速执行指南

## 🔔 全自动执行（无需任何操作）

每周一 10:00 自动触发，分析完成后收到通知。

## 📝 完整执行指令（复制粘贴）

```
帮我执行 VOC 自动化分析：

1. 通过 MCP 拉取最近 15 天的数据：
   - 工单数据：dataset ID 2652 ([Ticket] Ticket List)
   - TG 消息：dataset ID 2459 ([客户360]Telegram聊天记录)
   - AI 对话：dataset ID 2812 ([PortalAgent] Langfuse Record - Prod & Dev)

2. 按 VOC 框架分析：
   - 概念困扰 / 能力缺口 / 产品残留问题
   - 识别高频问题（频次 >= 3）
   - 评估优先级（P0/P1/P2）
   - 与历史 VOC 对比（读取 /Users/yin.wang/Desktop/VOC产品洞察分析工具/VOC_三类问题分析结论表_20260612.xlsx）

3. 生成报告：
   - 保存 Markdown 到 /Users/yin.wang/Desktop/VOC产品洞察分析工具/VOC_分析报告_{今天日期}.md
   - 可选：生成 Excel 报告

4. 创建 Phabricator Tasks：
   - 为前 3 个 P0/P1 建议创建 task
   - 使用 mcp__mcp-now__pha_task_create
   - 显示创建的 task 链接
```

---

## 🎯 简化版（一句话触发）

```
读取 /Users/yin.wang/voc-automation/QUICK_START.md 并执行完整 VOC 分析流程
```

---

## 🧪 测试通知（立即触发）

如果想测试通知是否正常，在终端执行：
```bash
/Users/yin.wang/voc-automation/notify_voc_analysis.sh
```

应该会看到系统通知弹出。

---

## ⏰ 定时任务管理

### 查看定时任务状态
```bash
launchctl list | grep voc-analysis
```

### 停止定时任务
```bash
launchctl unload /Users/yin.wang/Library/LaunchAgents/com.user.voc-analysis-reminder.plist
```

### 重新启动定时任务
```bash
launchctl load /Users/yin.wang/Library/LaunchAgents/com.user.voc-analysis-reminder.plist
```

### 查看日志
```bash
# 通知日志
cat /Users/yin.wang/voc-automation/logs/reminder.log

# 错误日志
cat /Users/yin.wang/voc-automation/logs/reminder.error.log
```

---

## 📅 定时设置

**当前设置：** 每周一早上 10:00

**修改时间：**
编辑文件 `/Users/yin.wang/Library/LaunchAgents/com.user.voc-analysis-reminder.plist`

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Weekday</key>
    <integer>1</integer>  <!-- 0=周日, 1=周一, 2=周二... -->
    <key>Hour</key>
    <integer>9</integer>  <!-- 小时（24小时制）-->
    <key>Minute</key>
    <integer>10</integer> <!-- 分钟 -->
</dict>
```

修改后重新加载：
```bash
launchctl unload /Users/yin.wang/Library/LaunchAgents/com.user.voc-analysis-reminder.plist
launchctl load /Users/yin.wang/Library/LaunchAgents/com.user.voc-analysis-reminder.plist
```

---

## 🔄 工作流程（全自动）

```
周一 10:00
   ↓
系统通知："VOC 周报分析开始"
   ↓
Claude Code 自动执行：
  1. 拉取数据（MCP）
  2. AI 分析
  3. 生成报告
  4. 创建 Phabricator Tasks
   ↓
系统通知："✅ VOC 周报分析完成"
   ↓
查看报告和 Tasks
```

---

## ✅ 零配置优势

- ✅ 无需 Anthropic API key（使用当前 Claude Code 会话）
- ✅ 无需数据源 API（通过 MCP 拉取）
- ✅ 无需 Phabricator API（通过 MCP 创建 task）
- ✅ 灵活可控（你决定何时执行）
- ✅ 实时可见（所有过程在对话中展示）
