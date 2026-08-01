---
name: project-memory
description: Maintain tracker routing, domain language, ADRs, context, localization memory, and evidence-backed Codex Code Review Rules in the closest applicable AGENTS.md.
---

# Project Memory

## Purpose

Use `$project-memory` as the single public entry point for durable repository
memory:

- lean project-memory pointers in `AGENTS.md`;
- the exact `## Code Review Rules` section in the closest applicable
  `AGENTS.md`;
- tracker routing in `project-memory/config/issue-tracker.md`;
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
| `tracker-routing` | GitHub target plus human-readable tracker conventions. |
| `domain-memory` | Root/scoped context routing plus domain-doc/ADR setup, inline update, implementation closeout, or periodic review. |
| `translation-memory` | Localization memory only. |
| `agents-pointers` | Missing or stale project-memory pointers only. |
| `code-review-rules` | Evidence-backed Codex Code Review Rules in the closest applicable `AGENTS.md`. |
| `full-setup` | All applicable slices, only when explicitly requested. |

For `memory_slice=domain-memory`, resolve `domain_operation` from
`references/domain-modeling.md`: `setup-bootstrap`, `inline-update`,
`implementation-closeout`, or `periodic-review`.

Derive `execution_context` from repository evidence after selecting the slice;
it is not a user or caller option. Apply the exact ordered precedence in
`references/options.md`, which yields one of `fresh-setup`,
`existing-project-bootstrap`, or `current-project`. Do not redefine or reorder
those predicates in another reference.

Resolve `write_mode=propose` for a non-mutating run. Use `write_mode=apply` only
when the selected scope has write authority.

## Non-Negotiable Boundaries

- Use `AGENTS.md` for operating pointers and the exact `## Code Review Rules`
  section. Domain context, tracker detail, planning history, localization
  rules, and accepted decisions live in their dedicated memory surfaces.
- Keep Code Review Rules concise and behavior-focused. Store the invariant,
  consequence, and safe path in `AGENTS.md`; keep evidence, evaluation
  matrices, history coverage, and official-doc routing in the Project Memory
  references and run report.
- Load `references/domain-modeling.md` before creating, updating, reviewing, or
  reconciling `CONTEXT.md`, domain docs, or ADRs. Read the current
  memory-owning root's `CONTEXT.md` when it exists. During authorized
  setup/bootstrap, create or update root `CONTEXT.md` at every memory-owning
  root selected by that setup scope, even when evidence supports only a minimal
  entry point with explicit unknowns. Outside setup/bootstrap, use repository
  evidence until authorized durable content warrants creation. Treat the
  current Git repository as the selected root, then select every matched
  available scoped `CONTEXT.md`. For cross-repository work, explicit user scope
  or a durable linked Feature Spec Set authorizes repository identities; the
  composed caller must supply candidate local Git roots separately, verify each
  root against exactly one authorized identity, reject extra or unmatched
  roots, and run Project Memory once per verified repository. Never fabricate
  paths from Spec refs or discover scope from the ChatGPT App saved-project
  list.
- Use one `project-memory/` directory at each Git repository root. Internal
  monorepo projects use scoped `CONTEXT.md` files and centralized root ADRs,
  not nested `project-memory/` directories. Non-Git roots never own Project
  Memory.
- Seed durable memory only from strong repo evidence, committed behavior,
  accepted tracker decisions, final session evidence, or explicit user
  acceptance. Exclude tentative/rejected ideas, secrets, raw logs, and weak
  inferences. Mandatory root-context creation never authorizes invented domain
  facts; keep unsupported purpose, vocabulary, rules, or boundaries explicitly
  unresolved.
- Create `TRANSLATION.md` only when localization support or durable translation
  rules are evidenced or confirmed. Do not create empty ADR directories.
- Project Memory setup configures tracker routing and conventions but never
  creates Ideas, issues, or labels. It may create or update the authorized
  project-memory files and pointers; feature artifacts and their metadata
  belong to explicitly invoked feature workflows.
- Explicit setup/configure/initialize/update/refresh instructions authorize
  only the requested `memory_slice`. A ready implementation-closeout task authorizes
  only its named decisions, evidence, and target surfaces.
- Select `memory_slice=code-review-rules` only from an explicit Code Review
  Rules request. Do not infer it from ordinary code review, `AGENTS.md`
  maintenance, retrospective analysis, or an otherwise broad setup request.
- An explicitly invoked composed workflow may authorize
  `domain_operation=inline-update` only
  when its caller has durable domain-memory write authority. Tracker mutation
  authority alone is insufficient.
- Inspect-only, review-only, proposal, dry-run, or indirect suggestions are not
  write authority. Return the proposed change instead.
- Preserve unrelated custom prose, comments, overrides, domain docs, ADRs, and
  localization content.
- Ask only when the target or behavior-affecting value is materially ambiguous
  after repo evidence and documented defaults.

## Tracker Contract

GitHub Issues is the fixed tracker provider. `issue-tracker.md` records the
resolved GitHub target and human-readable conventions, not a provider option.
Project Memory does not store feature metadata, label mappings, implementation
delivery targets, branch or PR policy, or executor authorization. Those belong
to the consuming feature workflow and its explicit companion contract.

