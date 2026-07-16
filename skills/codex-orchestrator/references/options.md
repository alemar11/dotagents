# Orchestrator Option Contract

## Syntax And Hard Cut

Behavior fields use snake_case and enum values use lower-kebab. Resolve prose
directly to canonical values and persist only those values. Reject aliases,
retired fields, and unknown structured inputs.

This file owns every pre-conclusion App orchestration option. Merge fields live
only in `merge-authorization.md`, which is loaded after the fixed delivery
target is complete and only when the owner separately requests merge.

## Registry

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `visible_app_task_permission` | `not-requested`, `granted-by-authorized-user`, `denied-by-authorized-user` | `not-requested` | Explicit visible App task consent. |
| `existing_orchestrator_session_takeover_policy` | `deny`, `takeover-authorized` | `deny` | Active-root takeover. |
| `repository_layout` | `single-repository`, `monorepo`, `multi-repository-workspace` | Derived | Project topology. |
| `change_delivery_target` | `pull-request-ready-for-merge-but-not-merged` | Derived | Fixed App workstream target. |
| `change_delivery_permission` | `not-granted`, `granted-for-selected-target` | Derived | Exact target authority transferred by the execution-ready Feature Spec bundle. |
| `issue_update_permission` | `no-issue-changes`, `pull-request-closing-keyword-only`, `direct-issue-updates-explicitly-authorized` | `no-issue-changes` | Issue mutation authority. |
| `codex_review_requirement` | `required-on-current-pull-request-head`, `explicitly-skipped-by-authorized-user` | `required-on-current-pull-request-head` | Current-head review gate. |
| `delivery_decision_origin` | `inherited-from-feature-spec`, `overridden-by-implementation-issue`, `specified-by-authorized-user` | Derived | Origin of the fixed target; evidence remains separate. |
| `issue_repository_layout` | `single-repository`, `monorepo`, `multi-repository-workspace` | Derived | Issue-effective repository layout. |
| `pull_request_count_strategy` | `one-pull-request-total`, `one-pull-request-per-repository` | Derived | PR topology. |
| `parallelization` | `independent`, `depends-on`, `blocks`, `root-integrated` | Derived | Issue graph relationship; ids remain separate data. |
| `issue_completion_method` | `feature-pull-request-closing-keyword`, `repository-pull-request-closing-keyword`, `move-local-issue-to-done-after-proof`, `no-issue-completion` | Derived | Terminal issue lifecycle action. |
| `domain_closeout` | `not-applicable`, `implementation-closeout` | `not-applicable` | Durable decision closeout requirement. |
| `starting_checkout_branch_handling` | `preserve`, `branch-switch-authorized` | `preserve` | Owner checkout authority. |

App implementation requires
`visible_app_task_permission=granted-by-authorized-user`. Resolve it only after
the mandatory runtime surface gate verifies visible Codex App task creation and
App-managed worktree binding. After that gate, resolve permission before all
other runtime work. `not-requested` requires one direct permission question;
`denied-by-authorized-user`, no answer, or inability to ask aborts without
runtime artifacts. No field selects worker surface, worker count, checkout
strategy, unmanaged checkout fallback, task Goal behavior, or delivery owner.

## Fixed App Delivery

The App orchestrator does not offer a delivery-target choice. It accepts only
`change_delivery_target=pull-request-ready-for-merge-but-not-merged` together
with `change_delivery_permission=granted-for-selected-target`. Every other
target is unsupported for App execution and blocks before task dispatch. Do not
ask the user to select a target and do not downgrade after a capability failure.

## Derived Execution Fields

The App orchestrator derives:

| Field | Value |
| --- | --- |
| `execution_unit` | `feature-spec` |
| `feature_spec_task_cap` | `3` |
| `checkout_owner` | `codex-app-managed` |
| `lifecycle_owner` | `visible-feature-spec-task` |
| `root_implementation_fallback` | `forbidden` |

## Resolution Evidence

Every resolved row records scope id, field, canonical value, source category,
source ref, evidence fingerprint, resolver, and timestamp. Authorized mutations
require exact user/source evidence scoped to the affected workstream or object.

The complete delivery projection also carries `target_branch_name`, source and
issue refs, dependency ids, validation commands, and the evidence fields paired
with permission-bearing rows. Those are validated data, not enum options.

Worker-surface selection, checkout strategy, unmanaged worktree fallback,
actual execution location, delegation visibility, and numeric worker limits
are not options and are invalid as structured inputs.
