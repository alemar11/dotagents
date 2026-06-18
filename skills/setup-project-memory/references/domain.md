# Domain Memory

How agent workflows should consume this repo's domain memory when exploring the
codebase, planning work, or preparing implementation issues.

## Before exploring, read these

- `CONTEXT.md` at the repo root, or
- `CONTEXT-MAP.md` at the repo root if it exists; it points at the relevant
  context-specific `CONTEXT.md` files
- `project-memory/adr/` for root-level durable decisions
- In multi-context repos, also check context-specific `project-memory/adr/`
  directories near the relevant `CONTEXT.md`

If these files do not exist, proceed silently for fresh setup. During
existing-project bootstrap, setup may seed root `CONTEXT.md` and useful ADRs
when repo evidence or recent session history strongly supports the terms,
rules, open questions, or accepted decisions being recorded.

## File structure

Single-context repo:

```text
/
├── CONTEXT.md
├── project-memory/
│   └── adr/
│       ├── 0001-some-decision.md
│       └── 0002-another-decision.md
└── src/
```

Multi-context repo:

```text
/
├── CONTEXT-MAP.md
├── project-memory/
│   └── adr/                  # system-wide decisions
└── apps/
    ├── admin/
    │   ├── CONTEXT.md
    │   └── project-memory/
    │       └── adr/          # admin-specific decisions
    └── mobile/
        ├── CONTEXT.md
        └── project-memory/
            └── adr/          # mobile-specific decisions
```

## Use the glossary vocabulary

When output names a domain concept in a PRD, issue title, refactor proposal,
hypothesis, or test name, use the term as defined in the relevant `CONTEXT.md`.
Do not drift to synonyms the glossary explicitly avoids.

If a needed concept is not in the glossary, either reconsider the invented term
or note it as a candidate for the domain-modeling workflow.

## Flag ADR conflicts

If output contradicts an existing ADR, surface the conflict explicitly rather
than silently overriding it.

## Existing-project bootstrap

When setup seeds domain memory for an already-used project, load and follow
`$domain-modeling` before writing `CONTEXT.md` or ADRs.

Use repo vocabulary first:

- README and project docs
- source files, tests, schemas, and issue templates
- accepted decisions from commits, final session summaries, or explicit user
  acceptance

Do not record tentative proposals, rejected ideas, secrets, raw session logs, or
generic architecture advice as project memory.
