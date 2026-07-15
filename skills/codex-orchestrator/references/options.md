# Codex Orchestrator Option Contract

Load this reference during `CLAIM`, before worker, delivery, source, or closeout
decisions. It is the canonical registry for selectable orchestration behavior.
Runtime status, derived actions, paths, refs, ids, fingerprints, and evidence are
not options.

## Syntax And Hard Cut

- Option field names use snake_case and match
  `^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$`.
- Enum values use lower-kebab-case and match
  `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
- Authorized-user wording and source prose are selection evidence only.
  Normalize them once into the canonical field/value plus evidence; downstream
  logic never branches on the original phrase.
- Emit only the fields and values in this registry. Unknown or retired
  orchestration fields and values are invalid input and are never translated.

## Primary Human Choices

The delivery target is the normal per-workstream user-facing choice. Visible
Codex App task consent is the independent session permission below.

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `change_delivery_target` | `validated-changes-left-uncommitted`, `local-commit-created-without-pushing`, `changes-pushed-to-target-branch-without-pull-request`, `validated-draft-pull-request-published`, `pull-request-ready-for-merge-but-not-merged` | `validated-changes-left-uncommitted` for ad hoc work; `pull-request-ready-for-merge-but-not-merged` for Feature Spec-backed work | The observable stopping point for the workstream. Merge is never implied. |

Worker surface, count, per-wave parallelism, and serial or parallel sequencing
are derived runtime decisions, not options or user-provided data. When visible
threads are not enabled, the orchestrator chooses them from the work graph,
ownership boundaries, safety, tool availability, and live runtime capacity.
When visible threads are enabled, the visible-thread count is exactly the
number of implementation-eligible Feature Specs in the dispatched waves; only their start order and
serial or parallel scheduling remain derived. The root and every spawned Codex
thread may create internal background subagents within their assigned scope.

## Session Permissions And Context

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `visible_app_task_permission` | `not-requested`, `granted-by-authorized-user`, `denied-by-authorized-user` | `not-requested` | Explicit consent for visible Codex App tasks. The granted value selects mandatory one-thread-per-Feature-Spec execution. |
| `unmanaged_git_worktree_fallback_permission` | `not-granted`, `granted-by-authorized-user` | `not-granted` | Permission to use an unmanaged Git worktree when the App cannot create the required managed worktree. |
| `existing_orchestrator_session_takeover_policy` | `ask-authorized-user-before-takeover`, `take-over-only-if-existing-ledger-is-stale` | `ask-authorized-user-before-takeover` | Recovery policy when another orchestrator session claims overlapping scope. |
| `repository_layout` | `single-repository`, `monorepo`, `multi-repository-workspace` | From project memory or safe repository evidence | Durable repository layout. This is derived context, not an execution-order preference. |

`visible_app_task_permission=granted-by-authorized-user` both authorizes the
surface and requires its use for Feature Spec implementation. Map every
implementation-eligible Feature Spec to exactly one active visible thread,
group all generated issues and affected repositories for that Spec into that
thread, and title it with the exact Feature Spec title. The thread owns the
entire selected delivery target through merge-ready; the root does not perform
implementation, integration, validation, Codex-review request or polling,
feedback fixes, CI repair, PR mutation, or ready transition for that Spec.
Background Codex subagents are already authorized by orchestrator invocation
and require no separate session option.

Here, `implementation-eligible` means a Feature Spec whose start/dependency
gates passed and whose implementation is selected for dispatch in the current
wave. Queued, dependency-blocked, or capacity-deferred Specs receive their one
thread when their dispatch wave starts; serial scheduling does not require
creating every future thread in advance.

## Per-Workstream Permissions And Delivery

Resolve these fields independently for every stable workstream ID. Authority
or evidence from one workstream never applies to another by inheritance.

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `tracked_work_item_update_permission` | `read-only`, `propose-updates-only`, `apply-updates` | `read-only` | Whether the registered source item may be changed. |
| `change_delivery_permission` | `not-required-for-uncommitted-changes`, `not-granted`, `granted-for-selected-target` | Derived from the selected target | Permission to perform the Git or GitHub mutations required by `change_delivery_target`. |
| `issue_update_permission` | `no-issue-changes`, `pull-request-closing-keyword-only`, `direct-issue-updates-explicitly-authorized` | `no-issue-changes` | Which issue lifecycle mutations are permitted. |
| `pull_request_merge_permission` | `not-granted`, `granted-for-named-pull-request` | `not-granted` | Permission to merge the named pull request or pull-request set. |
| `pull_request_merge_confirmation` | `ask-authorized-user-after-checks`, `merge-automatically-after-checks` | `ask-authorized-user-after-checks` | Whether another confirmation is required after all merge gates pass. |
| `starting_checkout_branch_handling` | `keep-current-branch-checked-out`, `branch-switch-authorized`, `not-applicable` | `keep-current-branch-checked-out` | Whether the caller checkout may switch branches. |
| `scheduled_automation_change_permission` | `not-granted`, `granted-by-authorized-user` | `not-granted` | Permission to create or update the exact scheduled automation named by the row. |
| `temporary_source_execution_permission` | `not-granted`, `granted-by-authorized-user` | `not-granted` | Permission to dispatch implementation from a non-durable `draft-spec:<...>` source. It never grants delivery or issue changes. |
| `completion_evidence_policy` | `require-live-system-evidence`, `allow-simulated-evidence-by-authorized-user-exception` | `require-live-system-evidence` | Whether explicitly accepted simulated proof may replace unavailable live proof. |
| `delivery_decision_origin` | `safe-default-for-ad-hoc-work`, `inherited-from-feature-spec`, `overridden-by-implementation-issue`, `specified-by-authorized-user` | `safe-default-for-ad-hoc-work` for ad hoc work | Where the selected delivery target came from. Evidence remains separate data. |
| `workstream_repository_layout` | `single-repository`, `monorepo`, `multi-repository-workspace` | From the registered issue or session layout | Repository layout for this workstream. |
| `codex_review_requirement` | `required-on-current-pull-request-head`, `explicitly-skipped-by-authorized-user`, `not-needed-for-selected-delivery-target` | Required only for a merge-ready pull request | Whether the current pull-request head requires Codex review. |
| `pull_request_count_strategy` | `one-pull-request-total`, `one-pull-request-per-repository`, `no-pull-request` | Derived from target and repository layout | Number of pull requests used by the workstream. |
| `issue_completion_method` | `feature-pull-request-closing-keyword`, `repository-pull-request-closing-keyword`, `final-commit-closing-keyword`, `move-local-issue-to-done-after-proof`, `no-issue-completion` | Derived from tracker, target, and source contract | How the tracked issue reaches its terminal state. |

The following are required scoped data rather than enum options:

- `feature_spec_ref`: canonical Feature Spec URL/path/ref, or
  `not-applicable` for a non-Feature-Spec workstream.
- `feature_spec_title`: title transport from `ledger-template.md` for the exact
  canonical Feature Spec title, or `not-applicable` with the ref. Decode only
  when setting or comparing a live title.
- `target_branch_name`: exact branch, or `not-applicable` only for
  `validated-changes-left-uncommitted`.
- `target_pull_request_ref`: canonical `<owner>/<repo>#<number>`, `pending` for
  a pull-request target before publication, or `not-applicable` for a non-PR
  target.
