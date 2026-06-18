# Product Owner Decision Contracts

Version: v1
Status: Pilot

## Output Contract

Every run should produce:

- Intent（问题判断）
- Builder（最小验证方案）
- Seller（谁真的需要）
- Measurer（怎么判断有效）
- Critic（风险和反对意见）
- Archive（结论和下一步）
- Evidence（证据表）
- Decision
- Do Next
- Do Not Do Yet

## Allowed Decisions

Choose one primary decision:

| Decision | Use when | Not allowed when |
| --- | --- | --- |
| `explore` | Intent is plausible but evidence is incomplete | There is strong contradiction or unacceptable risk |
| `prototype` | A small proof can test value and feasibility | No user/adopter is clear or value cannot be tested |
| `pilot` | A real adopter is ready, metrics are observable, and risk boundaries are clear | High-risk review is unresolved or evidence is only internal belief |
| `enter_prd` | Builder/Seller/Measurer evidence is sufficient and owner commits next-stage review | Seller proof is guesswork or Measurer has no decision metric |
| `pause` | Key evidence, owner, timing, or resources are missing but can be resolved | The output does not state what must be learned next |
| `stop` | Strong contradiction, unacceptable risk, no user pull, no buildable path, or no measurable decision exists | The rationale is only "not good enough" |

## Evidence（证据表）

Each important claim must have one ledger row:

| Field | Required |
| --- | --- |
| Claim | yes |
| Level | `Fact` / `Assumption` / `Needs validation` / `Contradiction` |
| Source | yes |
| Decision relevance | yes |
| Needed validation | yes when not `Fact` |
| Owner | yes, or `missing` |

Evidence levels:

- `Fact`: directly provided by user or cited/verifiable source.
- `Assumption`: reasonable inference not yet validated.
- `Needs validation`: important claim requiring data, research, interview, or experiment.
- `Contradiction`: conflicting evidence or strong counterexample.

## Lane Evidence

Builder（最小验证方案）, Seller（谁真的需要）, and Measurer（怎么判断有效） must each include:

| Field | Allowed values / format |
| --- | --- |
| Input source | person, document, dataset, example, or `missing` |
| Current strength | `strong`, `medium`, `weak`, `missing` |
| Missing evidence | short list |
| Next validation | concrete validation action |
| Owner | named role/person or `missing` |

## PRD Entry Gate

Recommend `enter_prd` only when all conditions are true:

- Intent Owner and human owner are explicit.
- Builder（最小验证方案） includes MVP/prototype boundary and non-goals.
- Seller（谁真的需要） includes target adopter, current alternative, and objection or validation motion.
- Measurer（怎么判断有效） includes success, guardrail, and kill criteria.
- Evidence（证据表） has no unsupported strong claim.
- High-risk domains have required reviewer and mandatory controls.
- Owner explicitly accepts next-stage resourcing or review.

If any condition fails, choose `explore`, `prototype`, `pause`, or `stop`.

## High-Risk Gate

High-risk domains include asset movement, wallet policy, signing/key management, KYC/AML/compliance, customer data, internal confidential docs, and customer-facing ROI/fee/safety/yield claims.

When relevant, include:

| Field | Required value |
| --- | --- |
| High-risk domain detected | `yes` / `no` |
| Risk domain | concrete domain |
| Mandatory controls | concrete controls or `missing` |
| Required reviewer | PM, Security, Compliance, Legal, Data owner, Engineering owner, or `missing` |
| Blocked until review | `yes` / `no` |

Rules:

- Asset movement, signing, custody, and irreversible on-chain operations cannot be recommended as autonomous execution.
- Wallet policy changes are draft-only until schema validation, simulator/dry-run, human approval, and audit trail exist.
- KYC/AML/compliance outputs cannot make final compliance decisions.
- Customer data use requires permission boundary and PII handling.
- Customer-facing ROI, fee, safety, or yield claims require evidence and the relevant reviewer.
- If high-risk review is unresolved, the final decision cannot be `pilot` or `enter_prd`.

## Knowledge Publication

Default state for all generated artifacts is `draft`.

Canonical publication requires:

- explicit owner confirmation
- facts, assumptions, needs validation, and contradictions labeled
- sensitive customer material sanitized and permitted
- high-risk reviewer approval when relevant
- clear target location and reuse purpose

Do not claim a document, task, or Knowledge Hub article was created unless a tool actually created it.
