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
- root/scoped context routing
- translation memory decision
- `AGENTS.md` setup block state
- Code Review Rules section state when that slice is selected

Use `Unknown` only when a value is absent or ambiguous. If the user only asked
to view current settings, stop after the summary.

Reject runtime-only worker configuration in project-memory setup files; those
fields belong to Implement Feature.

## Settings Editor

When the requested section is unclear, use the setup-target question in
[setup-questions.md](setup-questions.md). Otherwise edit only the named or
required section and preserve unrelated custom prose, path
conventions and dry-run overrides
unless the user explicitly changes them.

Editable sections:

- `domain-memory`
- `translation-memory`
- `agents-pointers`
- `code-review-rules`
- `done`

For each selected setup section, show the current value first, then
`keep-current` and the relevant alternatives:

- `domain-memory`: show the current root `CONTEXT.md`, scoped routes, and
  centralized ADR root. Refresh those
  surfaces from evidence; during authorized setup/bootstrap, always create or
  update root `CONTEXT.md` at every memory-owning root selected by the setup
  scope. Do not present or persist a domain-layout enum.
- `translation-memory`: `enabled`, `not-applicable`, `needs-confirmation`.
- `agents-pointers`: create missing pointer block, refresh stale pointer block,
  or minimize copied setup detail into project-memory pointers.
- `code-review-rules`: inspect, propose, or update the exact Code Review Rules
  section in the closest applicable `AGENTS.md`.

After edits, show intended changed files and before/after settings. An explicit
request to set up, configure, initialize, update, or refresh project memory is
write authority for that scope, so proceed without a second confirmation. For
review-only, recommendation, dry-run, or indirectly suggested setup, return the
report without writing.

Ask only about a materially ambiguous target or behavior-affecting value that
repo evidence and the defaults below cannot resolve. Do not force the user
through unrelated editable sections. If ambiguity remains, load
[setup-questions.md](setup-questions.md) and use its applicable first-time-user
prompt.

## Decision Defaults

- Do not define durable worker assignments, worker-count limits, or scheduled
  checks in project memory.
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
- intended exact `## Code Review Rules` block, target instruction chain, and
  candidate evaluation when that slice is selected;
- `AGENTS.md` minimization plan;
- intended root `CONTEXT.md` creation or update, including evidence-backed
  content, stable routing, and any explicit unknowns;
- intended scoped `CONTEXT.md` files, or why root-only routing is sufficient;
- intended `TRANSLATION.md`, or why localization memory should not be written;
- intended ADR drafts, if any.

## Write Rules

For an explicit setup or update request:

- Update only files needed for the selected memory surfaces.
- Create or update `AGENTS.md` pointer block and apply only authorized
  minimization.
- When `code-review-rules` is selected, update the closest applicable
  `AGENTS.md` with the exact `## Code Review Rules` section. Keep the persisted
  block limited to accepted invariant, consequence, and safe path; preserve
  unrelated instructions and keep evidence, evaluation matrices, and
  provenance in the run report or Project Memory references.
- Create or update root and scoped `CONTEXT.md` through
  `references/domain-modeling.md`. During authorized setup/bootstrap, ensure
  root `CONTEXT.md` exists at every memory-owning root selected by the setup
  scope before writing any scoped context or completing setup.
- Create or update `TRANSLATION.md` only when localization memory is confirmed.
- Create ADRs only for accepted, load-bearing decisions.
- Preserve unrelated or uncertain content in `AGENTS.md`, `CONTEXT.md`,
  `TRANSLATION.md`, ADRs, and project docs.
- Do not duplicate moved project context in both `AGENTS.md` and project
  memory.

## AGENTS.md Pointer Block

Use this shape as a menu. Include only sections whose target surface exists,
is derived at runtime, or is authorized in the selected slice. Omit
`Localization` unless `TRANSLATION.md` exists or is authorized; never create a
broken pointer:

```markdown
## Agent skills

### Domain memory

[one-line summary of shared context and any scoped routing]. Read `CONTEXT.md` first, then follow its `Scoped Contexts` table when relevant.

### Localization

[one-line summary of supported localization memory]. See `<path-to-TRANSLATION.md>`.
```

Keep this block concise. Do not paste domain vocabulary, workflow procedures,
implementation policy, localization rules, worker-dispatch rules, or context
seed material into `AGENTS.md`. `$implement-feature` owns its session worker
questions, checkpoint, dispatch, and ledger progress record.

The `## Code Review Rules` section is a separate exact review contract, not a
project-memory pointer. Manage it only when the `code-review-rules` slice is
selected; do not fold its evaluation detail into this pointer block.

## Completion Report

Summarize only the applicable fields:

- execution context;
- files written;
- settings reviewed and changed;
- root/scoped context routing;
- localization-memory decision and evidence;
- `AGENTS.md` minimization outcome;
- Code Review Rules target, rule count, evaluation state, history coverage, and
  result when selected;
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
  separate project contexts, overlapping project ownership, repository-rule
  ownership, and localization conventions.

Keep Project Memory internals out of user-facing prompts. Ask about concrete
projects, repositories, paths, rules, and localization behavior, then
translate the answer to canonical configuration internally. Never ask the user
whether evidence is sufficient, combine two unresolved decisions in one
question, or ask a question already resolved by an explicit request, durable
repository evidence, or a documented default.
