# Implement Feature Gates

## Run Authorization Gate

Require `visible_app_task_permission=granted-by-authorized-user` before CLAIM.
That single disclosed grant covers the fixed inspect-through-ready flow for the
accepted bundle. It does not authorize scope expansion, merge, release,
deployment, post-merge closure, or target-repository instruction changes.

## Managed Checkout Gate

Require App-managed isolated checkout evidence for every affected repository.
Missing or non-isolated checkout proof blocks the run. Never create raw Git
worktrees, rotate the caller checkout, or transfer implementation to the root.

## Dependency And Integration Gate

Dispatch only after every cross-Spec dependency is verified merged. A
merge-ready upstream is still unfinished dependency evidence. Require the
bundle's focused validation plus every named integration gate. Multi-repository
completion requires exactly one distinct repo-owned integration Feature Spec
downstream of all implementation partials. Its task must own at least one
bounded path change and cross-repository proof, producing a real PR rather than
a no-op validation result.

## Pull Request, Review, And CI Gate

The only delivery gate is a pull request ready to merge and not merged. Every
affected repository must have a real `OPEN`, non-draft PR URL at its current head,
with the base equal to that repository's currently discovered default branch,
safe metadata, mandatory current-revision Codex review dispositioned, every
actionable finding resolved, and at least one applicable CI check run or status
context bound to that exact head SHA. Zero applicable CI results is a
`ci-unavailable` blocker, not a passing gate. Every required applicable result
must be successful; skipped or neutral evidence counts only when repository
rules prove it is not required.

Do not make draft status a circular prerequisite for mergeability. A task may
publish a draft while implementing; after substantive implementation, focused
validation, and `$autoreview`, convert it to ready-for-review with
`isDraft=false`. Only then request or wait for repository approvals and evaluate
the final mergeability/rule gate. The ready-for-review transition is not
`merge-ready` and grants no merge or queue authority.

For that same current head/base tuple, require the lifecycle to remain `OPEN`
and GitHub to report the PR
conflict-free and mergeable, with every repository-required base update,
approval, and merge-queue eligibility condition satisfied. Unknown, pending,
dirty/conflicting, behind-when-update-required, or otherwise blocked merge state
is not ready. Persist the observed mergeability and rule evidence; never enqueue
or merge the PR.

Review has no skip. Apply each exact tuple through `revision-observed`; the
helper invalidates older revision-bound gate evidence when head, base-ref,
merge-base, or material diff changes. A changed revision returns the task to
validation, `$autoreview`, request/poll/fix, and CI as applicable. Apply each
current proof through `gate-observed`, never by patching state.

## Domain Knowledge Closeout Gate

When the final issue carries a nonempty accepted `knowledge_delta`, invoke
`$project-memory` with `memory_slice=domain-memory` and
`domain_operation=implementation-closeout` only after integration proof.
Require `capture_outcome=captured`, every supplied accepted item still supported
and durably represented, every required named target reconciled, named verified
destinations, and complete documentation-diff verification. An unresolved,
rejected, or landed-behavior-contradicted item, `capture_outcome=deferred`, or
`capture_outcome=no-durable-change` blocks domain closeout and terminal
`merge-ready` pending an owner decision or separately authorized
planning/implementation correction.

## Tracker Closeout Gate

Derive closeout from the source backend. For GitHub, arm every generated
implementation issue in its owning PR and arm each implementation-eligible
Feature Spec in that Spec's designated default-branch whole-Spec closeout PR
only after its gates pass. For multi-repository work, the final integration
partial's default-branch PR also arms any accepted hosted parent/global Feature
Spec with a fully qualified ref, but only after every partial gate passes. Use
fully qualified issue refs across repositories, record every closing link as
`armed`, and do not report any hosted item closed before merge. Closing keywords
count only on PRs whose base is the repository default branch.

For local Markdown, complete substantive acceptance, integration proof, and the
domain knowledge closeout gate when present. Then move each issue from its exact scoped
active path to its exact scoped `done/` destination on the delivery branch,
apply one `source-moved` transition to that predeclared destination
with an unchanged body fingerprint, commit and push the move, rerun final
validation and `$autoreview`, convert draft PRs to ready-for-review, then obtain
current-revision review and CI at that resulting head before terminal merge-ready
state.
Record closeout as prepared; the default-branch completion signal appears only
when the later PR merge lands the move.

## Terminal Gate

Before `merge-ready`, require scope and acceptance proof, preserved owner
changes, current diff and validation, non-trivial `$autoreview`, dependency and
integration proof, current-head review, CI, ready PRs, prepared tracker
closeout, any required captured domain knowledge closeout, default-branch PR
bases, current conflict-free mergeability and repository-rule satisfaction, and
no unresolved actionable work. For local
issues, the current reviewed head must include the committed and pushed
active-to-`done/` moves.

Require the machine-derived terminal projection, then apply
`external-handoff-recorded` with exact PR URLs, head/base/merge-base revisions,
checks, closeout vehicle, and next merge action. Then stop and release the
active-root claim. Neither root nor task merges, performs post-merge
verification, or closes hosted tracker items. A later GitHub workflow owns
those actions.
