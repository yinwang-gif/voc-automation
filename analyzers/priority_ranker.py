from __future__ import annotations

from typing import Any, Dict, List


class PriorityRanker:
    """优先级排序器。"""

    priority_order = {"P0": 0, "P1": 1, "P2": 2}

    def rank(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(
            issues,
            key=lambda issue: (
                self.priority_order.get(issue.get("priority", "P2"), 3),
                -int(issue.get("frequency", 0) or 0),
                issue.get("title", ""),
            ),
        )
