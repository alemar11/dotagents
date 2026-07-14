# Plan Feature Option Contract

Load this reference before resolving a Plan Feature run. It is the canonical
registry for selectable planning behavior and the delivery projection consumed
by Codex Orchestrator.

## Syntax And Hard Cut

- Field names use snake_case; enum values use lower-kebab-case.
- Counts, paths, slugs, refs, fingerprints, and evidence remain separate data.
- User wording and tracker prose are selection evidence only. Persist only the
  canonical field/value plus evidence.
- Retired planning and delivery fields are invalid input and are never
  translated. Active Feature Specs and generated issues must already use this
  registry before the runtime consumes them.

## Run Registry

Resolve these fields before the first phase handoff.

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `mode` | `full-flow`, `spec-only`, `issues-from-existing-spec` | `full-flow` for new intent | A direct existing Feature Spec split resolves to `issues-from-existing-spec`; an explicit stop after the Feature Spec resolves to `spec-only`. |
| `execution_profile` | `lean-spec`, `lean-issues`, `standard` | `standard` | Internal optimization only; it cannot weaken gates. |
| `tracker_backend` | `github`, `local` | From project memory | Planning-artifact write authority for the current artifact set. |
| `effective_target` | `configured-tracker`, `local-dry-run`, `draft-publish-commands` | `configured-tracker` | Derived from tracker routing plus the current-run mutation option. |
| `no_mutation_override` | `none`, `dry-run`, `temp`, `rehearsal`, `validation`, `disabled-writes`, `draft-output` | `none` | Changes planning-artifact output, never implementation delivery. |
| `no_mutation_output` | `not-applicable`, `local-artifacts`, `publish-commands` | Derived | Non-mutating output shape. |
| `local_mirror` | `not-requested`, `requested` | `not-requested` | Applies only to hosted planning artifacts. |
| `repository_layout` | `single-repository`, `monorepo`, `multi-repository-workspace` | From project memory or safe repository evidence | Planning graph layout, not execution order. |
| `workspace_context` | `multi-repository-workspace`, `not-applicable` | Derived | Selects workspace-only partial Feature Spec and child-source behavior. |
| `change_delivery_target` | `local-commit-created-without-pushing`, `changes-pushed-to-target-branch-without-pull-request`, `validated-draft-pull-request-published`, `pull-request-ready-for-merge-but-not-merged` | `pull-request-ready-for-merge-but-not-merged` | Exact implementation stopping point. Merge is never implied. |
| `change_delivery_permission` | `not-granted`, `granted-for-selected-target` | `granted-for-selected-target` for the default Feature Spec PR target | Permission transferred by the Feature Spec. Non-default targets require exact evidence. |
| `issue_update_permission` | `no-issue-changes`, `pull-request-closing-keyword-only`, `direct-issue-updates-explicitly-authorized` | Derived from tracker and target | Final-commit closure remains independently authorized. |
| `codex_review_requirement` | `required-on-current-pull-request-head`, `explicitly-skipped-by-authorized-user`, `not-needed-for-selected-delivery-target` | Derived from target | The explicit skip requires exact scoped evidence. |
| `pull_request_count_strategy` | `one-pull-request-total`, `one-pull-request-per-repository`, `no-pull-request` | Derived from target and affected repositories | Every involved repository uses the same target branch for per-repository PR delivery. |
| `partial_output` | `withhold`, `allow-non-agent-ready` | `withhold` | The non-default value never permits `ready-for-agent`. |

`local_mirror_path` is validated repo-relative data when a mirror is requested;
otherwise use `not-applicable`.

`target_branch_name` is required data for every delivery target. PR targets
default to `feature/<feature_slug>` unless a current source contract or repo
policy provides another valid branch. Commit or push targets require exact
authorized-user evidence naming the branch.

`child_repository_layout` is data for repo-scoped workspace partial Feature
Specs. It uses the same values as `repository_layout` and is `not-applicable`
outside repo-scoped workspace partials.

Resolve `workspace_context` before phase handoff. Precedence is: an explicit
current Feature Spec value; `repository_layout=multi-repository-workspace`;
linked parent/global or sibling-partial evidence; safe project-memory evidence;
otherwise `not-applicable`. A contradiction stops as `needs-owner`.

## Per-Issue Registry

Resolve these fields after the issue graph exists and before emitting an issue
or its `## Orchestrator Handoff`.

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `delivery_decision_origin` | `inherited-from-feature-spec`, `overridden-by-implementation-issue` | `inherited-from-feature-spec` | Override evidence remains separate. |
| `change_delivery_target` | Same four run-level targets | Inherited | Records the issue-effective stopping point. |
| `change_delivery_permission` | `not-granted`, `granted-for-selected-target` | Inherited | Must be re-resolved atomically with any issue override. |
| `issue_repository_layout` | `single-repository`, `monorepo`, `multi-repository-workspace` | From the issue target repository | Preserves heterogeneous child layouts. |
| `issue_update_permission` | Same run-level values | Inherited | Re-resolve with tracker, target, and completion method. |
| `codex_review_requirement` | Same run-level values | Inherited or derived from an override | Never infer a skip from prose. |
| `pull_request_count_strategy` | Same run-level values | Inherited | Re-resolve with any target override. |
| `parallelization` | `independent`, `depends-on`, `blocks`, `root-integrated` | Derived | Dependency ids remain data. |
| `issue_completion_method` | `feature-pull-request-closing-keyword`, `repository-pull-request-closing-keyword`, `final-commit-closing-keyword`, `move-local-issue-to-done-after-proof`, `no-issue-completion` | Derived from tracker and target | Names the terminal lifecycle action. |
| `domain_closeout` | `not-applicable`, `implementation-closeout` | `not-applicable` | Decisions and targets remain data. |

