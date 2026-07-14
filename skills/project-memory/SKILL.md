---
name: project-memory
description: Maintain tracker routing, domain language, ADRs, context, decisions, and localization memory.
---

# Project Memory

## Purpose

Use `$project-memory` as the single public entry point for durable repository
memory:

- lean project-memory pointers in `AGENTS.md`;
- tracker and delivery routing in `project-memory/config/issue-tracker.md`;
- durable project topology in `project-memory/config/project-layout.md`;
- issue type/state mappings in `project-memory/config/triage-labels.md`;
- domain layout in `project-memory/config/domain.md`;
- `CONTEXT.md`, domain docs, and ADRs under `project-memory/adr/`;
- optional `TRANSLATION.md` when localization rules are real.

Use the smallest requested `memory_slice`. Tracker routing does not require
domain or localization work, and domain updates do not require tracker setup.

Load `references/options.md` before resolving any branch. Normalize natural
language and legacy fields once, then use only canonical field/value
assignments in current handoffs and reports.

## Operations And Shape

| `memory_slice` | Owns |
| --- | --- |
| `tracker-routing` | Tracker backend, delivery mode, issue-type mapping, and triage-state mapping. |
| `project-layout` | Durable project topology: `single-repo`, `monorepo`, or `multi-repo-workspace`. |
| `domain-memory` | Domain layout plus context/domain-doc/ADR setup, inline update, implementation closeout, or periodic review. |
| `translation-memory` | Localization memory only. |
| `agents-pointers` | Missing or stale project-memory pointers only. |
| `full-setup` | All applicable slices, only when explicitly requested. |

For `memory_slice=domain-memory`, resolve `domain_operation` from
`references/domain-modeling.md`: `setup-bootstrap`, `inline-update`,
`implementation-closeout`, or `periodic-review`.

`execution_context` is orthogonal to `memory_slice` and `domain_operation`:

- `execution_context=fresh-setup`: selected files are missing;
- `execution_context=existing-project-bootstrap`: reconcile accepted repo or recent same-repo
  session evidence;
- `execution_context=orchestrator-workspace`: configure only root coordination memory and never
  create project/feature artifacts during setup;
- `execution_context=current-project`: operate on established project memory
  without bootstrap semantics.

Resolve `write_mode=propose` for a current-run no-mutation override; otherwise
use `write_mode=apply` only when the selected scope has write authority.

## Non-Negotiable Boundaries

- Use `AGENTS.md` for operating pointers only. Domain context, tracker detail,
  planning history, localization rules, and accepted decisions live in their
  dedicated memory surfaces.
- Load `references/domain-modeling.md` before creating, updating, reviewing, or
  reconciling `CONTEXT.md`, domain docs, or ADRs. Reading
  `project-memory/config/domain.md` is not equivalent.
- Seed durable memory only from strong repo evidence, committed behavior,
  accepted tracker decisions, final session evidence, or explicit user
  acceptance. Exclude tentative/rejected ideas, secrets, raw logs, and weak
  inferences.
- Create `TRANSLATION.md` only when localization support or durable translation
  rules are evidenced or confirmed. Do not create empty ADR directories.
- Explicit setup/configure/initialize/update/refresh instructions authorize
  only the requested `memory_slice`. A ready implementation-closeout task authorizes
  only its named decisions, evidence, and target surfaces.
- An explicitly invoked composed workflow may authorize
  `domain_operation=inline-update` only
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
| `delivery_mode` | `pull-request`, `direct-commit` | `issue-tracker.md`, Feature Specs, generated issues |
| `project_topology` | `single-repo`, `monorepo`, `multi-repo-workspace` | `project-layout.md` |

Treat uppercase kebab values as read aliases and normalize touched values.
Do not add durable keys for Codex runtime workspace shape, source-root lists,
worktree paths, setup flow, GitHub repo, coordination repo, workers,
publication/issue-mutation authority, scheduled checks, or current-run
no-mutation intent. Use prose, planning artifacts, or the orchestrator ledger
for those concerns.

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
| Project layout | `project-layout.md` and `setup-workflow.md` for edits. |
| Domain setup/bootstrap | `domain.md`, `domain-modeling.md`, `context-seed.md`; add `session-history.md` only for `execution_context=existing-project-bootstrap`. |
| Domain inline update / implementation closeout / periodic review | `domain-modeling.md`; add `domain.md` only when target layout or ownership is ambiguous, and `documentation-shapes.md` only when no stronger local shape exists. |
| Translation | `translation.md`. |
| Pointer/settings work | `setup-workflow.md`. |

Do not load domain, localization, or session-history evidence for tracker-only
work. This operation-specific loading rule is part of the token contract.

## Workflow

### 1. Resolve Slice, Operation, And Write Authority

Select the smallest `memory_slice` and `execution_context` above. For
`domain_operation=implementation-closeout`, carry only the named decisions,
evidence, targets, and integrated feature proof. For
temporary/rehearsal/validation work, resolve `write_mode=propose` rather than
persisting the no-mutation intent as configuration.

### 2. Inspect Focused Evidence

- tracker: current setup, remotes/config, templates, tracker docs, and relevant
  local/workspace conventions;
- project layout: Git root shape, package/workspace manifests,
  `CONTEXT-MAP.md`, child repository evidence, and existing project-memory
  topology config;
- domain: current pointers, README/docs/manifests, relevant source/tests/schema,
  context files, domain layout, and ADRs;
- translation: translation memory, locale catalogs/config, copy guidance, and
  market requirements;
- pointers: `AGENTS.md` and the files it should index.

For existing-project domain bootstrap, use `session-history.md` only when
recent same-repo evidence is strong enough to be durable.

When `AGENTS.md` mixes concerns, keep operating rules there and route project
purpose/vocabulary to `CONTEXT.md`, localization to `TRANSLATION.md`, tracker
and layout settings to `project-memory/config/*`, and accepted load-bearing
decisions to ADRs.

### 3. Resolve Settings Or Delta

For setup/review, summarize only the selected `memory_slice` and use `Unknown`
for ambiguous values. Resolve only its behavior-affecting settings. For
`domain_operation=implementation-closeout` or
`domain_operation=inline-update`, summarize the carried decisions, evidence,
named targets, and write authority instead of unrelated setup.

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

Report `memory_slice`, `domain_operation`, `execution_context`, `write_mode`,
files changed, reviewed settings/surfaces, evidence, and consuming workflows.
For `memory_slice=domain-memory`, also report `capture_outcome`; other slices
omit that domain-only field. Keep destinations, accepted/rejected decisions,
and deferral explanations as separate data. For
`domain_operation=implementation-closeout`, also report the source
task/decision, durable decisions accepted or rejected, named targets updated,
feature proof, and documentation-diff verification. Mention unavailable or
weak session evidence plainly.

## Reference Responsibilities

- `options.md`: canonical option fields, values, and legacy normalization.
- `setup-workflow.md`: settings editor, normalization, pointers, and report.
- `project-layout.md`: durable `project_topology` configuration and topology
  detection boundaries.
- `issue-tracker-*.md`, `tracker-publishing.md`, `triage-labels.md`: tracker,
  artifact, type/state, source-ref, and completion contracts.
- `domain.md`: domain-memory layout and ownership.
- `domain-modeling.md`: domain setup, inline update, implementation closeout,
  and periodic review semantics.
- `documentation-shapes.md`: fallback context and ADR shapes.
- `context-seed.md`, `session-history.md`: initial and session-backed bootstrap.
- `translation.md`: optional localization memory.
