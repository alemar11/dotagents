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
- Use the incoming `mode` and `write_mode`; do not create phase-specific
  choices.
- Treat tracker routing, repository topology, issue types, and workflow states
  as Project Memory facts.
- Publish only with `write_mode=apply`. With `write_mode=propose`, write
  nothing and return bodies, locations, metadata, and publication order rather
  than executable commands.
- Withhold incomplete or contradictory issues. Do not publish them under a
  weaker workflow state.
- Keep cross-Feature-Spec edges in the Feature Spec. Generated issue
  dependencies are intra-Spec only.
- Give every issue one Execution Contract table and no duplicate delivery or handoff
  projection.
- Run structural graph compression before freezing IDs or invoking
  `$plan-harder`; issue count is report data only.
- Load `non-app-delivery.md` when the current request explicitly selects its
  target, or when the source Feature Spec contains exactly one target and one
  resolvable `explicit_instruction_ref`.

## Phase Inputs

Receive:

- a durable `source_spec_ref`, or a proposed ref only with
  `write_mode=propose`;
- the complete Feature Spec body and validated cross-Spec dependency graph;
- planning identity, affected repositories, allowed paths, and shared target
  branch;
- tracker backend and repository layout facts for every owning repository;
- workspace parent/child refs when applicable;
- optional `knowledge_delta` plus separate `planning_blockers`. In
  `issues-from-existing-spec`, accept the delta only as explicit accepted
  invocation data separate from the unchanged source;
- `non_app_delivery_target` and its non-option `explicit_instruction_ref` only
  when the conditional reference was loaded.

Stop when an apply run lacks a durable source ref, when proposed and durable
refs are mixed ambiguously, or when the source still has blocking open
questions.

## Workflow

### 1. Validate The Source Contract

Read the Feature Spec and verify:

- exactly one `## Feature Dependencies` section exists and its table has
  exactly the `upstream_feature_spec_ref` and `dependency_reason` columns, even
  for `mode=issues-from-existing-spec`; reject absence, duplicates, extra
  columns, or prose-derived edges before issue generation;
- problem, goals, requirements, acceptance criteria, repository scope, and
  validation expectations are complete;
- affected repositories and allowed paths resolve to real planning scope;
- the target branch is valid and shared across all affected repositories;
- a dedicated integration partial uses a target branch distinct from the
  ordinary partial branch in the same owner repository;
- every Feature Spec dependency ref resolves and the cross-Spec graph is
  acyclic;
- every applied multi-repository source and dependency ref is globally
  unambiguous: `owner/repository#<number>` or a canonical hosted URL for GitHub,
  and `<repository_slug>/<repo-relative-spec-path>` for local Markdown;
- the complete parent/child Feature Spec mapping exists for multi-repository
  work;
- portable evidence contains no developer-machine absolute path;
- non-App data is absent or contains exactly one target plus exactly one
  resolvable `explicit_instruction_ref` whose instruction selects the same
  target and scope under the loaded conditional reference;
- the Feature Spec body contains neither `knowledge_delta` nor
  `## Domain Knowledge Handoff`;
- a present phase-level knowledge delta contains decisions, target surfaces,
  and evidence. Normalize every target to one affected repository plus one
  portable repo-relative path. In `issues-from-existing-spec`, require every
  target to be contained by the unchanged source repository/path scope and
  reject the explicit invocation data otherwise. Never infer it from Feature
  Spec prose, rewrite the source, or widen immutable scope to carry it.

Return blockers without output when these checks fail.

### 2. Build Vertical Slices

Load `references/vertical-slices.md`. Split by independently valuable behavior,
not architecture layer. Prefer a small graph in which each issue:

- delivers a testable user or system outcome;
- owns a bounded set of allowed paths and affected repositories;
- has explicit acceptance criteria and validation;
- can merge safely once its dependencies finish;
- avoids duplicating another issue's scope.

Use provisional generated IDs such as `01`, `02`, and `03` while shaping the
graph. Freeze stable IDs only after integration and closeout ownership is final
and the structural graph-compression gate passes. IDs are planning graph
identities and remain separate from hosted issue numbers.

For each issue, store only `dependency_ids` pointing to earlier generated IDs.
Require every ref to exist, reject self-dependencies, and validate the graph is
acyclic. Derive which issues an issue blocks by scanning all dependency lists;
do not store a second reverse-edge field.

Feature Spec dependencies affect when the whole Feature Spec may start. Do not
copy upstream Feature Spec refs into an issue's dependency list.

### 3. Assign Repository Scope

For a single repository or monorepo issue, use `current-repository` as the
affected repository when no repo slug is needed. For a workspace issue, list
the exact child repo slugs.

Set `allowed_paths` to the smallest safe repo-relative or repo-qualified scope.
Include shared contracts or integration fixtures only when the slice owns
them. Reject overlapping scopes that could make independent execution unsafe,
or add an explicit dependency between the affected issues.

