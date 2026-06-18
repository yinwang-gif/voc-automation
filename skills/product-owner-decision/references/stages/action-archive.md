# Archive（结论和下一步）

Turn product thinking into organizational memory and next action.

## Do

- Produce final artifact summary.
- Choose one decision: `explore`, `prototype`, `pilot`, `enter_prd`, `pause`, or `stop`.
- Recommend archive location and lifecycle state.
- Recommend 1-3 next actions.
- Recommend task creation only when concrete.
- Identify reusable skill/playbook/template opportunities.
- Distinguish draft artifacts from canonical knowledge.
- State Knowledge Hub save status honestly.

## Do Not

- Claim a task was created unless tool call succeeded.
- Claim a document was saved unless tool call succeeded.
- Save draft, sensitive, or high-risk material as canonical without owner confirmation and required review.
- Hide unresolved questions.
- End without action.

## Output

```md
## Archive（结论和下一步）

## Final Artifact Summary

- Intent（问题判断）:
- Builder（最小验证方案）:
- Seller（谁真的需要）:
- Measurer（怎么判断有效）:
- Critic（风险和反对意见）:

## Decision

- Decision: explore / prototype / pilot / enter_prd / pause / stop
- Rationale:
- PRD Entry Gate: pass / fail
- High-risk blocked: yes / no

## Archive Recommendation

| Artifact | Lifecycle state | Location | Reason |
| --- | --- | --- | --- |

Lifecycle states: draft / owner-reviewed / canonical / superseded / stale / inconclusive.

## Next Actions

| Action | Owner | Priority | Output |
| --- | --- | --- | --- |

## Task Readiness

| Task | Owner | Deadline | Acceptance Criteria | Readiness |
| --- | --- | --- | --- | --- |

Readiness values: ready / needs owner / needs validation / blocked.

## Do Next

1. ...

## Do Not Do Yet

- ...

## Reusable Knowledge

- Skill / template candidate:
- Memory candidate:
- Research follow-up:

## Knowledge Hub Save Status

- Save requested by user: yes / no
- Tool available and succeeded: yes / no
- Saved location:
- If not saved, suggested local path:

## Gate

Conclusion: Pass / Needs input / Blocked
Reason:
```
