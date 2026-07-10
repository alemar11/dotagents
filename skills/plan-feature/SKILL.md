---
name: plan-feature
description: Manual feature planning into Product Requirements Documents (PRDs) and agent-ready issues, including prd-only and issues-from-existing-prd modes.
---

# Plan Feature

## Goal

Run feature planning from one public invocation. This skill owns the planning
pipeline and its internal Product Requirements Document (PRD) and issue phases:

`$project-memory` if needed -> `$grill-me-with-context` when scope needs
clarification -> PRD phase -> issue phase with `$plan-harder` per generated
issue.

Use this skill to turn rough feature intent into a written PRD and agent-ready
vertical issues. In orchestrator workspaces, those issues may be cross-repo
vertical outcomes. Do not implement the feature.

A feature is the capability or outcome being planned; the PRD is the durable
planning artifact that describes that feature's scope, requirements, acceptance
criteria, and delivery mode.

## Invocation Boundary

- Use only when the user explicitly invokes `$plan-feature`, explicitly asks to
  run the Plan Feature skill, or a manually invoked parent workflow explicitly
  routes to `$plan-feature`.
- Do not auto-select this skill for ordinary feature, planning, PRD, issue
  splitting, implementation, or triage requests.
- If feature planning would help but the user did not invoke this skill, answer
  or plan normally and ask before switching into the Plan Feature workflow.

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
If the user supplies new feature intent without naming a mode or asking to stop
at the PRD, use `full-flow`; issue splitting is part of that default. Use
`prd-only` only when the user explicitly requests a PRD without generated
issues, and use `issues-from-existing-prd` only when a durable PRD is supplied.

## Hard Requirements

- Keep PRD writing and issue splitting as internal phases, not separate public
  skill invocations.
- Load `references/prd-phase.md` before drafting, writing, or publishing a PRD.
- Load `references/issue-phase.md` before splitting a PRD into issues.
- Load `references/prd-template.md`, `references/issue-body-template.md`, and
  `references/vertical-slices.md` when the relevant phase requires them.
- Load and follow `$plan-harder` once for every generated implementation issue,
  using issue-hardening mode on its caller surface.
- Before writing, returning, or publishing generated implementation issues, run
  the issue phase verticality gate from `references/vertical-slices.md`; repair,
  merge, split, re-harden, or withhold any issue that is horizontal,
  chore-only, or otherwise not a justified vertical/enabling slice.
- Write or publish `ready-for-agent` artifacts only after the required tracker
  routing is available and no planning blockers remain. An explicit request for
  partial non-agent-ready output is the only exception: unresolved items may be
  returned or published as `needs-info` or `ready-for-human`, never as
  `ready-for-agent`, and only after their target and metadata are resolved.
- Treat the configured `tracker_backend` as planning-artifact write authority:
  `github` publishes PRDs and generated issues through `$github-issues`, while
  `local` writes the configured Markdown files.
- Use draft output only when the current run explicitly asks for a dry run,
  temp/rehearsal/validation pass, disabled writes, or another no-mutation
  override.
- Treat persistent local planning artifacts separately from temporary hosted
  issue body files. In hosted tracker mode, do not keep
  repo-local PRD, issue, `.scratch/`, or `project-memory/features/` mirrors
  unless the configured target or current run explicitly asks for a local
  artifact target.
- Carry accepted planning identity through every phase: selected context,
  product or project slug, workspace path when applicable, and authoritative
  feature slug.
- Carry accepted delivery mode through every phase using structured values:
  `pull-request` or `direct-commit`.
- Carry `source_prd_ref` from the PRD phase or existing durable PRD source into
  the issue phase. In `draft-publish-commands` runs, use the stable draft ref
  from `$project-memory` `references/tracker-publishing.md` until a
  hosted PRD issue number or local PRD path exists, and carry the PRD title,
  feature slug, project slug when applicable, and PRD body fingerprint with the
  draft handoff.
- Use structured values from setup, the PRD phase, and the issue phase. Keep
  prose values only for explanations, reasons, and free-form notes.
- Treat `$codex-orchestrator` worker choices and runtime authorization as
  session-only decisions. Do not include worker authorization defaults or copy
  session worker choices into PRDs, generated issues, `## Orchestrator Handoff`,
  local issue files, hosted issue bodies, or draft publish commands.

