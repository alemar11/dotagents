# Implement Feature Gates

`run-state` protects identity, ordering, and claim release. Root must prove the
external predicates below from current App, Git, GitHub, review, and CI reads.

## Dispatch

- The complete connected bundle is durable and internally consistent.
- Every selected Spec belongs to the dependency-ready frontier and exactly one
  repository/App project.
- Authorization binds exact source fingerprints, assignments, branches, paths,
  validation, Goal objective, and publication scope.
- The run owns every selected source and repository claim.
- The root Goal is authoritatively active.
- Each worker thread, title, managed checkout, branch, baseline head, and
  isolation is observed before implementation authority.
- The current wave's complete baseline set is accepted before any GO message.
- No more than three live tasks have non-overlapping repository-qualified paths.

## Assignment Head

For every assignment, independently bind these facts to its current exact head:

- allowed-path diff and repository status;
- accepted validation commands and results;
- terminal `$autoreview` result and resolved actionable findings;
- exact-head Codex review request and clean result, or the one permitted
  persistent warned-timeout;
- configured CI results, or provider proof that CI is `not-configured`;
- canonical PR repository/base/head identity and non-draft state;
- branch rules, approvals, mergeability, conflicts, and queue eligibility;
- tracker and optional domain-memory closeout preparation;
- no merge, enqueue, deployment, release, or post-merge mutation by this run.

Any head change invalidates every head-bound fact and returns the assignment to
the applicable validation/review phase.

## Terminal Sequence

1. Reconcile every pending or unknown owner operation by the same operation
   identity.
2. Stop worker mutations. Re-read every thread and managed checkout.
3. Independently reproduce every current-head assignment predicate above.
4. Record each exact thread/head/PR handoff with `run-state task ready`.
5. Re-read `run show`; require no planned or live assignment and no unresolved
   operation.
6. Journal `complete-goal`, call `update_goal(status=complete)`, read back the
   exact completed Goal, finish the operation, and call `goal complete`.
7. Immediately call `run finish --outcome completed`, atomically releasing
   claims.

If truth changes before step 6, return to the owning phase. Drift after Goal
completion blocks state finish and requires owner attention; never falsify or
reopen the Goal.

The successful output is one `pull-request-ready-for-merge` handoff per selected
assignment plus blocked next-frontier refs. A later workflow owns merges and
post-merge closure.
