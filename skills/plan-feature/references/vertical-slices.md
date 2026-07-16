# Vertical Slice Guide

Use this reference while splitting and validating implementation issues.

## Core Rule

A vertical slice delivers one independently testable user or system outcome
through every required layer. Do not split by architecture alone.

Good slices read like outcomes:

- a user can export one supported data set end to end;
- an operator can observe and retry one failed workflow;
- one consumer can adopt a compatible API path with its integration proof.

Weak slices read like layers:

- create the database table;
- add the API endpoint;
- build the UI;
- write tests later.

Layer work may appear inside one issue's implementation plan, but it is not a
reason to create a separate issue unless it delivers a reusable enabling
capability with its own acceptance and validation.

## Slice Construction

For each candidate issue:

1. Name one observable outcome.
2. Identify the smallest repository and path scope that can deliver it.
3. Include all layers needed for that outcome.
4. Define specific acceptance criteria.
5. Name preferred validation and a realistic fallback.
6. Add only dependencies that are technically necessary.
7. Confirm it can land safely when those dependencies complete.

Prefer fewer complete issues over many coordination-heavy issues. Do not create
an issue merely to hold shared notes, planning, documentation, or tracker
administration.

## Enabling Slices

An enabling slice is valid only when all of these are true:

- multiple later outcomes genuinely depend on it;
- it creates a usable, testable capability rather than a stub;
- its acceptance criteria prove that capability independently;
- combining it with one consumer would create unsafe scope or duplicate work.

Otherwise fold the enabling work into the first vertical consumer.

## Multi-Repository Slices

Prefer one issue per independently mergeable repository outcome. Use one
cross-repository issue only when the repositories must change atomically or one
integration owner must prove the complete behavior.

Each issue must identify:

- exact affected repository slugs;
- repo-relative or repo-qualified allowed paths;
- interface, schema, version, migration, fixture, or deployment contracts;
- named integration gates and validation order;
- sibling Feature Spec refs when repo-scoped partials exist.

Expected PR slots are planning context, not completion proof. The executor
records real PR links during implementation.

Every multi-repository bundle has exactly one distinct repo-owned integration
partial downstream of all implementation partials and at least one integration
issue that owns a bounded repo/path change and proves the cross-repository result
after those upstream merges. A validation-only or no-op issue cannot satisfy the
App's real-PR conclusion; withhold the App-compatible bundle if no concrete
integration vehicle exists. This structure does not depend on a knowledge
delta.

## Dependency Graph

Use stable generated IDs and one forward list per issue:

```text
01: dependency_ids: none
02: dependency_ids: 01
03: dependency_ids: 01
04: dependency_ids: 02, 03
```

Rules:

- every ID resolves inside the current Feature Spec;
- no issue depends on itself;
- dependency edges form an acyclic graph;
- a dependency represents a real implementation prerequisite, not preferred
  scheduling;
- the list contains generated IDs, never hosted issue numbers or upstream
  Feature Spec refs;
- reverse edges are derived by scanning all lists and are never stored.

An agent-ready issue may list unfinished dependencies: it is ready for the
queue, but execution waits until those dependencies finish.

Cross-Feature-Spec dependencies stay in the Feature Spec's dependency table.
They gate the complete downstream Feature Spec and always wait for upstream
merge plus integration proof.

## Scope Overlap Gate

Two issues may be independently executable only when their allowed paths and
contracts do not create unsafe concurrent edits. When overlap exists:

- narrow one issue's scope;
- combine the outcomes when they are not independently useful; or
- add a dependency when ordered ownership is necessary.

Do not introduce a selectable scheduling field. Independence is derived from
the graph and actual path scope by the eventual orchestrator.

## Domain Knowledge Closeout

When the issue phase receives a knowledge delta, exactly one final
implementation/integration issue persists it. No Feature Spec body carries the
payload. Exclude the selected owner and its outgoing `dependency_ids`, derive
the nodes with no dependents in the remaining graph, then make the owner depend
directly on every such node and reject any issue that depends on the owner.

For a multi-repository bundle, persist the delta only on the final issue of its
dedicated repo-owned integration partial. That partial exists regardless of the
delta, and its Feature Dependencies point to every implementation partial so all
cross-Spec edges wait for upstream merge. Apply the owner-excluded terminal rule
only inside that integration partial; never copy sibling-partial issue IDs
across Specs.

The final issue must:

- prove integrated feature behavior;
- invoke `$project-memory domain-memory` only after implementation proof;
- carry exact decisions, target surfaces, and evidence;
- cover every target surface with the same issue's `affected_repositories` and
  `allowed_paths`;
- verify the resulting documentation diff.

Never create a docs-only closeout slice.

## Readiness Gate

Every agent-ready issue must have:

- one bounded vertical goal;
- explicit non-goals;
- complete requirements and acceptance criteria;
- preferred validation plus a fallback or explicit `None`;
- exactly one `## Execution Contract` containing the six required normal
  fields from `references/options.md`;
- valid generated dependency IDs and an acyclic graph;
- portable source and evidence refs;
- no unresolved human decision or placeholder question;
- a completed final stable `$plan-harder` issue-hardening pass, after graph and
  scope stabilization;
- domain closeout only on the unique final issue when required.

For explicit non-App planning, the same section also carries the conditional
target field and the bundle is not App-compatible.

Withhold any issue that fails this gate and report its blockers. Do not emit a
weaker agent-ready variant.

## Repair Order

When validation fails, repair in this order:

1. feature scope and acceptance ambiguity;
2. vertical slice boundaries;
3. repository/path overlap;
4. dependency graph;
5. validation and integration proof;
6. domain closeout ownership;
7. template and metadata consistency.

Re-run `$plan-harder` for any issue materially changed by repairs, keep only the
final stable result and one provenance line, then repeat the readiness gate.
