# Chief of Staff states

The `chief-of-staff` namespace describes coordination in the invoking App task.
These states are transient conversation facts, not configuration or a persisted
workflow ledger. App task lifecycle and GitHub PR state remain externally owned;
creation receipts and requested outcomes do not establish observed completion.
Every transition and resume retains the same visible coordinator task, project
association and execution location. Chief of Staff must be projectless or in its
original saved project location; Deliver coordinators must be in their saved
repository checkouts. A separate coordinator worktree or unverifiable location
fails preflight, including on resume. Recovery never moves the coordinator or
creates a replacement. Only implementation workers use isolated worktrees.

| State | Meaning | Allowed next states |
| --- | --- | --- |
| `preflight` | Resolve the complete selected scope and verify all standalone project mappings. No dispatch or follow-up is allowed. | `coordinating`, `blocked` |
| `coordinating` | Reconcile, create or continue repository Deliver tasks and consume verified results. | `waiting`, `preflight`, `blocked`, `completed` |
| `waiting` | Existing tasks or required inputs are pending; absence of a result proves neither failure nor success. | `coordinating`, `preflight`, `blocked` |
| `blocked` | A configuration, capability, authority or evidence gap prevents further authorized progress. Preserve results and task identities. | `preflight` |
| `completed` | Every selected repository has delivered ready PRs and required cross-repository evidence is verified. | `preflight` on explicit user continuation |

Completion ends autonomous coordination. An explicit user continuation re-enters
`preflight`, retaining previous completion evidence for revalidation rather than
automatically redispatching delivered work.

Enter `preflight` on invocation or resume and whenever scope or mapping evidence
changes. The global gate includes coordinator execution locations. A failed global
project gate blocks all dispatches and follow-ups while
leaving running tasks untouched. During coordination, a delivery-specific blocker
does not stop independent work; retain that blocker as assignment data and enter
the run-level `blocked` state only when no authorized progress remains. A pending
task can remain `waiting`; do not mistake a normal wait for a terminal blocker.

User attention and uncertain setup remain external observations with their last
known task identity, reason and evidence. Reconcile uncertain effects before any
retry. If observation cannot recover, report `blocked` without declaring that the
task failed or creating a replacement. A stopped or interrupted run is incomplete
and resumes through `preflight`; it is never reported as `completed`.
