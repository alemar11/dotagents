---
name: plan-feature
description: Plan a feature through full-flow, prd-only, or issues-from-existing-prd modes before implementation.
---

# Plan Feature

## Goal

Run feature planning from one public invocation. This skill owns the planning
pipeline and its internal PRD and issue phases:

`$project-memory` if needed -> `$grill-me-with-context` when scope needs
clarification -> PRD phase -> issue phase with `$plan-harder` per generated
issue.

Use this skill to turn rough feature intent into a written PRD and agent-ready
vertical issues. In orchestrator workspaces, those issues may be cross-repo
vertical outcomes. Do not implement the feature.

## Modes

Choose the smallest mode that satisfies the request:

- `full-flow`: default for rough new feature intent. Resolve setup, grill with
  context, produce or publish the PRD, then split it into hardened issues.
- `prd-only`: for clarified intent that should become a PRD but should not be
  split into issues yet.
- `issues-from-existing-prd`: for an existing durable PRD that needs generated
  implementation issues. Do not rewrite the PRD unless the user explicitly asks.

For `prd-only` mode, stop after the PRD phase report. For
`issues-from-existing-prd` mode, skip feature grilling unless the PRD has
unresolved blockers that affect scope, acceptance criteria, dependencies,
validation, publication target, permissions, or cross-repo contracts.

## Hard Requirements

- Keep PRD writing and issue splitting as internal phases, not separate public
  skill invocations.
- Load `references/prd-phase.md` before drafting, writing, or publishing a PRD.
- Load `references/issue-phase.md` before splitting a PRD into issues.
- Load `references/prd-template.md`, `references/issue-body-template.md`, and
  `references/vertical-slices.md` when the relevant phase requires them.
- Load and follow `$plan-harder` once for every generated implementation issue.
- Write or publish artifacts only after setup is available and no gates remain.
- Separate local file write authorization from external issue-tracker mutation
  authorization. Local writes never imply GitHub or other hosted mutation.
- Treat persistent local planning artifacts separately from temporary hosted
  issue body files. In GitHub or GitHub-coordination modes, do not keep
  repo-local PRD, issue, `.scratch/`, or `project-memory/features/` mirrors
  unless the configured target or current run explicitly asks for a local
  artifact target.
- Carry accepted planning identity through every phase: selected context,
  product or project slug, workspace path when applicable, and authoritative
  feature slug.
- Carry accepted delivery mode through every phase using structured values:
  `one-feature-branch`, `one-pr-per-repo`, `one-pr-per-issue`, or
  `direct-commit`.
- Carry `source_prd_ref` from the PRD phase or existing durable PRD source into
  the issue phase. In `draft-publish-commands` runs, use the stable draft ref
  from `$project-memory` `references/tracker-publishing.md` until a
  hosted PRD issue number or local PRD path exists, and carry the PRD title,
  feature slug, project slug when applicable, and PRD body fingerprint with the
  draft handoff.
- Use structured values from setup, the PRD phase, and the issue phase. Keep
  prose values only for explanations, reasons, and free-form notes.

## External Skill Calls

This skill may call:

- `$project-memory` when project memory or tracker setup is missing or
  needs review.
- `$grill-me-with-context` when feature scope, terms, decisions, or gates need
  repo-backed clarification.
- `$plan-harder` once per generated implementation issue.
- `$github-issues` only for GitHub issue publishing, issue type/label handling,
  parent/sub-issue relationships, and dry-run command mechanics.

## Workflow

### 1. Resolve Mode And Setup

Inspect the user request and source material to choose `full-flow`, `prd-only`,
or `issues-from-existing-prd`.

Inspect the repo for:

- `project-memory/agents/issue-tracker.md`,
- `project-memory/agents/triage-labels.md`,
- `project-memory/agents/domain.md`.

If any of these files are missing, incomplete, stale, or inconsistent with the
current planning target, load and run `$project-memory` first. Use the
user's planning goal as context, but keep setup focused on routing and memory.
In orchestrator workspace mode, setup is config-only and must not create project
or feature folders.

Before writing or publishing, resolve the effective target for the current run:

- configured tracker mode from `project-memory/agents/issue-tracker.md`,
- whether local file writes are allowed,
- whether GitHub or other external tracker mutation is explicitly authorized in
  this run,
- any local dry-run target or current-run override.

For tracker publishing mechanics, use `$project-memory`
`references/tracker-publishing.md`; this includes `source_prd_ref` handling for
`draft-publish-commands`.

