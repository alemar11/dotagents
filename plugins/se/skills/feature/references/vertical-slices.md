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
2. Identify the smallest complete repository and path scope that can implement,
   integrate, validate, and document it.
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

Every issue belongs to one repo-owned Feature Spec and may change only that
Spec's Git repository. When repositories must coordinate atomically or one
integration owner must prove the complete behavior, express the ordering
through linked Feature Dependencies and place combined proof on an existing
issue owned by the proof member; never create one issue that edits multiple Git
repositories.

Each issue must identify:

- its exact affected repository identity and, for a linked member, stable
  repository key;
- repo-relative or repo-qualified allowed paths;
- interface, schema, version, migration, fixture, or deployment contracts;
- named integration gates and validation order;
- linked Feature Spec refs when the feature spans repositories.

Potential delivery artifacts are planning context, not completion proof. The
executor records real delivery evidence during implementation.

Assign every cross-repository boundary to an existing implementation member
whose accepted repository, paths, tools, and validation budget can execute the
combined proof. Record the exact peer Feature Specs as Feature Dependencies and
put the executable integration contract on that proof-owning member. Different
consumers may own different boundaries against the same producer HEAD. Withhold
the bundle when no existing member can own a required proof; never synthesize
an integration-only Spec, issue subtree, branch, or worker.

## Dependency Graph

Durable seeds keep their generated IDs and forward lists unchanged. Use
provisional candidate keys only for missing slices while shaping the graph, then
assign unused IDs to those slices after structural compression passes:

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

An agent-ready issue may list unfinished intra-Spec dependencies: it is ready
for the queue, but its worker executes it only after those issues finish.

Cross-Feature-Spec dependencies stay in the Feature Spec's dependency table.
Peer workers may start before those upstream Specs finish so they can collaborate.
Final dependent or combined proof must bind the exact prerequisite delivery
evidence and requires merge only when the durable dependency contract explicitly
says merged input is necessary.

## Scope Overlap Gate

Two issues may be independently executable only when their allowed paths and
contracts do not create unsafe concurrent edits. When overlap exists:

- narrow one issue's scope;
- combine the outcomes when they are not independently useful; or
- add a dependency when ordered ownership is necessary.

Do not introduce a selectable scheduling field. Independence is derived from
the graph and actual path scope by the eventual orchestrator. Never narrow an
otherwise complete safe path envelope merely to make slices appear independent;
combine or order the affected outcomes instead.

## Structural Graph Compression Gate

Run this gate on every complete candidate issue graph after repository scope,
integration ownership, and domain-closeout ownership are assigned, but before
stable IDs or internal hardening passes for missing slices. Durable seed IDs are
already stable.
Evaluate structure rather than issue count;
the number of candidates is measurement data, never a threshold, cap, option,
or reason to block publication.

Retain an issue only when it has:

- an independently valuable user or system outcome;
- a safe landing state once its real dependencies finish;
- acceptance and validation proof distinct from sibling issues; and
- enough independent value to justify another dependency, hardening pass,
  tracker item, and execution boundary.

Repair the graph when any candidate is only an architecture layer, test batch,
documentation update, tracker action, or fragment of the same observable
outcome as a sibling. Fold an invalid enabling slice into its first consumer,
combine candidates that share one outcome and substantially the same scope or
proof, narrow unsafe overlap, and remove dependencies that encode preferred
order rather than technical necessity. Add a dependency instead of combining
only when both outcomes remain independently valuable and ordered ownership is
required.

A durable seed is fixed input. Never merge, remove, renumber, rewrite, or change
scope/dependencies on it through compression. Apply repairs only to unpublished
candidates; when the gate requires a durable-node change, stop on a graph
conflict and require separately authorized replacement.

Never compress across Feature Specs. Run the gate independently for each
implementation-eligible Spec. Preserve every required combined-proof owner and the unique final
domain-closeout owner. A repair must stay inside the
accepted Feature Spec scope; otherwise return a planning blocker instead of
widening the source.

After repairs, rerun the owner-excluded terminal derivation from `Domain
Knowledge Closeout` when a closeout owner exists, and replace that owner's
`dependency_ids` with every terminal in the repaired remaining graph only when
the owner is unpublished; a durable owner must already match. Then
revalidate verticality, overlap, dependencies, acyclicity, integration
ownership, and domain-closeout ownership. Freeze generated IDs only after the
gate passes: freeze only missing IDs and never renumber durable seeds. Report
the candidate count, final count, combined or removed
slices, removed artificial dependencies, retained enabling or integration
reasons, and avoided initial hardening passes, calculated as candidate count
minus final count. Report later repair passes separately. Persist none of this
as an option, Feature Spec field, Execution Contract row, or issue-body section.

If later issue hardening exposes a graph-level defect, discard the affected
hardening results, return to this gate, restabilize the graph and IDs, and
re-harden every materially changed unpublished issue. Never use hardening to
rewrite a durable seed.

## Domain Knowledge Closeout

When the issue phase receives a knowledge delta, one final implementation
closeout issue per nonempty repository-owned target shard persists it. No
Feature Spec body carries the payload. Exclude each selected owner and its
outgoing `dependency_ids`, derive the nodes with no dependents in that member's
remaining graph, then make the owner depend directly on every such node and
reject any issue that depends on the owner.

For a multi-repository bundle, one explicit canonical decision target in the
exact `<feature-id>--<repository-key>/<repo-relative-path>` form owns the full
cross-repository ADR or decision record. Its prefix must resolve to a declared
Feature Spec Set member and its path must fit that member's accepted paths.
Other member shards may persist only repo-local context changes and backlinks
that copy that exact target. Every
selected owner's accepted paths contain its complete shard, and its Feature
Dependencies name the exact peer inputs required for final proof. Apply the
owner-excluded terminal rule independently inside each member; never copy issue IDs
across Specs.

The final issue must:

- prove integrated feature behavior;
- invoke `$se:learn domain-memory` only after implementation proof;
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
- exactly one `## Execution Contract` matching the field registry in
  `references/issue-body-template.md`;
- valid generated dependency IDs and an acyclic graph;
- portable source and evidence refs;
- no unresolved human decision or placeholder question;
- a passed structural graph-compression gate before IDs were frozen;
- a completed final stable internal issue-hardening pass, after graph and scope
  stabilization;
- domain closeout only on the unique final issue when required.

Withhold any issue that fails this gate and report its blockers. Do not emit a
weaker agent-ready variant.

## Repair Order

When validation fails, repair in this order:

1. feature scope and acceptance ambiguity;
2. vertical slice boundaries;
3. repository/path overlap;
4. structural graph compression;
5. dependency graph;
6. validation and integration proof;
7. domain closeout ownership;
8. template and metadata consistency.

Re-run internal issue hardening for any issue materially changed by repairs, keep
only the final stable result and one provenance line, then repeat the readiness
gate.
