---
name: plan-harder
description: Create a higher-rigor implementation plan or harden a single issue before coding. Use when the user explicitly asks for deeper planning, a harder plan, a stress-tested plan, or an agent-ready issue brief; research first, ask focused clarifying questions, and review for gaps before implementation starts.
---

# Plan Harder

## Goal

Produce a deeper implementation plan than a normal planning pass. Slow down,
reduce ambiguity, surface hidden risks, and leave behind a concrete plan that
is ready for careful execution.

Only create the plan. Do not implement the work.

Plan Harder has two modes:

- **Full-plan mode**: create a phased implementation plan for a feature,
  migration, refactor, or other multi-step change.
- **Issue-hardening mode**: make one vertical slice or issue agent-ready by
  adding the missing execution detail an implementation agent needs.

## Planning-Only Contract

- Do not implement the work.
- Do not open PRs, mutate GitHub state, publish artifacts, or silently continue
  into coding after the plan.
- In full-plan mode, repo writes are limited to the saved plan file under
  `plans/` unless the user explicitly asks for chat-only output.
- In issue-hardening mode, do not create a `plans/` file by default. Return a
  compact issue-ready brief for the caller to embed in the issue, PRD, or local
  tracker artifact. Only edit a local issue file when the user or calling skill
  explicitly provides that file as the target.
- If the broader request includes later implementation, issue creation, or
  orchestration, finish the plan first and make the handoff explicit instead of
  blending phases together.

## Trigger Rules

- Use when the user explicitly invokes `plan-harder` or asks for a harder,
  deeper, or more stress-tested plan.
- Use issue-hardening mode when the user asks to harden, solidify, make
  agent-ready, or de-risk a single issue or vertical slice before implementation.
- Use issue-hardening mode when another skill invokes `plan-harder` on one
  issue as a pre-implementation rigor pass.
- Use when the task is ambiguous, high-risk, multi-phase, or likely to hide
  ordering problems or missing validation steps.
- Do not use for straightforward planning work that does not need an extra
  review pass.

## Output Mode

- Direct full-plan default: save the plan to `plans/<topic>-plan.md`.
- Issue-hardening default: return a compact issue-ready brief in chat for the
  caller to embed; do not save under `plans/`.
- If the user explicitly says not to write a file, not to write Markdown, or
  to keep the plan in chat, return the plan in chat only and say that no file
  was saved.
- When the plan is meant to feed later implementation or GitHub issue creation,
  end with issue-sized work slices and a clear handoff note.
- When hardening an existing issue, end with a clear implementation handoff for
  exactly that issue and name any remaining blocker that prevents assignment.

## Workflow

### 1. Choose the Mode

- Use full-plan mode for a feature, migration, refactor, or plan that still
  needs phases or multiple tasks.
- Use issue-hardening mode for one existing issue, one vertical slice, or one
  work item produced by a PRD or issue-splitting skill.
- If another skill calls Plan Harder with an issue body, treat that as
  issue-hardening mode unless it explicitly asks for a saved full plan.

### 2. Research First

- Inspect the codebase, architecture, existing patterns, and nearby tests.
- Identify dependencies, edge cases, rollout concerns, and likely failure
  modes before drafting the plan.
- In issue-hardening mode, inspect only the files, tests, docs, and contracts
  needed to make that issue executable; do not expand into a full feature plan.

### 3. Clarify High-Risk Unknowns

- Ask focused clarifying questions before drafting the plan when ambiguity
  could materially change the work.
- Ask only the minimum question batch needed to eliminate wrong plan branches.
- Prefer `request_user_input` when available.
- Respect the runtime limit of 1-3 questions per `request_user_input` call;
  if more clarification is needed, ask only the highest-signal next batch.
- If `request_user_input` is unavailable, ask the same focused questions in
  plain chat with concise numbered options and a recommended default.
- Prefer short numbered questions over paragraphs.
- Offer multiple-choice options when practical.
- Suggest reasonable defaults when appropriate.
- Include a fast-path reply such as `defaults` when the recommended choices are
  acceptable.
- Include a low-friction "not sure - use default" option when that meaningfully
  reduces back-and-forth.
- Do not ask questions that a quick, low-risk discovery read can answer from
  the repo, config, or nearby docs.
- Prioritize questions about:
  - scope and non-goals
  - success criteria
  - compatibility constraints
  - rollout/rollback expectations
  - validation expectations
- Use this underspecification checklist when deciding whether clarification is
  required before the plan is final:
  - the objective is unclear
  - "done" is unclear
  - scope boundaries are unclear
  - constraints are unclear
  - the target environment is unclear
  - safety or reversibility is unclear

### 4. Fetch Official Docs When Needed

- If the plan depends on external libraries, frameworks, APIs, or tools whose
  current behavior matters, fetch the relevant official documentation before
  finalizing tasks.
- Use the runtime's best official-doc path for the current environment rather
  than relying on memory when the detail is likely to drift.

### 5. Draft the Output

In full-plan mode, create a phased plan with:

