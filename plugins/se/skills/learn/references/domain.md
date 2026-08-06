<!-- SE-owned reference derived from the durable repository-context contract. -->

# Context Domain And Routing

Use this reference to discover and route durable project context in a Git
repository. `CONTEXT.md` is the entry point; flat topic files and ADRs are
loaded only when their scope or `Read when` condition applies.

## Discovery Order

1. Read `CONTEXT.md` at the current memory-owning Git root when it exists.
2. Follow every non-overlapping matching row in its `## Scoped Contexts` table.
   A matched row without a context file is still a routing fact; inspect its
   owned paths directly without inventing vocabulary or a dangling pointer.
3. Read the indexed `project-context/<topic>.md` files whose scope and `Read
   when` condition match the affected paths.
4. Read `TRANSLATION.md` beside each selected context when localization memory
   exists and is material.
5. Read `project-context/adr/index.md` when it exists, then the relevant ADRs.

The current Git repository is the default selected root. Explicit user scope or
a validated linked Feature Plan set may authorize additional repository
identities, but a composed caller must supply candidate local Git roots and
verify each root against exactly one identity. Reject extra or unmatched roots.
Never fabricate a path from a hosted ref, saved project, common parent, or path
proximity.

## Memory-Owning Roots

Use exactly one `project-context/` directory per Git repository root. An
internal monorepo scope is not a separate memory-owning root and must not create
a nested `project-context/` directory. Non-Git roots never own Project Context.

## Repository Layout

Single repository:

```text
/
├── AGENTS.md
├── CONTEXT.md
├── TRANSLATION.md                 # optional
└── project-context/
    ├── adr/
    │   ├── index.md
    │   └── ADR-0001-descriptive-name.md
    ├── backend-api.md
    └── worker-runtime.md
```

Monorepo:

```text
/
├── AGENTS.md
├── CONTEXT.md                     # shared context and scope routing
├── TRANSLATION.md                 # optional shared localization
├── project-context/               # one flat topic/ADR root
│   ├── adr/
│   └── worker-runtime.md
└── apps/
    ├── accounting/
    │   ├── CONTEXT.md             # scope-specific delta
    │   └── TRANSLATION.md         # optional scope-specific sidecar
    └── support/
```

Repository-wide topic files live directly under `project-context/`. A scoped
topic declares its scope in the file header instead of creating a topic
subdirectory.

## Root Routing Table

Use this table only when internal scopes are meaningful:

```markdown
## Scoped Contexts

| Scope | Owned paths | Context |
| --- | --- | --- |
| Accounting | `apps/accounting/`, `packages/ledger/` | `apps/accounting/CONTEXT.md` |
| Support | `apps/support/` | — |
```

Rows must have one stable scope name and non-overlapping owned paths. Select
every matching row. Ask the owner to resolve overlap before persisting a table.

## Ownership

Root `CONTEXT.md` owns shared purpose, vocabulary, cross-scope boundaries,
routing, the topic index, ADR index pointer, and explicit unknowns. A scoped
`CONTEXT.md` owns only its scope delta and links back to the root.

Topic files own conditional detail, examples, rationale, domain contracts, and
operational notes. `AGENTS.md` owns only always-active rules and short
pointers. `TRANSLATION.md` owns localization rules beside the context they
serve. ADRs own accepted load-bearing decisions.

Do not duplicate the same normative rule across these surfaces. If a topic or
ADR contradicts an existing `AGENTS.md` rule or ADR, stop and surface the
conflict.

## Bootstrap And Closeout

Authorized setup/bootstrap creates or updates root `CONTEXT.md` at every
selected Git root, even when evidence supports only a minimal entry point with
explicit unknowns. Rich vocabulary, topic files, rules, and scoped contexts
require strong repository evidence or explicit accepted decisions.

For existing projects, load `domain-modeling.md` before writing. For an
implementation closeout, reconcile each accepted durable decision against
landed behavior and update only the named context, topic, project document, or
ADR surfaces.

Never record tentative proposals, rejected ideas, secrets, raw session logs, or
generic architecture advice as durable context.
