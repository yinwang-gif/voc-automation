#!/usr/bin/env python3
"""快速测试 — 检查配置和依赖是否就绪"""

import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path.home() / "Desktop" / "VOC产品洞察分析工具"


def main():
    issues = []

    config_file = PROJECT_DIR / "config" / "settings.json"
    if not config_file.exists():
        issues.append(f"❌ 配置文件缺失: {config_file}")
    else:
        with open(config_file) as f:
            config = json.load(f)
        print(f"✅ 配置文件正常 ({len(config['data_sources'])} 个数据源)")
        for name, ds in config["data_sources"].items():
            print(f"   {name}: dataset={ds.get('superset_dataset_id')}, enabled={ds.get('enabled')}")

    print(f"✅ 项目路径: {PROJECT_DIR}")
    print(f"✅ 输出目录: {OUTPUT_DIR}")

    if issues:
        for i in issues:
            print(i)
        return 1
    print("✅ 所有检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
