#!/bin/bash
# VOC 自动化分析 - 全自动执行脚本
# 每周一 10:00 由 launchctl 触发

LOG_DIR="/Users/yin.wang/voc-automation/logs"
LOG_FILE="$LOG_DIR/reminder.log"
ERR_FILE="$LOG_DIR/reminder.error.log"

mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] VOC 分析开始" >> "$LOG_FILE"

# 通知：开始分析
osascript -e 'display notification "正在拉取数据、分析、创建 PHA Task..." with title "📊 VOC 周报分析开始" sound name "Glass"'

# 本周一的日期，作为文件名
REPORT_DATE=$(date '+%Y-%m-%d')
REPORT_DIR="/Users/yin.wang/Desktop/VOC产品洞察分析工具"
REPORT_FILE="$REPORT_DIR/VOC_周报_${REPORT_DATE}.xlsx"

mkdir -p "$REPORT_DIR"

# 加载 shell 环境并执行分析（zsh 会 source .zshrc/.zshenv）
/usr/bin/env zsh -l -c "
cd /Users/yin.wang/voc-automation

claude -p --permission-mode bypassPermissions '
读取 /Users/yin.wang/voc-automation/QUICK_START.md 并执行完整 VOC 分析流程，包括：

- 通过 MCP 拉取数据（工单/Telegram/Langfuse）
- 按 VOC 框架分析
- 创建 Phabricator Tasks

将所有分析结果和 Task 创建结果写入 $REPORT_FILE（Excel 文件），包含以下 Sheet：

Sheet 1「数据概览」：数据源名称、拉取数量、状态、备注
Sheet 2「VOC 分析」：问题分类（概念困扰/能力缺口/产品残留问题）、具体问题描述、频次、优先级（P0/P1/P2）、数据来源（工单号/TG消息ID）、改进建议
Sheet 3「原始依据」：每条问题的原始数据原文，包括工单标题和描述原文、TG 消息原文、用户原话摘录，确保每一条分析结论都有据可查
Sheet 4「PHA Tasks」：Task 编号、标题、优先级、Phabricator 链接、创建状态

全程自动执行，不需要问我确认。
'
" >> "$LOG_FILE" 2>> "$ERR_FILE"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] VOC 分析完成 → $REPORT_FILE" >> "$LOG_FILE"
    osascript -e "display notification \"报告已保存到桌面\" with title \"✅ VOC 周报分析完成\" sound name \"Glass\""
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] VOC 分析失败 (exit code: $EXIT_CODE)" >> "$LOG_FILE"
    osascript -e 'display notification "请检查日志" with title "❌ VOC 周报分析失败" sound name "Basso"'
fi
