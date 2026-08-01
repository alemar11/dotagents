# Issue Phase

Use this internal phase to split one complete Feature Spec into hardened,
vertical implementation issues. Do not use it as a public skill.

## Goal

Produce the smallest useful issue graph that implements the Feature Spec while
preserving repository boundaries, acceptance criteria, validation, and any
deferred domain-memory closeout.

## Boundaries

- Do not change Feature Spec scope or invent requirements.
- Do not perform implementation or domain-memory writes.
- Follow `references/publication.md` for the shared GitHub target, publication
  modes, stable refs, and recovery contract; this phase owns only issue-graph
  publication details.
- Use the incoming `run_mode` and derived `source_route`; do not create
  phase-specific choices.
- Treat the current Git remote and affected repository identities as explicit
  intake or validated Feature Spec Set data. Treat issue types, workflow
  states, and their explicit transports as `workflow contract` facts.
  Reject missing, unknown, or GitHub-incompatible transports instead of
  inferring them.
- Publish only with `run_mode=publish`. With `run_mode=preview`, write
  nothing and return bodies, locations, metadata, and publication order rather
  than executable commands.
- Withhold incomplete or contradictory issues. Do not publish them under a
  weaker workflow state.
- Keep cross-Feature-Spec edges in the Feature Spec. Generated issue
  dependencies are intra-Spec only.
- Give every issue one six-field Execution Contract table and no duplicate
  handoff projection.
- Treat generated issues as strong executor-ready starting briefs. Protect the
  stable planning contract directly while preserving compatible executor-owned
  operational edits; never compare a whole tracker body or compute its digest.
- Run structural graph compression before freezing IDs or hardening missing
  issues; issue count is report data only.
- The only stable issue-scope mutation is the separately invoked
  `scope_repair_request` branch owned by `scope-repair.md`. It may add a
  monotonic `allowed_paths` envelope to the named durable issue while preserving
  every other stable field and executor-owned update. It never synthesizes,
  hardens, renumbers, or changes dependencies.

## Phase Inputs

Receive:

- `run_mode` and the frozen derived `source_route`;
- a durable `source_spec_ref`, or a proposed ref only with
  `run_mode=preview`;
- the complete Feature Spec body and validated cross-Spec dependency graph;
- planning identity, affected repositories, allowed paths, and shared target
  branch;
- optional shared `feature_id` and the validated identical `Feature Spec Set`
  when multiple repositories are affected;
- current durable implementation-issue bodies, generated IDs, refs, metadata,
  relationships, and verification evidence when any exist;
- optional `knowledge_delta` plus separate `planning_blockers`. On the
  existing-source route, accept the delta only as explicit accepted invocation
  data or an exact continuation handoff, always separate from the unchanged
  source;
- optional exact continuation handoff from an incomplete publication, containing
  `feature_slug`, every staged or durable Spec ref, multi-repository publication
  transaction identity plus reconstructable templates when present, selected
  `source_idea_refs` plus verified prior outcome refs, and the complete
  `knowledge_delta` until its final owner issue is durable.

Stop when a publish run lacks a durable source ref, when proposed and durable
refs are mixed ambiguously, or when the source still has blocking open
questions.

When a continuation handoff is present, compare its identity, Spec refs,
transaction state, and exact delta with current durable state before graph
work. Resume only when they match. If the handoff says a nonempty delta still
lacks a durable owner, omission or any changed delta item blocks; never treat
that retry as `no-durable-change`.

## Workflow

When `scope_repair_request` is present, first run the complete source and durable
state reads below, then delegate the narrow before/after comparison, mutation
order, audit, recovery, and result to `scope-repair.md`. Rerun verticality,
overlap, dependency, acceptance coverage, and full-bundle validation after the
repair. Stop before ordinary slice synthesis, graph compression, hardening,
metadata repair, or issue creation.

### 1. Validate The Source Contract

Read the Feature Spec and verify:

