# Domain Memory

Use this reference to discover and route durable domain memory in a repository
or coordination workspace. When domain memory exists, root `CONTEXT.md` is the
single entry point; optional scoped `CONTEXT.md` files extend it for
independently meaningful internal domains.

## Discovery order

1. Read `CONTEXT.md` at the current memory-owning root when it exists. If it is
   intentionally absent, use repository evidence and create it only with
   authorized durable content or verified topology-routing evidence.
2. In a multi-repository coordination workspace, use its
   `## Repository Registry` to select every affected child repository and read
   each available child root `CONTEXT.md`. A missing optional child context is
   not a broken route.
3. At the current Git repository root, or at each child root selected by the
   workspace registry, use `## Scoped Contexts`, when present, to select every
   matching scoped `CONTEXT.md` from the affected paths or accepted product
   identities. Multiple non-overlapping matches are valid.
4. Read `TRANSLATION.md` beside each selected context when localization memory
   exists and is material.
5. Read relevant ADRs from every selected memory-owning root's existing
   `project-memory/adr/` tree.

The coordination-workspace root and every available selected
child-repository root context apply to cross-repository work. A scoped context
records only its delta and never replaces or overrides its repository root
silently. Stop only when repository or scoped rows overlap or ownership remains
indeterminate; do not treat multiple non-overlapping affected scopes as an
ambiguity. If no scoped row matches inside a selected repository, use that
repository's root context when it exists.

When root `CONTEXT.md` exists or its creation is authorized, `AGENTS.md` should
point at it and carry agent operating rules. It should not duplicate domain
vocabulary, tracker procedures, planning history, localization rules, or
context seed material after those items have a Project Memory home.

## Memory-owning roots

Use exactly one `project-memory/` directory per memory-owning root:

- a Git repository root owns its repository memory;
- a non-Git multi-repository coordination-workspace root may own coordination
  memory;
- an internal monorepo project is not a memory-owning root and must not create
  a nested `project-memory/` directory;
- child repositories in a multi-repository workspace remain independent
  memory-owning roots.

## Repository layout

Single-repository project with domain memory:

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

Monorepo:

```text
/
├── CONTEXT.md                 # shared context and scope routing
├── project-memory/
│   └── adr/                   # all repository decisions
│       ├── 0001-system-decision.md
│       └── accounting/
│           └── 0002-ledger-boundary.md
└── apps/
    ├── accounting/
    │   ├── CONTEXT.md         # accounting-specific delta
    │   └── TRANSLATION.md     # optional scoped localization rules
    └── support/               # routed scope; context optional until evidenced
```

Multi-repository coordination workspace:

```text
/
├── CONTEXT.md                 # workspace overview and repository routing
├── project-memory/
│   └── adr/                   # coordination decisions only
└── repositories/              # child repositories or durable pointers
    ├── backend/               # independent memory-owning root
    └── mobile/                # context may be absent until evidenced
```

Project Memory setup stays config-only in a coordination workspace. It may
create or refresh root memory surfaces, but it does not create initiative,
feature, issue, integration, or runtime-orchestration artifacts. Those belong
to the planning or implementation workflow that creates real work.

## Root routing tables

Use this canonical table only when the root has scoped internal contexts:

```markdown
## Scoped Contexts

| Scope | Owned paths | Context |
| --- | --- | --- |
| Accounting | `apps/accounting/`, `packages/ledger/` | `apps/accounting/CONTEXT.md` |
| Support | `apps/support/` | — |
```

Each row must have one stable scope name, one or more repository- or
workspace-relative owned paths, and an optional context path. Populate
`Context` only when the scoped file exists or its creation is authorized; use
`—` otherwise. Rows must be non-overlapping. Select all rows matched by the
affected paths. Ask the owner to resolve an overlap by choosing one owner or
splitting the paths before persisting the table. When a matched row has no
context, use its owned paths to inspect scope evidence directly without
inventing vocabulary or creating a dangling pointer.

For a multi-repository coordination workspace, use this registry for stable
repository identity and routing:

```markdown
## Repository Registry

| Repository | Role | Location | Context |
| --- | --- | --- | --- |
| backend | Core APIs | `repositories/backend/` | `repositories/backend/CONTEXT.md` |
| docs | Product documentation | `repositories/docs/` | — |
```

Use portable workspace-relative locations or canonical remote identities.
Exclude developer-specific absolute paths, worktrees, live branch state,
worker assignments, validation transcripts, and copied child-repository
memory. Detailed tracker, validation, branch, and implementation rules remain
owned by each child repository. The `Context` cell is optional: populate it
only when the child root context exists or its creation is authorized; use `—`
otherwise. For cross-repository work, select the affected registry rows, read
each available child root context, and then apply that child's own scoped
routing when relevant. When a child context is absent, keep the workspace root
coordination context, inspect child repository evidence directly, and do not
invent child vocabulary or create a dangling pointer.

## Root and scoped ownership

Root `CONTEXT.md` owns:

- project or workspace purpose and stable non-goals;
- shared product areas and repository roles;
- shared domain vocabulary;
- cross-scope rules and boundaries;
- scoped-context routing;
- the workspace repository registry when applicable;
- system-wide open questions and ADR pointers.

A scoped `CONTEXT.md` owns only the selected scope's delta:

- scope purpose and non-goals;
- scope-specific vocabulary;
- boundaries and handoffs with other scopes;
- scope-specific durable rules;
- relevant centralized ADR links;
- unresolved scope questions.

Do not copy shared root sections into every scoped file. Link back to the root
and preserve one owner for each rule or term.

## ADR ownership

Keep every ADR beneath the memory-owning root's `project-memory/adr/`.
Repository-wide decisions may live directly there. Scope-specific decisions
may use a stable subdirectory such as `project-memory/adr/accounting/`, but the
scope must not create its own `project-memory/` tree.

If output contradicts an existing ADR, surface the conflict explicitly rather
than silently overriding it.

## Translation memory

Create `TRANSLATION.md` only when localization support is clear from durable
evidence or explicit user confirmation. Place it beside the context whose
localization rules it owns. Child repositories in a coordination workspace
keep their own translation memory.

Use `references/translation.md` for the file shape. Keep localization guidance
there instead of copying it into `AGENTS.md` or `CONTEXT.md`.

## Bootstrap and closeout

For a detected monorepo or multi-repository workspace, verified topology is
enough evidence for a minimal root routing `CONTEXT.md`. Rich vocabulary,
rules, boundaries, and scoped context files still require the evidence in
`references/context-seed.md`.

For an already-used project, load `references/domain-modeling.md` before
writing root or scoped context or ADRs. When implementation closeout carries
accepted durable decisions, reconcile them against landed behavior, update
only the named root/scoped context, project doc, or centralized ADR surfaces,
and verify the documentation diff.

Do not record tentative proposals, rejected ideas, secrets, raw session logs,
or generic architecture advice as Project Memory.
