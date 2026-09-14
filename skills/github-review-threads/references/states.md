# GitHub Review States and Records

This file owns the `review_state` namespace and resumable review record.
States are transient interpretations of external GitHub evidence. The caller
retains the record in its existing task context or requested artifact; the skill
creates no ledger, reservation files, or one-use markers. GitHub owns PR HEAD,
comments, reviews, reactions, thread IDs, and resolution state.

## Review record

Retain repository and PR URL/number, expected full `head_sha`, request comment
ID/URL, exact request text, authenticated author, request creation time,
original deadline, and observed review IDs/URLs with their commit and author.
An automatic cycle instead records its verified trigger identity/time and HEAD;
it has no explicit request comment. Keep requested values distinct from provider
readback. Record the latest observation time and `review_state` separately.

For `review-pr`, preserve the original 30-minute deadline. An old typed receipt
may supply historical IDs, times, and HEAD, but every external fact must be
reconciled with GitHub. Do not fabricate missing fields or treat a receipt or
consumed marker as proof of success. Missing correlation or deadline evidence
blocks a resumed wait rather than starting a replacement cycle.

## Review states

| `review_state` | Meaning |
| --- | --- |
| `not-requested` | No verified request or automatic trigger is established. |
| `pending` | A verified cycle has no terminal result; acknowledgment alone stays pending. |
| `clean` | Correlated terminal provider evidence reports no findings for the expected HEAD. |
| `findings` | Correlated terminal review evidence reports findings for the expected HEAD. |
| `stale` | The PR HEAD changed or the selected result belongs to another commit. |
| `ambiguous` | Multiple cycles, conflicting results, or missing attribution prevent a unique conclusion. |
| `error` | Provider failure or unavailable access prevents observing the selected cycle; report which. |

A verified request moves `not-requested` to `pending`. Observation can move
`pending` to `clean`, `findings`, `stale`, `ambiguous`, or `error`. Clean and
findings finish the selected cycle; neither authorizes another request.
Timeout or caller stop retains `pending` and the original deadline. Later
read-only reconciliation can discover a terminal result without extending the
wait. Reconcile errors or ambiguity before resuming. HEAD drift requires a
caller-selected new target; historical evidence stays bound to its old HEAD.

## Feedback and mutations

Classify feedback as `actionable`, `already-addressed`, `informational`,
`obsolete`, or `needs-user-decision`, with evidence. Classification is transient
and never authorizes resolving a thread.

Report each mutation as verified, already satisfied without a write, previewed,
or unconfirmed, with its exact target and readback. An uncertain request or reply
requires read-only reconciliation; stop if success or nonapplication cannot be
established. Already-resolved threads do not prove who resolved them. A clean
review does not imply every thread should be resolved.