- exactly one `## Feature Dependencies` section exists and its table has
  exactly the `upstream_feature_spec_ref` and `dependency_reason` columns, even
  on the existing-source route; reject absence, duplicates, extra columns, or
  prose-derived edges before issue generation;
- problem, goals, requirements, acceptance criteria, repository scope, and
  validation expectations are complete;
- acceptance criteria are unique, individually provable checkboxes with stable
  wording and order;
- every paid, external, non-repeatable, or otherwise constrained validation has
  a prose failure policy naming its attempt/retry budget, allowed fallback,
  retained evidence, and required terminal outcome;
- affected repositories and allowed paths resolve to real planning scope;
- the target branch is valid and shared by every generated issue owned by that
  Feature Spec; linked Specs may use different branch names;
- every Feature Spec dependency ref resolves and the cross-Spec graph is
  acyclic;
- every published multi-repository source and dependency ref is globally
  unambiguous: `owner/repository#<number>` or a canonical hosted URL;
- the complete linked Feature Spec Set exists for multi-repository work;
- portable evidence contains no developer-machine absolute path;
- the Feature Spec body contains neither `knowledge_delta` nor
  `## Domain Knowledge Handoff`;
- a present phase-level knowledge delta contains decisions, target surfaces,
  and evidence. Normalize every target to one affected repository plus one
  portable repo-relative path. On the existing-source route, require every
  target to be contained by the unchanged source repository/path scope and
  reject the explicit invocation data otherwise. Never infer it from Feature
  Spec prose, rewrite the source, or widen immutable scope to carry it.

Return blockers without output when these checks fail.

### 2. Discover Durable State And Seed Vertical Slices

Before synthesizing a graph, enumerate the complete current durable issue state
for every implementation-eligible Feature Spec. For GitHub, use pure read
operations through `$gitstack:github-issues` in either planning mode, with mutation
fields omitted. Read every open or closed implementation issue attached to the
Feature Spec and every candidate carrying its durable `source_spec_ref`,
following pagination through the complete result set. If the connector cannot
prove all-state enumeration and pagination completeness, require GitStack's
read-only gap fallback to use paginated `gh api` reads. A fixed-limit
`gh issue list` result is never completeness proof. If GitStack cannot prove
complete state, block before graph synthesis, absence claims, no-op, or
proposal output.

Parse every durable candidate's generated ID, title, source ref, Execution
Contract, stable planning fields, hardening provenance, metadata, and parent
relationship. Validate its vertical outcome against the current Feature Spec.
A durable candidate with stale source identity, missing or contradictory stable
obligations inside its claimed vertical outcome or scope, widened scope,
invalid provenance, malformed dependencies, or duplicate identity is a
conflict; do not ignore it and draft a replacement. Preserve compatible
executor-owned checkbox progress, implementation/design rewrites, additional or
equivalent tests, clarifications, status, evidence, and in-scope fixes.
Obligations outside that claimed slice remain eligible uncovered behavior for
new missing slices.

Seed the candidate graph with every valid durable issue. Its generated ID,
vertical outcome, title, stable planning contract, dependencies, and
integration/closeout role are fixed inputs, not suggestions for model
regeneration. Its execution record remains mutable. Derive
which current Spec obligations those retained slices cover, then synthesize
only independently valuable uncovered behavior. If retained slices cover the
complete Spec, synthesize nothing. If no durable issue exists, build the graph
normally from the complete Spec.

Load `references/vertical-slices.md`. Split uncovered scope by independently
valuable behavior, not architecture layer. Prefer a small graph in which each
issue:

- delivers a testable user or system outcome;
- owns a bounded set of allowed paths and affected repositories;
- has explicit acceptance criteria and validation;
- can merge safely once its dependencies finish;
- avoids duplicating another issue's scope.

Use provisional candidate keys while shaping missing slices. Reserve every
retained generated ID and never renumber it. Assign final IDs to missing slices
only after integration and closeout ownership is final and the structural
graph-compression gate passes. IDs are planning graph identities and remain
separate from hosted issue numbers.

