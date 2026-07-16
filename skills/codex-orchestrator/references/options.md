# Orchestrator Option Contract

## Syntax And Hard Cut

Behavior fields use snake_case and enum values use lower-kebab. Resolve prose
directly to canonical values and persist only those values. Reject aliases,
retired fields, and unknown structured inputs.

Load `core/options.md` first. It owns shared non-merge authority,
repository-layout, delivery, review, and checkout-preservation fields. Merge
fields live only in `core/merge-authorization.md`, which is loaded after the
delivery target is complete and only when the owner separately requests merge.
This file owns only App adapter options and derived values.

## Registry

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `visible_app_task_permission` | `not-requested`, `granted-by-authorized-user`, `denied-by-authorized-user` | `not-requested` | Explicit visible App task consent. |

App implementation requires
`visible_app_task_permission=granted-by-authorized-user`. Resolve it only after
the mandatory runtime surface gate verifies visible Codex App task creation and
App-managed worktree binding. After that gate, resolve permission before all
other runtime work. `not-requested` requires one direct permission question;
`denied-by-authorized-user`, no answer, or inability to ask aborts without
runtime artifacts. No field selects worker surface, worker count, checkout
strategy, unmanaged checkout fallback, task Goal behavior, or delivery owner.

## Fixed App Delivery

The App adapter does not offer a delivery-target option. It accepts only the
shared canonical row
`change_delivery_target=pull-request-ready-for-merge-but-not-merged` together
with `change_delivery_permission=granted-for-selected-target`. Every other
target is unsupported for App execution and blocks before task dispatch. Do not
ask the user to select a target and do not downgrade after a capability failure.

## Derived Execution Fields

The shared ledger records `execution_adapter` as `codex-app-task` or
`codex-cli-session`. The selected public skill derives this value. It is never
a user option.

For the App adapter, also derive:

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

Retired mixed-surface fields such as checkout strategy, unmanaged worktree
fallback, actual execution location, delegation visibility, or numeric worker
limits are invalid.
