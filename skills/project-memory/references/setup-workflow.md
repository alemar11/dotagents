# Setup Workflow Details

Use this reference for the interactive setup editor, draft checklist, write
rules, `AGENTS.md` pointer block, and completion report. Keep the public
`SKILL.md` focused on routing and hard boundaries.

When a composed caller selects multiple Git repositories, run setup
independently in each selected repository. Never create shared coordination
memory at their common parent.

## Current Settings Summary

When reviewing existing setup, summarize values in the selected setup slice
before recommending changes. Include the full list only for an explicit full
review:

- execution context: `fresh-setup`, `existing-project-bootstrap`, or
  `current-project` (derived in the exact
  precedence from `options.md`, not a stored key or option)
- resolved GitHub target as exact `owner/repository` factual routing data
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

- `github-target`
- `artifact-marker-mapping`
- `issue-type-mapping`
- `workflow-state-mapping`
- `domain-memory`
- `translation-memory`
- `agents-pointers`
- `done`

For each selected configuration section, show the current value first, then
`keep-current` and the relevant alternatives:

- `github-target`: the exact resolved `owner/repository`; replacement requires
  an explicit repository target or one unambiguous GitHub remote and is factual
  routing data, never a provider choice.
- `artifact-marker-mapping`: default or custom GitHub `label` for the `idea`
  marker.
- `issue-type-mapping`: default GitHub `native-type`, evidence-backed GitHub
  fallback `label` or exact `body-field`,
  with one transport and exact tracker value per canonical type.
- `workflow-state-mapping`: default or custom GitHub `label`, with one
  transport and exact tracker value per state.
- `domain-memory`: show the current root `CONTEXT.md`, scoped routes, and
  centralized ADR root. Refresh those
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

- Require one resolved GitHub repository target. When it cannot be resolved,
  report the prerequisite.
- For dry runs or no-mutation runs, do not let a GitHub remote force GitHub
  mutation. Resolve `write_mode=propose` and treat it as current-run behavior,
  not durable issue-tracker configuration.
- Do not define durable worker assignments, worker-count limits, scheduled
  checks, publication policy, or issue mutation policy in project memory.
- Default the canonical `idea` artifact marker to the GitHub `idea` label. Ask
  only when tracker evidence shows that the label is conflicting or customized.
- Read root `CONTEXT.md` first when it exists. During authorized domain
  setup/bootstrap, always create or update it at every memory-owning root
  selected by the setup scope. Populate only evidence-backed purpose,
  vocabulary, rules, boundaries, and routing. When richer evidence is absent,
  keep a minimal entry point and state the missing knowledge explicitly rather
  than inventing it.
- For a verified monorepo, use repository evidence for root scope routing.
  Create scoped contexts only when durable evidence and authority support their
  content. Every additional Git repository explicitly selected by a composed
  setup follows the mandatory root-context rule; repositories outside that
  scope remain untouched.
- Recommend enabled translation memory only when localization support and
  durable translation rules are confirmed by evidence or the user.

## Draft Checklist

Before writing, show only applicable items from this list:

- current settings summary for review mode;
- before/after summary for proposed changes;
- intended `AGENTS.md` pointer block;
- `AGENTS.md` minimization plan;
- intended `project-memory/config/issue-tracker.md`;
- intended `project-memory/config/triage-labels.md`;
- intended root `CONTEXT.md` creation or update, including evidence-backed
  content, stable routing, and any explicit unknowns;
- intended scoped `CONTEXT.md` files, or why root-only routing is sufficient;
- intended `TRANSLATION.md`, or why localization memory should not be written;
- intended ADR drafts, if any.

## Write Rules

After direct write authority or separate affirmative confirmation:

- Create `project-memory/config/` if needed.
- Write or update the authorized setup files under `project-memory/config/`.
- In review mode, update only files needed for separately confirmed changes.
- Keep triage mapping data in the typed mapping tables defined below. The
  resolved GitHub target in `issue-tracker.md` is factual routing prose, not a
  selectable behavior field, and is explicitly exempt from configuration-table
  serialization.
- When full setup or mapping work creates or refreshes
  `project-memory/config/triage-labels.md`, include the canonical
  `artifact_marker: idea` mapping alongside the issue-type and workflow-state
  mappings. Require each mapping table to contain its canonical identity,
  `Transport`, `Tracker value`, and `Meaning` columns. Reject a missing,
  unknown, or GitHub-incompatible transport instead of inferring it or reading
  retired column shapes. If an existing repository lacks only that marker mapping, report
  Idea capture and Idea-source consumption as unavailable until setup adds it;
  do not invalidate or block unrelated workflows.
- Keep `issue-tracker.md` limited to the resolved GitHub target and
  human-readable tracker conventions. Implementation delivery policy belongs
  to executors.
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
  mapping does not authorize writing GitHub Idea issues.
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
questions, checkpoint, dispatch, and ledger progress record.

## Completion Report

Summarize only the applicable fields:

- execution context;
- files written;
- settings reviewed and changed;
- selected issue tracker;
- artifact-marker transport and mapping;
- issue-type and workflow-state transport and mapping;
- root/scoped context routing;
- localization-memory decision and evidence;
- `AGENTS.md` minimization outcome;
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
  conflicting issue locations, separate project contexts, overlapping project
  ownership, repository-rule ownership,
localization conventions, artifact-marker mappings, issue-type mappings, and
workflow-state mappings.

Keep Project Memory internals out of user-facing prompts. Ask about concrete
projects, repositories, paths, trackers, rules, and localization behavior, then
translate the answer to canonical configuration internally. Never ask the user
whether evidence is sufficient, combine two unresolved decisions in one
question, or ask a question already resolved by an explicit request, durable
repository evidence, or a documented default.
