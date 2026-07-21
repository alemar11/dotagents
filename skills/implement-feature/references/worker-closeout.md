# Worker Closeout

The worker's only successful handoff is `pull-request-ready-for-merge` for its
single repository assignment.

For a local tracker, perform only the predeclared active-to-done move after
substantive, integration, and optional domain-closeout proof. Commit and push
that move, then regenerate validation, AutoReview, Codex review, CI, and
mergeability evidence for the resulting head.

Before reporting ready:

1. Reconcile the worker's publication and review operations with root.
2. Stop edits and read the exact checkout head and allowed-path diff.
3. Reproduce validation, AutoReview, Codex review, configured-CI or
   `not-configured`, PR identity, rules, approvals, conflicts, mergeability, and
   tracker/domain-closeout evidence for that head.
4. Confirm that neither worker nor root merged, enqueued, deployed, released,
   or performed post-merge closure.
5. Report exact assignment ID, thread ID, repository, target branch, head,
   canonical PR URL, evidence summary, warnings, and `next_action=return-to-root`.

Root independently re-reads this evidence before calling `run-state task ready`.
The worker does not complete the Goal or finish run state.
