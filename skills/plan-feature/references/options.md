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
  selectable field or value not listed below. Do not translate retired fields,
  aliases, or prose values.
- Keep facts, paths, slugs, refs, dependency IDs, and evidence as data rather
  than options.

## Run Registry

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `mode` | `full-flow`, `spec-only`, `issues-from-existing-spec` | `full-flow` for new intent | Select the planning phases to run. |
| `write_mode` | `apply`, `propose` | `apply` for an explicit Plan Feature request to create durable planning artifacts | `apply` writes through the configured tracker; `propose` performs no writes. |

Resolve both fields once before phase work:

- Use `spec-only` only when the user explicitly stops after the Feature Spec.
- A nonempty `knowledge_delta` has no durable owner in `spec-only`. Under either
  write mode, return only a blocked non-durable preview plus the exact delta and
  withhold all tracker/file publication. Do not silently change `write_mode` or
  add a marker to the Feature Spec; durable publication requires a later
  explicit `full-flow` run that can persist the payload on its final issue.
- Use `issues-from-existing-spec` only when a complete canonical durable Feature
  Spec already exists and can be consumed unchanged. A proposed or chat-only
  body is not durable. Any required schema or content change blocks issue
  generation until a separate explicitly authorized Feature Spec update lands.
- Any request that forbids writes, asks for a dry run, or asks to inspect the
  result before publication resolves to `write_mode=propose`.
- An explicit Plan Feature request to create or plan durable artifacts defaults
  to `write_mode=apply` through the configured tracker. This is Plan Feature's
  invocation contract; Project Memory resolves its own write authority
  independently.
- `write_mode=propose` returns proposed bodies, target locations, metadata,
  and publication order. Never return executable publication commands.
- Withhold incomplete Feature Specs and implementation issues from both
  publication and proposed output intended for later agent-ready application.
  Return blockers instead.

## Project Memory Facts

Read these facts from their canonical Project Memory files. They are not run
options and must not appear in the Run Registry:

- `tracker_backend`: `github` or `local`, from
  `project-memory/config/issue-tracker.md`;
- `repository_layout`: `single-repository`, `monorepo`, or
  `multi-repository-workspace`, from
  `project-memory/config/project-layout.md`;
- issue type and workflow-state mappings from
  `project-memory/config/triage-labels.md`.

If a required fact is absent, stale, or contradictory, route to the matching
Project Memory slice before planning. Do not turn a missing fact into another
Plan Feature option.

## Execution Data

Carry only the data needed to connect planning artifacts:

- planning identity: `feature_slug` and any applicable `product_slug`,
  `project_slug`, `workspace_path`, or `context_file`;
- source identity: a durable `source_spec_ref`, or in `write_mode=propose`
  `proposed-spec:<feature_slug>` for a single Feature Spec,
  `proposed-spec:<project_slug>/<feature_slug>` for a multi-repository parent,
  and `proposed-spec:<project_slug>/<feature_slug>/<repository_slug>` for each
  repo-scoped partial;
- applied multi-repository source identity: use `owner/repository#<number>` or a
  canonical hosted URL for every GitHub partial, and
  `<repository_slug>/<repo-relative-spec-path>` for every local partial. Use the
  same globally unambiguous refs in sibling maps and Feature Dependencies;
- issue scope: `affected_repositories`, `allowed_paths`, and one
  `target_branch_name` shared by all affected repositories inside the current
  Feature Spec. For a local
  Markdown issue, the affected set includes the tracker-owning repository and
  the allowed paths include both its exact active path and exact derived
  `done/` destination. Both must resolve inside that affected Git repository and
  its future App-managed checkout; otherwise normal App-compatible output is
  withheld unless the explicit non-App contract applies;
- issue graph: `dependency_ids` containing generated issue IDs inside the
  current Feature Spec;
- proposal identity: `proposed-issue:<feature_slug>/<NN>` for a single Feature
  Spec, or
  `proposed-issue:<project_slug>/<feature_slug>/<repository_slug>/<NN>` for an
  issue owned by a multi-repository partial. A parent/global Feature Spec is a
  coordination artifact and does not own generated implementation issues;
- multi-repository integration identity: every multi-repository bundle has
  exactly one evidence-selected integration owner repository that receives
  a dedicated integration partial with proposed source ref
  `proposed-spec:<project_slug>/<feature_slug>/<repository_slug>/integration`
  and proposed issue refs
  `proposed-issue:<project_slug>/<feature_slug>/<repository_slug>/integration/<NN>`.
  This identity is derived data, not a new run option, and exists independently
  of `knowledge_delta`;
- optional workspace links between a parent Feature Spec and repo-scoped
  partial Feature Specs;
- an optional `knowledge_delta` object with `decisions`, `target_surfaces`, and
  `evidence` lists;
- a separate `planning_blockers` list for unresolved planning questions.

Absence of `knowledge_delta` means planning introduced no durable project
knowledge. When present, all three lists must be explicit and the delta is
carried as run/phase data and persisted only on exactly one final
implementation/integration issue. It never appears in a Feature Spec body.
Normalize each target surface to one canonical affected repository and one
portable repo-relative path after rejecting absolute paths and `..` traversal.
The final issue must include that repository in `affected_repositories`, and
its `allowed_paths` must contain the exact target or an explicit ancestor scope
that contains it. In `issues-from-existing-spec`, all targets must already be
contained by the unchanged Feature Spec repository/path scope; reject
out-of-scope invocation data instead of widening the source or generated issue.
`capture_outcome` is derived only in the completion report: `deferred` when the
delta is present and `no-durable-change` when it is absent. It is never input or
persisted Feature Spec metadata.

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
`git check-ref-format --branch`. Paths must be
repo-relative or explicitly repo-qualified; never publish machine-local absolute
paths.

## Issue Execution Contract

Every generated issue has exactly one `## Execution Contract` table with
these fields:

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

Normal artifacts are App-compatible and rely on the App orchestrator's fixed
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

Every newly produced Feature Spec contains a `## Feature Dependencies` table
with exactly these columns:

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
