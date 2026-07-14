# Initial CONTEXT.md Seed

Use this reference when `project-memory` bootstraps a non-empty repo and
repo evidence can support a useful first `CONTEXT.md`.

## Evidence threshold

Seed `CONTEXT.md` only when at least one durable repo source supports the
content:

- README, vision docs, architecture docs, product docs, or component docs
- AGENTS.md rules that describe accepted repo behavior
- package manifests, schemas, tests, source directories, or public APIs
- accepted user decisions and committed repo behavior

Issues, PRs, PRDs, tracker discussions, and final session summaries may help
discover candidate knowledge, but they are not durable repo authority by
themselves. Before citing a candidate in `CONTEXT.md`, capture or verify it in a
repo-owned document, ADR, source file, schema, or test. Tracker links may remain
as optional provenance in that durable source.

Do not seed from guesses, tentative plans, rejected options, secrets, raw logs,
or generic architecture advice.

When `AGENTS.md` is a source, capture only durable project context or accepted
repo behavior. Leave agent operating rules in `AGENTS.md`, and move tracker or
triage details to `project-memory/config/*` instead of copying them into
`CONTEXT.md`.

## Seed shape

Load and follow `references/domain-modeling.md` before writing. Keep the initial
seed short
and useful. Include only sections that have evidence:

```markdown
# Context

## Project Purpose

## Product Areas

## Domain Vocabulary

## Durable Rules And Boundaries

## Open Questions
```

When a neighboring `TRANSLATION.md` exists and localization affects domain
terms, audience, product naming, or user-facing copy, `CONTEXT.md` may include
a one-line pointer such as `Localization: see TRANSLATION.md`. Do not require
this pointer and do not create broken links.

Use concise bullets. Link or name source files when that helps future agents
verify the statement, for example `README.md`, `VISION.md`, `docs/...`,
`agents/README.md`, `be/docs/openapi.yaml`, or a specific source/test path.

## What to capture

- Project purpose and explicit non-goals.
- Product areas, subprojects, services, packages, or ownership boundaries.
- Canonical names and terms future PRDs/issues should reuse.
- Durable rules that affect implementation, validation, promotion, or docs.
- Open questions only when current evidence clearly leaves a decision
  unresolved or conflicting.

## What to avoid

- Full architecture inventories or file trees.
- Repeating command lists already owned by AGENTS.md or README files.
- Copying agent operating instructions that should remain in `AGENTS.md`.
- Recording translation or localization rules that belong in `TRANSLATION.md`.
- Long research notes that belong in project docs.
- ADR-level decisions unless the user explicitly asks to record accepted
  decisions and the evidence is load-bearing.