- a short overview
- prerequisites
- logical sprints or phases
- atomic tasks with clear boundaries
- validation per task
- testing strategy
- risk and rollback notes

Each task should be:

- small enough to commit independently when practical
- specific about files or areas touched when known
- explicit about dependencies on earlier tasks
- testable or otherwise verifiable
- concrete about what "done" means

In issue-hardening mode, create a compact issue brief with:

- issue goal and non-goals,
- assumptions and resolved interpretation,
- implementation approach,
- likely files or areas to inspect,
- dependencies or blockers,
- acceptance criteria,
- validation commands or checks,
- risks and rollback notes,
- handoff instructions for the implementation agent.

Keep the brief small enough to paste into an issue body or issue comment.

### 6. Save Only When the Mode Calls For It

- In full-plan mode, ensure a `plans/` directory exists in the current working
  directory before saving.
- If `plans/` does not exist, create it before saving the plan.
- Save the generated full plan to `plans/<topic>-plan.md`.
- Derive `<topic>` from the request using kebab-case.
- If the user explicitly asked for chat-only or no-file output, skip the write
  and keep the same structure in the returned plan.
- In issue-hardening mode, skip the `plans/` write unless the user explicitly
  asks for a saved plan. If a local issue file path is explicitly provided as
  the target, update that issue file instead of creating a separate plan file.

Examples:

- `fix auth timeout bug` -> `plans/auth-timeout-bug-plan.md`
- `design a safer webhook retry flow` ->
  `plans/safer-webhook-retry-flow-plan.md`

### 7. Run a Gotcha Pass

- Re-read the saved plan, issue brief, or edited issue file and look for:
  - missing steps
  - missing dependencies
  - vague acceptance criteria
  - unsafe ordering
  - rollout or rollback gaps
  - missing validation
- If real gaps remain, ask the minimum follow-up questions needed and update
  the saved plan or issue brief.

### 8. Review Before Returning

- Review the saved plan or issue brief for:
  - missing dependencies
  - ordering failures
  - unhandled edge cases
  - vague or untestable tasks
- If explicit delegation is allowed in the current run, you may ask a subagent
  to perform this review. Tell the reviewer not to ask questions and to return
  only actionable feedback.
- Otherwise, perform the same review locally before returning.
- Incorporate useful review feedback before finishing.

## Plan Template

Use this for full-plan mode.

```markdown
# Plan: [Task Name]

**Generated**: [Date]
**Estimated Complexity**: [Low/Medium/High]

## Overview
[Summary of the work and the recommended approach]

## Prerequisites
- [Dependencies or requirements]
- [Tools, libraries, access, or docs needed]

## Sprint 1: [Name]
**Goal**: [What this phase accomplishes]
**Demo/Validation**:
- [How to demo or verify the phase]

### Task 1.1: [Name]
- **Location**: [File paths or areas]
- **Description**: [What to do]
- **Complexity**: [1-10]
- **Dependencies**: [Earlier tasks or `None`]
- **Acceptance Criteria**:
  - [Specific outcome]
- **Validation**:
  - [Tests or verification steps]

### Task 1.2: [Name]
[...]

## Sprint 2: [Name]
[...]

## Testing Strategy
- [How to validate the work]
- [What to verify per phase]

## Potential Risks & Gotchas
- [What could go wrong]
- [Mitigation]

## Rollback Plan
- [How to safely undo or disable the change]
```

## Issue-Hardening Template

Use this for issue-hardening mode.

```markdown
## Implementation Plan

### Goal
[The exact vertical slice this issue should deliver.]

### Non-Goals
- [What this issue should not attempt.]

### Resolved Interpretation
- [Assumptions or decisions this plan relies on.]

### Approach
- [Concrete implementation approach.]

### Likely Touch Points
- [Files, modules, routes, tests, or docs to inspect or modify.]

### Dependencies
- [Blocking issues, prerequisites, or `None`.]

### Acceptance Criteria
- [ ] [Specific, verifiable outcome.]

### Validation
- [Command, test, manual check, or log/metric to verify.]

### Risks & Rollback
- [Risk and mitigation.]

### Handoff
[One short instruction to the implementation agent about where to start and what not to broaden.]
```

## Output Expectations

- In full-plan mode, return the final saved plan path, or explicitly say that
  the plan stayed in chat-only mode with no file written.
- In issue-hardening mode, return the hardened issue brief or the local issue
  file path that was updated, and explicitly say that no `plans/` file was
  created unless one was requested.
- Summarize the main phases, the riskiest assumptions, and any open questions
  that remain.
- If clarification was needed, restate the resolved interpretation before
  summarizing the plan.
- Include the explicit handoff boundary for any later implementation,
  orchestration, or GitHub follow-up.
- Do not implement the plan.

## Example Requests

- "Plan harder for this auth migration before we touch any code."
- "Give me a deeper, stress-tested implementation plan for this feature."
- "Make a harder plan for this refactor and save it under `plans/`."
- "Harden this issue before I give it to an agent."
- "Make this vertical slice agent-ready without creating a separate plan file."