Every issue records its effective delivery tuple even when it is inherited:
`delivery_decision_origin`, `change_delivery_target`,
`change_delivery_permission`, `issue_update_permission`,
`codex_review_requirement`, `pull_request_count_strategy`,
`issue_completion_method`, and `target_branch_name`.

## Effective Planning-Artifact Target

| `tracker_backend` | `no_mutation_override` | `no_mutation_output` | `effective_target` |
| --- | --- | --- | --- |
| `github` | `none` | `not-applicable` | `configured-tracker` |
| `local` | `none` | `not-applicable` | `configured-tracker` |
| `github` | Any non-`none` value | `publish-commands` | `draft-publish-commands` |
| `github` | Any non-`none` value | `local-artifacts` | `local-dry-run` |
| `local` | Any non-`none` value | `local-artifacts` | `local-dry-run` |

Reject every other combination. Downstream phases branch only on
`effective_target`; they never reinterpret the mutation reason.

## Cross-Field Validation

- `local_mirror=requested` requires GitHub configured-tracker output and a safe
  `local_mirror_path`; otherwise the path is `not-applicable`.
- `local-commit-created-without-pushing` and
  `changes-pushed-to-target-branch-without-pull-request` require
  `pull_request_count_strategy=no-pull-request` and
  `codex_review_requirement=not-needed-for-selected-delivery-target`.
- PR targets require `one-pull-request-total` for one affected repository or
  `one-pull-request-per-repository` for multiple affected repositories. The
  latter uses the same `target_branch_name` in every involved repository.
- `validated-draft-pull-request-published` requires
  `codex_review_requirement=not-needed-for-selected-delivery-target`.
- `pull-request-ready-for-merge-but-not-merged` requires
  `required-on-current-pull-request-head` or an exact scoped explicit skip.
- Every target requires `change_delivery_permission=granted-for-selected-target`
  before an issue may be `ready-for-agent`.
- `tracker_backend=local` uses
  `issue_update_permission=no-issue-changes` and
  `issue_completion_method=move-local-issue-to-done-after-proof`.
- GitHub PR targets use
  `issue_update_permission=pull-request-closing-keyword-only` and either
  `feature-pull-request-closing-keyword` or
  `repository-pull-request-closing-keyword` according to PR count.
- GitHub `changes-pushed-to-target-branch-without-pull-request` requires
  `issue_update_permission=direct-issue-updates-explicitly-authorized` and
  `issue_completion_method=final-commit-closing-keyword`. The issue permission
  requires separate evidence; delivery permission alone is insufficient.
- `local-commit-created-without-pushing` cannot close a hosted issue. Use
  `no-issue-completion` for GitHub or the local done move for local trackers.
- Every `target_branch_name` must pass
  `git check-ref-format --branch <target_branch_name>`.
- `repository_layout=multi-repository-workspace` publishes parent/global and
  child repo artifacts in separate option-resolution runs. Repo-scoped child
  issue graphs must use one tracker backend, while child layouts remain
  explicit through `child_repository_layout` and `issue_repository_layout`.
- An issue target override atomically re-resolves permission, issue updates,
  review requirement, PR count, completion method, and branch. Reject any tuple
  retaining incompatible feature-level values.
- `parallelization=independent` requires no dependency or blocked ids;
  `depends-on` requires dependency ids only; `blocks` requires blocked ids only;
  `root-integrated` may carry either when justified. The graph remains acyclic.
- `repository_integration_method` and `pr_closeout` are retired. Derive their
  former behavior from `change_delivery_target` and
  `pull_request_count_strategy`.

## Resolution Record

Record one six-column row per run field plus `local_mirror_path` and
`target_branch_name` before the first phase handoff. Record one row per
per-issue field plus issue-effective `target_branch_name` before emitting each
issue.

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `run:<field>` | `run` | `<run field>` | `<canonical value>` | `default`, `tracker-config`, `project-layout-config`, `source-spec`, `authorized-user-instruction`, or `runtime-derived` | `<ref or none>` |
| `issue:<NN>:<field>` | `issue:<NN>` | `<issue field>` | `<canonical value>` | `source-spec`, `authorized-user-instruction`, or `runtime-derived` | `<ref>` |

Keep `row_id` unique. Encode literal `|` in evidence as `%7C`. Every non-default
source requires non-empty evidence. Permission-bearing values require
`permission-source-ref`, exact `scope-ref`, and `target-ref`; branch mutations
also require `target-branch=<target_branch_name>`.

The default Feature Spec target and its delivery permission may use
`source=default`; its delivery and PR-closing-keyword permission rows use
`permission-source-ref=feature-spec-default:<feature_slug>` plus exact scope,
target, and branch tokens. Inherited issue rows preserve those tokens, change
only `scope-ref`, and add `permission-transfer-ref=run`. Every commit-only,
push-without-PR, draft-PR, explicit review skip, direct issue update, or issue
override requires `authorized-user-instruction` or a current source contract
that preserves `permission-source-ref=authorized-user:<instruction-ref>` and
equivalent scoped evidence. Runtime-derived values never grant permission.

## Fingerprints

Canonicalize all rows with columns `row_id`, `scope_id`, `field`, `value`,
`source`, and `evidence`; trim cells, encode `|`, sort bytewise by `row_id`,
serialize tab-separated rows with trailing newlines, and SHA-256 hash the UTF-8
bytes. Emit `option_rows_fingerprint: sha256:<lowercase-hex>`.

Each issue repeats this process for its own per-issue rows and emits
`issue_option_rows_fingerprint`. A missing row, duplicate id, invalid value, or
fingerprint mismatch is blocking; never reinterpret prose to repair it.

## Canonical Input Requirement

Feature Specs and generated issues must already use this registry. Reject
noncanonical artifacts instead of translating or rewriting them.