Feature workflows must own the artifact markers, issue types, workflow states,
exact GitHub values, and the read/write behavior that uses them. They must load
their own contract, reject unknown or unsupported values, and delegate GitHub
transport and mutation safety to `$gitstack:github-issues`. Project Memory does
not provide a fallback registry or compatibility mapping for those concerns.
Do not add durable keys for Codex runtime project topology, repository sets,
source-root lists, worktree paths, setup flow, GitHub repo, workers,
implementation delivery, publication/issue-mutation authority, scheduled
checks, or current-run mutation intent. Use prose, planning artifacts, or the
controller ledger for those concerns.

`references/setup-workflow.md` owns the settings editor, canonical table
validation, draft checklist, pointer block, and completion report.
When touching `issue-tracker.md`, preserve useful prose and remove runtime-only
configuration rows within the authorized scope.

## Reference Loading Matrix

Load only the selected branch:

| Work | Required references |
| --- | --- |
| Tracker routing | `issue-tracker-github.md`, `tracker-publishing.md`, and `setup-workflow.md` for edits. |
| Domain setup/bootstrap | `domain.md`, `domain-modeling.md`, `context-seed.md`, and `setup-workflow.md`; add `session-history.md` only when the derived context is `existing-project-bootstrap`. |
| Domain inline update / implementation closeout / periodic review | `domain-modeling.md`; add `domain.md` only when target layout or ownership is ambiguous, and `documentation-shapes.md` only when no stronger local shape exists. |
| Translation | `translation.md` and `setup-workflow.md`. |
| Pointer/settings work | `setup-workflow.md`. |
| Code review rules | `code-review-rules.md`; add its evidence-mining, rule-evaluation, and official-docs references only when their routing conditions apply. |

Do not load domain, localization, or session-history evidence for tracker-only
or code-review-only work unless the selected reference explicitly routes to
historical evidence. This operation-specific loading rule is part of the token
contract.
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

- tracker: current setup, remotes/config, tracker docs, and relevant local
  conventions;
- domain: current pointers, README/docs/manifests, relevant source/tests/schema,
  root and scoped context files, context routing, and ADRs;
- translation: translation memory, locale catalogs/config, copy guidance, and
  market requirements;
- pointers: `AGENTS.md` and the files it should index;
- code review rules: the root-to-target `AGENTS.md` chain, existing Code Review
  Rules, affected code/tests/contracts, and bounded accepted history when
  routed by `references/code-review-rules.md`.

For existing-project domain bootstrap, use `session-history.md` only when
recent same-repo evidence is strong enough to be durable.

When `AGENTS.md` mixes concerns, keep operating rules there and route project
purpose/vocabulary to `CONTEXT.md`, localization to `TRANSLATION.md`, tracker
settings to `project-memory/config/*`, and accepted load-bearing decisions to
ADRs.

### 3. Resolve Settings Or Delta

For setup/review, summarize only the selected `memory_slice` and use `Unknown`
for ambiguous values. Resolve only its behavior-affecting settings. For
`domain_operation=implementation-closeout` or
`domain_operation=inline-update`, summarize the carried decisions, evidence,
named targets, and write authority instead of unrelated setup.
For `memory_slice=code-review-rules`, summarize the target instruction chain,
existing rule section, candidate set, evaluation state, and write authority.

### 4. Draft And Show The Change

Before writing, show intended files and meaningful before/after values. Follow
the loading matrix and existing local formats. Preserve repository-specific
GitHub conventions without adding provider configuration.

### 5. Write And Verify Authorized Memory

Update only authorized files. Keep `AGENTS.md` pointer-first. Use
`domain-modeling.md` for domain content and reconcile implementation-closeout
decisions against behavior that actually landed; omit provisional planning
language and verify the docs diff alongside feature proof.

For `memory_slice=code-review-rules`, update only the closest applicable
`AGENTS.md`. Preserve unrelated instructions and pointers, use the exact
`## Code Review Rules` heading, and persist only the accepted invariant,
consequence, and safe path. Do not persist evaluation matrices, confidence,
history provenance, issue IDs, session IDs, or generic starter rules.

For authorized domain setup/bootstrap, ensure root `CONTEXT.md` exists at every
memory-owning root selected by the setup scope before completion. Scoped
contexts remain optional and evidence-backed. Every additional Git repository
explicitly selected by an authorized composed setup follows the same mandatory
root-context rule; repositories outside that scope remain untouched.

Project Memory setup does not create Feature Spec, Idea, or issue subtrees and
does not create runtime worker configuration or state. It never creates Idea
artifacts.

### 6. Report

Report `memory_slice`, `domain_operation`, `execution_context`, `write_mode`,
files changed, reviewed settings/surfaces, evidence, and consuming workflows.
For `memory_slice=domain-memory`, also report `capture_outcome`; other slices
omit that domain-only field. For `memory_slice=code-review-rules`, also report
the target `AGENTS.md`, rule count, candidate evaluation state, history
coverage, and result state. Keep destinations, accepted/rejected decisions,
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
- `issue-tracker-github.md`, `tracker-publishing.md`: tracker artifact, source-ref,
  publication, and completion contracts.
- `domain.md`: root/scoped context discovery, routing, and ownership.
- `domain-modeling.md`: domain setup, inline update, implementation closeout,
  and periodic review semantics.
- `code-review-rules.md`: Code Review Rules discovery, evaluation, rendering,
  and `AGENTS.md` update semantics.
- `documentation-shapes.md`: fallback context and ADR shapes.
- `context-seed.md`, `session-history.md`: initial and session-backed bootstrap.
- `translation.md`: optional localization memory.
