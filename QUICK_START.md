# VOC 分析快速执行指南

## 🔔 全自动执行（无需任何操作）

每周一 10:00 自动触发，分析完成后收到通知。

## 📝 完整执行指令（用于手动触发）

```
帮我执行 VOC 自动化分析：

1. 通过 MCP 拉取最近 8 天的数据：
   - 工单数据：dataset ID 2652 ([Ticket] Ticket List)，chart 5978
   - TG 消息：dataset ID 2459 ([客户360]Telegram聊天记录)
   - AI 对话：dataset ID 2812 ([PortalAgent] Langfuse Record - Prod & Dev)，charts 6111, 6108

2. 按 VOC 框架分析：
   - 概念困扰 / 能力缺口 / 产品残留问题
   - 识别高频问题（频次 >= 3）
   - 评估优先级（P0/P1/P2）
   - 与历史 VOC 对比

3. 对每个 P0/P1 问题运行产品决策（调用 product-owner-decision skill）：
   - 产出决策：explore / prototype / pilot / enter_prd / pause / stop
   - 给出：决策理由、证据分级、下一步、先别做、是否高风险域
   - 约束：单条反馈不等于已验证需求；高风险域（资金/钱包/签名/KYC/合规/客户数据/对客 ROI）未评审时不得 pilot 或 enter_prd

4. 生成 Excel 报告，包含 5 个 Sheet：
   - 数据概览 / VOC 分析 / 原始依据 / 产品决策 / PHA Tasks
   - 「VOC 分析」增加一列「产品决策」便于对照

5. 创建 Phabricator Tasks（P0/P1）：
   - 使用 mcp__mcp-now__pha_task_create
   - task 描述中附「产品决策建议」（决策 + 下一步 + 先别做 + 高风险提示）
   - 显示创建的 task 链接

全程自动执行，不需要问我确认。
```

## 🧪 手动测试

```bash
./notify_voc_analysis.sh
```

## ⏰ 定时任务管理

### 查看状态
```bash
launchctl list | grep voc-analysis
```

### 停止
```bash
launchctl unload ~/Library/LaunchAgents/com.user.voc-analysis.plist
```

### 重启
```bash
launchctl load ~/Library/LaunchAgents/com.user.voc-analysis.plist
```

### 修改时间
编辑 `setup.sh` 中的 StartCalendarInterval（Weekday/Hour/Minute），重新运行 `./setup.sh`

## 🔄 工作流程（全自动）

```
周一 10:00
   ↓
系统通知："VOC 周报分析开始"
   ↓
Claude Code 自动执行：
  1. MCP 拉取数据（Superset）
  2. VOC 框架分析
  3. 对 P0/P1 跑产品决策（product-owner-decision skill）
  4. 生成 Excel 报告（5 Sheet）
  5. MCP 创建 Phabricator Tasks（附决策建议）
   ↓
系统通知："✅ VOC 周报分析完成"
   ↓
查看报告和 Tasks
```

## ✅ 零配置优势

- ✅ 无需数据源 API（通过 MCP 拉取）
- ✅ 无需 Phabricator API（通过 MCP 创建 task）
- ✅ 全自动执行（周一 10:00 自动触发）
- ✅ 实时通知（分析开始/完成均有系统通知）
