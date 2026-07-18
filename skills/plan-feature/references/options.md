# Plan Feature Option Contract

Load this reference before the first Plan Feature phase. It is the sole owner
of default-path selectable Plan Feature behavior. The one conditional non-App
extension remains owned by `non-app-delivery.md` and is valid only after its
current-request-or-durable-source predicate is satisfied.

## Syntax And Hard Cut

- Field names use snake_case and enum values use lower-kebab-case.
- User wording is selection evidence, never an alternative value.
- Before rejecting unknown fields, inspect the current request and any durable
  source Feature Spec for the non-App predicate. Load `non-app-delivery.md` when
  the current user explicitly selects a non-App stopping point, or when a
  canonical source already carries exactly one `non_app_delivery_target` and
  exactly one resolvable `explicit_instruction_ref`. Validate that conditional
  field together with the Run Registry. Otherwise reject it and every other
  selectable field or value not listed below.
- Reject retired fields, values, partial-flow requests, and aliases instead of
  translating them. Plan Feature has one convergent planning pipeline.
- Keep facts, paths, slugs, refs, dependency IDs, evidence, and derived route or
  result state as data rather than options.

## Run Registry

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `write_mode` | `apply`, `propose` | `apply` for an explicit Plan Feature request to create durable planning artifacts | `apply` writes through the configured tracker; `propose` performs no writes. |

Resolve `write_mode` once before phase work:

- Any request that forbids writes, asks for a dry run, or asks to inspect the
  result before publication resolves to `write_mode=propose`.
- An explicit Plan Feature request to create or plan durable artifacts defaults
  to `write_mode=apply` through the configured tracker. This is Plan Feature's
  invocation contract; Project Memory resolves its own write authority
  independently.
- `write_mode=propose` returns the complete proposed Feature Spec bundle:
  bodies, target locations, mapped metadata, relationships, and publication
  order. It writes nothing and never returns executable publication commands.
- Withhold incomplete Feature Specs and implementation issues in either write
  mode. Never return a standalone Feature Spec as a successful Plan Feature
  result or mark a partial bundle agent-ready. Uniquely marked hosted
  publication-transaction staging issues are temporary non-executable transport,
  not Feature Specs or successful output.

## Derived Source Route

Freeze the route from intake evidence before any Feature Spec is drafted or
published. Resolve enough accepted planning identity to locate the canonical
target, then inspect both any supplied ref and that exact target. One canonical
final durable candidate selects the existing-source route unless exact recovery
evidence binds it to an incomplete multi-repository publication transaction.
That recognized transaction selects a continuation of the new-source route;
otherwise no durable candidate selects that route. Multiple, conflicting,
foreign, or ambiguous candidates block. Do not broadly scan unrelated planning
artifacts. The route is derived execution data, not a selectable field:

- `source_route=new-source`: no canonical durable `source_spec_ref` was supplied
  or discovered at intake, or the invocation exactly resumes one recognized
  multi-repository publication transaction. Draft, publish, resume, or propose
  the required Feature Spec set, then produce its complete implementation issue
  graph, metadata, and relationships.
- `source_route=existing-source`: exactly one canonical durable
  `source_spec_ref` was supplied or discovered at intake. Validate and preserve
  the source body and ref unchanged, skip Feature Spec drafting and publication,
  then converge its implementation issues, metadata, and relationships. When
  that source is any member of a multi-repository bundle, traverse its canonical
  parent, child, sibling, and Feature Dependency links and validate the complete
  connected coordination, implementation, and integration Spec set; the parent
  itself owns no implementation issues.

A `proposed-spec:` ref never selects the existing-source route. A durable ref
created later in a new-source run does not change the frozen route. A chat body,
temporary file, or unresolved shorthand is not a durable existing source.
Exact partial-publication artifacts from one recognized multi-repository
transaction are new-source continuation evidence, not canonical durable Specs.
Hosted staging roles carry unique transaction markers; local final roles require
the exact continuation handoff and predeclared final-body match. Neither selects
the existing-source route.

