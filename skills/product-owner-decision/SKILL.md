---
name: product-owner-decision
description: Use when the user asks to run 产品决策 / product decision on customer feedback, product ideas, internal requests, technical opportunities, or PRD-prep questions. Produces an evidence-backed decision: explore, prototype, pilot, enter_prd, pause, or stop.
---

# Product Owner Decision

Use this skill when the user says things like:

- "帮我跑一下产品决策"
- "这个反馈帮我做个产品决策"
- "先别写 PRD，判断要不要继续做"
- "这个需求客户催得很急，帮我看证据和风险"

## Core Output

Run the Product Owner Decision Playbook and produce:

- Intent（问题判断）
- Builder（最小验证方案）
- Seller（谁真的需要）
- Measurer（怎么判断有效）
- Critic（风险和反对意见）
- Archive（结论和下一步）
- Evidence（证据表）
- Decision: `explore` / `prototype` / `pilot` / `enter_prd` / `pause` / `stop`
- Do Next
- Do Not Do Yet

## Workflow

1. Treat raw customer feedback, tickets, insights, product ideas, or internal requests as input evidence.
2. Separate facts from assumptions, needs validation, and contradictions.
3. Build three evidence lanes:
   - Builder（最小验证方案）: smallest buildable or fakeable proof.
   - Seller（谁真的需要）: who cares, current alternative, objections, validation motion.
   - Measurer（怎么判断有效）: success, guardrail, kill criteria, data/eval feasibility.
4. Run Critic（风险和反对意见） before recommending escalation.
5. Choose one decision and explain why.
6. End with 1-3 concrete next actions and explicit "do not do yet" items.

## Required Gates

- Do not recommend `enter_prd` unless PRD Entry Gate passes.
- Do not recommend `pilot` or `enter_prd` when high-risk review is unresolved.
- Do not treat a single customer quote as validated market demand.
- Do not claim a task, document, or Knowledge Hub article was created unless a tool actually created it.

High-risk domains include asset movement, wallet policy, signing/key management, KYC/AML/compliance, customer data, internal confidential docs, and customer-facing ROI/fee/safety/yield claims.

## References

Load these only when needed:

- `references/contracts.md`: output contract, gates, evidence standard, and high-risk rules.
- `references/customer-feedback-to-opportunity.md`: golden example for customer feedback.
- `references/knowledge-base.md`: local knowledge lifecycle and save rules.
- `references/stages/intent-framing.md`: detailed Intent（问题判断） instructions.
- `references/stages/builder-proof.md`: detailed Builder（最小验证方案） instructions.
- `references/stages/seller-proof.md`: detailed Seller（谁真的需要） instructions.
- `references/stages/measurer-contract.md`: detailed Measurer（怎么判断有效） instructions.
- `references/stages/critic-review.md`: detailed Critic（风险和反对意见） instructions.
- `references/stages/action-archive.md`: detailed Archive（结论和下一步） instructions.

The packaged `skill/` directory is standalone. Do not assume Workmate runtime files, eval fixtures, tests, or repository-specific playbook files are present after installation.
