# Domain Memory

Use this reference to discover and route durable domain memory in a Git
repository. When domain memory exists, root `CONTEXT.md` is the
single entry point; optional scoped `CONTEXT.md` files extend it for
independently meaningful internal domains.

## Discovery order

1. Read `CONTEXT.md` at the current memory-owning root when it exists. During
   authorized setup/bootstrap, create or update it at every memory-owning root
   selected by the setup scope, even when available evidence supports only a
   minimal entry point with explicit unknowns. Outside setup/bootstrap, use
   repository evidence and create it only with authorized durable content.
2. At the current Git repository root, use `## Scoped Contexts`, when present,
   to select every
   matching scoped `CONTEXT.md` from the affected paths or accepted product
   identities. Multiple non-overlapping matches are valid.
3. Read `TRANSLATION.md` beside each selected context when localization memory
   exists and is material.
4. Read relevant ADRs from the selected Git root's existing
   `project-memory/adr/` tree.

Explicit user scope or a durable linked Feature Spec Set authorizes the
selected repository identities. A composed cross-repository caller supplies
candidate local Git roots separately, verifies each root against exactly one
authorized identity, rejects extra or unmatched roots, and applies this
discovery order independently in each verified repository. Never fabricate a
local path from a Spec ref. A scoped context records only its delta and never
replaces or overrides its repository root silently. Stop only when scoped rows
overlap or ownership remains indeterminate. If no scoped row matches, use the
repository root context when it exists.

When root `CONTEXT.md` exists or its creation is authorized, `AGENTS.md` should
point at it and carry agent operating rules. It should not duplicate domain
vocabulary, tracker procedures, planning history, localization rules, or
initial context material after those items have a Project Memory home.

## Memory-owning roots

Use exactly one `project-memory/` directory per Git repository root:

- a Git repository root owns its repository memory;
- an internal monorepo project is not a memory-owning root and must not create
  a nested `project-memory/` directory.

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

## Root routing tables

Use this canonical table only when the root has scoped internal contexts:

```markdown
## Scoped Contexts

| Scope | Owned paths | Context |
| --- | --- | --- |
| Accounting | `apps/accounting/`, `packages/ledger/` | `apps/accounting/CONTEXT.md` |
| Support | `apps/support/` | — |
```

Each row must have one stable scope name, one or more repository-relative owned
paths, and an optional context path. Populate
`Context` only when the scoped file exists or its creation is authorized; use
`—` otherwise. Rows must be non-overlapping. Select all rows matched by the
affected paths. Ask the owner to resolve an overlap by choosing one owner or
splitting the paths before persisting the table. When a matched row has no
context, use its owned paths to inspect scope evidence directly without
inventing vocabulary or creating a dangling pointer.

## Root and scoped ownership

Root `CONTEXT.md` owns:

- project purpose and stable non-goals;
- shared product areas and internal scope roles;
- shared domain vocabulary;
- cross-scope rules and boundaries;
- scoped-context routing;
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

For a decision spanning multiple Git repositories, require one explicitly
selected canonical ADR-owning repository and one qualified
`canonical_decision_target` in the exact
`<feature-id>--<repository-key>/<repo-relative-path>` form. The prefix must
resolve to the declared ADR-owning member of the caller's validated Feature
Spec Set; the remainder is a path inside that member. Project Memory runs
independently in every selected repository: the canonical owner may write the
full decision, while another repository may write only its repo-local context
delta and a backlink that copies the exact canonical target. Never duplicate the
canonical ADR, infer its owner from the current task or saved-project list, or
write across repository roots in one Project Memory invocation.

If output contradicts an existing ADR, surface the conflict explicitly rather
than silently overriding it.

## Translation memory

Create `TRANSLATION.md` only when localization support is clear from durable
evidence or explicit user confirmation. Place it beside the context whose
localization rules it owns.

Use `references/translation.md` for the file shape. Keep localization guidance
there instead of copying it into `AGENTS.md` or `CONTEXT.md`.

## Bootstrap and closeout

Authorized setup/bootstrap always creates or updates root `CONTEXT.md` at every
Git repository selected by the setup scope. For a detected monorepo, verified
repository structure supports stable root routing. For an evidence-poor
repository, keep the root as a minimal entry point
and state unsupported project knowledge as unresolved. Rich vocabulary, rules,
boundaries, and scoped context files still require the evidence in
`references/context-seed.md`.

For an already-used project, load `references/domain-modeling.md` before
writing root or scoped context or ADRs. When implementation closeout carries
accepted durable decisions, reconcile them against landed behavior, update
only the named root/scoped context, project doc, or centralized ADR surfaces,
and verify the documentation diff.

Do not record tentative proposals, rejected ideas, secrets, raw session logs,
or generic architecture advice as Project Memory.
