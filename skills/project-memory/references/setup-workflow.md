# Setup Workflow Details

Use this reference for the interactive setup editor, draft checklist, write
rules, `AGENTS.md` pointer block, and completion report. Keep the public
`SKILL.md` focused on routing and hard boundaries.

## Current Settings Summary

When reviewing existing setup, summarize values in the selected setup slice
before recommending changes. Include the full list only for an explicit full
review:

- execution context: `orchestrator-workspace`, `fresh-setup`,
  `existing-project-bootstrap`, or `current-project` (derived in the exact
  precedence from `options.md`, not a stored key or option)
- `repository_layout`
- `tracker_backend`
- `artifact_marker` transport and mapping
- `issue_type` transport and mapping
- `workflow_state` transport and mapping
- root/scoped context routing
- translation memory decision
- `AGENTS.md` setup block state

Use `Unknown` only when a value is absent or ambiguous. If the user only asked
to view current settings, stop after the summary.

Reject runtime-only worker configuration in project-memory setup files; those
fields belong to Implement Feature.

## Settings Editor

When the requested section is unclear, use the setup-target question in
[setup-questions.md](setup-questions.md). Otherwise edit only the named or
required section and preserve unrelated custom prose, comments, mappings, path
conventions, dry-run overrides, project labels, and tracker-specific values
unless the user explicitly changes them.

Editable sections:

- `issue-tracker`
- `project-layout`
- `artifact-marker-mapping`
- `issue-type-mapping`
- `workflow-state-mapping`
- `domain-memory`
- `translation-memory`
- `agents-pointers`
- `done`

For each selected configuration section, show the current value first, then
`keep-current` and the relevant alternatives:

- `issue-tracker`: `github` or `local`.
- `project-layout`: `single-repository`, `monorepo`, or
  `multi-repository-workspace`.
- `artifact-marker-mapping`: default or custom GitHub `label`, or canonical
  local `local-header`, for the `idea` marker.
- `issue-type-mapping`: default GitHub `native-type`, evidence-backed GitHub
  fallback `label` or exact `body-field`, or canonical local `local-header`,
  with one transport and exact tracker value per canonical type.
- `workflow-state-mapping`: default or custom GitHub `label`, or canonical local
  `local-header`, with one transport and exact tracker value per state.
- `domain-memory`: show the current root `CONTEXT.md`, scoped routes, workspace
  repository registry when applicable, and centralized ADR root. Refresh those
  surfaces from evidence; during authorized setup/bootstrap, always create or
  update root `CONTEXT.md` at every memory-owning root selected by the setup
  scope. Do not present or persist a domain-layout enum.
- `translation-memory`: `enabled`, `not-applicable`, `needs-confirmation`.
- `agents-pointers`: create missing pointer block, refresh stale pointer block,
  or minimize copied setup detail into project-memory pointers.

After edits, show intended changed files and before/after settings. An explicit
request to set up, configure, initialize, update, or refresh project memory is
write authority for that scope, so proceed without a second confirmation. For
review-only, recommendation, dry-run, or indirectly suggested setup, wait for
affirmative confirmation before writing.

Ask only about a materially ambiguous target or behavior-affecting value that
repo evidence and the defaults below cannot resolve. Do not force the user
through unrelated editable sections. If ambiguity remains, load
[setup-questions.md](setup-questions.md) and use its applicable first-time-user
prompt.

## Decision Defaults

- Default to GitHub for code repos with a GitHub remote; default to local
  markdown when no clear GitHub issue tracker exists.
- Default `repository_layout` from durable repo evidence: `single-repository` for one
  Git repo and one primary context, `monorepo` for one Git repo with multiple
  independently planned contexts, and `multi-repository-workspace` for a parent
  coordination workspace with multiple child Git repos. Ask when evidence is
  contradictory.
- For dry runs or no-mutation runs, do not let a GitHub remote force GitHub
  mutation. Resolve `write_mode=propose` and treat it as current-run behavior,
  not durable issue-tracker configuration.
