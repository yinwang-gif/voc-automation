#!/bin/bash
# 测试 VOC 分析

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🧪 测试 VOC 分析..."
"$DIR/notify_voc_analysis.sh"
echo "✅ 测试完成"
