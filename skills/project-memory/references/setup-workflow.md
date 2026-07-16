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
- `issue_type` mapping
- `workflow_state` mapping
- domain memory layout
- context seed decision
- translation memory decision
- `AGENTS.md` setup block state

Use `Unknown` only when a value is absent or ambiguous. If the user only asked
to view current settings, stop after the summary.

Reject runtime-only worker configuration in project-memory setup files; those
fields belong to Codex Orchestrator.

## Settings Editor

When the requested section is unclear, ask which section to change. Otherwise
edit only the named or required section and preserve unrelated custom prose,
comments, mappings, path conventions, dry-run overrides, project labels, and
tracker-specific values unless the user explicitly changes them.

Editable sections:

- `issue-tracker`
- `project-layout`
- `issue-type-mapping`
- `workflow-state-mapping`
- `domain-memory`
- `translation-memory`
- `context-seed`
- `agents-pointers`
- `done`

For each selected section, show the current value first, then `keep-current`
and the relevant alternatives:

- `issue-tracker`: `github` or `local`.
- `project-layout`: `single-repository`, `monorepo`, or
  `multi-repository-workspace`.
- `issue-type-mapping`: default GitHub mapping, canonical local mapping, or
  custom per canonical type.
- `workflow-state-mapping`: default GitHub lowercase labels, canonical local
  mapping, or custom per canonical state.
- `domain-memory`: `single-context`, `multi-context`, `orchestrator-context`.
- `translation-memory`: `enabled`, `not-applicable`, `needs-confirmation`.
- `context-seed`: `seed-context`, `routing-only`.
- `agents-pointers`: create missing pointer block, refresh stale pointer block,
  or minimize copied setup detail into project-memory pointers.

After edits, show intended changed files and before/after settings. An explicit
request to set up, configure, initialize, update, or refresh project memory is
write authority for that scope, so proceed without a second confirmation. For
review-only, recommendation, dry-run, or indirectly suggested setup, wait for
affirmative confirmation before writing.

Ask only about a materially ambiguous target or behavior-affecting value that
repo evidence and the defaults below cannot resolve. Do not force the user
through unrelated editable sections.

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
- Default domain layout to `single-context` unless `CONTEXT-MAP.md`, repo
  evidence, or orchestrator mode implies otherwise.
- Recommend `seed-context` only when non-empty repo evidence supports useful
  domain memory; otherwise use `routing-only`.
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
- intended `project-memory/config/domain.md`;
- intended `CONTEXT.md` seed, or why none should be written;
- intended `TRANSLATION.md`, or why localization memory should not be written;
- intended ADR drafts, if any.

For orchestrator workspace mode, preserve these points in the draft:

- selected local or GitHub tracker backend;
- linked partial Feature Specs, local project folders, vertical issues, repo pointer
  sheets, and integration gates are durable planning artifacts only when
  `$plan-feature` writes them for real feature planning;
- setup is config-only and must not create project or feature folders;
- child repos keep their own `AGENTS.md`, `CONTEXT.md`, optional
  `TRANSLATION.md`, `project-memory`, validation, branches, commits, and PRs;
- `codex-orchestrator` owns runtime worker state and ledgers.
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
- Create or update `CONTEXT.md` through `references/domain-modeling.md` when
  seed/bootstrap is accepted.
- Create or update `TRANSLATION.md` only when localization memory is confirmed.
- Create ADRs only for accepted, load-bearing decisions.
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

### Issue types and workflow states

[one-line summary of the canonical issue type/workflow state vocabulary and its tracker mappings]. See `project-memory/config/triage-labels.md`.

### Domain memory

[one-line summary of single-context, multi-context, or orchestrator layout]. See `project-memory/config/domain.md`.

### Localization

[one-line summary of supported localization memory]. See `<path-to-TRANSLATION.md>`.
```

Keep this block concise. Do not paste domain vocabulary, tracker procedures,
implementation policy, localization rules, worker-dispatch rules, or context seed
material into `AGENTS.md`. `$codex-orchestrator` owns its session worker
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
- issue-type and workflow-state mapping;
- domain-memory layout;
- localization-memory decision and evidence;
- `AGENTS.md` minimization outcome;
- workspace mode, if applicable;
- session-history window and whether it was used;
- context seed evidence and seeded terms/rules/open questions;
- `TRANSLATION.md` audience, locale, terminology, or open questions seeded;
- ADRs created or updated;
- workflows that can now consume setup.
