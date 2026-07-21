# Worker Publication And Delivery

Load for commit, push, PR, ready transition, CI, tracker closeout, or
mergeability work.

GitStack owns Git and GitHub behavior. Resolve its current bundled workflow and
runtime from the App catalog; do not pin a plugin version or validate one copy
and execute another.

Before an irreversible GitStack mutation, record the exact owner request with
`run-state operation begin` and require `launch_authorized=true`. Invoke the
typed GitStack workflow only for that new receipt, then record or reconcile its
result with `operation finish`. Ambiguous transport requires
exact-target readback and never a blind retry.

Keep provider text in file-backed inputs when the owner supports them. Never
interpolate untrusted title, body, comment, reply, or warning text into shell
commands, environment variables, substitutions, logs, or errors.

Commit through `$gitstack:git-commit`. Use a regular commit unless repository
instructions require one targeted fixup. Never autosquash or rewrite a
published branch. Every new head invalidates previous head-bound evidence.

Create or update the assignment's one delivery PR from the exact authored
target branch against its repository's discovered default branch. Resolve the
exact PR number and canonical URL before readying it, and require that URL's
owner/repository to equal the assignment claim. Re-read the same PR and prove
open, non-draft, unchanged identity, current head, configured CI or
provider-backed `not-configured`, branch rules, approvals, base freshness,
conflict state, mergeability, and merge-queue eligibility.

New PRs from `$gitstack:yeet` are drafts. After the final current-head
AutoReview, Codex review, actionable-finding loop, and configured CI result are
terminal, journal `owner=gitstack`, `action=ensure-pull-request-ready`, the
assignment ID, exact PR URL, and exact head. Read the same PR first. If it is
still draft, invoke the current GitHub connector
`github_mark_pull_request_ready_for_review` exactly once; use GitStack's
same-target authenticated provider fallback only when that connector operation
is unavailable. If it is already non-draft, perform no write. In either case,
re-read the same PR and require non-draft plus the unchanged URL, repository,
head SHA, head branch, base branch, and observed repository default branch.
Finish the operation with exactly those fields and
`status=ready-for-review`. An ambiguous mutation is reconciled by readback
under the same operation key and is never relaunched.

The ready-for-review transition is nonterminal and does not replace the final
rules, approvals, conflict, or mergeability reads. Arm hosted closing refs only in
their designated default-branch PRs and leave issues open until merge. Never
enqueue or merge.