For every local Markdown issue, derive its exact active path and matching
`done/` destination from the owning tracker subtree. Add the tracker-owning
repository to `affected_repositories`, and add both exact paths to
`allowed_paths`, including in proposal output. The eventual move is therefore
inside the issue's authorized execution scope; do not replace either path with a
wildcard. Verify both paths resolve inside that affected Git repository and a
future App-managed checkout can expose them. If the tracker artifact lives at a
non-Git workspace root or outside every affected repository, withhold normal
App-compatible output unless the explicit non-App contract applies; never
invent a tracker-owning repository.

All issues use the Feature Spec's shared `target_branch_name`. Repository
topology stays a Project Memory fact and is not copied into a selectable issue
field.

### 4. Assign Integration And Domain Closeout

Every multi-repository bundle has exactly one dedicated repo-owned integration
partial whose Feature Dependencies cover every implementation partial.
Generate at least one real integration issue from that partial after the
upstream merge waits; this issue owns the cross-repository proof whether or not
`knowledge_delta` exists. It must own a bounded repository/path change plus the
proof, not a no-op or validation-only task, so it can produce the App's required
PR. If no such integration vehicle exists, withhold the App-compatible bundle
as blocked. Keep its `dependency_ids` local to the integration partial.

All integration issues use the integration partial's distinct branch derived as
`<ordinary_target_branch_name>-integration`; with the default ordinary branch
this is `feature/<feature_slug>-integration`. Never reuse the ordinary partial's
branch in the same owner repository.

If `knowledge_delta` is absent, generate no domain closeout section.

If `knowledge_delta` is present:

1. For a single Feature Spec, reuse or append the closeout owner. Temporarily
   remove that owner and its outgoing `dependency_ids`, derive the nodes with no
   dependents in the remaining intra-Spec graph, and require the owner's final
   `dependency_ids` to include every such node. Reject any graph in which
   another issue depends on the owner. Reuse a candidate only when it can remain
   topologically last after these dependencies; otherwise append a new owner.
2. For a multi-repository bundle, accept the delta as phase data only while
   generating the dedicated integration partial's issues. Require that
   partial's Feature Dependencies to cover every implementation partial and
   therefore wait for all upstream merges. Reject delta assignment to the
   coordination parent or an ordinary implementation partial. Within the
   integration partial, reuse or append the closeout owner and apply the same
   owner-excluded terminal algorithm only to that partial. Reject a dependent
   of the owner and never copy sibling-partial issue IDs. Reuse is valid only
   when the owner can remain topologically last inside that partial; otherwise
   append a new owner.
3. Copy the exact decisions, portable targets, and evidence into that final
   issue's `## Domain Knowledge Closeout` section.
4. Before hardening, require every target repository in that payload to appear
   in the final issue's `affected_repositories` and every normalized target path
   to equal or descend from one of that issue's `allowed_paths`. Add a missing
   repository or path only when it is already inside the accepted Feature Spec
   scope; otherwise withhold the issue as blocked. Never rely on Project Memory
   to write outside the issue's execution scope.
5. Require `$project-memory domain-memory` with
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

After repairs, rerun step 4's owner-excluded terminal derivation when
`knowledge_delta` is present, using the repaired remaining graph and replacing
the closeout owner's `dependency_ids`. Then rerun verticality, overlap,
dependency, acyclicity, integration, and closeout validation. Topologically
assign or renumber final generated IDs so the closeout owner is last and every
`dependency_ids` entry points to a strictly earlier generated ID. Freeze those
IDs for rendering and publication; never retain a reused ID that would depend
on the same or a later ID.

### 6. Harden Every Retained Issue

After structural compression and graph ownership have stabilized, invoke
`$plan-harder` at least once for each final retained issue with
`planning_mode=issue-hardening` and `output_surface=caller`. Merge the returned
brief into the issue template:

- implementation approach into `## Implementation Plan`;
- acceptance details into `## Acceptance Criteria`;
- commands and fallbacks into `## Validation`;
- material dependency reasons into `## Context` or implementation prose,
  without repeating dependency IDs;
- edge cases and constraints into the owning requirements or context section.

Do not paste the hardening brief wholesale or create duplicate top-level
sections. Preserve exactly one standard hardening provenance line for the final
stable pass.

Run final verticality, scope-overlap, dependency, validation, and readiness
gates. If hardening exposes a graph-level defect, discard affected results,
return to step 5, restabilize the graph and IDs, and re-harden every materially
changed issue. For an issue-local repair, run another hardening pass on that
issue before output. Supersede earlier briefs and persist only final stable
results; pass count is derived work, not an option or artifact field.

### 7. Render The Execution Contract

Use `references/issue-body-template.md`. Every issue has exactly one
`## Execution Contract` table containing:

