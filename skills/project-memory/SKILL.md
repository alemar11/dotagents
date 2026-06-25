---
name: project-memory
description: Configure or review lean project-memory before planning, PRD, issue-splitting, triage, or domain-memory workflows, including CONTEXT.md seeds and optional TRANSLATION.md memory.
---

# Project Memory

## Goal

Configure the repo memory that other skills consume:

- `AGENTS.md` for lean operating pointers.
- `project-memory/agents/issue-tracker.md` for PRD and issue routing.
- `project-memory/agents/triage-labels.md` for issue type and state mappings.
- `project-memory/agents/domain.md` for context, translation, and ADR layout.
- `CONTEXT.md` and optional `project-memory/adr/` for domain memory.
- `TRANSLATION.md` when localization support or translation rules are real.

Run this once per code repo, monorepo, or orchestrator workspace before
planning, publishing PRDs, splitting issues, triaging, or updating
project-backed domain memory. Re-run it when tracker routing, mappings,
domain-memory layout, localization policy, or `AGENTS.md` pointers change.

## Boundaries

- Always use `AGENTS.md` for setup pointers when an agent-instruction file is
  needed.
- Keep `AGENTS.md` pointer-first: operating rules stay there; domain context,
  tracker detail, planning history, localization rules, and accepted decisions
  move to project memory.
- Load and follow `$domain-modeling` before creating or updating `CONTEXT.md`
  or ADRs.
- Seed `CONTEXT.md`, `TRANSLATION.md`, or ADRs only from strong repo evidence,
  final session summaries, committed behavior, or explicit user acceptance.
- Create `TRANSLATION.md` only when localization support or durable translation
  rules are clear from evidence or confirmed by the user.
- Do not record tentative proposals, rejected ideas, secrets, raw logs, broad
  doctrine, or weak session inferences.
- Do not create empty `project-memory/adr/` directories just to show intent.
- In orchestrator workspace mode, configure only root setup files. Do not create
  `projects/<project>/`, feature PRDs, or issue files during setup.
- Ask for confirmation before writing files.

## Structured Values

Use `lower_snake_case` keys and `lower-kebab-case` values for setup-owned
structured fields. Treat older uppercase kebab-case values as legacy aliases
when reading existing artifacts; rewrite touched values to lower-kebab-case.

| Key | Values |
| --- | --- |
| `setup_mode` | `fresh-setup`, `existing-project-bootstrap`, `orchestrator-workspace` |
| `tracker_mode` | `github`, `local-markdown`, `orchestrator-local`, `orchestrator-github`, `other` |
| `effective_target` | `configured-tracker`, `local-dry-run`, `draft-publish-commands` |
| `local_artifact_writes`, `external_tracker_mutation` | `allowed`, `disallowed` |
| `delivery_mode` | `one-feature-branch`, `one-pr-per-repo`, `one-pr-per-issue`, `direct-commit` |
| `default_worker_authorization` | comma-separated `$codex-orchestrator` worker capabilities, default `inspect, implement` |
| `domain_memory_layout` | `single-context`, `multi-context`, `orchestrator-context` |
| `context_seed_mode` | `seed-context`, `routing-only` |
| `translation_memory` | `enabled`, `not-applicable`, `needs-confirmation` |

Detailed meanings and generated-file shapes live in the references listed
below.

## Workflow

### 1. Choose Setup Mode

- Use `fresh-setup` when setup files are missing. In non-empty repos, also check
  whether evidence supports an initial `CONTEXT.md` seed.
- Use `existing-project-bootstrap` when reconciling existing docs, partial
  project memory, accepted knowledge, recent same-repo session history, or ADR
  candidates.
- Use `orchestrator-workspace` only for a parent coordination workspace that
  plans across independent repos. Do not treat it as a monorepo.
- For temp, rehearsal, validation, or dry-run work, keep external mutation
  disallowed unless the user explicitly authorizes it.

### 2. Inspect Evidence

Read enough current state to avoid guessing:

- `git remote -v`, `.git/config`, `AGENTS.md`, `README.md`, docs, manifests,
  source directories, tests, schemas, issue templates, and tracker docs.
- `project-memory/agents/*`, `CONTEXT.md`, `CONTEXT-MAP.md`,
  `TRANSLATION.md`, and `project-memory/adr/` when present.
