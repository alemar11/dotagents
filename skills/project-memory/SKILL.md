---
name: project-memory
description: Create and maintain durable project memory for tracker, delivery, context, decisions, and localization.
---

# Project Memory

## Goal

Provide the public entry point for creating and maintaining the repo memory
that other skills consume:

- `AGENTS.md` for lean operating pointers.
- `project-memory/agents/issue-tracker.md` for PRD and issue routing.
- `project-memory/agents/triage-labels.md` for issue type and state mappings.
- `project-memory/agents/domain.md` for context, translation, and ADR layout.
- `CONTEXT.md` and optional `project-memory/adr/` for domain memory.
- `TRANSLATION.md` when localization support or translation rules are real.

Use this skill both for initial setup and for later reconciliation after
implementation, accepted decisions, tracker changes, or localization changes.
Configure or update only the memory surfaces needed for the requested workflow.
An explicitly requested full first-time setup may create all applicable
surfaces, but tracker routing does not require domain or localization work, and
domain work does not require tracker setup. Re-run only the affected slice when
routing, mappings, domain knowledge, localization policy, or `AGENTS.md`
pointers change.

`$project-memory` is the normal public invocation for durable memory changes.
For the `domain-memory` slice, it must load and follow `$domain-modeling` as the
semantic engine for `CONTEXT.md`, relevant domain docs, and ADR updates. Callers
that already compose `$domain-modeling`, such as `$grill-me-with-context`, may
continue to use that specialist directly.

## Boundaries

- Always use `AGENTS.md` for setup pointers when an agent-instruction file is
  needed.
- Keep `AGENTS.md` pointer-first: it is an operating index, not the durable
  home for project knowledge. Operating rules stay there; domain context,
  tracker detail, planning history, localization rules, and accepted decisions
  move to project memory.
- Load and follow `$domain-modeling` before creating or updating `CONTEXT.md`
  or ADRs. Reading `project-memory/agents/domain.md` alone does not satisfy this
  requirement.
- Seed `CONTEXT.md`, `TRANSLATION.md`, or ADRs only from strong repo evidence,
  final session summaries, committed behavior, or explicit user acceptance.
- Create `TRANSLATION.md` only when localization support or durable translation
  rules are clear from evidence or confirmed by the user.
- Do not record tentative proposals, rejected ideas, secrets, raw logs, broad
  doctrine, or weak session inferences.
- Do not create empty `project-memory/adr/` directories just to show intent.
- In orchestrator workspace mode, configure only root setup files. Do not create
  `projects/<project>/`, feature PRDs, or issue files during setup.
- Treat an explicit user request to set up, configure, initialize, update, or
  refresh project memory as write authority for the requested slice. A
  ready-for-execution implementation task that explicitly requires
  `$project-memory domain-memory` and names its durable decisions, evidence, and
  target surfaces is also write authority for that closeout. Show the intended
  files and meaningful values, but do not ask for redundant confirmation.
- A view, inspect, review-only, recommendation, dry-run, or indirect suggestion
  is not write authority. In those cases, show the proposal and wait for
  confirmation before writing.
- Ask only when the target or a behavior-affecting value is materially
  ambiguous and repo evidence plus documented defaults do not resolve it.
  Never require choices for unrelated setup slices.

## Structured Values

Use human-first Markdown with typed configuration tables for behavior-affecting
settings. `$project-memory` is the normal editor for these tables: read current
values, resolve requested changes from repo evidence and documented defaults,
ask only about materially ambiguous values, preserve custom prose, normalize
known keys, and report unknown keys instead of silently deleting them.

Use `lower_snake_case` keys and `lower-kebab-case` values for setup-owned
structured fields. Treat older uppercase kebab-case values as legacy aliases
when reading existing artifacts; rewrite touched values to lower-kebab-case.

| Key | Type | Allowed values | Meaning | Owner |
| --- | --- | --- | --- | --- |
| `tracker_backend` | enum | `github`, `local` | Where durable PRDs and implementation issues are written. | `issue-tracker.md` |
| `delivery_mode` | enum | `pull-request`, `direct-commit` | How implementation work is published after validation. | `issue-tracker.md`, PRDs, and generated issues |

