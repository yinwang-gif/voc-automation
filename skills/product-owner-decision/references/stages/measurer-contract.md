# Measurer（怎么判断有效）

Define what evidence would make the team continue, change, pause, or stop.

## Do

- Define output metric and input metrics.
- Define qualitative and quantitative evidence separately.
- Define experiment or observation plan.
- Define success criteria, guardrails, and kill criteria.
- Include Cobo risk guardrails when relevant.
- For AI Agent / Hybrid products, define agent evaluation metrics and review method.
- For data products, define source, owner, grain, delay, missing rate, and permissions.
- Add lane evidence fields.

## Do Not

- Use vanity metrics without decision use.
- Leave success undefined until after launch.
- Ignore safety/compliance/asset guardrails.
- Recommend `pilot` or `enter_prd` when value cannot be observed.

## Output

```md
## Measurer（怎么判断有效）

- Behavior to change:
- Current baseline:
- Desired change:
- Decision this measurement supports:

## Metrics Tree

| Level | Metric | Decision use |
| --- | --- | --- |

## Evidence Plan

| Evidence | Type | Collection method | Owner |
| --- | --- | --- | --- |

## Criteria

| Type | Criteria |
| --- | --- |
| Success | |
| Guardrail | |
| Kill | |

## Lane Evidence

| Field | Value |
| --- | --- |
| Input source | |
| Current strength | strong / medium / weak / missing |
| Missing evidence | |
| Next validation | |
| Owner | |

## Review Cadence

- ...

## Gate

Conclusion: Pass / Needs input / Blocked
Reason:
```