- `delivery_permission_source_issue_ref`: exact generated issue that transferred
  delivery permission, or `not-applicable`.
- `issue_update_permission_source_issue_ref`: exact generated issue that
  transferred issue-update permission, or `not-applicable`.

## Derived Runtime Fields

These fields are recorded for auditability but are never user-selectable
options:

| Field | Allowed values or shape | Derivation |
| --- | --- | --- |
| `actual_execution_location` | `current-orchestrator-session`, `background-codex-subagent`, `visible-codex-app-task` | Actual runtime evidence for the workstream. |
| `delivery_gate_status` | `ready`, `blocked`, `not-applicable` | Required data, permission, and proof for the selected delivery target. |
| `delivery_allowed_actions` | Canonical action list | `change_delivery_target` plus its valid permission row. |
| `worker_allowed_actions` | Canonical action list from `worker.md` | Exact worker assignment; actions are independent and non-cumulative. |
| `feature_spec_thread_assignment` | One exact Feature Spec ref and title mapped to one visible thread id, or `not-applicable` | Required runtime mapping when visible task permission is granted; never a user option. |

`delivery_allowed_actions` derives as follows:

| `change_delivery_target` | Required delivery actions |
| --- | --- |
| `validated-changes-left-uncommitted` | `edit-files`, `run-validation` |
| `local-commit-created-without-pushing` | `edit-files`, `run-validation`, `create-local-commit` |
| `changes-pushed-to-target-branch-without-pull-request` | `edit-files`, `run-validation`, `create-local-commit`, `push-target-branch` |
| `validated-draft-pull-request-published` | `edit-files`, `run-validation`, `create-local-commit`, `push-target-branch`, `create-or-update-pull-request` |
| `pull-request-ready-for-merge-but-not-merged` | Draft-PR actions plus the review actions required by `codex_review_requirement`, then `mark-pull-request-ready` only after the current-head review policy and remaining gates pass |

