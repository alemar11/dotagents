# Setup Workflow Details

Use this reference for the interactive setup editor, draft checklist, write
rules, `AGENTS.md` pointer block, and completion report. Keep the public
`SKILL.md` focused on routing and hard boundaries.

## Current Settings Summary

When reviewing existing setup, summarize available values before recommending
changes:

- `setup_mode`
- `tracker_mode`
- `effective_target`
- `run_authorization`: `local_artifact_writes` and `external_tracker_mutation`,
  including whether each value is durable or current-run only
- `delivery_mode`
- `issue_type` mapping
- `triage_state` mapping
- `domain_memory_layout`
- `context_seed_mode`
- `translation_memory`
- `AGENTS.md` setup block state

Use `Unknown` only when a value is absent or ambiguous. If the user only asked
to view current settings, stop after the summary.

If existing setup files contain the legacy worker-authorization setup key,
report it as stale orchestrator-owned state. Remove it from any touched
`project-memory/agents/*` file after confirmation; do not offer it as an
editable project-memory setting.

## Settings Editor

When editing setup, ask which section to change and preserve unrelated custom
prose, comments, mappings, path conventions, dry-run overrides, project labels,
and tracker-specific values unless the user explicitly changes them.

Editable sections:

- `issue-tracker`
- `run-authorization`
- `delivery-mode`
- `issue-type-mapping`
- `triage-state-mapping`
- `domain-memory`
- `translation-memory`
- `context-seed`
- `agents-pointers`
- `done`

For each selected section, show the current value first, then `keep-current`
and the relevant alternatives:

- `issue-tracker`: `github`, `local-markdown`, `orchestrator-local`,
  `orchestrator-github`, `other`.
- `run-authorization`: `local-artifacts-only`, `external-tracker-only`,
  `both-allowed`, `both-disallowed`. Treat as current-run authority unless the
  user explicitly asks for durable defaults.
- `delivery-mode`: `one-feature-branch`, `one-pr-per-repo`,
  `one-pr-per-issue`, `direct-commit`.
- `issue-type-mapping`: default GitHub mapping, canonical local mapping, or
  custom per canonical type.
- `triage-state-mapping`: default GitHub lowercase labels, canonical local
  mapping, or custom per canonical state.
- `domain-memory`: `single-context`, `multi-context`, `orchestrator-context`.
- `translation-memory`: `enabled`, `not-applicable`, `needs-confirmation`.
- `context-seed`: `seed-context`, `routing-only`.
- `agents-pointers`: create missing pointer block, refresh stale pointer block,
  or minimize copied setup detail into project-memory pointers.

After edits, show intended changed files and before/after settings. Ask for
confirmation before writing.

## Decision Defaults

- Default to GitHub for code repos with a GitHub remote; default to local
  markdown when no clear GitHub issue tracker exists.
- For dry runs or no-external-mutation runs, do not let a GitHub remote force
  GitHub mutation. Record any override as current-run only unless the user says
  to persist it.
- Default delivery mode to `one-feature-branch` for one git repo and
  `one-pr-per-repo` for true multi-repo or orchestrator work.
- Do not define worker authorization in project memory. `$codex-orchestrator`
  resolves worker capability modes per workstream and session.
- Default domain layout to `single-context` unless `CONTEXT-MAP.md`, repo
  evidence, or orchestrator mode implies otherwise.
- Recommend `seed-context` only when non-empty repo evidence supports useful
  domain memory; otherwise use `routing-only`.
- Recommend `translation_memory=enabled` only when localization support and
  durable translation rules are confirmed by evidence or the user.

## Draft Checklist

Before writing, show:

- current settings summary for review mode;
- before/after summary for proposed changes;
- intended `AGENTS.md` pointer block;
- `AGENTS.md` minimization plan;
- intended `project-memory/agents/issue-tracker.md`;
- intended `project-memory/agents/triage-labels.md`;
- intended `project-memory/agents/domain.md`;
- intended `CONTEXT.md` seed, or why none should be written;
- intended `TRANSLATION.md`, or why localization memory should not be written;
- intended ADR drafts, if any.

For orchestrator workspace mode, preserve these points in the draft:

- selected local or GitHub coordination backend;
- project folders, PRDs, vertical issues, repo pointer sheets, and integration
  gates are durable planning artifacts;
- setup is config-only and must not create project or feature folders;
- child repos keep their own `AGENTS.md`, `CONTEXT.md`, optional
  `TRANSLATION.md`, `project-memory`, validation, branches, commits, and PRs;
- `codex-orchestrator` owns runtime worker state and ledgers.

## Write Rules

After confirmation:

- Create `project-memory/agents/` if needed.
- Write or update the three setup files under `project-memory/agents/`.
- In review mode, update only files needed for confirmed changes.
- Create or update `AGENTS.md` pointer block and apply only confirmed
  minimization.
- Create or update `CONTEXT.md` with `$domain-modeling` when seed/bootstrap is
  accepted.
- Create or update `TRANSLATION.md` only when localization memory is confirmed.
- Create ADRs only for accepted, load-bearing decisions.
- Preserve unrelated or uncertain content in `AGENTS.md`, `CONTEXT.md`,
  `TRANSLATION.md`, ADRs, and project docs.
- Do not duplicate moved project context in both `AGENTS.md` and project
  memory.

## AGENTS.md Pointer Block

Use this shape and omit the `Localization` section unless `TRANSLATION.md`
exists or is confirmed:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where PRDs and issues live]. See `project-memory/agents/issue-tracker.md`.

### Triage types and labels

[one-line summary of issue type and state vocabulary]. See `project-memory/agents/triage-labels.md`.

### Domain memory

[one-line summary of single-context, multi-context, or orchestrator layout]. See `project-memory/agents/domain.md`.

### Localization

[one-line summary of supported localization memory]. See `<path-to-TRANSLATION.md>`.
```

Keep this block concise. Do not paste domain vocabulary, tracker procedures,
delivery details, localization rules, or context seed material into `AGENTS.md`.
For orchestrator workspaces, explicitly say the workspace coordinates external
repos and child repos keep their own project memory and code ownership.

## Completion Report

Summarize:

- setup mode;
- files written;
- settings reviewed and changed;
- selected issue tracker;
- run authorization and whether it is durable or current-run only;
- delivery mode defaults;
- issue-type and triage-state mapping;
- domain-memory layout;
- localization-memory decision and evidence;
- `AGENTS.md` minimization outcome;
- workspace mode and coordination backend, if applicable;
- session-history window and whether it was used;
- context seed evidence and seeded terms/rules/open questions;
- `TRANSLATION.md` audience, locale, terminology, or open questions seeded;
- ADRs created or updated;
- workflows that can now consume setup.
