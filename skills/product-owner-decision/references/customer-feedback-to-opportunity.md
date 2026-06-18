# Example: Customer Feedback To Product Opportunity

## Input

```text
客户经常问为什么提现手续费这么高，CS 每次都要解释。能不能在 Portal 自动解释费用组成，并给客户优化建议？

帮我跑一下产品决策。
```

Supporting context:

```text
过去 30 天有 18 个提现费用相关 ticket。
常见问题：
- 为什么同样金额，不同链费用不一样？
- 为什么预计费用和最终扣费有差异？
- 是否可以推荐更便宜的链？
当前处理方式：CS 手动解释 network fee、Cobo fee、链上拥堵、币种/链差异。

可以解释：
- network fee 可能随链上状态变化
- Cobo fee 与产品配置相关
- 不同链、币种、地址类型会影响费用

不能承诺：
- 保证最低费用
- 保证某条链永远更便宜
- 自动替客户选择提现路径
```

## Good Decision Split

- Fee explanation: `prototype`
- Optimization recommendation: `explore`
- Formal PRD: not yet

## Why

Fee explanation has a low-cost prototype path and can reduce repeated CS explanation.

Optimization recommendation is riskier because it can become a customer-facing fee claim and may require reliable chain/fee data, reviewer approval, and careful wording.

## Expected Output Shape

### Intent（问题判断）

- Topic: Portal withdrawal fee explanation.
- Target user: enterprise customers who withdraw frequently, plus CS teams who repeatedly explain fees.
- Desired behavior change: customers understand fee composition before asking CS.
- Why now: 18 related tickets in the last 30 days.
- Target decision: `prototype` for fee explanation; `explore` for optimization recommendation.
- Non-goals: do not change fee calculation; do not auto-select chain; do not promise lowest fee.

### Builder（最小验证方案）

- Minimal closed loop: withdrawal page trigger -> fee explanation card -> customer understands network fee / Cobo fee / chain difference -> repeated CS question decreases.
- MVP/prototype boundary: fee explanation card + CS reusable script.
- Not in scope: automatic lowest-fee recommendation, automatic route selection, fee-saving promise.

### Seller（谁真的需要）

- First adopter: high-frequency withdrawal customers and CS.
- Current alternative: customer asks CS; CS explains manually.
- Objection: customer may want "how to make it cheaper", not only explanation.
- Validation motion: test explanation with 5 frequent cases or CS-reviewed scenarios.

### Measurer（怎么判断有效）

- Output metric: fee-related tickets or follow-up questions.
- Input metric: card view/read rate.
- Quality metric: CS handling time.
- Guardrail: no increase in fee-misunderstanding complaints.
- Kill criteria: data fields cannot be shown reliably, or explanation does not reduce follow-up.

### Critic（风险和反对意见）

- Weakest dimension: Measurer（怎么判断有效）, because ticket tagging and instrumentation may be missing.
- Evidence laundering risk: CS feedback shows repeated confusion, not proof that recommendation will work.
- High-risk domain: customer-facing fee claims.

### Archive（结论和下一步）

- Decision: `prototype` for explanation; `explore` for optimization.
- Do next:
  1. Cluster recent fee tickets.
  2. Confirm available fee fields, freshness, and accuracy boundary.
  3. Create explanation-card prototype and CS script.
- Do not do yet:
  - Do not promise fee savings.
  - Do not auto-select chain.
  - Do not enter formal PRD for optimization recommendation.

### Evidence（证据表）

| Claim | Level | Source | Decision relevance | Needed validation | Owner |
| --- | --- | --- | --- | --- | --- |
| There were 18 withdrawal-fee tickets in 30 days | Fact | user-provided ticket excerpt | Supports explore/prototype | Verify tagging accuracy | CS lead |
| Explanation card can reduce CS questions | Assumption | product hypothesis | Supports prototype | Test prototype or CS script | Portal PM |
| Cheaper-chain recommendation will help customers | Needs validation | Sales/CS feedback | Affects optimization path | Validate data reliability and customer intent | Portal PM |
| Cobo can promise lowest fee | Contradiction | stated constraints | Blocks recommendation wording | Remove promise | Portal PM |
