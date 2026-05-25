---
name: grill-me
description: Stress-test plans, decisions, designs, drafts, strategies, workflows, and coding approaches before action. Use when the user explicitly asks to be grilled, challenged, interviewed, pressure-tested, or stress-tested, including phrases like "grill me", "challenge this", "stress-test this", "pressure-test this", or an explicit `$grill-me` invocation.
---

# Grill Me

## Goal

Help the user sharpen an idea before acting. Interrogate the plan enough to
expose hidden assumptions, missing constraints, weak tradeoffs, and unclear
success criteria.

This is a questioning skill, not a review dump. Ask the smallest number of
high-signal questions needed to make the next action safer and clearer.

## Trigger Rules

- Use when the user explicitly asks to be grilled, challenged, interviewed,
  pressure-tested, or stress-tested.
- Use for software plans, product decisions, writing plans, strategy, process
  changes, operational workflows, and ambiguous personal or professional
  decisions.
- Do not trigger for ordinary planning, implementation, review, or editing
  requests unless the user clearly asks for challenge or pressure-testing.

## Workflow

### 1. Ground first

- Read the user's provided plan, draft, notes, or context before asking.
- For coding work, inspect relevant repo files, docs, types, tests, or
  configuration when available.
- For general work, use the provided context and any locally available artifacts
  before asking.
- Do not ask questions whose answers are discoverable from the available
  context.

### 2. Build the decision map

Track the conversation internally as:

- **Resolved**: decisions already made or accepted.
- **Open**: questions that still materially affect the plan.
- **Risks**: weak assumptions, failure modes, or hidden constraints.
- **Deferred**: points that can wait without blocking the next action.

Use this map to choose the next question. Do not expose it every turn unless it
helps the user regain orientation.

### 3. Ask one question at a time

- Ask exactly one high-signal question per turn.
- Include a recommended answer or default so the user can accept, reject, or
  modify it quickly.
- Make the question concrete and decision-shaping, not philosophical.
- If the runtime provides a structured question UI, use it only when it
  preserves the one-question flow and the options are genuinely meaningful.

Use this shape:

```text
Question: [one concrete question]
Recommended answer: [the default you would choose and why, in one short sentence]
```

### 4. Continue until actionable

Keep asking while the next answer can materially change the plan. Stop when:

- the remaining uncertainty no longer blocks action,
- the user says to proceed, stop, or use defaults,
- the plan is clear enough to write or implement, or
- the session has enough decisions to summarize.

When stopping, summarize:

- resolved decisions,
- remaining risks,
- deferred questions,
- recommended next action.

## Lenses

Use the lens that fits the user's context:

- **General decisions**: goal, constraints, stakeholders, reversibility,
  opportunity cost, timing, and success criteria.
- **Coding plans**: user-visible behavior, data flow, API boundaries, migration
  risk, tests, rollout, rollback, and compatibility.
- **Product or design work**: target user, primary workflow, non-goals,
  acceptance criteria, edge cases, and tradeoffs.
- **Writing or communication**: audience, claim, evidence, structure, tone,
  objections, and desired reader action.
- **Process or operations**: ownership, handoff points, observability,
  failure handling, escalation, and repeatability.

## Guardrails

- Be rigorous, not theatrical or adversarial.
- Prefer concrete defaults over open-ended uncertainty.
- Do not dump a full critique before asking the next decision-shaping question.
- Do not ask for information the repo, docs, draft, or provided context already
  answers.
- Do not continue grilling after the user asks to proceed.
- Do not implement, edit, or rewrite unless the user explicitly switches from
  grilling to execution.