- Do not define durable worker assignments, worker-count limits, scheduled
  checks, publication policy, or issue mutation policy in project memory.
- Default the canonical `idea` artifact marker to the GitHub `idea` label or
  local `artifact_marker: idea`. Ask only when tracker evidence shows that the
  label is conflicting or customized.
- Read root `CONTEXT.md` first when it exists. During authorized domain
  setup/bootstrap, always create or update it at every memory-owning root
  selected by the setup scope. Populate only evidence-backed purpose,
  vocabulary, rules, boundaries, and routing. When richer evidence is absent,
  keep a minimal entry point and state the missing knowledge explicitly rather
  than inventing it.
- For a verified monorepo or multi-repository workspace, use stable topology
  evidence for root scope or repository routing. Create scoped contexts only
  when durable evidence and authority support their content. A child-repository
  root selected by the authorized setup scope follows the mandatory
  root-context rule; child repositories outside that scope remain optional and
  untouched.
- Recommend enabled translation memory only when localization support and
  durable translation rules are confirmed by evidence or the user.

## Draft Checklist

Before writing, show only applicable items from this list:

- current settings summary for review mode;
- before/after summary for proposed changes;
- intended `AGENTS.md` pointer block;
- `AGENTS.md` minimization plan;
- intended `project-memory/config/project-layout.md`;
- intended `project-memory/config/issue-tracker.md`;
- intended `project-memory/config/triage-labels.md`;
- intended root `CONTEXT.md` creation or update, including evidence-backed
  content, stable routing, and any explicit unknowns;
- intended workspace repository-registry context pointers, omitting child
  context paths that do not exist and are not authorized for creation;
- intended scoped `CONTEXT.md` files, or why root-only routing is sufficient;
- intended `TRANSLATION.md`, or why localization memory should not be written;
- intended ADR drafts, if any.

For orchestrator workspace mode, preserve these points in the draft:

- selected local or GitHub tracker backend;
- accepted parent Feature Specs, linked repo-scoped partial Feature Specs,
  repo-owned local planning subtrees, vertical issues, sibling mappings, and
  integration partials or gates are durable planning artifacts only when
  `$plan-feature` handles them during real feature planning;
- setup is config-only and must not create Feature Spec or issue subtrees;
- setup must not create Idea issues, Idea files, or `planning/ideas/`
  subtrees;
- local planning artifacts remain inside their owning child repositories;
- child repos keep their own `AGENTS.md`, `CONTEXT.md`, optional
  `TRANSLATION.md`, `project-memory`, validation, branches, commits, and PRs;
- `implement-feature` owns runtime worker state and ledgers.
- project memory must not carry worker surfaces, worker counts, approval state,
  or runtime worker progress.

## Write Rules

After direct write authority or separate affirmative confirmation:

- Create `project-memory/config/` if needed.
- Write or update the authorized setup files under `project-memory/config/`.
- In review mode, update only files needed for separately confirmed changes.
- Require any touched `issue-tracker.md` setup header to use canonical
  lower-snake-case keys with backticked structured values. Report unknown
  fields as invalid instead of rewriting them.
- Keep behavior-affecting setup fields in typed configuration tables with
  `Key`, `Type`, `Value`, `Allowed values`, and `Meaning` columns before
  explanatory prose.
- When tracker-routing or full setup creates or refreshes
  `project-memory/config/triage-labels.md`, include the canonical
  `artifact_marker: idea` mapping alongside the issue-type and workflow-state
  mappings. Require each mapping table to contain its canonical identity,
  `Transport`, `Tracker value`, and `Meaning` columns. Reject a missing,
  unknown, or backend-incompatible transport instead of inferring it or reading
  retired column shapes. If an existing repository lacks only that marker mapping, report
  Idea capture and Idea-source consumption as unavailable until setup adds it;
  do not invalidate or block unrelated workflows.