On the existing-source route, any missing section, blocking question,
nonportable evidence, schema repair, persisted knowledge payload, or content
correction blocks the run until a separately authorized Feature Spec update
lands. A missing or ambiguous required linked partial also blocks. Plan Feature
must not rewrite or republish any immutable source.

## Complete-Bundle Convergence

The desired terminal state is one complete, internally consistent bundle:

- every required Feature Spec and globally unambiguous source ref;
- a nonempty final hardened issue graph for every implementation-eligible
  Feature Spec; coordination-only parents own no issues;
- mapped issue type and workflow state;
- parent/sub-issue, sibling, dependency, and cross-repository relationships;
- one valid Execution Contract per issue; and
- any required final integration and domain-closeout owner.

Before graph synthesis, enumerate the current durable bundle and seed the
candidate graph with every contract-equivalent issue as a fixed ID/slice. Derive
covered obligations and synthesize only uncovered scope. Then compare the
stabilized complete desired state with that durable snapshot:

- retain contract-equivalent existing issues plus exact identities and
  relationships;
- create or propose only missing artifacts;
- repair only missing mapped tracker metadata or a supported parent/sub-issue
  attachment when bodies and identities already match;
- return a verified no-op when the applied bundle is already complete; and
- stop on duplicate, extra, stale, or conflicting implementation artifacts.

Never renumber or regenerate a retained issue. Immediately before returning a
proposal or no-op, or performing the first mutation, re-read the owning Feature
Spec, explicit Project Memory transports/values, and complete issue, metadata,
and relationship state. Recompute or block on drift and verify exact target
absence again before every create.

Dependency data, sibling maps, Feature Dependencies, and other source-body
relationships are body contract, not repairable tracker relationships. On the
existing-source route a missing source-body relationship requires a separately
authorized source update. Never rewrite a conflicting issue, silently replace
it, invent a parallel ID, or treat an incomplete bundle as a successful
terminal result. Proposed output may describe a complete target bundle, but it
remains non-durable and non-executable until applied and verified.

## Project Memory Facts

Read these facts from their canonical Project Memory files. They are not run
options and must not appear in the Run Registry:

- `tracker_backend`: `github` or `local`, from
  `project-memory/config/issue-tracker.md`;
- `repository_layout`: `single-repository`, `monorepo`, or
  `multi-repository-workspace`, from
  `project-memory/config/project-layout.md`;
- issue type and workflow-state mappings, including each row's explicit
  transport and exact tracker value, from
  `project-memory/config/triage-labels.md`; reject missing, unknown, or backend-
  incompatible transports rather than inferring them;
- the `artifact_marker=idea` mapping from that same file only when
  `source_idea_refs` are supplied or the user explicitly requests captured-Idea
  discovery.

If a required fact is absent, stale, or contradictory, route to the matching
Project Memory slice before planning. Do not turn a missing fact into another
Plan Feature option. A missing Idea marker mapping blocks only Idea capture,
discovery, or consumption; it does not invalidate an unrelated Plan Feature
run.

## Execution Data

Carry only the data needed to connect planning artifacts:

- planning identity: `feature_slug` and any applicable `product_slug`,
  `project_slug`, `workspace_path`, or `context_files`; include every applicable
  available context used for planning: the current or coordination root,
  affected child-repository roots, and scoped contexts matched by affected
  paths. Omit roots and routes with no context file;
- optional explicit Idea-discovery intent: when exact refs are absent and the
  source route is new-source, a direct request to find, list, or plan from
  captured Ideas authorizes read-only discovery through `idea-discovery.md`.
  This is invocation evidence, not a field in the Run Registry. Only explicit
  user selection produces `source_idea_refs`;
- optional `source_idea_refs`: explicitly selected durable GitHub or local Idea
  refs accepted as planning input only on the new-source route when there is no
  durable `source_spec_ref`. Multiple refs must describe one bounded feature.
  Reject every `proposed-idea:` ref;