If the user asked for a rehearsal, temp run, dry run, validation pass, or other
non-mutating run, treat external mutation as disallowed even when persisted
setup points at GitHub. Use the configured local dry-run target when one exists;
otherwise ask for a local target or return draft publish commands.

When `tracker_mode` is `github` or `orchestrator-github` and external mutation
is authorized, the hosted tracker is authoritative. Temporary files needed for
`$github-issues` or `gh --body-file` must be created outside the repo and
removed after mutation. Do not use `.scratch/` as a staging area in hosted
tracker mode unless the user explicitly asks to keep a local mirror.

Resolve the planning identity before writing:

- `feature_slug`: accepted lowercase kebab-case slug for this feature.
- For multi-context repos or monorepos: accepted `product_slug`,
  `workspace_path`, and `context_file` selected from `CONTEXT-MAP.md` or
  project memory.
- For orchestrator workspaces: accepted `project_slug` and `feature_slug`.
- `delivery_mode`: `one-feature-branch` for a single git repo, including
  monorepos; `one-pr-per-repo` for orchestrator or true cross-repo features;
  `one-pr-per-issue` or `direct-commit` only when explicitly authorized.

If a multi-context local-markdown repo has no accepted product/context or the
feature slug is not product/workspace namespaced according to tracker
conventions, stop before PRD writing or issue writing and resolve that identity
first. If the delivery mode is ambiguous because the feature might cross
multiple git repositories, stop before writing and resolve that delivery mode
first.

### 2. Clarify Scope When Needed

For `full-flow`, load and run `$grill-me-with-context` on the feature intent
unless the supplied source is already clear enough to produce a PRD and issues.
For `prd-only`, use the same clarification path when the intent is not already
clear enough to produce a PRD, then stop after the PRD phase.

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

For `issues-from-existing-prd`, inspect the PRD's open questions first. Use
`$grill-me-with-context` only if the PRD has blockers that materially affect
issue splitting.

### 3. Run The PRD Phase

Skip this step only in `issues-from-existing-prd` mode when the PRD is already
durable and the user did not request a PRD update.

Load `references/prd-phase.md` and pass:

```text
Plan-feature mode: <full-flow|prd-only|issues-from-existing-prd>

Run authorization:
- Persistent local artifact writes: <allowed|disallowed>, allowed only when the
  `tracker_mode` is `local-markdown` or `orchestrator-local`, the
  `effective_target` is `local-dry-run`, or the run explicitly requested a
  local mirror.
- External tracker mutation: <allowed|disallowed>, based on explicit
  authorization in this run.
- Hosted tracker body-file temp files: transient outside the repo and cleaned
  up after mutation.
- Configured tracker: <tracker_mode from project-memory/agents/issue-tracker.md>.
- Effective target for this run:
  <configured-tracker|local-dry-run|draft-publish-commands>.
- Source PRD ref:
  <pending until PRD phase returns #<number>, local path, or draft-prd:<slug>>.

Planning identity:
- feature_slug: <accepted feature slug>
- product_slug: <accepted product slug, for monorepos/multi-context repos>
- workspace_path: <accepted workspace path, for monorepos/multi-context repos>
- context_file: <selected CONTEXT.md, for monorepos/multi-context repos>
- project_slug: <accepted orchestrator project slug, for orchestrator modes>
- delivery_mode: <one-feature-branch|one-pr-per-repo|one-pr-per-issue|direct-commit>
```

Require the PRD phase to return `source_prd_ref`. In `draft-publish-commands`
mode, this is a deterministic `draft-prd:<feature-slug>` or
`draft-prd:<project-slug>/<feature-slug>` value plus a publish-order note that
the PRD must be created first and issue bodies must replace the draft ref with
the hosted PRD number before mutation.

If the PRD phase discovers a new blocker, route the blocker back through
`$grill-me-with-context` using the same one-question loop, then continue only
after the blocker is resolved or explicitly deferred as non-blocking.

Stop here in `prd-only` mode and return the PRD phase report.

### 4. Run The Issue Phase

After the PRD is written, published, supplied as an existing durable PRD, or
returned as a `draft-publish-commands` dry-run with a deterministic
`source_prd_ref`, load `references/issue-phase.md`. In
`draft-publish-commands` mode, the issue phase may only generate draft issue
commands or bodies for inspection. It must not mutate external trackers or mark
the generated issues agent-ready until the draft `Source PRD` ref is replaced
with the hosted PRD number or durable local PRD path.

Pass explicit run authorization:

