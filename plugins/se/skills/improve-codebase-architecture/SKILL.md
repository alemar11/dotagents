---
name: improve-codebase-architecture
description: "Find evidence-backed architecture improvements and pressure-test one selected refactor before implementation. Use for module-boundary, coupling, testability, or codebase-health work; do not use for ordinary bug fixes, formatting, or code review."
---

# Improve Codebase Architecture

## Goal

Surface architecture improvements that would make a codebase easier to
understand, test, and change. Present concrete candidates first. Only after the
user chooses a candidate, pressure-test the selected direction one decision at
a time and capture accepted durable domain or architecture decisions through
`$se:learn`.

This is a discovery and decision-shaping skill, not an automatic refactor.

## Trigger Rules

- Use when the user asks for architecture improvement, codebase health,
  module-boundary review, deep-module opportunities, coupling reduction,
  testability improvements, or agent-friendly architecture.
- Use when a planning session needs architecture candidates before choosing a
  concrete implementation path.
- Do not use for normal code review, bug diagnosis, formatting cleanup, or
  generic implementation work unless architecture discovery is explicitly in
  scope.
- Do not propose interfaces or edit production code before the user picks a
  candidate.

## Workflow

Load `references/options.md` before classifying candidate strength.

### 1. Ground in repo evidence

- Inspect project docs and root `CONTEXT.md` when it exists, treating the
  current Git repository as a selected root. For cross-repository work, use
  explicit user scope or a durable linked Feature Spec Set to authorize
  repository identities, require candidate local Git roots separately, verify
  each root against one authorized identity, and inspect each verified
  repository independently. Then read every available scoped `CONTEXT.md`
  matched by affected paths in each selected root's `Scoped Contexts` table,
  the relevant root `project-context/adr/` trees, package boundaries, public
  APIs, tests, and the files near the requested area. When a root or matched
  route has no context, inspect its repository paths directly.
- If subagents are available and the repo is large, use bounded read-only
  exploration slices; otherwise inspect sequentially.
- Prefer source-backed call paths and concrete file references over broad
  architecture prose.

Look for:

- concepts that require bouncing through many shallow files,
- interfaces nearly as complex as their implementations,
- test-only extractions that reduce locality,
- tightly coupled modules leaking implementation details,
- missing test seams around real behavior,
- duplicated adapters or integration logic that suggest a real boundary,
- ADRs or docs that conflict with current code behavior.

### 2. Build candidate improvements

For each candidate, identify:

- files and modules involved,
- current friction,
- proposed architectural move,
- expected benefit for locality, testability, and change safety,
- risks and migration cost,
- evidence from code or docs,
- `recommendation_strength=strong|worth-exploring|speculative`.

Use separate prose to explain why a candidate received that value. Human
headings may capitalize the value for display, but downstream selection must
branch on `recommendation_strength`.

Apply a deletion test to suspected shallow modules: would removing the module
concentrate complexity in one place, or merely move the same complexity
elsewhere?

### 3. Present candidates before drilling in

Return a concise candidate report in chat by default. If the user asks for an
artifact or the candidate set is large, create a temporary self-contained HTML
report using `references/report-shape.md`.

Do not propose the final interface yet. Ask the user which candidate they want
to explore.

### 4. Pressure-test the selected candidate

After the user chooses a candidate, track resolved decisions, material unknowns,
risks, and deferred questions internally. Ask exactly one high-signal question
per turn, include a concise recommended answer, and do not ask for facts already
available in the inspected repository or project context. Continue only while
another answer can materially change the selected refactor, and stop when the
direction is actionable or the user asks to proceed.

Use this shape:

```text
Question: [one concrete decision-shaping question]
Recommended answer: [the evidence-backed default and why, in one short sentence]
```

After an answer establishes a durable project-specific term, rule, boundary, or
architecture decision, prepare the smallest evidence-backed handoff with the
accepted knowledge, intended named targets, and evidence. Invoke
`$se:learn` with `memory_slice=domain-memory` and
`domain_operation=inline-update` only when the current request or caller handoff
also supplies explicit scoped capture authority. Otherwise report the decision
as deferred with its intended targets and evidence. Do not capture rejected,
tentative, or unresolved points.

Use it to resolve:

- target behavior and non-goals,
- the module boundary or seam,
- what sits behind the interface,
- migration and compatibility constraints,
- tests that should survive or be added,
- rollout and rollback shape,
- domain terms or ADR-worthy decisions that should be documented.

### 5. Finish with a scoped recommendation

Summarize:

- selected candidate,
- resolved architecture decisions,
- `capture_outcome` plus docs updated through `$se:learn`, or explicitly
  deferred decisions with their intended targets and evidence,
- implementation path,
- tests to add or preserve,
- remaining risks and deferred questions.

## Guardrails

- Do not invent architecture issues without file-backed evidence.
- Do not force a refactor when the existing shape is acceptable.
- Do not bury ADR conflicts; call them out and ask whether to revisit them.
- Keep speculative candidates clearly labeled.
- Do not dump a full critique before the next decision-shaping question or
  continue pressure-testing after the user asks to proceed.
- Do not implement until the user explicitly switches from architecture
  discovery to execution.

## References

- Canonical candidate-strength option: `references/options.md`
