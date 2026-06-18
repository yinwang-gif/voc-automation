# Knowledge Lifecycle

The skill must work without a knowledge base. Use this reference when the user asks for examples, prior decisions, standards, saved artifacts, or when a high-risk Cobo domain appears.

## Artifact Lifecycle

All run artifacts are `draft` by default.

| State | Meaning |
| --- | --- |
| draft | Generated or working artifact, not owner-reviewed |
| owner-reviewed | Human owner has reviewed and accepted it as useful working material |
| canonical | Approved for future reuse as organizational knowledge |
| superseded | Replaced by a newer decision, brief, or guardrail |
| stale | Evidence is old or no longer reliable |
| inconclusive | Validation was run but did not support a clear decision |

## Use Protocol

Use existing knowledge as context, not proof that the current case is true.

- Examples help with structure.
- Prior decisions help with precedent.
- Guardrails help with risk boundaries.
- Evidence ledgers help with claim discipline.

If no relevant knowledge is available, say so and continue with explicit assumptions.

## Save Rules

Save only after Archive（结论和下一步） or final full-pass output, and only when the user asks to save or explicitly confirms archive.

Do not save:

- intermediate drafts
- unresolved brainstorming
- sensitive customer or internal details without permission and sanitization
- generated claims that are not labeled as assumptions
- high-risk recommendations before required review
- raw customer feedback as canonical knowledge

## Canonical Publication

Canonical knowledge requires all of the following:

- owner explicitly confirms save
- facts / assumptions / needs validation / contradictions are labeled
- sensitive customer material is sanitized and permitted
- high-risk content has required reviewer approval or is clearly marked unresolved
- archive path and reuse purpose are clear

Agent-generated judgments are not canonical until owner-reviewed.

## High-Risk Publication

High-risk materials must remain draft unless the required reviewer approves them.

| Domain | Required reviewer |
| --- | --- |
| Asset movement, signing, custody, wallet policy | PM + Security + Engineering owner |
| KYC / AML / compliance | Compliance owner |
| Customer-sensitive data | Data owner + Security |
| Internal strategy or confidential docs | Document owner / leadership owner |
| Customer-facing ROI, fee, safety, or yield claims | PM + Legal/Compliance as applicable |

If applicability is unclear, mark `Needs validation` and keep the artifact draft.