## Discovery Source Registry

Each authoritative `## Discovery Sources` row has exactly one matching
`source:<Source ID>:tracked_work_item_update_permission` row. No delivery,
issue, merge, checkout, branch, worker, or permission-transfer field is valid at
a discovery-source scope. Resolve those only after registering a surfaced item
as a workstream.

## Resolution Record

Before dispatch, record exactly one row for every session field and data item.
Before mutation in a workstream, record exactly one row for every per-workstream
field and required data item. Inactive fields use their canonical
`not-applicable`, `not-granted`, or `no-*` value rather than being omitted.

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `session:<field>` | `session` | `<session field>` | `<canonical value>` | `default`, `authorized-user-instruction`, `runtime-capability`, `runtime-derived`, or `project-layout-config` | `<instruction, source, tool ref, or none>` |
| `source:<Source ID>:tracked_work_item_update_permission` | `source:<Source ID>` | `tracked_work_item_update_permission` | `<canonical value>` | `<allowed source>` | `<instruction, source, tool ref, or none>` |
| `<scope_id>:<field>` | `workstream:<id>` | `<per-workstream field>` | `<canonical value>` | `default`, `source-contract`, `authorized-user-instruction`, `runtime-capability`, or `runtime-derived` | `<instruction, source, tool ref, or none>` |

Keep `row_id` unique. This section owns the exact six-column schema:
`row_id`, `scope_id`, `field`, `value`, `source`, and `evidence`. Trim only outer
cell whitespace and encode a literal `|` in evidence as `%7C`.

Every permission-bearing value requires non-empty `permission-source-ref`,
exact `scope-ref`, and non-empty `target-ref` tokens. Branch mutations
additionally require `target-branch=<target_branch_name>`.
`permission-source-ref=feature-spec-default:<feature_slug>` is valid only for
the canonical Feature Spec PR delivery grant and its PR-closing-keyword issue
permission. Explicit authorized-user grants use
`permission-source-ref=authorized-user:<instruction-ref>`. A source contract may
preserve these tokens but must not synthesize them from prose. Runtime
capability may restrict a value; it never grants mutation permission.

## Resolution Source Constraints

- Safe defaults may select only:
  - `visible_app_task_permission=not-requested`;
  - every `not-granted`, `read-only`, `no-*`, or live-evidence value;
  - `validated-changes-left-uncommitted` for ad hoc work; and
  - `safe-default-for-ad-hoc-work`.
- `visible_app_task_permission=granted-by-authorized-user` and
  `denied-by-authorized-user` require authorized-user evidence.
- Every `granted-*`, `apply-updates`, branch-switch, automated-merge,
  simulated-evidence, or explicit-skip value requires exact scoped
  authorized-user evidence or a current source contract that preserves it.
- A source-contract grant with
  `permission-source-ref=feature-spec-default:<feature_slug>` is valid only for
  `change_delivery_permission=granted-for-selected-target` or
  `issue_update_permission=pull-request-closing-keyword-only` when the same
  contract selects `pull-request-ready-for-merge-but-not-merged`.
- `change_delivery_target=pull-request-ready-for-merge-but-not-merged` may come
  from the Feature Spec default, a current source contract, or an authorized
  user instruction.
