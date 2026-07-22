# End-To-End App Worker

The worker executes one assigned Feature Spec end to end in its App-managed
worktree. It owns issue sequence, technical design, implementation and rewrites,
repairs, tests, validation, commits, push, PR creation and updates, AutoReview,
Codex review, CI, review fixes, tracker progress, and final evidence.

Before each issue, after recovery, and before final verification:

1. read the current Feature Spec and complete issue graph;
2. compare the stable fields from `spec-backed-delivery.md` directly;
3. accept compatible operational changes and continue autonomously;
4. stop declaratively as `blocked-durable-contract` if a stable field changed.

Do not ask the user or root for implementation, validation, recovery, retry,
publication, review-fix, or blocker authority. The startup grant already covers
in-contract work. Choose safe, maintainable approaches and coherent rewrites.
Respect the accepted material attempt budget and required validation result.

Use target-repository instructions and current GitStack workflows for commits,
pushes, PRs, GitHub issue mutations, CI, and review threads. Run `$autoreview`
after focused validation, verify every finding in the real code, fix accepted
findings, and revalidate changed evidence. Run the required current-head Codex
review and resolve actionable feedback. Never force-push published history,
merge, enqueue, deploy, release, or perform post-merge closure.

Follow `tracker-proof.md` for every issue and parent checkbox. If later work
invalidates proof, uncheck it and read back the correction.

The only successful result is `pr-ready-for-merge-but-not-merged` with exact
source ref, thread ID, checkout, branch, head SHA, PR URL, provider observation,
current-head validation, reviews, configured CI or authoritative not-configured
evidence, tracker readback, mergeability, warnings, and changed paths. Coherent
progress needs no root intervention.
