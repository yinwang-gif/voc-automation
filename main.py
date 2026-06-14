from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

from scheduler.workflow_runner import WorkflowRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VOC 自动化分析工具")
    parser.add_argument(
        "--config",
        default="config/settings.json",
        help="配置文件路径，默认 config/settings.json",
    )
    return parser.parse_args()


def main() -> int:
    if load_dotenv:
        load_dotenv()

    args = parse_args()
    config_path = Path(args.config).expanduser()
    runner = WorkflowRunner(str(config_path))
    result = runner.run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
