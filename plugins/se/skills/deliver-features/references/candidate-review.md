# Delivery Features Candidate Review

Load this reference before `review-candidate`. It owns reviewer independence,
the transient receipt, immutable target, fixed profile, checkout lifecycle, and
the Feature-wide review-revision budget. [states.md](states.md) owns every
Delivery Features disposition value. G owns the separate hosted review lifecycle.
Compose [`se:adversarial-review`](../../adversarial-review/SKILL.md) for the
generic skeptical review posture and finding contract. This reference owns the
Delivery Features handoff and evidence boundaries around that review.

## Candidate and checkout

Enter only after the assigned worker has passed required validation, committed
the stable Feature candidate, become quiescent, and proved its worktree clean.
Bind the review to the exact Feature-contract content identity, repository,
intended base branch and full base SHA, candidate branch and full HEAD,
candidate tree identity, complete Feature delta, repository instructions, and
validation evidence.

Candidate Review owns one unique detached temporary checkout outside the
candidate worktree. Materialize it at the bound candidate HEAD, resolve its
intended base to the bound full SHA, and prove its tree clean before launch.
The reviewer must be unable to edit the candidate or perform Git or hosted
mutations.

Start one fresh local noninteractive Codex reviewer execution for that snapshot.
It must be independent of the implementation worker's conversation and request
`gpt-5.6-sol` with `xhigh` reasoning explicitly. Never substitute a same-context
self-review or another profile.

After any attempt, independently observe the reviewer stopped, verify the
checkout's cleanliness and identities when it was created, remove it, and prove
the temporary path and worktree registration are gone. Cleanup is required even
after launch failure, interruption, findings, or an indeterminate result. If
cleanup fails or remains uncertain, retain the exact path in the result and
block completion rather than deleting an ambiguous target.

Several candidates may be reviewed concurrently only when the orchestrator
already authorized their independent worker lanes. Each checkout and reviewer
remains bound to one repository, Feature, base, and candidate HEAD.

## Transient receipt

Return one `candidate-review-receipt-v1` in task history with every field below.
It is an evidence artifact, not a persisted checkpoint.

| field | requirement |
| --- | --- |
| `receipt_version` | Exact value `candidate-review-receipt-v1`. |
| `feature_contract_identity` | Immutable content identity of the authoritative Feature contract reviewed. |
| `repository_key` | Canonical repository identity used by the owning claim. |
| `base_branch` | Intended integration or immediate stack-parent branch. |
| `base_sha` | Full reviewed base SHA. |
| `candidate_branch` | Exact Feature candidate branch. |
| `candidate_head` | Full reviewed candidate HEAD. |
| `candidate_tree_identity` | Immutable identity of the complete reviewed candidate tree. |
| `reviewer_execution_identity` | Independently observed identity of the fresh reviewer execution, or exact `not-created` only when non-creation is authoritative. |
| `reviewer_model` | Exact value `gpt-5.6-sol`. |
| `reviewer_reasoning` | Exact value `xhigh`. |
| `review_revision_ordinal` | `0` for the initial candidate; `1` or `2` for a review-driven repair or rebuttal revision. |
| `execution_attempt_ordinal` | `1`, or `2` only when an ordinal-1 receipt for the same immutable review target proves `not-executed`. |
| `execution_disposition` | One canonical `candidate_review_execution_disposition`. |
| `pre_review_snapshot` | Cleanliness plus exact base, HEAD, tree, and delta evidence before launch, or exact `not-created` only when checkout non-creation is authoritative. |
| `candidate_review_disposition` | One canonical local review disposition. Use `indeterminate` when execution did not yield an admissible verdict. |
| `findings` | Severity-ordered findings, or an empty list. |
| `post_review_snapshot` | Exact checkout state observed after the attempt, or explicit evidence that no checkout existed. |
| `checkout_cleanup_disposition` | One canonical `candidate_review_checkout_disposition`, with the retained path when cleanup was not proved. |

`reconcile` rejects a missing field, noncanonical value, mismatched identity,
unproved execution independence, dirty snapshot, or cleanup result other than
`removed` or `not-created`. Present absence alone never proves `not-created`.
`completed` requires a concrete execution identity and an otherwise admissible
result. `not-executed`, `interrupted`, and `ambiguous` require local disposition
`indeterminate`; attempt `2` additionally requires the matching attempt-1
receipt. A valid receipt never contains a claim token.

## Execution recovery

A `completed` execution returns its admitted local disposition to `reconcile`.
A provably `not-executed` first attempt may retry once against the identical
snapshot after cleanup is proved; that retry keeps the same revision ordinal
and does not consume review-revision budget. A second `not-executed` result
blocks.

An `interrupted` or `ambiguous` execution blocks unless authoritative evidence
can recover the result of that exact attempt. Never launch a replacement merely
because no admissible result is visible. Cleanup failure or uncertainty blocks
regardless of the execution disposition.

## Revision convergence

The initial stable candidate uses revision ordinal `0`. Permit at most two
review-driven repair or rebuttal revisions for one selected Feature across
local and hosted review combined. Batch all findings addressed by one worker
return into one revision. A code repair, a local rebuttal review of unchanged
code, or a hosted-finding rebuttal review each advances the ordinal once;
infrastructure retries do not.

Local `findings` return the same worker for focused repair or evidence-backed
rebuttal, invalidated validation, and a new independent review. `clean` permits
publication only while all receipt identities remain current. If another
review-driven revision is required after ordinal `2`, preserve the last result
and return budget-exhaustion evidence to `reconcile -> blocked`.

Reconstruct ordinals from admissible task-history receipts on resume. Never
reset the budget by changing a finding, HEAD, worker, or reviewer.

## Invalidation

Any Feature-contract content, candidate content, ancestry, base-tip, full-HEAD,
tree, or complete-delta change invalidates the receipt. Immediately before
publication, ready transition, final delivery proof, and claim release, require
the authoritative contract, intended base branch and tip, candidate HEAD, tree,
and effective delta to equal the receipt. A changed hosted-review repair must
pass Candidate Review again before push.

Receipts, prompts, paths, and ordinals remain transient in task history. Never
add them to repository claims or treat them as current workflow position.