Do not add durable setup keys for workspace shape, setup flow, GitHub repo,
coordination repo, worker surfaces, worker counts, publication authority, issue
mutation authority, scheduled checks, or dry-run/no-mutation intent. Record
real repo targets, path conventions, and cross-repo links in prose, PRDs,
generated issues, or the orchestrator ledger as appropriate.

Legacy cleanup:

- Map old tracker and delivery fields through `references/tracker-publishing.md`
  before acting.
- Remove current-run or runtime-only fields from any `issue-tracker.md` file you
  touch; `references/setup-workflow.md` owns the exact write-normalization rule.

When touching `project-memory/agents/issue-tracker.md`, normalize the setup
header:

- use `lower_snake_case` keys;
- wrap structured values in backticks;
- keep behavior-affecting fields in a typed configuration table before prose;
- require `tracker_backend` and `delivery_mode`;
- remove legacy durable rows such as `tracker_mode`, `tracker_writes`,
  `setup_mode`, `github_repo`, `coordination_repo`, `project_label_format`, and
  path-pattern keys from the configuration table; preserve real custom targets
  or path conventions in prose when they are still needed;
- preserve unrelated custom prose, labels, delivery rules, and dry-run notes.

Detailed meanings and generated-file shapes live in the references listed
below.

## Workflow

### 1. Choose Operation And Slice

- Select the smallest slice needed:
  - `tracker-routing`: issue tracker, delivery mode, issue-type mapping, and
    triage-state mapping;
  - `domain-memory`: domain layout, context seed or reconciliation, relevant
    domain-doc updates, and accepted ADR routing or capture;
  - `translation-memory`: localization memory only;
  - `agents-pointers`: missing or stale project-memory pointers only;
  - `full-setup`: all applicable slices, only when explicitly requested.
- Use `fresh-setup` when files for the selected slice are missing. For a
  `domain-memory` or explicit `full-setup` slice in a non-empty repo, also check
  whether evidence supports an initial `CONTEXT.md` seed.
- Use `existing-project-bootstrap` when the selected slice reconciles existing
  docs, partial project memory, accepted knowledge, recent same-repo session
  history, or ADR candidates.
- Use `implementation-closeout` for a `domain-memory` slice carried by a final
  implementation or integration task. Reconcile only the named decisions and
  target surfaces against behavior that actually landed, using current source,
  tests, validation, and accepted tracker decisions as evidence. Do not rerun
  unrelated setup or mine session history by default.
- Use `orchestrator-workspace` only for a parent coordination workspace that
  plans across independent repos. Do not treat it as a monorepo, and do not
  require a global PRD when linked partial PRDs describe the workspace feature.
- For temp, rehearsal, validation, or dry-run work, use a current-run
  no-mutation override unless the user explicitly authorizes tracker writes. Do
  not persist no-mutation intent as a durable issue-tracker config row.

### 2. Inspect Evidence

Read only the evidence needed for the selected slice:

- `tracker-routing`: existing tracker setup, `git remote -v`, `.git/config`,
  issue templates, tracker docs, `.scratch/`, and workspace `projects/` signals;
- `domain-memory`: `AGENTS.md`, README/docs/manifests, relevant source/tests or
  schemas, existing context files, domain setup, and ADRs;
- `translation-memory`: existing translation memory plus locale catalogs,
  i18n/l10n config, product copy guidance, and target-market requirements;
- `agents-pointers`: `AGENTS.md` and the project-memory files it should index.

Do not scan domain, localization, or session-history evidence for a
tracker-only edit.

When `AGENTS.md` already contains setup or project context, classify content
before writing:

- keep agent operating rules in `AGENTS.md`;
- move project purpose, vocabulary, boundaries, and open questions to
  `CONTEXT.md`;
- move localization policy to `TRANSLATION.md`;
- move tracker, triage, delivery, and domain layout to
  `project-memory/agents/*`;
