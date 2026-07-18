# Domain Memory Modeling

Use this internal reference whenever `memory_slice=domain-memory` creates,
updates, reviews, or reconciles `CONTEXT.md`, relevant domain docs, or ADRs.
`$project-memory domain-memory` is the public invocation; this reference owns
the internal semantic workflow.

## Goal

Keep a project's shared language and durable decisions current. Turn accepted
terminology, boundaries, rules, and decisions into lightweight documentation
that future agents and maintainers can reuse. Do not invent a domain model
before there is evidence from the user, repository, or existing docs.

## Operation Boundary

Honor the `domain_operation` and `write_mode` options resolved by
`$project-memory`. Use its evidence-derived `execution_context`; never accept
that classification as a caller-selected option:

- `execution_context=fresh-setup`: create the smallest evidence-backed initial context surface.
- `execution_context=existing-project-bootstrap`: reconcile accepted knowledge from current repo
  evidence and, when explicitly loaded, strong recent same-repo history.
- `domain_operation=inline-update`: capture durable decisions accepted during a direct composed
  workflow such as `$grill-me-with-context`.
- `domain_operation=implementation-closeout`: reconcile a carried knowledge delta against the
  behavior and validation that actually landed.
- `domain_operation=periodic-review`: report or propose changes by default; write only when the
  evidence and acceptance satisfy Project Memory's authority boundary.

Stay within the selected context, authorized target surfaces, and evidence
boundary. Do not expand into tracker, localization, pointer, or unrelated
domain surfaces.

When a caller supplies a `knowledge_delta`, treat it as input data: accepted
terms, rules, boundaries, or decisions plus evidence and intended targets.
Reconcile it against the current repository before capture. Do not reduce it to
an enum or treat its presence as write authority.

## Workflow

### 1. Inspect existing context

- Resolve the current memory-owning root and read its `CONTEXT.md` first when
  it exists. If it is intentionally absent, use repository evidence and create
  it only with authorized durable content or verified topology-routing
  evidence. In a multi-repository coordination workspace, follow its
  `Repository Registry`
  to every affected child repository and read each available child root
  `CONTEXT.md`. An empty registry context cell means no child context exists;
  inspect that child's repository evidence without inventing or creating a
  context unless separately authorized. Also inspect the relevant
  `project-memory/adr/` trees, `README.md`, project docs, product specs, issue
  templates, and nearby source or tests that define the vocabulary already in
  use.
- When a selected repository's root `CONTEXT.md` contains
  `## Scoped Contexts`, select every non-overlapping row matched by the
  affected paths or accepted product identities, then read each available
  scoped `CONTEXT.md`. The coordination root and selected repository root
  remain applicable after selection. For a matched row without a context file,
  inspect its owned paths directly and create the scoped file only when
  authorized evidence supports durable scope-specific content.
- Stop and ask only when scoped routes overlap or ownership remains
  indeterminate. Do not guess, and do not mistake legitimate cross-scope work
  for routing ambiguity.
- Prefer updating an existing relevant file over creating a new one.
- If no root context exists and an authorized durable term or rule needs a
  home, create `CONTEXT.md` at the memory-owning root. For a verified monorepo
  or multi-repository workspace, create the minimal root routing surface before
  creating any scoped context.
- If no suitable authorized destination exists, defer capture and name the
  missing file or surface explicitly.

### 2. Sharpen the model

Track only durable items:

- **Terms**: project-specific words, aliases, and nearby concepts that differ.
- **Boundaries**: where a concept, workflow, actor, or module stops and another
  starts.
- **Rules**: invariants, permissions, lifecycle transitions, validations, and
  failure states.
- **Decisions**: accepted choices future work should not relitigate.
- **Open questions**: unresolved points that must remain visibly uncertain.

Challenge fuzzy terms with concrete edge cases before recording them. When two
names appear synonymous, resolve whether they are aliases or distinct concepts.

### 3. Update the smallest durable surface

- Add or revise shared glossary entries and rules in root `CONTEXT.md`; put
  only scope-specific deltas in the selected scoped `CONTEXT.md`.
- Add workflow or behavioral detail to the closest relevant project doc.
- Add an ADR beneath the memory-owning root's `project-memory/adr/` only for an
  accepted, load-bearing decision future agents would otherwise reopen. Use a
  scope subdirectory when useful; never create nested scoped
  `project-memory/` directories.
- Leave unresolved questions explicit rather than smoothing them over.
- Use project vocabulary and link durable repo sources such as source files,
  tests, schemas, project docs, or ADRs when available.
- Treat issues, PRs, tracker discussions, and session history as discovery
  evidence or optional provenance, not as the sole authority for durable
  context. Restate accepted meaning in a repo-owned source and cite that source.

Use `references/documentation-shapes.md` only when the project does not already
have a stronger local format.

### 4. Handle periodic review

When invoked by an automation or batch workflow:

- Treat conversations, session logs, issue activity, and commit history as
  candidate evidence, not authority by themselves.
- Re-read current context and relevant repo evidence before accepting a
  candidate.
- Default to a review report or proposed patch when acceptance is unclear.
- Do not create an ADR from batch review alone unless the decision is clearly
  accepted and load-bearing.
- Keep candidates whose destination is missing or evidence is weak under a
  concise `Deferred Candidates` result.

Use this closeout shape when useful:

```markdown
## Accepted Updates

- Durable item captured now, with destination.

## Deferred Candidates

- Candidate still needing acceptance, evidence, or a destination.

## ADR-worthy Decisions

- Accepted load-bearing decision that may deserve an ADR.

## No Durable Change

- Use when nothing warrants capture.
```

Omit empty sections unless `No Durable Change` is the only correct result.

### 5. Return the capture result

Return to `$project-memory`:

- docs created or updated,
- terms, rules, boundaries, or decisions captured,
- evidence used,
- candidates or capture deferred and why,
- unresolved domain questions,
- ADR-worthy decisions,
- the derived `capture_outcome` result (`captured`, `deferred`, or
  `no-durable-change`) plus separate destination or deferral data,
- documentation-diff verification for
  `domain_operation=implementation-closeout`.

For a nonempty implementation-closeout delta, account for every accepted item
and every required named target. Return `capture_outcome=captured` only when all
are reconciled, each destination is updated or verified already current, and
the complete documentation diff is verified. If any item, target, evidence, or
destination remains unresolved, return `capture_outcome=deferred` with the
specific destination and reason; `no-durable-change` cannot complete that
closeout. If landed behavior rejects or contradicts a supplied accepted item,
do not silently reinterpret the delta: return `deferred` and require an owner
decision or a separately authorized planning/implementation correction.

## Guardrails

- Do not record transient preferences, tentative ideas, rejected proposals,
  secrets, raw logs, or weak inferences.
- Do not create ADRs for small preferences.
- Do not remove existing domain notes unless the user explicitly invalidates
  them or durable repo evidence proves them stale.
- Do not ask questions answerable from the repository.
- Do not rewrite broad docs to add one narrow term.
- Do not make runtime skills depend on repo-maintenance documentation.
