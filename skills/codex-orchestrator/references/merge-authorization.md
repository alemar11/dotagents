# Post-Conclusion Merge Authorization

Load this reference only after the App orchestrator has completed its fixed
delivery target and the owner separately requests merge. Never load or resolve
these fields during intake, CLAIM, registration, dispatch, task execution, or
delivery gating.

| Field | Allowed values | Resolution |
| --- | --- | --- |
| `pull_request_merge_permission` | `not-granted`, `granted-for-named-pull-request` | Resolve for the exact named PR only after the delivery target is complete. |
| `pull_request_merge_confirmation` | `ask-authorized-user-after-checks`, `merge-automatically-after-checks`, `not-applicable` | Resolve only with the same post-conclusion owner instruction. |

These fields have no pre-conclusion defaults. Their absence before this
reference is loaded means unresolved, not denied or not applicable. Permission
and confirmation are independently scoped, non-cumulative, and never inherited
from a Feature Spec, implementation issue, delivery grant, review state, or PR
readiness.