## External Skill Calls

This skill may call:

- `$project-memory`'s `tracker-routing` slice when required tracker setup is
  missing or needs review; broader setup remains out of scope unless separately
  requested.
- `$grill-me-with-context` when feature scope, terms, decisions, or planning
  blockers need repo-backed clarification.
- `$plan-harder` once per generated implementation issue.
- `$github-issues` only for GitHub issue publishing, issue type/label handling,
  parent/sub-issue relationships, and dry-run command mechanics for PRDs and
  generated implementation issues. After implementation scheduling starts,
  issue lifecycle comments, labels, direct closure, and closeout mutation belong
  to `$codex-orchestrator` using `$github-issues`.
- In GitHub tracker mode, `$github-issues` owns safe `gh --body-file`
  transport, transient body-file cleanup, partial-publication recovery, and
  dry-run command mechanics. `plan-feature` supplies sanitized titles, bodies,
  metadata, target repo, and parent relationships; it must not embed generated
  Markdown bodies in ad hoc shell commands.

## Workflow

### 1. Resolve Mode And Setup

Inspect the user request and source material to choose `full-flow`, `prd-only`,
or `issues-from-existing-prd`.

Inspect the repo for the setup required by the selected mode:

- `project-memory/agents/issue-tracker.md`,
- `project-memory/agents/triage-labels.md`.

Read `project-memory/agents/domain.md`, `CONTEXT.md`, or `CONTEXT-MAP.md` when
they exist or when context selection is material. Missing domain or localization
memory alone does not require broad setup before planning.

If tracker routing or issue mappings are missing, incomplete, stale, or
inconsistent with the current planning target, load `$project-memory`'s
`tracker-routing` slice, scoped to only the missing values. Use the user's
planning goal as context; do not bootstrap unrelated domain, localization, ADR,
or `AGENTS.md` content. In orchestrator workspace mode, setup is config-only
and must not create project or feature folders.

Before writing or publishing, resolve the effective target for the current run:

- configured tracker backend from `project-memory/agents/issue-tracker.md`,
- any explicit no-mutation override such as dry run, temp, rehearsal,
  validation pass, disabled writes, or draft-only output,
- any local dry-run target or explicit local mirror request.

For tracker publishing mechanics, use `$project-memory`'s `references/tracker-publishing.md`;
this includes `source_prd_ref` handling for `draft-publish-commands`.

If the user asked for a rehearsal, temp run, dry run, validation pass, or other
non-mutating run, do not write local tracker files or mutate a hosted tracker
even when persisted setup points at a writable target. Use the configured local
dry-run target when one exists; otherwise ask for a local target or return draft
publish commands.

When `tracker_backend` is `github` and no no-mutation override is active, the
hosted tracker is authoritative and the PRD/issues should be published there.
`$github-issues` owns the transient `gh --body-file` transport, including
creating body files outside the repo, using non-interpolating writes, verifying
tracker state, and cleaning up. Do not use `.scratch/` as a staging area in
hosted tracker mode unless the user explicitly asks to keep a local mirror.

When `tracker_backend` is `local` and no no-mutation override is active, write
the PRD and generated implementation issues to the configured Markdown paths.

Resolve the planning identity before writing:

- `feature_slug`: accepted lowercase kebab-case slug for this feature.
- For multi-context repos or monorepos: accepted `product_slug`,
  `workspace_path`, and `context_file` selected from `CONTEXT-MAP.md` or
  project memory.
- For orchestrator workspaces: accepted `project_slug` and `feature_slug`.
- `delivery_mode`: `pull-request` by default. For a single repo or monorepo, use
  one feature branch and PR. For true multi-repo work, every involved repo uses
  the same branch name and opens its own PR. Use `direct-commit` only when
  explicitly authorized.

If a multi-context local Markdown repo has no accepted product/context or the
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
- open planning blockers that would change the PRD or issue split.

If this clarification resolves durable terms, rules, boundaries, or accepted
decisions, carry forward whether `$grill-me-with-context` captured them in docs
or explicitly deferred them because the destination was missing or out of
scope.

