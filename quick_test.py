#!/usr/bin/env python3
"""
快速测试脚本 - 使用现有的 VOC 分析报告测试工具

用法：
    python quick_test.py /path/to/VOC_近半月用户反馈分析_20260612.md
"""

import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def extract_suggestions_from_md(md_path: Path):
    """从现有的 MD 报告中提取建议"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 简单解析：找到第一个 P0/P1 建议
    suggestions = []
    lines = content.split('\n')

    current_suggestion = {}
    in_suggestion = False

    for line in lines:
        # 检测建议开始
        if '#### 🔴 P0/P1' in line or '#### 🟡 P1' in line:
            if current_suggestion:
                suggestions.append(current_suggestion)
            current_suggestion = {
                'priority': 'P0' if '🔴' in line else 'P1',
                'title': line.replace('####', '').replace('🔴', '').replace('🟡', '').replace('P0/P1', '').replace('P1', '').strip().split('-')[0].strip(),
                'description': '',
                'suggestions': []
            }
            in_suggestion = True
        elif in_suggestion:
            if line.startswith('**建议：**') or line.startswith('**建议操作：**'):
                # 接下来的内容是建议
                continue
            elif line.startswith('####') or line.startswith('---'):
                # 下一个段落开始
                if current_suggestion:
                    suggestions.append(current_suggestion)
                    current_suggestion = {}
                in_suggestion = False
            elif line.strip():
                if not current_suggestion['description']:
                    current_suggestion['description'] += line.strip() + '\n'
                elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                    current_suggestion['suggestions'].append(line.strip())

    if current_suggestion:
        suggestions.append(current_suggestion)

    return suggestions


def create_pending_tasks(suggestions, output_dir: Path):
    """生成待办任务清单"""
    pending_tasks = []

    for i, suggestion in enumerate(suggestions[:3], 1):  # 只取前3个
        task = {
            'tool': 'mcp__mcp-now__pha_task_create',
            'params': {
                'title': suggestion['title'],
                'description': f"""## 问题背景
根据 VOC 用户反馈分析报告，该问题被标记为 {suggestion['priority']} 优先级。

{suggestion['description']}

## 建议操作
{chr(10).join(suggestion['suggestions'])}

---
**数据来源：** VOC 自动化分析工具（快速测试）
**分析时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            },
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        pending_tasks.append(task)

    # 保存到文件
    output_file = output_dir / 'pending_pha_tasks.json'
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pending_tasks, f, ensure_ascii=False, indent=2)

    return output_file, pending_tasks


def main():
    if len(sys.argv) < 2:
        md_file = Path('/Users/yin.wang/Desktop/VOC产品洞察分析工具/VOC_近半月用户反馈分析_20260612.md')
        print(f"📄 使用默认报告文件: {md_file}")
    else:
        md_file = Path(sys.argv[1])

    if not md_file.exists():
        print(f"❌ 文件不存在: {md_file}")
        return 1

    print(f"\n🚀 开始快速测试...")
    print(f"📖 读取报告: {md_file}")

    # 提取建议
    suggestions = extract_suggestions_from_md(md_file)
    print(f"✅ 提取到 {len(suggestions)} 个建议")

    # 生成待办任务清单
    output_dir = Path('/Users/yin.wang/Desktop/VOC产品洞察分析工具')
    output_file, pending_tasks = create_pending_tasks(suggestions, output_dir)

    print(f"\n📋 生成待办任务清单: {output_file}")
    print(f"   共 {len(pending_tasks)} 个待创建的 task\n")

    # 显示待办任务
    for i, task in enumerate(pending_tasks, 1):
        print(f"{'='*60}")
        print(f"Task {i}: {task['params']['title']}")
        print(f"{'='*60}")
        print(task['params']['description'][:200] + '...\n')

    print(f"\n✅ 测试完成！")
    print(f"\n📌 下一步：在 Claude Code 中执行")
    print(f"   帮我读取 {output_file} 并创建所有 Phabricator task")

    return 0


if __name__ == '__main__':
    sys.exit(main())