Require a nonempty final graph for every implementation-eligible Feature Spec.
Every linked Spec enters independently. If the source has no implementable
vertical outcome, return a planning blocker rather than an empty successful
bundle.

For each issue, store only `dependency_ids` pointing to earlier generated IDs.
Require every ref to exist, reject self-dependencies, and validate the graph is
acyclic. Derive which issues an issue blocks by scanning all dependency lists;
do not store a second reverse-edge field.

Feature Spec dependencies identify peer inputs required for final proof; they do
not by themselves forbid an ordinary peer worker from starting early and
collaborating. Do not copy upstream Feature Spec refs into an issue's dependency
list.

### 3. Assign Repository Scope

For one affected Git repository, use `current-repository` when no repo slug is
needed. For multi-repository work, list the exact canonical repository
identities.

Apply the canonical allowed-path scope table in `spec-phase.md` to each slice.
Project the Feature Spec's complete safe envelope down to the smallest complete
scope that can implement and validate the issue outcome. Include owned shared
contracts, adapters, configuration, tests, fixtures, generated-contract inputs,
and technical documentation whenever they are reasonably required. Do not
reduce the scope to guessed file names or omit foreseeable supporting paths
merely to manufacture disjoint execution. Reject genuine overlapping scopes
that could make independent execution unsafe, or add an explicit dependency
between the affected issues.

All issues use the Feature Spec's shared `target_branch_name`. Repository shape
is not copied into a selectable issue field.

### 4. Assign Combined Proof And Domain Closeout

For every cross-repository boundary, choose an existing implementation member
whose worker can execute the proof within its accepted paths and tools. Record
the required producer members in Feature Dependencies and describe the exact
revision vector, startup, wiring, health, validation, evidence, and cleanup in
that member's Integration Execution Contract. Assign each component process to
the proof owner or its owning peer and require that worker's pre/post HEAD
readback; never assume the proof owner can access peer filesystems. Multiple
consumer members may own separate proofs against one producer. A bundle-wide
criterion must name one existing member as owner, carry its globally unique
criterion ID only in that member's Acceptance Criteria, and list that ID in the
same member's Feature Spec Set responsibility cell. Combined proof IDs follow
the same exact-once ownership rule. If no existing member can own an obligation,
withhold the bundle instead of creating another Spec, issue subtree, branch, or
worker.

If `knowledge_delta` is absent, generate no domain closeout section.

If `knowledge_delta` is present:

1. For a single Feature Spec, reuse or append the closeout owner. Temporarily
   remove that owner and its outgoing `dependency_ids`, derive the nodes with no
   dependents in the remaining intra-Spec graph, and require the owner's final
   `dependency_ids` to include every such node. Reject any graph in which
   another issue depends on the owner. Reuse an unpublished candidate only when
   it can remain topologically last after these dependencies; reuse a durable
   seed only when its existing closeout payload and dependencies are already
   exact. Otherwise append a new owner without modifying the retained issue.
2. For a multi-repository feature, partition targets into repository-owned
   shards. Every cross-repository decision must name one exact
   `canonical_decision_target` in the form
   `<feature-id>--<repository-key>/<repo-relative-path>`. The Feature ID and
   repository key must resolve to one declared Feature Spec Set member, and the
   path must be contained by that member's accepted paths. That member's shard
   owns the full ADR or decision record; another repository's shard may own
   only its repo-local context change and a backlink that copies the exact same
   canonical target string, never a duplicate canonical record. Repository-
   owned `target_surfaces` use only
   `current-repository/<repo-relative-path>`; a repo slug never selects a root.
   Assign each nonempty shard to
   one existing implementation member whose accepted repository and paths
   contain all targets in that shard. Within every selected member, reuse or
   append one closeout owner and apply the same owner-excluded terminal
   algorithm only to that member. Reject a dependent of the owner and never
   copy peer issue IDs. Reuse an unpublished candidate only when it can remain
   topologically last inside that member; reuse a durable seed only when its
   existing closeout payload and dependencies are already exact. Otherwise
   append a new owner. Withhold the feature when any shard or canonical target
   lacks an in-scope owner.