If planning blockers emerge, continue the grill-style one-question flow until
they are resolved or explicitly deferred as non-blocking. Do not write or
publish agent-ready artifacts while a planning blocker remains unresolved or
deferred in a way that can affect scope, acceptance criteria, dependencies,
validation, publication target, permissions, or cross-repo contracts. If the
user explicitly requested partial non-agent-ready output, carry the blocker
into that output and apply the exception defined in the issue phase.

For `issues-from-existing-prd`, inspect the PRD's open questions first. Use
`$grill-me-with-context` only if the PRD has blockers that materially affect
issue splitting.

### 3. Run The PRD Phase

Skip this step only in `issues-from-existing-prd` mode when the PRD is already
durable and the user did not request a PRD update.

Load `references/prd-phase.md` and pass the phase handoff fields defined there,
including mode, effective target, no-mutation override, source PRD ref state,
planning identity, and delivery mode.

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
commands or bodies for inspection. Draft commands may show the intended future
mapped labels, but they are not executable agent-ready issues until the draft
`Source PRD` ref is replaced with the hosted PRD number or durable local PRD
path.

Pass the same phase handoff fields defined in `references/issue-phase.md`, with
`source_prd_ref` resolved or carried from the draft handoff.

Require the issue phase to use the configured issue target, mapped issue
metadata, PRD parent/sub-issue relationships, related issue links, `$plan-harder`
in issue-hardening caller mode per issue, the verticality gate, graph
validation, copied delivery mode, and the `## Orchestrator Handoff` shape from
`references/issue-body-template.md`.
`references/issue-phase.md` owns the detailed issue body, workspace,
publication, draft-output, and placeholder rules.

If the issue phase discovers a product, domain, dependency, or
acceptance-criteria blocker, pause issue writing and route the blocker back
through `$grill-me-with-context`. Do not publish `needs-info` implementation
issues from the normal `plan-feature` flow. Publish partial `needs-info` or
`ready-for-human` issues only when the user explicitly asks for partial output
instead of a fully agent-ready issue set. If the PRD still has open questions
that affect scope, acceptance criteria, dependencies, validation, publication
target, permissions, or cross-repo contracts, treat them as issue-splitting
blockers and do not produce `ready-for-agent` issues.

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
- effective target used, including whether configured tracker artifacts were
  written/published or draft-only output was returned,
- planning identity used, including feature slug and product/context/project
  scope when applicable,
- delivery mode used,
- verticality gate result, including repairs, merges, splits, justified
  enabling-slice exceptions, or withheld anomalies,
- issue graph validation summary, including dependency and acyclicity checks,
- planning blockers resolved or deferred,
- durable domain or architecture decisions captured during clarification, or
  explicit deferred capture with destination and reason,
- any issue still blocked and why.

## Guardrails

- Do not implement the feature.
- Do not write broad docs directly from this skill; `$grill-me-with-context` and
  `$domain-modeling` own durable context and ADR updates.
- Do not let durable terms, rules, or accepted decisions stop only in PRDs,
  issue bodies, or chat when clarification resolved them; report where they
  were captured or explicitly defer them with destination and reason.
- Do not create PRDs or issues in locations not configured by
  `project-memory/agents/issue-tracker.md`.
- Do not keep repo-local `.scratch/` or `project-memory/features/` copies for
  hosted tracker runs unless the user explicitly asked for a local
  mirror or the effective target is a local dry-run override.
- Do not treat `needs-info` issues as agent-ready output; they are waiting for
  human/reporter input and must be re-triaged before implementation.
- If required tracker setup cannot be completed, stop with the current state
  and next question instead of writing tracker artifacts.
- If a planning blocker remains unresolved, withhold agent-ready artifacts and
  return the blocker. Only an explicit request for partial non-agent-ready
  output permits a `needs-info` or `ready-for-human` artifact; keep its blocker
  visible and do not describe it as executable.

## References

- `references/prd-phase.md`: internal PRD drafting, writing, publishing, path
  sanitization, and `source_prd_ref` rules.
- `references/issue-phase.md`: internal issue splitting, hardening, graph
  validation, publishing, and completion rules.
- `references/prd-template.md`: default PRD shape.
- `references/issue-body-template.md`: generated implementation issue body
  template.
- `references/vertical-slices.md`: issue splitting rules.
- `references/full-flow-dry-run.md`: validation fixture for the
  `plan-feature` -> PRD phase -> issue phase -> `$codex-orchestrator`
  planning and orchestration handoff.
