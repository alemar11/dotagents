# Review Mutation Authority

Load before a GitStack review mutation or its recovery. Authority is available
only after accepted baseline and active root Goal evidence.

GitStack owns request recognition, provider transport, receipts, findings,
replies, resolutions, waits, warnings, and readback reconciliation. Implement
Feature never duplicates those field registries or pins a GitStack version.

Before physical mutation, record the exact owner request with
`run-state operation begin`, binding the current run revision and Git head.
Launch only when it returns `launch_authorized=true`; an existing key requires
reconciliation and never authorizes another provider call. After GitStack
returns, record `succeeded`, `failed`, or `unknown` with
`operation finish`. An `unknown` result requires owner/provider readback and
must be reconciled under the same operation key; never post, reply, resolve, or
wait again under another key.

The review request, provider artifact, repository, PR, and full head must agree.
A recognized request without provider output is pending, not correlation
failure. The wait deadline is exactly request start plus 45 minutes and is never
reset or extended. Pending at the deadline needs the separately journaled
persistent warning before it becomes `warned-timeout`.

Thread resolution requires exact thread identity, committed repair evidence,
provider readback, and `isResolved=true`. Summary-only findings have no
synthetic thread. Review operations grant no merge, enqueue, deploy, Goal,
task, or worktree authority.
