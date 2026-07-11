---
name: project-memory
description: Maintain tracker routing, domain language, ADRs, context, decisions, and localization memory.
---

# Project Memory

## Purpose

Use `$project-memory` as the single public entry point for durable repository
memory:

- lean project-memory pointers in `AGENTS.md`;
- tracker and delivery routing in `project-memory/agents/issue-tracker.md`;
- issue type/state mappings in `project-memory/agents/triage-labels.md`;
- domain layout in `project-memory/agents/domain.md`;
- `CONTEXT.md`, domain docs, and ADRs under `project-memory/adr/`;
- optional `TRANSLATION.md` when localization rules are real.

Use the smallest requested slice. Tracker routing does not require domain or
localization work, and domain updates do not require tracker setup.

## Operations And Shape

| Slice | Owns |
| --- | --- |
| `tracker-routing` | Tracker backend, delivery mode, issue-type mapping, and triage-state mapping. |
| `domain-memory` | Domain layout plus context/domain-doc/ADR setup, inline update, implementation closeout, or periodic review. |
| `translation-memory` | Localization memory only. |
| `agents-pointers` | Missing or stale project-memory pointers only. |
| `full-setup` | All applicable slices, only when explicitly requested. |

For `domain-memory`, use an explicit operation from
`references/domain-modeling.md`: `setup-bootstrap`, `inline-update`,
`implementation-closeout`, or `periodic-review`.

Execution context is orthogonal to the slice and operation:

- `fresh-setup`: selected files are missing;
- `existing-project-bootstrap`: reconcile accepted repo or recent same-repo
  session evidence;
- `orchestrator-workspace`: configure only root coordination memory and never
  create project/feature artifacts during setup;
- current-run no-mutation override: review/propose without persistent writes.

## Non-Negotiable Boundaries

- Use `AGENTS.md` for operating pointers only. Domain context, tracker detail,
  planning history, localization rules, and accepted decisions live in their
  dedicated memory surfaces.
- Load `references/domain-modeling.md` before creating, updating, reviewing, or
  reconciling `CONTEXT.md`, domain docs, or ADRs. Reading
  `project-memory/agents/domain.md` is not equivalent.
- Seed durable memory only from strong repo evidence, committed behavior,
  accepted tracker decisions, final session evidence, or explicit user
  acceptance. Exclude tentative/rejected ideas, secrets, raw logs, and weak
  inferences.
- Create `TRANSLATION.md` only when localization support or durable translation
  rules are evidenced or confirmed. Do not create empty ADR directories.
- Explicit setup/configure/initialize/update/refresh instructions authorize
  only the requested slice. A ready implementation-closeout task authorizes
  only its named decisions, evidence, and target surfaces.
- An explicitly invoked composed workflow may authorize `inline-update` only
  when its caller has durable domain-memory write authority. Tracker mutation
  authority alone is insufficient.
- Inspect-only, review-only, proposal, dry-run, or indirect suggestions are not
  write authority. Return the proposed change instead.
- Preserve unrelated custom prose, mappings, comments, overrides, domain docs,
  ADRs, and localization content.
- Ask only when the target or behavior-affecting value is materially ambiguous
  after repo evidence and documented defaults.

## Structured Configuration

Behavior-affecting setup uses human-first Markdown tables with
`lower_snake_case` keys and `lower-kebab-case` values:

| Key | Values | Owner |
| --- | --- | --- |
| `tracker_backend` | `github`, `local` | `issue-tracker.md` |
| `delivery_mode` | `pull-request`, `direct-commit` | `issue-tracker.md`, PRDs, generated issues |

Treat uppercase kebab values as read aliases and normalize touched values.
Do not add durable keys for workspace shape, setup flow, GitHub repo,
coordination repo, workers, publication/issue-mutation authority, scheduled
checks, or current-run no-mutation intent. Use prose, planning artifacts, or
the orchestrator ledger for those concerns.

`references/setup-workflow.md` owns the settings editor, legacy-key migration,
table normalization, draft checklist, pointer block, and completion report.
When touching `issue-tracker.md`, require `tracker_backend` and `delivery_mode`,
preserve useful prose, and remove runtime-only/legacy table rows unless their
meaning is deliberately retained as prose.

