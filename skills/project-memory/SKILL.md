---
name: project-memory
description: Maintain tracker routing, domain language, ADRs, context, decisions, and localization memory.
---

# Project Memory

## Purpose

Use `$project-memory` as the single public entry point for durable repository
memory:

- lean project-memory pointers in `AGENTS.md`;
- tracker routing in `project-memory/config/issue-tracker.md`;
- durable project topology in `project-memory/config/project-layout.md`;
- canonical artifact-marker, issue-type, and workflow-state vocabulary and
  repository mappings in
  `project-memory/config/triage-labels.md`;
- root-first domain routing through `CONTEXT.md`, with optional scoped
  `CONTEXT.md` files;
- domain docs and centralized ADRs under the memory-owning root's
  `project-memory/adr/`;
- optional `TRANSLATION.md` when localization rules are real.

Use the smallest requested `memory_slice`. Tracker routing does not require
domain or localization work, and domain updates do not require tracker setup.

Load `references/options.md` before resolving any branch. Resolve natural
language directly to canonical field/value assignments and reject noncanonical
structured fields in current handoffs and reports.

## Operations And Shape

| `memory_slice` | Owns |
| --- | --- |
| `tracker-routing` | Tracker backend plus canonical artifact-marker, issue-type, and workflow-state vocabulary and mappings. |
| `project-layout` | Durable project topology: `single-repository`, `monorepo`, or `multi-repository-workspace`. |
| `domain-memory` | Root/scoped context routing plus domain-doc/ADR setup, inline update, implementation closeout, or periodic review. |
| `translation-memory` | Localization memory only. |
| `agents-pointers` | Missing or stale project-memory pointers only. |
| `full-setup` | All applicable slices, only when explicitly requested. |

For `memory_slice=domain-memory`, resolve `domain_operation` from
`references/domain-modeling.md`: `setup-bootstrap`, `inline-update`,
`implementation-closeout`, or `periodic-review`.

Derive `execution_context` from repository evidence after selecting the slice;
it is not a user or caller option. Apply the exact ordered precedence in
`references/options.md`, which yields one of `orchestrator-workspace`,
`fresh-setup`, `existing-project-bootstrap`, or `current-project`. Do not
redefine or reorder those predicates in another reference.

Resolve `write_mode=propose` for a non-mutating run. Use `write_mode=apply` only
when the selected scope has write authority.

## Non-Negotiable Boundaries

- Use `AGENTS.md` for operating pointers only. Domain context, tracker detail,
  planning history, localization rules, and accepted decisions live in their
  dedicated memory surfaces.
- Load `references/domain-modeling.md` before creating, updating, reviewing, or
  reconciling `CONTEXT.md`, domain docs, or ADRs. Read the current
  memory-owning root's `CONTEXT.md` when it exists. During authorized
  setup/bootstrap, create or update root `CONTEXT.md` at every memory-owning
  root selected by that setup scope, even when evidence supports only a minimal
  entry point with explicit unknowns. Outside setup/bootstrap, use repository
  evidence until authorized durable content warrants creation. Treat the
  current Git repository as a selected root; in a coordination workspace also
  follow its repository registry to affected child roots and read each
  available child root context. Then select every matched available scoped
  `CONTEXT.md` from each selected repository root.
- Use one `project-memory/` directory per memory-owning root: one at a Git
  repository root, or one at a non-Git coordination-workspace root. Internal
  monorepo projects use scoped `CONTEXT.md` files and centralized root ADRs,
  not nested `project-memory/` directories.
- Seed durable memory only from strong repo evidence, committed behavior,
  accepted tracker decisions, final session evidence, or explicit user
  acceptance. Exclude tentative/rejected ideas, secrets, raw logs, and weak
  inferences. Mandatory root-context creation never authorizes invented domain
  facts; keep unsupported purpose, vocabulary, rules, or boundaries explicitly
  unresolved.
- Create `TRANSLATION.md` only when localization support or durable translation
  rules are evidenced or confirmed. Do not create empty ADR directories.
- Project Memory setup configures Idea routing and marker mappings but never
  creates Idea issues or files. Idea artifacts belong to an explicitly invoked
  Idea-capture workflow.
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
| `repository_layout` | `single-repository`, `monorepo`, `multi-repository-workspace` | `project-layout.md` |

Project Memory does not store implementation delivery targets, branch or PR
policy, or executor authorization. Those belong to the current Feature Spec or
the executing workflow. Unknown tracker keys and retired repository-layout
values are invalid input; configuration must already use this schema before the
runtime consumes it.

`references/triage-labels.md` is the sole reusable registry for canonical
`artifact_marker`, `issue_type`, and `workflow_state` values. The generated
`project-memory/config/triage-labels.md` is the repository-specific source of
truth for their tracker mappings. Consuming skills must load that mapping and
must not define parallel enums or aliases.
The `artifact_marker: idea` mapping is required only for Idea capture and
Idea-source consumption. If it is absent, stop those Idea-specific operations
with a setup prerequisite while leaving unrelated planning and implementation
workflows valid.
Do not add durable keys for Codex runtime workspace shape, source-root lists,
worktree paths, setup flow, GitHub repo, coordination repo, workers,
implementation delivery, publication/issue-mutation authority, scheduled
checks, or current-run mutation intent. Use prose, planning artifacts, or the
orchestrator ledger for those concerns.

