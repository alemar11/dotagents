# Review PR States

Default request-and-wait and explicit inspect-only scope are caller instructions,
not persisted configuration. The skill has no saved workflow position: resume
reconstructs the exact PR/HEAD, caller-retained request record, original
deadline, and observed provider evidence. It owns no agents, implementation, or
repair state.

| `review_pr_result` | Meaning |
| --- | --- |
| `completed` | Verified GitHub evidence establishes a terminal clean or findings verdict for the selected explicit request and expected current HEAD. |
| `inspected` | Read-only inspection returned available review evidence and gaps without requesting or waiting. |
| `pending` | The selected review remains unanswered at the original deadline or caller stop; retain the record and deadline. |
| `deferred` | A draft PR or unresolved target selection requires caller action before requesting/waiting. |
| `blocked` | Required capability, request correlation, target stability, or provider evidence prevents responsible monitoring. |

A completed review is not an accepted implementation. Findings are returned to
the caller, not converted to repair-required or an adjudicated verdict here.
Provider verdicts and finding identities remain external GitHub evidence.
This file owns the review record and `review_state` interpretations below;
retain the record and original deadline unchanged in the caller handoff.

Inspect-only ends with inspected, even when no review exists. Default invocation
requests a missing review, resumes a matching pending request, or immediately
returns a verified terminal result. Pending resumes against the same deadline;
a later terminal readback can yield completed without extending the wait.
Deferred/blocked resumes only after reconciling its cause. HEAD drift blocks the
bound run; a caller may invoke a new run with the new target. Historical evidence
remains attributable to its original HEAD and never becomes current by re-entry.

## Review record

Retain repository and PR URL/number, expected full `head_sha`, request comment
ID/URL, exact request text, authenticated author, request creation time,
original 30-minute deadline, and observed review IDs/URLs with their commit and
author. Keep requested values distinct from provider readback. Record the latest
observation time and `review_state` separately.

The caller retains this record in its existing task context or requested
artifact; the skill creates no ledger, reservation files, or one-use markers.
An old receipt can supply historical IDs, times, and HEAD, but every external
fact must be reconciled with GitHub. Never fabricate missing fields or treat a
receipt as proof of success. Missing correlation or deadline evidence blocks
a resumed wait instead of starting a replacement cycle.

## Review evidence states

`review_state` is a transient interpretation of external GitHub evidence,
separate from the `review_pr_result` returned to the caller.

| `review_state` | Meaning |
| --- | --- |
| `not-requested` | No verified explicit request is established. |
| `pending` | A verified cycle has no terminal result; acknowledgment alone stays pending. |
| `clean` | Correlated terminal provider evidence reports no findings for the expected HEAD. |
| `findings` | Correlated terminal provider evidence reports findings for the expected HEAD. |
| `stale` | The PR HEAD changed or the selected result belongs to another commit. |
| `ambiguous` | Multiple cycles, conflicting results, or missing attribution prevent a unique conclusion. |
| `error` | Provider failure or unavailable access prevents observing the selected cycle. |

A verified request moves `not-requested` to `pending`. Observation can move
`pending` to `clean`, `findings`, `stale`, `ambiguous`, or `error`. Clean and
findings complete the selected cycle; neither authorizes another request.
Timeout or caller stop retains pending and the original deadline. Reconcile
errors or ambiguity before resuming. Historical evidence stays bound to its
original HEAD; a new target needs a caller-selected run.
