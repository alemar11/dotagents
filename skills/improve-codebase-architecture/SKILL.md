---
name: improve-codebase-architecture
description: Find evidence-backed architecture improvement candidates, then use grill-me-with-context to sharpen the selected refactor before implementation.
---

# Improve Codebase Architecture

## Goal

Surface architecture improvements that would make a codebase easier to
understand, test, and change. Present concrete candidates first. Only after the
user chooses a candidate, use `$grill-me-with-context` to pressure-test the selected
direction and capture durable domain or architecture decisions.

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

### 1. Ground in repo evidence

- Inspect project docs, `CONTEXT.md`, `CONTEXT-MAP.md`,
  `project-memory/agents/domain.md`, `project-memory/adr/`, package
  boundaries, public APIs, tests, and the files near the requested area.
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
- recommendation strength: `Strong`, `Worth exploring`, or `Speculative`.

Apply a deletion test to suspected shallow modules: would removing the module
concentrate complexity in one place, or merely move the same complexity
elsewhere?

### 3. Present candidates before drilling in

Return a concise candidate report in chat by default. If the user asks for an
artifact or the candidate set is large, create a temporary self-contained HTML
report using `references/report-shape.md`.

Do not propose the final interface yet. Ask the user which candidate they want
to explore.

### 4. Grill the selected candidate

After the user chooses a candidate, load and follow `$grill-me-with-context`.

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
- docs updated by `$grill-me-with-context`,
- implementation path,
- tests to add or preserve,
- remaining risks and deferred questions.

## Guardrails

- Do not invent architecture issues without file-backed evidence.
- Do not force a refactor when the existing shape is acceptable.
- Do not bury ADR conflicts; call them out and ask whether to revisit them.
- Keep speculative candidates clearly labeled.
- Do not implement until the user explicitly switches from architecture
  discovery to execution.
