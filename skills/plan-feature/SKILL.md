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
- Separate local file write authorization from external issue-tracker mutation
  authorization. A composing-skill handoff may authorize local writes without
  authorizing GitHub or another hosted tracker mutation.
- Carry accepted planning identity through every handoff: selected context,
  product or project slug, workspace path when applicable, and authoritative
  feature slug.
- Carry accepted delivery topology through every handoff. Use human-readable
  labels: `One Feature Branch`, `One PR Per Repo`, `One PR Per Issue`, or
  `Direct Commit`.

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

Before continuing, resolve the effective target for the current run:

- configured tracker mode from `project-memory/agents/issue-tracker.md`,
- whether local file writes are allowed,
- whether GitHub or other external tracker mutation is explicitly authorized in
  this run,
- any local dry-run target or current-run override.

If the user asked for a rehearsal, temp run, dry run, validation pass, or
otherwise disallowed external mutation, treat external tracker mutation as
disallowed even when persisted setup points at GitHub. Use the configured local
dry-run target when one exists; otherwise stop and ask for a local target or
return draft publish commands instead of mutating the external tracker.

Resolve the planning identity before writing:

- `feature_slug`: accepted lowercase kebab-case slug for this feature.
- For multi-context repos or monorepos: accepted `product_slug`,
  `workspace_path`, and `context_file` selected from `CONTEXT-MAP.md` or
  project memory.
- For orchestrator workspaces: accepted `project_slug` and `feature_slug`.
- `delivery_topology`: `One Feature Branch` for a single git repo, including
  monorepos; `One PR Per Repo` for orchestrator or true cross-repo features;
  `One PR Per Issue` or `Direct Commit` only when explicitly authorized.

If a multi-context local-markdown repo has no accepted product/context or the
feature slug is not product/workspace namespaced according to tracker
conventions, stop before PRD writing and resolve that identity first.
If the delivery topology is ambiguous because the feature might cross multiple
git repositories, stop before PRD writing and resolve that topology first.

### 2. Grill the feature with context

Load and run `$grill-me-with-context` on the feature intent.

Use it to resolve:

- feature goal and non-goals,
- users, workflows, and success criteria,
- domain terms, rules, and accepted decisions,
- open gates or blockers that would change the PRD or issue split.

If gates or blockers emerge, continue the grill-style one-question flow until
they are resolved or explicitly deferred as non-blocking. Do not write or
publish the PRD or issues while a gate remains unresolved or deferred in a way
that can affect scope, acceptance criteria, dependencies, validation,
publication target, permissions, or cross-repo contracts.

### 3. Produce and write the PRD

When no gates remain, load and run `$to-prd`.

Pass the resolved grilling output as the PRD source and explicitly state:

```text
Run authorization:
- Local file writes: allowed by $plan-feature because setup exists and no
  blocking feature-planning gates remain.
- External tracker mutation: <allowed|disallowed>, based on explicit
  authorization in this run.
- Configured tracker: <tracker mode from project-memory/agents/issue-tracker.md>.
- Effective target for this run: <configured target|local dry-run target|draft
  external publish commands only>.

Planning identity:
- feature_slug: <accepted feature slug>
- product_slug: <accepted product slug, for monorepos/multi-context repos>
- workspace_path: <accepted workspace path, for monorepos/multi-context repos>
- context_file: <selected CONTEXT.md, for monorepos/multi-context repos>
- project_slug: <accepted orchestrator project slug, for orchestrator modes>
- delivery_topology: <One Feature Branch|One PR Per Repo|One PR Per Issue|Direct Commit>
```

Ask `$to-prd` to use the configured target from
`project-memory/agents/issue-tracker.md`. If the configured target is a local
orchestrator workspace, pass the accepted `<project-slug>` and
`<feature-slug>` and allow `$to-prd` to create the feature directory only when
writing the PRD. If the configured target is a GitHub coordination repo, pass
the accepted `<project-slug>` so `$to-prd` can apply the matching project label
to the PRD parent issue when external mutation is authorized. If `$to-prd`
discovers a new blocker, route the blocker back through
`$grill-me-with-context` using the same one-question loop, then continue only
after the blocker is resolved or explicitly deferred as non-blocking.

### 4. Split and write issues

After the PRD is written or published, load and run `$to-issues` on that PRD.

Pass explicit run authorization:

```text
Run authorization:
- Local file writes: allowed by $plan-feature because the PRD is written and no
  blocking issue-splitting gates remain.
- External tracker mutation: <allowed|disallowed>, based on explicit
  authorization in this run.
- Configured tracker: <tracker mode from project-memory/agents/issue-tracker.md>.
- Effective target for this run: <configured target|local dry-run target|draft
  external publish commands only>.

Planning identity:
- feature_slug: <authoritative slug from $plan-feature/$to-prd or PRD path>
- product_slug: <accepted product slug, for monorepos/multi-context repos>
- workspace_path: <accepted workspace path, for monorepos/multi-context repos>
- context_file: <selected CONTEXT.md, for monorepos/multi-context repos>
- project_slug: <accepted orchestrator project slug, for orchestrator modes>
- delivery_topology: <topology recorded in the PRD Delivery Topology section>
```

Require `$to-issues` to use the configured issue target, apply configured issue
types and triage labels, attach GitHub implementation issues to the PRD issue
when GitHub or GitHub coordination mode is configured, use the configured title
formats, apply the `<project-slug>` GitHub label to GitHub coordination issues,
and confirm that `$plan-harder` ran once per generated issue. If external
tracker mutation is disallowed, require `$to-issues` to return draft publish
commands or write to the effective local target instead of mutating GitHub.

In orchestrator workspace mode, require generated issues to include affected
repos, cross-repo contracts, integration gates, repo PR links or placeholders,
issue-level scheduling and closeout metadata, and completion instructions that
require cross-repo integration proof before closing or moving to `issues/done/`.
Do not require every issue to restate the full PRD delivery topology when a
durable `Source PRD` pointer is present; use explicit issue-level topology
overrides only for exceptions.

If `$to-issues` discovers a product, domain, dependency, or acceptance-criteria
blocker, pause issue writing and route the blocker back through
`$grill-me-with-context`. Do not publish `needs-info` implementation issues from the
normal `$plan-feature` flow. Publish partial `needs-info` or `ready-for-human`
issues only when the user explicitly asks for partial output instead of a fully
agent-ready issue set. If the PRD still has open questions that affect scope,
acceptance criteria, dependencies, validation, publication target, permissions,
or cross-repo contracts, treat them as issue-splitting gates and do not produce
`ready-for-agent` issues.

### 5. Report completion

Summarize:

- setup status,
- PRD location,
- number of issues written or published,
- GitHub PRD parent/sub-issue relationship, when applicable,
- orchestrator project/feature path and affected repos, when applicable,
- issue types and labels/statuses applied,
- completion instructions included,
- run authorization applied, including whether external mutation occurred,
- planning identity used, including feature slug and product/context/project
  scope when applicable,
- delivery topology used,
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
