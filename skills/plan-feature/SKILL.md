---
name: plan-feature
description: Plan a new feature from initial intent to agent-ready implementation issues. Use when the user wants one wrapper workflow for feature planning, repo-backed grilling, PRD creation, and vertical issue splitting before implementation.
---

# Plan Feature

## Goal

Run the full feature-planning pipeline from one invocation:

`$setup-project-memory` if needed -> `$grill-me-with-context` -> `$to-prd` ->
`$to-issues`.

Use this skill to turn a rough feature idea into a written PRD and
agent-ready vertical issues. In orchestrator workspaces, those issues may be
cross-repo vertical outcomes. Do not implement the feature.

## Hard Requirements

- Keep this skill as a thin orchestrator over the component skills.
- Load and follow each component skill before handing work to it.
- Do not duplicate grilling, domain-modeling, PRD drafting, vertical slicing,
  or issue-hardening instructions.
- Do not skip `$to-issues` hardening; `$to-issues` must still run
  `$plan-harder` once for every generated issue.
- Write or publish artifacts only after setup is available and no gates remain.

## Workflow

### 1. Check project memory

Inspect the repo for:

- `project-memory/agents/issue-tracker.md`,
- `project-memory/agents/triage-labels.md`,
- `project-memory/agents/domain.md`.

If any of these files are missing, load and run `$setup-project-memory` first.
Use the user's current feature-planning goal as context, but keep setup focused
on routing and memory. In orchestrator workspace mode, setup is config-only and
must not create project or feature folders.

### 2. Grill the feature with context

Load and run `$grill-me-with-context` on the feature intent.

Use it to resolve:

- feature goal and non-goals,
- users, workflows, and success criteria,
- domain terms, rules, and accepted decisions,
- open gates or blockers that would change the PRD or issue split.

If gates or blockers emerge, continue the grill-style one-question flow until
they are resolved or explicitly deferred. Do not write or publish the PRD or
issues while a gate remains unresolved.

### 3. Produce and write the PRD

When no gates remain, load and run `$to-prd`.

Pass the resolved grilling output as the PRD source and explicitly state:

```text
Write authorization: granted by $plan-feature because setup exists and no
feature-planning gates remain.
```

Ask `$to-prd` to use the configured target from
`project-memory/agents/issue-tracker.md`. If the configured target is a local
orchestrator workspace, pass the accepted `<project-slug>` and
`<feature-slug>` and allow `$to-prd` to create the feature directory only when
writing the PRD. If `$to-prd` discovers a new blocker, route the blocker back
through `$grill-me-with-context` using the same one-question loop, then
continue only after the blocker is resolved or explicitly deferred as
non-blocking.

### 4. Split and write issues

After the PRD is written or published, load and run `$to-issues` on that PRD.

Pass explicit write authorization:

```text
Write authorization: granted by $plan-feature because the PRD is written and no
issue-splitting gates remain.
```

Require `$to-issues` to use the configured issue target, apply configured issue
types and triage labels, attach GitHub implementation issues to the PRD issue
when GitHub or GitHub coordination mode is configured, use the configured title
formats, and confirm that `$plan-harder` ran once per generated issue.

In orchestrator workspace mode, require generated issues to include affected
repos, cross-repo contracts, integration gates, repo PR links or placeholders,
and completion instructions that require cross-repo integration proof before
closing or moving to `issues/done/`.

If `$to-issues` discovers a product, domain, dependency, or acceptance-criteria
blocker, pause issue writing and route the blocker back through
`$grill-me-with-context`. Do not publish `needs-info` implementation issues from the
normal `$plan-feature` flow. Publish partial `needs-info` or `ready-for-human`
issues only when the user explicitly asks for partial output instead of a fully
agent-ready issue set.

### 5. Report completion

Summarize:

- setup status,
- PRD location,
- number of issues written or published,
- GitHub PRD parent/sub-issue relationship, when applicable,
- orchestrator project/feature path and affected repos, when applicable,
- issue types and labels/statuses applied,
- completion instructions included,
- gates resolved or deferred,
- any issue still blocked and why.

## Guardrails

- Do not implement the feature.
- Do not write broad docs directly from this skill; `$grill-me-with-context` and
  `$domain-modeling` own durable context and ADR updates.
- Do not create PRDs or issues in locations not configured by
  `project-memory/agents/issue-tracker.md`.
- Do not treat `needs-info` issues as agent-ready output; they are waiting for
  human/reporter input and must be re-triaged before implementation.
- If setup cannot be completed or a gate remains unresolved, stop with the
  current state and next question instead of writing partial artifacts.