3. Copy each exact repository-owned shard—its decisions or qualified backlinks,
   portable targets, evidence, and canonical target identity—into that
   member's final `## Domain Knowledge Closeout` section.
4. Before hardening each owner, require every target repository in its payload
   to equal the final issue's sole Git repository and every normalized target
   path to equal or descend from one of that issue's `allowed_paths`. Add a
   missing path only when it is already inside the accepted Feature Spec scope;
   otherwise withhold the issue as blocked. Never rely on another context
   workflow or worker to write another repository.
5. Require `$software-project:project-context domain-memory` with
   `memory_slice=domain-memory` and
   `domain_operation=implementation-closeout` only after integrated behavior
   is proven. The issue completes this step only with
   `capture_outcome=captured`, every accepted delta item and required named
   target reconciled, named destinations reported, and the documentation diff
   verified. `deferred` or `no-durable-change` for a nonempty accepted delta is
   a blocker, not closeout success. Any supplied accepted item rejected or
   contradicted by landed behavior is likewise blocked pending an owner decision
   or separately authorized planning/implementation correction.

Never generate a docs-only closeout issue. The final issue must own real
integration behavior and validation.

### 5. Compress The Candidate Graph

Run the canonical structural graph-compression gate from
`references/vertical-slices.md` independently for every
implementation-eligible Feature Spec. Follow its count-neutral retain, repair,
scope, integration, and closeout rules exactly. Withhold any graph that cannot
pass without widening the accepted Feature Spec scope.

Treat every durable seed from step 2 as fixed. Compression may combine, remove,
or reshape unpublished candidates, but it must not renumber, merge, rewrite, or
change dependencies or scope on a retained durable issue. If the gate can pass
only by changing a durable node, stop on a graph conflict and require a
separately authorized replacement rather than synthesizing a parallel graph.

After repairs, rerun the owner-excluded terminal derivation from this section
for every
repository-owned closeout owner when `knowledge_delta` is present, using each
member's repaired remaining graph and replacing an unpublished closeout
owner's `dependency_ids`; a retained owner must already match the result. Then
rerun verticality, overlap,
dependency, acyclicity, integration, and closeout validation. Build a transient
acceptance coverage map from every Feature Spec criterion to one or more final
issues. Spec and issue criteria are independently authored and need not be
textually identical. Require every Spec criterion to be covered, reject
contradictory or scope-widening issue criteria, and keep each artifact's own
criterion text, count, and order stable. Recompute this map after hardening; do
not persist it unless concise human-readable coverage evidence is useful.
Topologically
assign unused final generated IDs only to missing slices so the closeout owner
is last and every `dependency_ids` entry points to a strictly earlier generated
ID. Never renumber a durable seed. If no unused ID placement can satisfy the
forward-dependency contract without changing a retained issue, stop on a graph
conflict. Freeze the resulting IDs for rendering and publication.

### 6. Converge With Durable Issue State

After the complete structural graph and stable generated IDs are known, compare
it with the complete durable snapshot enumerated before synthesis in step 2.
Compare by generated ID, owning Feature Spec, title, stable planning contract,
tracker metadata, and parent/sub-issue attachment. The stable contract is the
required goal/outcome and Non-Goals; repositories, allowed paths, source and
branch identity; dependencies; acceptance-criterion
text/count/order; safety constraints; and material validation constraints,
including retry/attempt budgets and required terminal outcome. Compare those
sections and fields directly; do not compute a whole-body, result, assignment,
message, or tracker-text digest.
For issue comparison, source and branch identity mean the rendered
`source_spec_ref` and `target_branch_name`.
Do not perform a fresh model split merely to recreate comparison prose.