- move accepted load-bearing decisions to ADRs;
- preserve or ask about stale, conflicting, or weakly evidenced content.

For an `existing-project-bootstrap` domain-memory slice, read
`references/session-history.md` and use recent session evidence only when it is
strong enough to be durable. Do not load session history for tracker-only,
translation-only, or pointer-only setup.

### 3. Review Or Confirm Settings

If relevant memory files already exist, or the user asks to
show/review/change settings, summarize the selected slice before proposing
edits. Include only known values; use `Unknown` when absent or ambiguous.
Summarize all slices only for an explicit full review. For
`implementation-closeout`, summarize the carried decisions, evidence, and named
targets instead of unrelated setup settings.

Resolve only decisions in the selected setup slice:

- issue tracker backend;
- delivery mode;
- issue type and triage state mappings;
- domain-memory layout and context seed mode;
- localization memory state;
- `AGENTS.md` pointer creation or minimization.

Use `references/setup-workflow.md` for the settings editor protocol, option
sets, write-authority rules, draft checklist, `AGENTS.md` block, and completion
report.

### 4. Draft Project Memory

Before writing, show the intended files and the relevant before/after summary.
Load only references needed by the selected slice:

- tracker routing: `issue-tracker-github.md` or `issue-tracker-local.md`, plus
  `tracker-publishing.md` and `triage-labels.md`;
- domain memory: `domain.md`, `context-seed.md`, and `session-history.md` only
  for an existing-project bootstrap;
- translation memory: `translation.md`;
- settings and pointers: `setup-workflow.md`.

For custom tracker workflows, write `issue-tracker.md` from the user's described
workflow instead of forcing a hosted-tracker template, but keep the durable
configuration table focused on `tracker_backend` and `delivery_mode` when the
workflow still reduces to local or GitHub artifacts.

### 5. Write Authorized Project Memory

After an explicit setup, configure, initialize, update, or refresh request, a
separate affirmative confirmation, or an authorized `implementation-closeout`
task:

- Create or update only the authorized project-memory files.
- Preserve unrelated custom prose, mappings, comments, overrides, docs, ADRs,
  and `TRANSLATION.md` content.
- Keep `AGENTS.md` concise and pointer-only for project memory.
- Use `$domain-modeling` for `CONTEXT.md` and ADR shape.
- For `implementation-closeout`, require `$domain-modeling` to reconcile the
  carried decisions with implemented behavior before writing. Omit provisional
  planning language that the implementation did not prove, update only the
  named durable surfaces, and verify their diff alongside the feature-level
  integration proof.
- Use `references/translation.md` for `TRANSLATION.md`.
- Optionally add a one-line `CONTEXT.md` pointer to neighboring
  `TRANSLATION.md` only when localization affects audience, domain terms,
  product naming, or user-facing copy. Do not require the pointer or create
  broken links.
- In orchestrator workspace mode, do not create project or feature folders.
- Do not create extra orchestration setup files; session worker questions belong
  in `$codex-orchestrator`, and runtime worker state belongs in the orchestrator
  checkpoint and ledger.
- Before reporting completion, grep any touched `issue-tracker.md` for legacy
  keys: `tracker_mode`, `tracker_writes`, `effective_target`,
  `local_artifact_writes`, and `external_tracker_mutation`. Remove them or
  report why they must remain.

### 6. Report Completion

Report the operation, slice, files written, and only the settings or memory
surfaces reviewed or changed. Include tracker, domain, localization,
`AGENTS.md`, context/translation/ADR, and session-history details only when they
were part of this run, plus the workflows that can now consume the setup.

For `implementation-closeout`, also report the implementation task or source
decision, evidence checked, durable decisions captured or rejected, target
surfaces updated, and documentation-diff verification.

If session history is unavailable or weak, say so plainly. Future
`$domain-modeling`, `$grill-me-with-context`, and planning workflows can keep
filling project memory incrementally.

## Reference Responsibilities

- `issue-tracker-*.md`: tracker-specific artifact locations, publication rules,
  delivery defaults, runtime boundaries, title formats, and completion.
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