- Keep `issue-tracker.md` limited to `tracker_backend` plus human-readable
  tracker conventions. Implementation delivery policy belongs to Feature Specs
  and executors.
- Keep `project-layout.md` limited to `repository_layout`. Do not store
  source-root lists, worktree paths, worker surfaces, thread limits, or Codex
  App runtime state there.
- Preserve custom prose outside known configuration tables. Report unknown
  configuration keys instead of silently deleting them.
- Create or update `AGENTS.md` pointer block and apply only authorized
  minimization.
- Create or update root and scoped `CONTEXT.md` through
  `references/domain-modeling.md`. During authorized setup/bootstrap, ensure
  root `CONTEXT.md` exists at every memory-owning root selected by the setup
  scope before writing any scoped context or completing setup.
- Create or update `TRANSLATION.md` only when localization memory is confirmed.
- Create ADRs only for accepted, load-bearing decisions.
- Do not create Idea tracker artifacts during setup. Configuring the marker
  mapping does not authorize writing GitHub Idea issues, local Idea files, or
  `planning/ideas/` directories.
- Preserve unrelated or uncertain content in `AGENTS.md`, `CONTEXT.md`,
  `TRANSLATION.md`, ADRs, and project docs.
- Do not duplicate moved project context in both `AGENTS.md` and project
  memory.

## AGENTS.md Pointer Block

Use this shape as a menu. Include only sections whose target file exists or is
authorized in the selected slice. Omit `Localization` unless `TRANSLATION.md`
exists or is authorized; never create a broken pointer:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where Feature Specs and issues live]. See `project-memory/config/issue-tracker.md`.

### Project layout

[one-line summary of project topology]. See `project-memory/config/project-layout.md`.

### Artifact markers, issue types, and workflow states

[one-line summary of the canonical artifact-marker, issue-type, and workflow-state vocabulary and its tracker mappings]. See `project-memory/config/triage-labels.md`.

### Domain memory

[one-line summary of shared context and any scoped routing]. Read `CONTEXT.md` first, then follow its `Scoped Contexts` table when relevant.

### Localization

[one-line summary of supported localization memory]. See `<path-to-TRANSLATION.md>`.
```

Keep this block concise. Do not paste domain vocabulary, tracker procedures,
implementation policy, localization rules, worker-dispatch rules, or context seed
material into `AGENTS.md`. `$implement-feature` owns its session worker
questions, checkpoint, dispatch, and ledger progress record. For orchestrator
workspaces, explicitly say the workspace coordinates external repos and child
repos keep their own project memory and code ownership.

## Completion Report

Summarize only the applicable fields:

- execution context;
- files written;
- settings reviewed and changed;
- selected issue tracker;
- project topology;
- artifact-marker transport and mapping;
- issue-type and workflow-state transport and mapping;
- root/scoped context routing;
- localization-memory decision and evidence;
- `AGENTS.md` minimization outcome;
- workspace mode, if applicable;
- session-history window and whether it was used;
- root-context creation or update, evidence-backed terms/rules/routing, and
  explicit unknowns;
- `TRANSLATION.md` audience, locale, terminology, or open questions seeded;
- ADRs created or updated;
- workflows that can now consume setup.

## Standard Ambiguity Questions

Normally ask no questions. After repository evidence and the defaults above
leave a material ambiguity, load
[setup-questions.md](setup-questions.md) and use exactly one applicable
evidence-first template. Its canonical question set covers setup target,
conflicting project structure, conflicting issue locations, separate project
contexts, overlapping project ownership, workspace-versus-repository rules,
localization conventions, artifact-marker mappings, issue-type mappings, and
workflow-state mappings.

Keep Project Memory internals out of user-facing prompts. Ask about concrete
projects, repositories, paths, trackers, rules, and localization behavior, then
translate the answer to canonical configuration internally. Never ask the user
whether evidence is sufficient, combine two unresolved decisions in one
question, or ask a question already resolved by an explicit request, durable
repository evidence, or a documented default.
