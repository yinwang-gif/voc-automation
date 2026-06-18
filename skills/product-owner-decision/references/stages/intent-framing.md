# Intent Framing

Turn messy input into a clear Intent（问题判断）.

## Do

- Extract target user, problem, desired behavior change, timing, constraints, and product type.
- Identify source type: idea, customer feedback, strategy question, or existing product.
- Identify Intent Owner and human owner.
- Identify decisions that cannot be delegated to the agent.
- Separate facts, assumptions, needs validation, and contradictions.

## Do Not

- Write a PRD.
- Propose a full solution too early.
- Invent missing facts.
- Skip to feature list.

## Output

```md
## Intent（问题判断）

- Topic:
- Target user:
- Desired behavior change:
- Why now:
- Target decision: explore / prototype / pilot / enter_prd / pause / stop
- Product type: Traditional / AI Agent / Hybrid / Unknown
- Source type: Idea / Customer Feedback / Strategy Question / Existing Product
- Intent Owner:
- Human owner:
- Non-goals:
- Decisions not delegated to agent:

## Evidence Notes

| Claim | Level | Source | Decision relevance | Needed validation | Owner |
| --- | --- | --- | --- | --- | --- |

## Gate

Conclusion: Pass / Needs input / Blocked
Reason:
```