- Other delivery targets that perform Git or GitHub mutations require a source
  contract or authorized-user instruction naming that exact target and branch.
- `delivery_decision_origin=inherited-from-feature-spec` comes only from the
  Feature Spec. `overridden-by-implementation-issue` requires explicit issue
  evidence. `specified-by-authorized-user` requires a direct instruction.
- `codex_review_requirement=explicitly-skipped-by-authorized-user` requires
  evidence tokens for the exact workstream and immutable pull-request ref when
  the instruction names a specific PR.

## Cross-Field Validation

- Every visible Codex App task requires
  `visible_app_task_permission=granted-by-authorized-user`.
- With `visible_app_task_permission=granted-by-authorized-user`, every
  implementation-eligible Feature Spec requires exactly one active visible
  thread titled with that Spec's exact title. One thread must not own multiple
  Feature Specs, and one Feature Spec must not be split across multiple active
  visible threads. Multiple generated issues or repository PRs for one Spec
  remain owned by its single thread.
- In that granted mode, no Feature Spec implementation or review work may use
  `actual_execution_location=current-orchestrator-session` or a
  background-only worker. If the visible thread surface is unavailable or an
  assigned thread fails, steer, resume-equivalent, or replace the visible
  thread for the same Spec; otherwise stop as `needs-owner` or blocked. Never
  fall back to root implementation or review.
- `feature_spec_ref` and `feature_spec_title` must both be `not-applicable` or
  both be concrete. Re-read Feature Spec source/handoff evidence before
  dispatch or recovery and reject a row whose pair does not match it. Generic
  issue permission-transfer refs do not establish Feature Spec backing.
- An unmanaged Git worktree fallback in the App requires
  `unmanaged_git_worktree_fallback_permission=granted-by-authorized-user`.
- `multi-repository-workspace` requires loading
  `references/multi-repo-workspace.md` before dispatch.
- `validated-changes-left-uncommitted` requires
  `change_delivery_permission=not-required-for-uncommitted-changes`,
  `target_branch_name=not-applicable`, `target_pull_request_ref=not-applicable`,
  `pull_request_count_strategy=no-pull-request`, and
  `codex_review_requirement=not-needed-for-selected-delivery-target`.
- Every other delivery target requires
  `change_delivery_permission=granted-for-selected-target` before its mutation
  actions can run. A missing grant yields `delivery_gate_status=blocked`.
- `local-commit-created-without-pushing` and
  `changes-pushed-to-target-branch-without-pull-request` require an exact valid
  `target_branch_name`, `target_pull_request_ref=not-applicable`, and
  `pull_request_count_strategy=no-pull-request`.
- Pull-request targets require an exact valid `target_branch_name`, a pending or
  live `target_pull_request_ref`, and `one-pull-request-total` or
  `one-pull-request-per-repository`.
- `validated-draft-pull-request-published` requires
  `codex_review_requirement=not-needed-for-selected-delivery-target`.
- `pull-request-ready-for-merge-but-not-merged` requires
  `required-on-current-pull-request-head` or an exact scoped explicit skip.
- `pull_request_merge_confirmation=merge-automatically-after-checks` requires
  `pull_request_merge_permission=granted-for-named-pull-request`.
- `final-commit-closing-keyword` requires
  `changes-pushed-to-target-branch-without-pull-request` and
  `issue_update_permission=direct-issue-updates-explicitly-authorized`.
- Pull-request closing-keyword methods require a pull-request target and at
  least `pull-request-closing-keyword-only` issue permission.
- `move-local-issue-to-done-after-proof` is valid with any non-uncommitted
  target after the target's validation and integration proof passes.
- Every non-`not-applicable` `target_branch_name` must pass
  `git check-ref-format --branch <target_branch_name>`.
- `repository_integration_method` is retired. Derive integration behavior from
  `change_delivery_target`, `pull_request_count_strategy`, and repository refs.

## Canonical Input Requirement

Ledgers, Feature Specs, generated issues, and handoffs must already use this
registry before the runtime consumes them. Reject noncanonical artifacts; do
not guess their meaning or emit compatibility aliases.
