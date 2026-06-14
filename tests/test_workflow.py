from __future__ import annotations

import json
import os
from pathlib import Path

from scheduler.workflow_runner import WorkflowRunner


def test_full_workflow():
    output_dir = Path("/tmp/voc-automation-output")
    pending_file = output_dir / "pending_pha_tasks.json"
    if pending_file.exists():
        pending_file.unlink()

    runner = WorkflowRunner("config/test_settings.json")
    result = runner.run()
    assert result["success"] is True
    assert os.path.exists(result["reports"][0])
    assert os.path.exists(result["reports"][1])
    assert os.path.exists(result["summary"])
    assert pending_file.exists()

    with pending_file.open("r", encoding="utf-8") as f:
        pending_tasks = json.load(f)
    assert len(pending_tasks) == 2
    assert pending_tasks[0]["tool"] == "mcp__mcp-now__pha_task_create"
