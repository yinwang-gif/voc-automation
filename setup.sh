#!/bin/bash
# VOC 自动化分析 — 一键安装脚本
set -e

echo "=== VOC 自动化分析 安装 ==="
echo ""

# 1. 检查 Claude Code CLI
if ! command -v claude &> /dev/null; then
    echo "❌ 未找到 claude CLI，请先安装：npm install -g @anthropic-ai/claude-code"
    exit 1
fi
echo "✅ Claude Code CLI 已安装"

# 2. 设置项目路径
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "📁 项目路径: $PROJECT_DIR"

# 3. 配置 API Key
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo ""
    echo "请输入你的 ANTHROPIC_AUTH_TOKEN（Claude API Key）："
    read -r API_KEY
    cat > "$PROJECT_DIR/.env" << EOF
ANTHROPIC_AUTH_TOKEN=${API_KEY}
ANTHROPIC_BASE_URL=https://litellm.sandbox.1cobo.com
ANTHROPIC_MODEL=claude-sonnet-4-5@20250929
ANTHROPIC_DEFAULT_HAIKU_MODEL=gemini-2.5-flash
EOF
    echo "✅ .env 已创建"
else
    echo "✅ .env 已存在，跳过"
fi

# 4. 复制 Claude Code MCP 权限配置
CLAUDE_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_DIR"
if [ -f "$PROJECT_DIR/.claude/settings.json" ]; then
    echo "📋 MCP 权限配置在 .claude/settings.json"
    echo "   请确保 claude code 已加载 mcp-now server"
fi

# 5. 安装 launchctl 定时任务
PLIST_SRC="$PROJECT_DIR/com.user.voc-analysis.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.user.voc-analysis.plist"

# 生成 plist（替换路径）
cat > "$PLIST_SRC" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.voc-analysis</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PROJECT_DIR}/notify_voc_analysis.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key><integer>1</integer>
        <key>Hour</key><integer>10</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${PROJECT_DIR}/logs/reminder.log</string>
    <key>StandardErrorPath</key>
    <string>${PROJECT_DIR}/logs/reminder.error.log</string>
    <key>RunAtLoad</key><false/>
    <key>WorkingDirectory</key>
    <string>${PROJECT_DIR}</string>
</dict>
</plist>
PLIST

mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DST"
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"
echo "✅ 定时任务已安装（每周一 10:00）"

# 6. 创建输出目录
OUTPUT_DIR="$HOME/Desktop/VOC产品洞察分析工具"
mkdir -p "$OUTPUT_DIR"
echo "✅ 输出目录: $OUTPUT_DIR"

echo ""
echo "=== 安装完成 ==="
echo ""
echo "⏰ 每周一 10:00 自动执行 VOC 分析"
echo "📊 结果输出到: $OUTPUT_DIR/"
echo ""
echo "🧪 手动测试: $PROJECT_DIR/test_notification.sh"
echo "📋 查看日志: cat $PROJECT_DIR/logs/reminder.log"