## Reference Loading Matrix

Load only the selected branch:

| Work | Required references |
| --- | --- |
| Tracker routing | `issue-tracker-github.md` or `issue-tracker-local.md`, `tracker-publishing.md`, `triage-labels.md`, and `setup-workflow.md` for edits. |
| Domain setup/bootstrap | `domain.md`, `domain-modeling.md`, `context-seed.md`; add `session-history.md` only for existing-project bootstrap. |
| Domain inline update / implementation closeout / periodic review | `domain-modeling.md`; add `domain.md` only when target layout or ownership is ambiguous, and `documentation-shapes.md` only when no stronger local shape exists. |
| Translation | `translation.md`. |
| Pointer/settings work | `setup-workflow.md`. |

Do not load domain, localization, or session-history evidence for tracker-only
work. This operation-specific loading rule is part of the token contract.

## Workflow

### 1. Resolve Slice, Operation, And Write Authority

Select the smallest slice and execution context above. For
`implementation-closeout`, carry only the named decisions, evidence, targets,
and integrated feature proof. For temporary/rehearsal/validation work, use a
current-run no-mutation override rather than persisting it as configuration.

### 2. Inspect Focused Evidence

- tracker: current setup, remotes/config, templates, tracker docs, and relevant
  local/workspace conventions;
- domain: current pointers, README/docs/manifests, relevant source/tests/schema,
  context files, domain layout, and ADRs;
- translation: translation memory, locale catalogs/config, copy guidance, and
  market requirements;
- pointers: `AGENTS.md` and the files it should index.

For existing-project domain bootstrap, use `session-history.md` only when
recent same-repo evidence is strong enough to be durable.

When `AGENTS.md` mixes concerns, keep operating rules there and route project
purpose/vocabulary to `CONTEXT.md`, localization to `TRANSLATION.md`, tracker
and layout settings to `project-memory/agents/*`, and accepted load-bearing
decisions to ADRs.

### 3. Resolve Settings Or Delta

For setup/review, summarize only the selected slice and use `Unknown` for
ambiguous values. Resolve only its behavior-affecting settings. For
implementation closeout or inline update, summarize the carried decisions,
evidence, named targets, and write authority instead of unrelated setup.

### 4. Draft And Show The Change

Before writing, show intended files and meaningful before/after values. Follow
the loading matrix and existing local formats. In custom tracker workflows,
preserve the described conventions while keeping the structured table limited
to `tracker_backend` and `delivery_mode`.

### 5. Write And Verify Authorized Memory

Update only authorized files. Keep `AGENTS.md` pointer-first. Use
`domain-modeling.md` for domain content and reconcile implementation-closeout
decisions against behavior that actually landed; omit provisional planning
language and verify the docs diff alongside feature proof.

In orchestrator-workspace setup, do not create project or feature folders. Do
not create orchestration runtime config files. Before completing a touched
`issue-tracker.md`, search for `tracker_mode`, `tracker_writes`,
`effective_target`, `local_artifact_writes`, and
`external_tracker_mutation`; remove them or explain why retained prose remains.

### 6. Report

Report the operation, slice, files changed, reviewed settings/surfaces, evidence,
and consuming workflows. For implementation closeout, also report the source
task/decision, durable decisions accepted or rejected, named targets updated,
feature proof, and documentation-diff verification. Mention unavailable or weak
session evidence plainly.

## Reference Responsibilities

- `setup-workflow.md`: settings editor, normalization, pointers, and report.
- `issue-tracker-*.md`, `tracker-publishing.md`, `triage-labels.md`: tracker,
  artifact, type/state, source-ref, and completion contracts.
- `domain.md`: domain-memory layout and ownership.
- `domain-modeling.md`: domain setup, inline update, implementation closeout,
  and periodic review semantics.
- `documentation-shapes.md`: fallback context and ADR shapes.
- `context-seed.md`, `session-history.md`: initial and session-backed bootstrap.
- `translation.md`: optional localization memory.
