# Domain Memory

How agent workflows should consume this repo's domain memory when exploring the
codebase, planning work, or preparing implementation issues.

## Before exploring, read these

- `CONTEXT.md` at the repo root, or
- `CONTEXT-MAP.md` at the repo root if it exists; it points at the relevant
  context-specific `CONTEXT.md` files
- `TRANSLATION.md` beside the relevant `CONTEXT.md`, when the project supports
  localization
- `project-memory/adr/` for root-level durable decisions
- In multi-context repos, also check context-specific `project-memory/adr/`
  directories near the relevant `CONTEXT.md`

If these files do not exist, setup should still run an initial context-seed
check for non-empty repos. During fresh setup, create root `CONTEXT.md` when
durable repo evidence supports useful first vocabulary, rules, boundaries, or
open questions. During existing-project bootstrap, setup may also create useful
ADRs when repo evidence or recent session history strongly supports accepted
load-bearing decisions being recorded.

`AGENTS.md` should point to these files and carry agent operating rules. It
should not duplicate domain vocabulary, tracker procedures, planning history,
localization rules, or context seed material after those items have a
project-memory home.

## File structure

Single-context repo:

```text
/
├── CONTEXT.md
├── TRANSLATION.md             # optional localization rules
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
    │   ├── TRANSLATION.md     # optional admin localization rules
    │   └── project-memory/
    │       └── adr/          # admin-specific decisions
    └── mobile/
        ├── CONTEXT.md
        ├── TRANSLATION.md     # optional mobile localization rules
        └── project-memory/
            └── adr/          # mobile-specific decisions
```

Orchestrator workspace:

```text
/
├── CONTEXT.md                 # coordination vocabulary
├── project-memory/
│   └── adr/                   # durable coordination decisions
└── projects/
    └── customer-growth/
        ├── PROJECT.md         # initiative-level overview and constraints
        ├── repos/
        │   ├── backend.md     # pointer sheet, not repo memory
        │   └── mobile.md
        └── features/
            └── team-invitations/
                ├── PRD.md
                ├── integration-gates.md
                └── issues/
                    ├── 01-accept-invitation.md
                    └── done/       # created on demand after first completion
```

In orchestrator workspace mode, root `CONTEXT.md` should define coordination
terms such as project, feature, vertical issue, repo pointer, integration gate,
and done. Child repos keep their own `AGENTS.md`, `CONTEXT.md`,
optional `TRANSLATION.md`, `project-memory/`, validation, branches, commits,
and PRs.

## Translation memory

Create `TRANSLATION.md` only when localization support is clear from repo
evidence or explicit user confirmation. Place it beside the relevant
`CONTEXT.md`: root-level for single-context repos, or context-specific in
multi-context repos.

Use `references/translation.md` for the file shape. Keep localization guidance
there instead of copying it into `AGENTS.md` or `CONTEXT.md`. `CONTEXT.md`
owns product vocabulary and boundaries; `TRANSLATION.md` owns how user-facing
language is translated for supported audiences and locales.

When translation rules affect domain terms, audience, product naming, or
user-facing copy, the neighboring `CONTEXT.md` may include a one-line pointer
to `TRANSLATION.md`. This pointer is optional; do not add it when it would be
stale, noisy, or broken.

## Use the glossary vocabulary

When output names a domain concept in a PRD, issue title, refactor proposal,
hypothesis, or test name, use the term as defined in the relevant `CONTEXT.md`.
Do not drift to synonyms the glossary explicitly avoids.

If a needed concept is not in the glossary, either reconsider the invented term
or note it as a candidate for the domain-modeling workflow.

## Flag ADR conflicts

If output contradicts an existing ADR, surface the conflict explicitly rather
than silently overriding it.

## Orchestrator boundaries

Orchestrator workspace memory coordinates work across repos. It should not copy
or replace child repo memory. Use `projects/<project>/repos/*.md` as pointer
sheets for repo path, role, tracker, validation, and linked work only.

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

## Initial context seed

For a non-empty repo without `CONTEXT.md`, fresh setup should recommend an
initial seed when README files, product docs, source/tests, or package metadata
can support a concise first glossary and boundary/rule list. Use
`references/context-seed.md` for the seed shape and keep ADR creation out of
fresh setup unless explicitly requested.