- `source_spec_ref`;
- `feature_slug`;
- `affected_repositories`;
- `allowed_paths`;
- `target_branch_name`;
- `dependency_ids`.

For an explicit non-App bundle, append a `non_app_delivery_target` row to that
same table and report that the complete bundle is App-incompatible. Do not add
`explicit_instruction_ref`, permission, review, PR-count, completion-method,
scheduling-mode, or worker configuration fields. The instruction ref remains
exactly once in the owning Feature Spec.

Dependency reasons belong in Context or implementation prose and must not
repeat the ID list. Reverse edges are a derived view only. The issue body may
include cross-repository notes, integration gates, and domain closeout data in
their dedicated sections; they are not extra knobs.

### 8. Validate Readiness

An applied issue may receive `ready-for-agent` only when:

- its source ref is durable;
- goal, requirements, acceptance criteria, and validation are complete;
- the Execution Contract contains every required field exactly once;
- affected repositories and allowed paths are unambiguous;
- a local issue includes its tracker-owning repository plus its exact active and
  derived `done/` paths;
- dependency IDs resolve, point only to strictly earlier generated IDs, and the
  graph is acyclic;
- named integration gates exist where needed;
- there are no open human decisions or placeholder questions;
- the structural graph-compression gate passed before hardening;
- the domain closeout owner is unique when required;
- every domain-closeout target surface is contained by that final issue's
  `affected_repositories` and `allowed_paths`;
- non-App compatibility is represented consistently across the full bundle.

A proposed issue may report `ready-for-agent` only as its intended future
mapping after the same content gates pass. Never emit or persist that workflow
state in a proposed body, label, or queue. Withhold failed issues and return
their blockers; never downgrade them into a partially agent-ready artifact.

### 9. Apply Or Propose

Order output topologically, with the final integration issue last for a
multi-repository bundle and its domain closeout attached only when a delta
exists.

- `write_mode=apply`, GitHub: publish each issue through
  `$gitstack:github-issues`. Translate each write to GitStack-owned
  `mutation_mode=apply`, its exact target, and one canonical `issue_operation`;
  apply the mapped task type and agent-ready state, attach it as a sub-issue of
  the Feature Spec when supported, verify every mutation, and retain the hosted
  ref separately from its generated ID.
- `write_mode=apply`, local: write
  `planning/features/<feature-slug>/issues/<NN>-<slug>.md` or the configured
  workspace equivalent. Issues owned by a dedicated integration partial use
  `planning/features/<feature-slug>/integration/issues/<NN>-<slug>.md` or the
  configured equivalent. Insert canonical `issue_type: task` and
  `workflow_state: ready-for-agent` header lines. Preserve generated IDs in
  filenames and dependency data. Render completion into the matching subtree:
  ordinary issues move to `planning/features/<feature-slug>/issues/done/`,
  while integration issues move to
  `planning/features/<feature-slug>/integration/issues/done/`. Before output,
  include the tracker-owning repository and both exact source and destination
  paths in each issue's Execution Contract.
- `write_mode=propose`: write nothing. Return every body, intended path or
  repository, mapped metadata, and the topological publication order. Use
  deterministic `proposed-issue:<feature_slug>/<NN>` refs, or
  `proposed-issue:<project_slug>/<feature_slug>/<repository_slug>/<NN>` for an
  issue owned by a multi-repository implementation partial. An issue owned by
  the dedicated integration partial uses
  `proposed-issue:<project_slug>/<feature_slug>/<repository_slug>/integration/<NN>`.
  State that neither source nor issues are executable until applied, and keep
  the intended workflow state out of the proposed bodies.

`write_mode=propose` never invokes GitStack. GitStack does not interpret Plan
Feature's tracker or write policy.

In a multi-repository workspace, publish each issue through its owning
repository's configured tracker. Preserve source links to sibling partial
Feature Specs and cross-repository integration gates. Do not create a separate
scheduling artifact; the issue graph is authoritative.

Use transient body transport outside repositories for hosted writes and remove
it after verified mutation. Plan Feature owns only the planning-artifact writes
performed in this phase.

### 10. Report

Return:

- Feature Spec ref and `mode` / `write_mode`;
- candidate and final issue counts, generated IDs, actual or proposed refs, and
  publication order;
- affected repositories and tracker route for each issue;
- dependency graph, topological order, and acyclicity proof;
- verticality, overlap, and compression repairs, retained-slice reasons,
  removed artificial dependencies, and avoided initial hardening calls;
- mapped issue type/state applied or proposed;
- confirmation that every issue has one valid Execution Contract;
- domain closeout issue and deferred capture result when required;
- withheld issues and blockers;
- explicit App incompatibility when a non-App target is present.

When `knowledge_delta` is present, report `capture_outcome=deferred` and the
final issue ref. Otherwise report `capture_outcome=no-durable-change`. This is
a derived report result, not persisted artifact metadata. Never report
planning-time capture.
