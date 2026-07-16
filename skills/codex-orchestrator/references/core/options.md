# Shared Orchestrator Option Contract

Field names use snake_case and assigned values use lower-kebab. Resolve prose
directly to canonical values and reject aliases, retired fields, and unknown
structured inputs.

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `existing_orchestrator_session_takeover_policy` | `deny`, `takeover-authorized` | `deny` | Shared active-root takeover. |
| `repository_layout` | `single-repository`, `monorepo`, `multi-repository-workspace` | Derived | Project topology. |
| `change_delivery_target` | `validated-changes-left-uncommitted`, `local-commit-created-without-pushing`, `changes-pushed-to-target-branch-without-pull-request`, `validated-draft-pull-request-published`, `pull-request-ready-for-merge-but-not-merged` | Derived | Per-workstream target. |
| `change_delivery_permission` | `not-required-for-uncommitted-changes`, `not-granted`, `granted-for-selected-target` | Derived | Exact target authority transferred by the execution-ready Feature Spec bundle. |
| `issue_update_permission` | `no-issue-changes`, `pull-request-closing-keyword-only`, `direct-issue-updates-explicitly-authorized` | `no-issue-changes` | Issue mutation authority. |
| `codex_review_requirement` | `required-on-current-pull-request-head`, `explicitly-skipped-by-authorized-user`, `not-needed-for-selected-delivery-target` | Derived | Current-head review gate. |
| `delivery_decision_origin` | `inherited-from-feature-spec`, `overridden-by-implementation-issue`, `specified-by-authorized-user` | Derived | Origin of the selected target; evidence remains separate. |
| `issue_repository_layout` | `single-repository`, `monorepo`, `multi-repository-workspace` | Derived | Issue-effective repository layout. |
| `pull_request_count_strategy` | `one-pull-request-total`, `one-pull-request-per-repository`, `no-pull-request` | Derived | PR topology for the selected target. |
| `parallelization` | `independent`, `depends-on`, `blocks`, `root-integrated` | Derived | Issue graph relationship; ids remain separate data. |
| `issue_completion_method` | `feature-pull-request-closing-keyword`, `repository-pull-request-closing-keyword`, `final-commit-closing-keyword`, `move-local-issue-to-done-after-proof`, `no-issue-completion` | Derived | Terminal issue lifecycle action. |
| `domain_closeout` | `not-applicable`, `implementation-closeout` | `not-applicable` | Durable decision closeout requirement. |
| `starting_checkout_branch_handling` | `preserve`, `branch-switch-authorized` | `preserve` | Owner checkout authority. |

Permissions are independent and non-cumulative. The invoked public skill
derives `execution_adapter`; user input never selects or changes adapters.

The complete delivery projection also carries `target_branch_name`, source and
issue refs, dependency ids, validation commands, and the evidence fields paired
with permission-bearing rows. Those are validated data, not enum options. Both
adapters must accept and preserve the full projection without inventing values.
