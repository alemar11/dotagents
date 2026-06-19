# Initial CONTEXT.md Seed

Use this reference when `setup-project-memory` bootstraps a non-empty repo and
repo evidence can support a useful first `CONTEXT.md`.

## Evidence threshold

Seed `CONTEXT.md` only when at least one durable repo source supports the
content:

- README, vision docs, architecture docs, product docs, or component docs
- AGENTS.md rules that describe accepted repo behavior
- package manifests, schemas, tests, source directories, or public APIs
- accepted user decisions, commits, issues, or final session summaries

Do not seed from guesses, tentative plans, rejected options, secrets, raw logs,
or generic architecture advice.

## Seed shape

Load and follow `$domain-modeling` before writing. Keep the initial seed short
and useful. Include only sections that have evidence:

```markdown
# Context

## Project Purpose

## Product Areas

## Domain Vocabulary

## Durable Rules And Boundaries

## Open Questions
```

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
- Long research notes that belong in project docs.
- ADR-level decisions unless the user explicitly asks to record accepted
  decisions and the evidence is load-bearing.
