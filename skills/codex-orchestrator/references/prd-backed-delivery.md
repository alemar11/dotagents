# PRD-Backed Delivery Reference

Use this reference when an implementation workstream is tied to a PRD issue,
generated implementation issues, or a user request such as "implement PRD #46".
It separates PRD delivery contracts from ad hoc implementation requests.

## When This Applies

Apply this reference when any of these are true:

- the user asks to implement a PRD issue or a set of generated implementation
  issues;
- an issue body contains `Source PRD: #<number>` or a linked PRD path;
- the source item was produced by `$plan-feature` or `$to-issues`;
- the source item has a `## Delivery`, `Delivery Mode`, `Completion`, or
  closeout section that defines branch, PR, or issue-closing behavior.

If none of those are true, treat the source as ad hoc or legacy work and use
the conservative authorization rules in `worker.md`.

## Authority Model

Record these three authorities separately in the ledger:

- **Delivery authority**: where the branch, PR shape, dependency graph, and
  closeout path come from. For generated issues this is usually the linked
  `Source PRD` plus the generated issue's copied delivery label and issue-level
  dependency fields.
- **Publication authority**: whether the root may commit, push, and open the
  draft PR after gates pass.
- **Issue mutation authority**: whether the root may directly comment, label,
  close, or otherwise mutate GitHub issues outside the PR body closeout path.

Do not collapse these into one boolean. A PRD can authorize a draft PR delivery
path without authorizing direct issue closure, merge, release, or unrelated
GitHub mutations.

## PRD-Backed Publication

When the owner asks to implement a PRD or generated PRD issue, and the PRD or
generated issue explicitly defines branch plus draft PR delivery, treat commit,
push, and draft PR creation as part of the PRD delivery contract after required
tests, integration checks, and `$autoreview` pass, unless the owner said
`local-only`, `inspect-only`, `no push`, `no PR`, or equivalent.

This PRD-backed publication authority is sufficient for the root orchestrator
to use `$git-commit` or `$yeet` for the named branch and draft PR. It is not
sufficient for merge, release, production deploy, final issue closure by direct
mutation, or broad GitHub cleanup.

Direct commit remains a special case. Use **Direct Commit** only when the PRD,
generated issue, or owner request explicitly says direct commit is authorized
and records the target branch plus closeout behavior.

## Required Resolution Steps

Before scheduling or publishing PRD-backed work:

1. Read the generated issue body and the linked `Source PRD`.
2. Resolve the effective delivery mode from the PRD first, then apply only
   issue-level overrides that are explicit and authorized.
3. Record delivery authority, publication authority, issue mutation authority,
   closeout vehicle, branch expectation, PR expectation, and integration proof
   target in the ledger.
4. Build the wave graph from the generated issues' dependency and
   parallelization fields. Queue-ready does not mean start-ready when an issue
   depends on another incomplete issue.
5. Stop as `Needs Owner` or `Blocked` if the PRD, issue body, dependency graph,
   branch expectation, or closeout path is missing, contradictory, or unsafe.

## Closeout Rules

For PRD-backed implementation, local code completion is not enough for
`Completed` when publication authority exists. A workstream reaches
`Completed` only after:

- acceptance criteria are satisfied with root-verifiable proof;
- required gates pass, including focused tests and `$autoreview` for
  non-trivial code edits;
- dependency and integration proof targets are satisfied;
- the expected branch and draft PR exist when PRD-backed publication is
  authorized; and
- the ledger records the PR URL or records why publication is blocked and moves
  the remaining action to `Needs Owner`, `Blocked`, or `Deferred`.

If PRD-backed publication is authorized and the only remaining action is
commit, push, or draft PR creation, keep that action in `Ready Next` and
execute it before stopping. Do not mark the work complete while an authorized
draft PR remains uncreated.

Close generated GitHub implementation issues through the relevant PR body by
default, using the closeout wording specified by the generated issue or PRD.
Direct comments, labels, manual issue closure, parent issue closure, merge, or
release still require explicit mutation authority. Close the PRD parent issue
only when the PRD closeout contract or owner request explicitly says the parent
should close, or when the published PR body is intentionally the parent
closeout vehicle.

## Worker Boundaries

The root orchestrator owns branch selection, shared PR shape, source closeout,
and final publication. Workers may inspect, implement, test, and report within
their assigned authorization mode. They may commit, push, or open PRs only when
the root assigns `push-pr` for a specific repo, branch, and closeout target.

For **One Feature Branch**, workers do not create independent feature PRs.
They provide patches, helper worktree diffs, or reviewed commits for root
integration into the shared branch. For **One PR Per Repo**, a repo-scoped
worker may prepare that repo's branch or PR only if the root assigned
repo-scoped `push-pr` authority.

## Ad Hoc And Legacy Sources

For ad hoc requests, PR reviews, CI diagnosis, local TODOs, or legacy issues
without a linked PRD delivery contract, `implement` means local code/docs
changes plus validation only. Commit, push, draft PR, issue mutation, merge,
and release require explicit owner authorization or a later `push-pr`,
`merge-close`, or `release` mode.