- derived `bound_source_idea_refs`: on the existing-source route, the union of
  exact `- Source Idea:` refs already present in the immutable intake Spec and
  every required linked partial. These refs authorize continuation validation
  and lifecycle reconciliation only, never new drafting. If the invocation
  also supplies `source_idea_refs`, require exact set equality with the bound
  set and reject additional, missing, different, proposed, or unbound refs;
- optional prior Idea planning outcomes, transient durable coverage maps, and
  report-only proposal projections. These are source evidence and derived run
  data, never options or Feature Spec fields;
- intake source identity: the optional canonical durable `source_spec_ref` that
  freezes the existing-source route;
- generated source identity: a durable ref published on the new-source apply
  path, or in `write_mode=propose` `proposed-spec:<feature_slug>` for a single
  Feature Spec, `proposed-spec:<project_slug>/<feature_slug>` for a
  multi-repository parent, and
  `proposed-spec:<project_slug>/<feature_slug>/<repository_slug>` for each
  repo-scoped partial;
- applied multi-repository source identity: use `owner/repository#<number>` or a
  canonical hosted URL for every GitHub partial, and
  `<repository-slug>/planning/features/<feature-slug>/SPEC.md` or
  `<repository-slug>/planning/features/<feature-slug>/integration/SPEC.md` for
  every local partial. Use the same globally unambiguous refs in sibling maps
  and Feature Dependencies;
- issue scope: `affected_repositories`, `allowed_paths`, and one
  `target_branch_name` shared inside each Feature Spec. For a local Markdown
  issue, the affected set includes the tracker-owning repository and the
  allowed paths include both its exact active path and exact derived `done/`
  destination. Both must resolve inside that affected Git repository;
- issue graph: `dependency_ids` containing generated issue IDs inside the
  current Feature Spec;
- current durable issue state: existing bodies, generated IDs, hosted or local
  refs, metadata, relationships, and verification evidence used only for exact
  convergence and recovery;
- proposal identity: `proposed-issue:<feature_slug>/<NN>` for a single Feature
  Spec, or
  `proposed-issue:<project_slug>/<feature_slug>/<repository_slug>/<NN>` for an
  issue owned by a multi-repository partial;
- multi-repository integration identity: exactly one evidence-selected owner
  repository receives a dedicated integration partial with proposed source ref
  `proposed-spec:<project_slug>/<feature_slug>/<repository_slug>/integration`
  and proposed issue refs
  `proposed-issue:<project_slug>/<feature_slug>/<repository_slug>/integration/<NN>`;
- optional workspace links between a parent Feature Spec and repo-scoped
  partial Feature Specs;
- optional multi-repository publication-continuation data: one generated transaction
  identity plus the complete predeclared role-to-target map, reconstructable
  parameterized body templates and their hashes, allowed ref slots, staged or
  finalized refs, the optional exact final-only body-metadata slot and value,
  any materialized final-body hashes, selected `source_idea_refs`, verified
  prior outcome refs, and completed plus exact missing operations. It is
  derived recovery data, not a run option or durable Project Memory
  configuration;
- an optional `knowledge_delta` object with `decisions`, `target_surfaces`, and
  `evidence` lists; and
- a separate `planning_blockers` list for unresolved planning questions.

Absence of `knowledge_delta` means planning introduced no durable project
knowledge. When present, all three lists must be explicit and the delta is
carried as run/phase data and persisted only on exactly one final
implementation/integration issue. It never appears in a Feature Spec body.
Normalize each target surface to one canonical affected repository and one
portable repo-relative path after rejecting absolute paths and `..` traversal.
The final issue must include that repository in `affected_repositories`, and
its `allowed_paths` must contain the exact target or an explicit ancestor scope
that contains it. On the existing-source route, all targets must already be
contained by the unchanged Feature Spec repository/path scope; reject
out-of-scope invocation data instead of widening the source or generated issue.
`capture_outcome` is derived only in the completion report: `deferred` when the
delta is present and `no-durable-change` when it is absent. It is never input or
persisted Feature Spec metadata.