Do not rerun hardening to synthesize comparison prose for a durable issue.
Treat its body as contract-equivalent only when the generated ID, title, stable
fields above, and `dependency_ids` exactly match the desired graph; required
sections occur exactly once; every current source requirement, acceptance
criterion, safety constraint, and material validation obligation is covered
without contradiction or scope widening; no blocker or placeholder remains;
and the final hardening provenance is valid. Checkbox markers, implementation
approach/internal design, safer or simpler rewrites, additional or equivalent
tests, compatible clarifications, progress/status/evidence, and concrete
in-scope refactors or fixes are a worker-mutable execution record and must be
preserved. Any stable-field drift is a conflict.

Then reconcile:

- retain an existing issue when its identity and stable planning fields match
  and it carries valid final hardening provenance, preserving compatible
  mutable execution content;
- treat an absent desired issue as missing and continue to hardening for that
  issue only;
- when a contract-equivalent issue exists but contract tracker metadata or its
  parent/sub-issue attachment is missing, record only that supported missing
  reconciliation operation;
- when every desired issue, metadata value, and parent/sub-issue attachment is
  exact, record a candidate no-op without hardening or mutation; after the
  final fresh read in step 10, return a no-op without hardening or mutation; and
- stop on duplicates, extra linked implementation issues, stable-field drift,
  conflicting generated IDs, stale source refs, invalid provenance, or any
  graph mismatch. Do not rewrite, close, replace, renumber, or silently adopt a
  conflicting artifact.

For a contract-equivalent GitHub issue, open or closed, an absent contract
`task` label is repairable because type is not executor lifecycle state; a
different contract type is a conflict. Only on an open issue that has not
progressed beyond planning is an absent contract `ready-for-agent` label
repairable; a conflicting canonical workflow state is a conflict. Resolve the
`workflow contract` values before recording the repair and use
`add-label` for each missing label. Unrelated repository labels are not Plan
Feature metadata. A closed issue with a contract-equivalent body is valid
progressed lifecycle state owned by the executor: after any safe type-label
repair, retain it without restoring `ready-for-agent` or reopening it.

An implementation issue already in a closed state remains part of durable state.
It must match the same contract; never create a duplicate active issue for it.
Partial-publication recovery resumes only missing issue, contract metadata, and
parent/sub-issue operations after the comparison passes.

### 7. Harden Every Missing Issue

After structural compression, graph ownership, and durable-state reconciliation
have stabilized, Plan performs one internal codebase-grounded hardening pass for
each missing final issue. Keep the pass bounded to the issue's accepted
repositories, paths, dependencies, and vertical outcome. Inspect the relevant
source files, architecture patterns, contracts, nearby tests, and documentation;
fetch official documentation when current external behavior materially affects
the plan. Resolve what can be established from that evidence and return a
planning blocker through the Plan profile in the Software Project clarification
protocol when a material unknown would change scope, ownership, acceptance, or
validation. Never silently widen the Feature Spec or issue graph.

Build transient hardening evidence for:

- implementation approach into `## Implementation Plan`;
- resolved interpretation and assumptions into `## Context` or implementation
  prose;
- likely files, modules, routes, tests, or documentation to inspect into the
  implementation plan;
- acceptance details into `## Acceptance Criteria`;
- commands and fallbacks into `## Validation`;
- material dependency reasons into `## Context` or implementation prose,
  without repeating dependency IDs;
- edge cases, failure modes, rollout concerns, and rollback constraints into
  the owning requirements or context section.

Run a final gotcha review for missing steps, dependencies, vague acceptance
criteria, unsafe ordering, missing validation, and omitted layers required to
prove the vertical outcome. If a gap remains material, withhold the issue and
report the blocker instead of emitting a weaker agent-ready variant.

Do not paste a separate hardening brief wholesale or create duplicate top-level
sections. Preserve exactly one standard hardening provenance line for the final
stable pass. Render the implementation approach as a planning-time
recommendation and include this exact meaning: "This is the planning-time
recommended approach. The implementing Codex task may replace it with a simpler
or safer design when the accepted goal, scope, constraints and acceptance
criteria remain unchanged."