```text
Plan-feature mode: <full-flow|issues-from-existing-prd>

Run authorization:
- Persistent local artifact writes: <allowed|disallowed>, allowed only when the
  `tracker_mode` is `local-markdown` or `orchestrator-local`, the
  `effective_target` is `local-dry-run`, or the run explicitly requested a
  local mirror.
- External tracker mutation: <allowed|disallowed>, based on explicit
  authorization in this run.
- Hosted tracker body-file temp files: transient outside the repo and cleaned
  up after mutation.
- Configured tracker: <tracker_mode from project-memory/agents/issue-tracker.md>.
- Effective target for this run:
  <configured-tracker|local-dry-run|draft-publish-commands>.
- Source PRD ref:
  <#<prd-number>|repo-relative PRD path|draft-prd:<slug>>.

Planning identity:
- feature_slug: <authoritative slug from plan-feature, PRD phase, or PRD path>
- product_slug: <accepted product slug, for monorepos/multi-context repos>
- workspace_path: <accepted workspace path, for monorepos/multi-context repos>
- context_file: <selected CONTEXT.md, for monorepos/multi-context repos>
- project_slug: <accepted orchestrator project slug, for orchestrator modes>
- delivery_mode: <mode recorded in the PRD Delivery Mode section>
```

Require the issue phase to use the configured issue target, issue types,
labels, title formats, PRD parent/sub-issue relationships, and GitHub
coordination project label when those modes apply. The issue phase must run
`$plan-harder` once per generated implementation issue and verify that every
`Parallelization` dependency resolves to a known issue ID in an acyclic graph
after the final hardened issue bodies are assembled. If external mutation is
disallowed, it must write to the effective local target or return draft publish
commands instead.

In orchestrator workspace mode, require generated issues to include affected
repos, cross-repo contracts, integration gates, repo PR links or placeholders,
issue-level scheduling and closeout metadata, and completion instructions that
require cross-repo integration proof before closing or moving to `issues/done/`.
Require every issue to copy the effective `Delivery mode` label from the PRD and
mark it as feature-level inherited metadata. Do not duplicate the full PRD
branch/PR details in each issue; use explicit issue-level delivery exceptions
only when an issue intentionally differs from the feature-level mode.

If the issue phase discovers a product, domain, dependency, or
acceptance-criteria blocker, pause issue writing and route the blocker back
through `$grill-me-with-context`. Do not publish `needs-info` implementation
issues from the normal `plan-feature` flow. Publish partial `needs-info` or
`ready-for-human` issues only when the user explicitly asks for partial output
instead of a fully agent-ready issue set. If the PRD still has open questions
that affect scope, acceptance criteria, dependencies, validation, publication
target, permissions, or cross-repo contracts, treat them as issue-splitting
gates and do not produce `ready-for-agent` issues.

### 5. Report Completion

Summarize:

- selected mode,
- setup status,
- PRD location or draft publish command status,
- number of issues written, published, or returned,
- GitHub PRD parent/sub-issue relationship, when applicable,
- orchestrator project/feature path and affected repos, when applicable,
- issue types and labels/statuses applied,
- completion instructions included,
- run authorization applied, including whether external mutation occurred,
- planning identity used, including feature slug and product/context/project
  scope when applicable,
- delivery mode used,
- issue graph validation summary, including dependency and acyclicity checks,
- gates resolved or deferred,
- any issue still blocked and why.

## Guardrails

- Do not implement the feature.
- Do not write broad docs directly from this skill; `$grill-me-with-context` and
  `$domain-modeling` own durable context and ADR updates.
- Do not create PRDs or issues in locations not configured by
  `project-memory/agents/issue-tracker.md`.
- Do not keep repo-local `.scratch/` or `project-memory/features/` copies for
  GitHub/GitHub-coordination runs unless the user explicitly asked for a local
  mirror or the effective target is a local dry-run override.
- Do not treat `needs-info` issues as agent-ready output; they are waiting for
  human/reporter input and must be re-triaged before implementation.
- If setup cannot be completed or a gate remains unresolved, stop with the
  current state and next question instead of writing partial artifacts.

## References

- `references/prd-phase.md`: internal PRD drafting, writing, publishing, path
  sanitization, and `source_prd_ref` rules.
- `references/issue-phase.md`: internal issue splitting, hardening, graph
  validation, publishing, and completion rules.
- `references/prd-template.md`: default PRD shape.
- `references/issue-body-template.md`: generated implementation issue body
  template.
- `references/vertical-slices.md`: issue splitting rules.
- `references/full-flow-dry-run.md`: dry-run fixture for the
  `plan-feature` -> PRD phase -> issue phase -> `$codex-orchestrator`
  planning and orchestration handoff.