- `.scratch/` for local markdown issue tracking and `projects/` for
  orchestrator workspace signals.
- Localization evidence: locale folders, translation catalogs, i18n/l10n
  packages, app/framework locale config, product docs, copy guidelines,
  app-store language metadata, or target-market language requirements.

When `AGENTS.md` already contains setup or project context, classify content
before writing:

- keep agent operating rules in `AGENTS.md`;
- move project purpose, vocabulary, boundaries, and open questions to
  `CONTEXT.md`;
- move localization policy to `TRANSLATION.md`;
- move tracker, triage, delivery, worker, and domain layout to
  `project-memory/agents/*`;
- move accepted load-bearing decisions to ADRs;
- preserve or ask about stale, conflicting, or weakly evidenced content.

For `existing-project-bootstrap`, read `references/session-history.md` and use
recent session evidence only when it is strong enough to be durable.

### 3. Review Or Confirm Settings

If setup files already exist, or the user asks to show/review/change settings,
summarize current settings before proposing edits. Include only known values;
use `Unknown` when absent or ambiguous.

Resolve these decisions for new setup or requested edits:

- issue tracker and current-run mutation authority;
- delivery mode and worker authorization defaults;
- issue type and triage state mappings;
- domain-memory layout and context seed mode;
- localization memory state;
- `AGENTS.md` pointer creation or minimization.

Use `references/setup-workflow.md` for the settings editor protocol, option
sets, draft checklist, write rules, `AGENTS.md` block, and completion report.

### 4. Draft Project Memory

Before writing, show the intended files and the relevant before/after summary.
Use these references as starting points:

- `references/issue-tracker-github.md`
- `references/issue-tracker-local.md`
- `references/issue-tracker-orchestrator-github.md`
- `references/issue-tracker-orchestrator-local.md`
- `references/tracker-publishing.md`
- `references/triage-labels.md`
- `references/domain.md`
- `references/context-seed.md`
- `references/translation.md`
- `references/session-history.md`
- `references/setup-workflow.md`

For `tracker_mode=other`, write `issue-tracker.md` from the user's described
workflow instead of forcing a hosted-tracker template.

### 5. Write Confirmed Setup

After confirmation:

- Create or update only the confirmed setup files.
- Preserve unrelated custom prose, mappings, comments, overrides, docs, ADRs,
  and `TRANSLATION.md` content.
- Keep `AGENTS.md` concise and pointer-only for project memory.
- Use `$domain-modeling` for `CONTEXT.md` and ADR shape.
- Use `references/translation.md` for `TRANSLATION.md`.
- Optionally add a one-line `CONTEXT.md` pointer to neighboring
  `TRANSLATION.md` only when localization affects audience, domain terms,
  product naming, or user-facing copy. Do not require the pointer or create
  broken links.
- In orchestrator workspace mode, do not create project or feature folders.

### 6. Report Completion

Report setup mode, files written, reviewed/changed settings, tracker target,
authorization, delivery and worker defaults, mappings, domain layout,
localization decision, `AGENTS.md` minimization, context/translation/ADR seeds,
session-history usage, and the workflows that can now consume this setup.

If session history is unavailable or weak, say so plainly. Future
`$domain-modeling`, `$grill-me-with-context`, and planning workflows can keep
filling project memory incrementally.

## Reference Responsibilities

- `issue-tracker-*.md`: tracker-specific artifact locations, publication rules,
  delivery defaults, worker defaults, title formats, and completion.
- `tracker-publishing.md`: shared effective target, draft publish, temporary
  body-file, and `source_prd_ref` contract.
- `triage-labels.md`: canonical issue type and workflow-state mappings.
- `domain.md`: context, translation, ADR layout, orchestrator boundaries, and
  domain-memory consumption.
- `context-seed.md`: minimal initial `CONTEXT.md` evidence threshold and shape.
- `translation.md`: optional `TRANSLATION.md` evidence threshold, location,
  shape, and pointer rule.
- `session-history.md`: same-repo session evidence lookup for existing-project
  bootstrap.
- `setup-workflow.md`: setup editor details, draft/write checklist,
  `AGENTS.md` pointer block, and completion report fields.