The provenance marker is role-based and must describe completion of the final
implementation-hardening pass without naming the invoking skill. This keeps
durable issue bodies independent from skill renames and plugin packaging.

Run final verticality, scope-overlap, dependency, validation, and readiness
gates. If hardening exposes a graph-level defect, discard affected results,
return to step 5, restabilize the graph and IDs, and re-harden every materially
changed issue. For a scope repair, run another hardening pass on that
issue before output. Never use hardening to rewrite an existing durable issue.
Supersede earlier transient results and persist only final stable results; pass
count is derived work, not an option or artifact field.

### 8. Render The Execution Contract

Use `references/issue-body-template.md`. Every issue has exactly one
`## Execution Contract` table containing:

- `source_spec_ref`;
- `feature_slug`;
- `affected_repositories`;
- `allowed_paths`;
- `target_branch_name`;
- `dependency_ids`.

Do not add permission, review, PR-count, completion-method,
scheduling-mode, or worker configuration fields.

Dependency reasons belong in Context or implementation prose and must not
repeat the ID list. Reverse edges are a derived view only. The issue body may
include cross-repository notes, integration gates, and domain closeout data in
their dedicated sections; they are not extra knobs.

### 9. Validate Readiness

A durable issue may receive `ready-for-agent` only when:

- its source ref is durable;
- goal, requirements, acceptance criteria, and validation are complete;
- acceptance criteria are unique, individually provable checkboxes whose text,
  count, and order are stable while checkbox markers remain executor-owned;
- every material paid, external, non-repeatable, or otherwise constrained
  validation has an explicit prose failure policy with attempt/retry budget,
  allowed fallback, retained evidence, and required terminal outcome;
- the Execution Contract contains every required field exactly once;
- affected repositories and allowed paths are unambiguous;
- dependency IDs resolve, point only to strictly earlier generated IDs, and the
  graph is acyclic;
- named integration gates exist where needed;
- there are no open human decisions or placeholder questions;
- the structural graph-compression gate passed before hardening;
- the domain closeout owner is unique when required;
- every domain-closeout target surface is contained by that final issue's
  `affected_repositories` and `allowed_paths`.

The generated brief must also require the eventual worker to re-read the
current Spec and complete issue set before each issue, after recovery, and
before final verification. Compatible operational edits remain usable. Drift
in a stable field blocks declaratively without asking the user from the worker
task. The implementing Codex task owns its issue checkbox markers after
current-head proof and a fresh artifact read, updates owning Spec criteria only
after Spec-level proof, and restores unchecked state when later invalidated.
Root coordination never edits or judges individual criteria.

A proposed issue may report `ready-for-agent` only as its intended future
contract value after the same content gates pass. Never emit or persist that workflow
state in a proposed body, label, or queue. Withhold failed issues and return
their blockers; never downgrade them into a partially agent-ready artifact.

### 10. Publish Or Preview

Immediately before returning a preview result, no-op, or performing the first
mutation, re-read the owning Feature Spec body and ref, the current
`workflow contract`, and the complete all-state issue, metadata, and
parent/sub-issue set with the same pagination proof as step 2. Compare that
fresh state with the frozen graph and prior snapshot. If any source, contract,
body, ID, metadata, relationship, or candidate absence changed during graph
work or hardening, discard the stale projection and restart convergence from
fresh source/state evidence; block when the change is foreign, conflicting, or
cannot be proved completely. This final read is mandatory in both planning modes.

For every GitHub repository, revalidate the contract's exact `task` and
`ready-for-agent` labels and collect the labels required by missing operations.
If the contract is missing or contradictory, block and never switch metadata
during recovery. Verify each exact label. Under `run_mode=publish`, create and
verify only a missing contract label through `issue_operation=create-label`
before the first issue or metadata mutation. Under `run_mode=preview`, report
each missing label creation as an intended operation and perform no mutation.
Preserve verified label creations in partial-failure recovery and retry only a
still-missing operation.

