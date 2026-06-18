# Product Owner Decision Skill

This is the package to share with colleagues.

## What To Send

Send this entire `skill/` directory.

Do not send only `SKILL.md`; the skill references local files under `references/`.

This directory is intentionally standalone. It should not contain Workmate runtime files such as `agent.md`, nested stage `skills/`, tests, eval fixtures, feedback-pipeline adapters, or playbook-only implementation files.

## Install

Copy this directory to the local skills folder:

```bash
mkdir -p ~/.agents/skills/product-owner-decision
cp -R skill/* ~/.agents/skills/product-owner-decision/
```

If the user is copying from the repository path directly:

```bash
mkdir -p ~/.agents/skills/product-owner-decision
cp -R projects/cobo-agents/cobo_agents/workmate/playbooks/references/experiments/product-owner-playbook/skill/* ~/.agents/skills/product-owner-decision/
```

Restart Claude Code / Codex if the skill is not picked up immediately.

## Use

Use natural prompts:

```text
这是一条客户反馈，帮我跑一下产品决策。
```

```text
这个想法先别写 PRD，帮我跑一下产品决策。
```

```text
这个需求客户催得很急，帮我跑一下产品决策，重点看证据和风险。
```

## Boundary

This is a pilot skill. It helps with product decision preparation. It does not automatically approve roadmap, PRD, high-risk product behavior, Knowledge Hub publication, or task creation.