`references/setup-workflow.md` owns the settings editor, canonical table
validation, draft checklist, pointer block, and completion report.
When touching `issue-tracker.md`, require `tracker_backend`, preserve useful
prose, and reject runtime-only or unknown table rows.

## Reference Loading Matrix

Load only the selected branch:

| Work | Required references |
| --- | --- |
| Tracker routing | `issue-tracker-github.md` or `issue-tracker-local.md`, `tracker-publishing.md`, `triage-labels.md`, and `setup-workflow.md` for edits. |
| Project layout | `project-layout.md` and `setup-workflow.md` for edits. |
| Domain setup/bootstrap | `domain.md`, `domain-modeling.md`, `context-seed.md`, and `setup-workflow.md`; add `session-history.md` only when the derived context is `existing-project-bootstrap`. |
| Domain inline update / implementation closeout / periodic review | `domain-modeling.md`; add `domain.md` only when target layout or ownership is ambiguous, and `documentation-shapes.md` only when no stronger local shape exists. |
| Translation | `translation.md` and `setup-workflow.md`. |
| Pointer/settings work | `setup-workflow.md`. |

Do not load domain, localization, or session-history evidence for tracker-only
work. This operation-specific loading rule is part of the token contract.
For any setup branch, load
[setup-questions.md](references/setup-questions.md) only when inspected
evidence and the defaults in `setup-workflow.md` leave a material ambiguity.
Normally ask no setup questions.

## Workflow

### 1. Resolve Options, Context, And Write Authority

Select the smallest `memory_slice`, resolve its operation, and derive
`execution_context` from current evidence. For
`domain_operation=implementation-closeout`, carry only the named decisions,
evidence, targets, and integrated feature proof. For
temporary/rehearsal/validation work, resolve `write_mode=propose` rather than
persisting run intent as configuration.

### 2. Inspect Focused Evidence

- tracker: current setup, remotes/config, templates, tracker docs, artifact
  marker labels, and relevant local/workspace conventions;
- project layout: Git root shape, package/workspace manifests, child repository
  evidence, and existing project-memory topology config;
- domain: current pointers, README/docs/manifests, relevant source/tests/schema,
  root and scoped context files, context routing, and ADRs;
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
to `tracker_backend`.

### 5. Write And Verify Authorized Memory

Update only authorized files. Keep `AGENTS.md` pointer-first. Use
`domain-modeling.md` for domain content and reconcile implementation-closeout
decisions against behavior that actually landed; omit provisional planning
language and verify the docs diff alongside feature proof.

For authorized domain setup/bootstrap, ensure root `CONTEXT.md` exists at every
memory-owning root selected by the setup scope before completion. Scoped
contexts remain optional and evidence-backed. A child-repository root selected
by the authorized setup scope follows the same mandatory root-context rule;
child repositories outside that scope remain optional and untouched.

In orchestrator-workspace setup, do not create Feature Spec, Idea, or issue
subtrees, and do not create runtime worker configuration or state. Project
Memory setup never creates Idea artifacts in any repository layout. Before
completing a touched `issue-tracker.md`, reject unknown configuration keys
rather than rewriting or removing them implicitly.

### 6. Report

Report `memory_slice`, `domain_operation`, `execution_context`, `write_mode`,
files changed, reviewed settings/surfaces, evidence, and consuming workflows.
For `memory_slice=domain-memory`, also report `capture_outcome`; other slices
omit that domain-only field. Keep destinations, accepted/rejected decisions,
and deferral explanations as separate data. For
`domain_operation=implementation-closeout`, also report the source
task/decision, durable decisions accepted or rejected, named targets updated,
feature proof, and documentation-diff verification. A nonempty accepted delta
is `captured` only when every item and required named target is reconciled and
verified; any unresolved target returns `capture_outcome=deferred`, while
`capture_outcome=no-durable-change` cannot complete that closeout. Mention
unavailable or weak session evidence plainly. A supplied accepted item that is
rejected or contradicted by landed behavior also returns `deferred` and requires
an owner decision or separately authorized planning/implementation correction;
it never counts as captured.

## Reference Responsibilities

- `options.md`: canonical option fields and values.
- `setup-workflow.md`: settings editor, normalization, pointers, and report.
- [setup-questions.md](references/setup-questions.md): conditional
  first-time-user ambiguity prompts and internal answer mapping.
- `project-layout.md`: durable `repository_layout` configuration and topology
  detection boundaries.
- `triage-labels.md`: sole reusable canonical artifact-marker,
  issue-type/workflow-state registry and repository mapping template.
- `issue-tracker-*.md`, `tracker-publishing.md`: tracker artifact, source-ref,
  publication, and completion contracts.
- `domain.md`: root/scoped context discovery, routing, and ownership.
- `domain-modeling.md`: domain setup, inline update, implementation closeout,
  and periodic review semantics.
- `documentation-shapes.md`: fallback context and ADR shapes.
- `context-seed.md`, `session-history.md`: initial and session-backed bootstrap.
- `translation.md`: optional localization memory.