Order output topologically, with the final combined-proof or closeout issue last
inside its owning implementation member and its domain closeout attached only
when a delta exists.

- `run_mode=publish`, GitHub: retain exact existing issues and publish only
  missing issues through
  `$gitstack:github-issues`. Translate each write to GitStack-owned
  `mutation_mode=apply`, its exact target, and one canonical `issue_operation`;
  resolve the contract's exact `task` and `ready-for-agent` labels
  independently, and apply them only after the body verifies. Attach the issue as a
  sub-issue of the Feature Spec when supported,
  repair only verified-missing contract metadata or parent/sub-issue attachment
  through the matching canonical GitStack operation, verify every mutation,
  and retain the hosted ref separately from its generated ID.
- `run_mode=preview`: write nothing. Return retained durable artifacts plus
  every missing proposed body, intended repository, contract metadata,
  relationship operation, and the topological publication order. Use
  deterministic `proposed-issue:<feature_slug>/<NN>` refs, or
  `proposed-issue:<feature_id>/<repository_key>/<NN>` for an issue owned by a
  linked multi-repository member.
  On the new-source route, state that neither proposed source nor proposed
  issues are executable until published. On the existing-source route, preserve
  the supplied source as durable and state that only the proposed issue or
  relationship remainder is non-executable. Keep the intended workflow state
  out of the proposed bodies.

`run_mode=preview` never invokes GitStack for publication or mutation. It may
use pure read operations with mutation fields omitted to prove current hosted
state and convergence safety. GitStack does not interpret Plan's tracker
or write policy.

In multi-repository work, publish each issue through GitHub in its owning
repository. Preserve source links to peer Feature Specs and
cross-repository integration gates. Do not create a separate scheduling
artifact; the issue graph is authoritative.

Use transient body transport outside repositories for hosted writes and remove
it after verified mutation. Plan owns only the planning-artifact writes
performed in this phase.

Immediately before each hosted create, re-read the exact target plus the owning
Feature Spec and contract inputs and prove that the frozen artifact is still
absent. Stop and restart or block if a foreign issue, source edit, contract
change, or ambiguous mutation result appears; never create a duplicate. Verify
every successful create before moving to the next operation.

When no issue, metadata, or relationship operation is missing, perform no
mutation and report the verified complete bundle as a no-op only after the
final fresh comparison above remains exact.

If publish exits before every required final issue carrying a nonempty
repository-owned `knowledge_delta` shard is durable and verified, the result is
incomplete and must include the exact
continuation handoff received or constructed by this run: `feature_slug`, all
staged or durable Spec refs, any multi-repository publication-transaction
identity and its role map plus reconstructable templates, selected Idea refs and
prior outcomes, the complete delta, verified completed operations, and exact
missing operations. Do not report `capture_outcome=no-durable-change` or omit
the delta.

### 11. Report

Return:

- Feature Spec ref, `run_mode`, and derived `source_route`;
- candidate and final issue counts, retained, created, missing, or proposed
  generated IDs and refs, repaired metadata or relationships, no-op state, and
  publication order;
- affected repositories and tracker route for each issue;
- dependency graph, topological order, and acyclicity proof;
- verticality, overlap, and compression repairs, retained-slice reasons,
  removed artificial dependencies, and avoided initial hardening passes;
- contract issue type/state published or proposed;
- confirmation that every issue has one valid Execution Contract;
- repository-owned domain closeout issues and deferred capture result when
  required;
- withheld issues and blockers;
- exact continuation handoff for any partial publication whose required
  domain-closeout owners are not all durable, including the complete
  `knowledge_delta` and missing operation list.

When `knowledge_delta` is present, report `capture_outcome=deferred` and every
final issue ref. Otherwise report `capture_outcome=no-durable-change`. This is
a derived report result, not persisted artifact metadata. Never report
planning-time capture.