Until the final issue carrying a nonempty delta is durable and verified, every
partial-failure result must return a continuation handoff containing the exact
delta, `feature_slug`, all durable or staged Spec refs, and any applicable
multi-repository publication-transaction identity and role map. A retry accepts
a handed-off delta only when every item and continuation identity matches
current tracker state; missing or conflicting continuation data blocks instead
of treating the delta as absent. Once the final owner issue is verified, omit
the recovery copy and use that durable issue as the sole handoff.

Default an ordinary implementation Feature Spec's `target_branch_name` to
`feature/<feature_slug>` unless repository policy or the source provides another
valid branch. For the dedicated integration partial, derive
`<ordinary_target_branch_name>-integration` from that resolved branch. With the
default this yields `feature/<feature_slug>-integration`; it always differs from
the ordinary partial branch in the same owner repository. Branch sharing is per
Feature Spec, not across parent and partial Specs. Across the complete
implementation-eligible bundle, each `(affected_repository,
target_branch_name)` pair has exactly one Feature Spec owner. Reusing the same
branch name in different repositories is valid; reusing it across two Specs in
the same repository is a collision even when paths are disjoint or execution is
serialized. Resolve a new bundle before publication, but stop rather than
rename a branch in an immutable existing source. Validate every branch with
`git check-ref-format --branch`. Paths must be repo-relative or explicitly
repo-qualified; never publish machine-local absolute paths.

## Issue Execution Contract

Every generated issue has exactly one `## Execution Contract` table:

| Field | Required data |
| --- | --- |
| `source_spec_ref` | Durable Feature Spec ref, or proposed ref only in `write_mode=propose`. |
| `feature_slug` | Canonical feature slug. |
| `affected_repositories` | Canonical repo slugs, or `current-repository`; for a local issue this includes its tracker-owning repository. |
| `allowed_paths` | Repo-relative or repo-qualified execution scope; for a local issue this includes its exact active and derived `done/` paths. |
| `target_branch_name` | The valid branch shared within this Feature Spec; the integration partial uses a distinct derived branch. |
| `dependency_ids` | Earlier generated issue IDs, or `none`. |

The section is the single execution projection. Do not duplicate its fields in
a delivery section, handoff section, or option table. Derive reverse dependency
edges by scanning `dependency_ids`; never persist a second reverse-edge list.

Normal artifacts are App-compatible and rely on `$implement-feature`'s fixed
reviewed, CI-clean pull-request-ready flow. Plan Feature does not select or
grant implementation, publication, review, merge, or issue-mutation authority.

In `write_mode=propose`, return the intended mapped issue type and workflow
state as report metadata only. Do not put an applied `workflow_state` line in a
proposed body or imply that a proposed issue has entered an execution queue.

Load `non-app-delivery.md` before structured option validation or drafting when
the current user explicitly requests a non-App stopping point, or when a
canonical durable source Spec already carries exactly one target and exactly
one resolvable `explicit_instruction_ref`. Validate its registry together with
this default-path registry. `explicit_instruction_ref` is evidence data, not an
option or issue field. That reference owns the sole optional extension to the
Execution Contract.

## Feature Dependency Contract

Every newly produced or supplied Feature Spec contains a
`## Feature Dependencies` table with exactly these columns:

| Field | Required data |
| --- | --- |
| `upstream_feature_spec_ref` | Unique durable upstream Feature Spec ref; proposed refs are allowed only in `write_mode=propose`. |
| `dependency_reason` | Non-empty portable explanation of the required upstream result. |

All cross-Feature-Spec edges wait for the upstream implementation to merge and
produce integration proof. Validate refs, uniqueness, self-reference, and the
reachable graph's acyclicity. Keep cross-Spec edges separate from intra-Spec
issue `dependency_ids`.

## Canonical Input Requirement

Existing Feature Specs and generated issues must already use this contract.
Reject incompatible structured input instead of translating or rewriting it.
