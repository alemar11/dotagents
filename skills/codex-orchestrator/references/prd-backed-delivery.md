# PRD-Backed Delivery Reference

Use this reference when an implementation workstream is tied to a PRD issue,
generated implementation issues, or a user request such as "implement PRD #46".
It separates PRD delivery contracts from ad hoc implementation requests.

## When This Applies

Apply this reference when any of these are true:

- the user asks to implement a PRD issue or a set of generated implementation
  issues;
- an issue body contains `Source PRD: #<number>` or a linked PRD path;
- a workspace PRD or generated issue links sibling repo-scoped partial PRDs for
  the same feature;
- an issue body contains `## Orchestrator Handoff`;
- the source item was produced by `$plan-feature`;
- the source item has a `## Delivery`, `Delivery Mode`, `Completion`, or
  closeout section that defines branch, PR, or issue-closing behavior.

If none of those are true, treat the source as ad hoc or legacy work and use
the conservative authorization rules in `worker.md`.

If `Source PRD` is a draft ref such as `draft-prd:<...>`, treat it as a dry-run
planning reference, not durable implementation authority. The root may inspect
the graph, but real worker dispatch, commit, push, PR creation, issue closeout,
or tracker mutation requires a hosted PRD number, a local PRD path, or an
explicit owner decision recorded with separate publication and issue-mutation
authority.

For generated implementation issues, `## Orchestrator Handoff` is the
canonical issue-level dispatch contract. It must restate the source PRD,
feature slug, delivery mode, affected repos or product scope, scope, start rule,
dependencies, validation, and closeout path. The handoff is not an
authorization grant: worker authorization, publication authority, and issue
mutation authority are still resolved by the root orchestrator from the owner
request, linked PRD, issue body, gate state, and current session authority.

For workspace features split across multiple repositories, a repo-scoped
partial PRD may be the entry point. Before scheduling, expand its linked sibling
partial PRDs and register the connected graph in the ledger. Treat each partial
PRD and generated issue as its own source item, use their cross-links to
understand which repo work can run together, and require cross-repo integration
proof before marking the feature graph complete.

## Authority Model

Record these three authorities separately in the ledger:

- **Delivery authority**: where the branch, PR shape, dependency graph, and
  closeout path come from. For generated issues this is usually the linked
  `Source PRD` plus the generated issue's copied delivery label, issue-level
  dependency fields, and `## Orchestrator Handoff`.
- **Publication authority**: whether the root may commit, push, open or update
  the draft PR, and, when separately authorized, mark it ready for review,
  request Codex review, and perform merge-ready PR discussion updates or
  no-update-needed dispositions after gates pass.
- **Issue mutation authority**: whether the root may directly comment, label,
  close, or otherwise mutate GitHub issues outside the PR body closeout path.

Do not collapse these into one boolean. A PRD can authorize a draft PR delivery
path without authorizing ready-for-review transition, Codex review request,
direct issue closure, merge, release, or unrelated GitHub mutations.

`$plan-feature` may publish the PRD and generated implementation issues before
implementation starts. After the root registers those generated issues as
workstreams, source lifecycle and closeout mutations are orchestrator-owned:
issue comments, label changes, direct closure when authorized, real PR link
recording, and integration proof all require the root's resolved issue mutation
authority.

## Structured Authority Values

Use these PRD-backed authority values in the ledger and worker prompts:

- `publication_authority`: `none` means no publication,
  `explicit-owner-authorization` means the owner authorized the recorded
  publication actions in the current run, `prd-backed-branch-plus-draft-pr`
  means the PRD delivery contract authorizes commit/push/draft PR only,
  `prd-backed-merge-ready-pr` means the PRD, generated issue, or current owner
  request explicitly extends PRD-backed publication to ready-for-review
  transition, `@codex review`, polling, and required discussion disposition
  after local gates, and `blocked` means publication is expected but blocked by
  a gate, access issue, or owner restriction.
- `publication_owner`: `root` means the root orchestrator owns the publication
  decision. A worker may execute assigned `commit`, `push`, or `pr` steps only
  inside an exact root-assigned scope. `none` means no publication owner exists.
- `issue_mutation_authority`: `none` means no direct issue mutation,
  `pr-body-closeout-only` means closure only through the relevant PR body, and
  `explicit-direct-mutation` means direct issue comments, labels, or closure are
  authorized.

`prd-backed-branch-plus-draft-pr` is a legacy-compatible draft-only value. Do
not reinterpret it as ready-for-review or Codex-review authority. Use
`prd-backed-merge-ready-pr` or `explicit-owner-authorization` when the source or
current owner request explicitly authorizes merge-ready closeout.

Delivery mode values are owned by the PRD and generated issue body. Worker
authorization modes are owned by `worker.md` and resolved per workstream by the
root orchestrator. Ignore legacy project-memory worker-authorization setup
values; they are not delivery, publication, or issue mutation authority.
Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases when reading existing artifacts. When updating an artifact
that contains legacy aliases, rewrite touched structured values to
lower-kebab-case.

## Scheduling Values

Use generated issue scheduling fields as the wave graph:

| Field | Start rule |
| --- | --- |
| `independent` | May start when authorization, ownership boundaries, and gates allow it. |
| `depends-on <issue>` | Queue-ready is not start-ready; wait for root-verifiable dependency proof. |
| `blocks <issue>` | May start when otherwise eligible; dependent work remains unassigned. |
| `root-integrated` | Keep implementation in root; workers may inspect or prove only if integration stays root-owned. |

## PRD-Backed Publication

When the owner asks to implement a PRD or generated PRD issue, and the PRD or
generated issue explicitly defines branch plus draft PR delivery, treat commit,
push, and draft PR creation as part of the PRD delivery contract after required
tests, integration checks, and `$autoreview` pass, unless the owner said
`local-only`, `inspect-only`, `no push`, `no PR`, or equivalent.

Treat ready-for-review transition, Codex review request, Codex feedback triage,
needed fixes, and PR discussion updates as part of the delivery contract only
when the source or current owner request explicitly authorizes merge-ready
closeout, records `publication_authority=prd-backed-merge-ready-pr`, or records
`publication_authority=explicit-owner-authorization` with those actions named.
`stay draft` or equivalent owner/source wording blocks merge-ready closeout
until the owner changes that decision.

This PRD-backed publication authority is sufficient for the root orchestrator
to use `$git-commit` for commit/push-only delivery, or `$yeet` when the resolved
delivery path requires draft PR creation or updating an existing PR.
Merge-ready publication authority is additionally sufficient to use
`$github-review-threads` for the `@codex review` request and the required PR
discussion update or no-update-needed disposition after the Codex review
completes. Neither authority is sufficient for merge, release, production
deploy, final issue closure by direct mutation, broad GitHub cleanup, or
switching the caller checkout away from its current branch. When worker or
integration worktrees are available, the root should publish from one of those
checkouts and preserve the caller checkout unless the owner explicitly
authorizes using it as the publication checkout.

Direct commit remains a special case. Use `direct-commit` only when the PRD,
generated issue, or owner request explicitly says direct commit is authorized
and records the target branch plus closeout behavior.

For local markdown trackers, `direct-commit` proves delivery but does not close
the local issue by itself. After validation and commit proof are recorded, move
the issue file to `issues/done/` unless the current run explicitly keeps
completed files in place for inspection. Use final-commit closure only for
hosted or custom sources that explicitly support that closeout path.

For local markdown trackers using `pull-request` delivery with merge-ready
closeout authority or a merge-ready closeout target, do not move the issue file
to `issues/done/` until local validation, real PR proof, required CI or
integration proof, and Codex review evidence plus disposition are recorded. If
any of those are missing, keep the local issue open and record the remaining
action as `needs-owner`, `blocked`, or `deferred`.

## Required Resolution Steps

Before scheduling or publishing PRD-backed work:

1. Read the generated issue body and the linked `Source PRD`. If the ref is
   `draft-prd:<...>`, stop before implementation scheduling unless the owner
   explicitly authorizes temporary-source execution and separately records the
   publication and issue-mutation authority that execution may use.
2. For generated issues, read `## Orchestrator Handoff` and verify it contains
   source PRD, feature slug, delivery mode, affected repos or product scope,
   scope, start rule, dependencies, validation, and closeout. If it is missing
   or contradicts the issue body, stop as `needs-owner` or route back through
   `$plan-feature` issue generation instead of dispatching implementation.
3. If the linked PRD is a workspace partial PRD, expand the connected sibling
   partial-PRD graph and record each partial PRD/source item plus cross-link in
   the ledger before building waves.
4. Resolve the effective delivery mode from the PRD first, then apply only
   issue-level overrides that are explicit and authorized.
5. Record delivery authority, publication authority, merge-ready closeout
   authority when any, issue mutation authority, closeout vehicle, branch
   expectation, PR expectation, publication checkout, caller checkout policy,
   integration proof target, and handoff projection in the ledger.
6. Build the wave graph from the generated issues' handoff start rules,
   dependency fields, and parallelization fields. Queue-ready does not mean
   start-ready when an issue depends on another incomplete issue.
7. Stop as `needs-owner` or `blocked` if the PRD, issue body, handoff,
   dependency graph, branch expectation, or closeout path is missing,
   contradictory, or unsafe.

## Closeout Rules

For PRD-backed implementation, local code completion is not enough for
`completed` when publication authority exists. A workstream reaches
`completed` only after:

- acceptance criteria are satisfied with root-verifiable proof;
- required gates pass, including focused tests and `$autoreview` for
  non-trivial code edits;
- dependency and integration proof targets are satisfied;
- the expected branch and PR exist when PRD-backed publication is authorized;
- if merge-ready closeout authority exists, the PR is marked ready for review
  when local gates pass;
- if merge-ready closeout authority exists, `@codex review` was requested, a
  completed Codex GitHub review exists for the latest PR state, and accepted
  actionable feedback was fixed or explicitly dispositioned; and
- the ledger records the PR URL, publication checkout, caller checkout
  disposition, and, when merge-ready closeout authority exists, Codex review
  evidence plus discussion update or no-update-needed disposition; otherwise it
  records why publication/review is blocked and moves the remaining action to
  `needs-owner`, `blocked`, or `deferred`.

If PRD-backed publication is authorized and the only remaining action is
commit, push, or draft PR creation, keep that action in `ready-next` and
execute it before stopping when runtime access allows. If merge-ready closeout
authority exists and the only remaining action is ready-for-review transition,
Codex review request, waiting for Codex's response, review-triggered fixes, or
PR discussion update or disposition, keep that action in `ready-next` and
execute or poll it before stopping when runtime access allows. If merge-ready
closeout is expected but not authorized, reclassify the remaining action as
`needs-owner` or `blocked` with the missing authority recorded.

Repo PR placeholders copied from PRDs or generated issues are not completion
proof. The root must replace or augment them during closeout with real PR links
or equivalent integration proof before marking a PRD-backed workstream
`completed`.

Close generated GitHub implementation issues through the relevant PR body by
default, using the closeout wording specified by the generated issue or PRD.
Direct comments, labels, manual issue closure, parent issue closure, merge, or
release still require explicit mutation authority. Close the PRD parent issue
only when the PRD closeout contract or owner request explicitly says the parent
should close, or when the published PR body is intentionally the parent
closeout vehicle.

## Worker Boundaries

The root orchestrator owns branch selection, shared PR shape, source closeout,
final publication, Codex review disposition, and merge-ready decision. Workers
may inspect, implement, test, and report within their assigned authorization
modes. The root derives those modes per workstream from the owner request,
source item, linked `Source PRD`, publication authority, issue mutation
authority, selected worker surface, dependency state, dirty-worktree state, and
gates. Workers may commit, push, open PRs, mark a PR ready for review, or
request Codex review only when the root lists the corresponding `commit`,
`push`, `pr`, or `review-ready` authorization mode for a specific repo,
branch/refspec, PR shape, and closeout target. These modes are capability flags,
not a cumulative ladder; list every allowed action explicitly. For
`review-ready`, also list the allowed sub-actions from `worker.md` so workers do
not infer Codex-review disposition authority.

For `pull-request`, workers do not create independent feature PRs unless the
source graph assigns them repo-scoped publication authority. In single-repo or
monorepo work, they provide patches, helper worktree diffs, or reviewed commits
for root integration into the feature branch. In multi-repo work, a repo-scoped
worker may prepare that repo's branch or draft PR only if the root assigned
repo-scoped `commit`, `push`, or `pr` authority matching each intended action.

## Ad Hoc And Legacy Sources

For ad hoc requests, PR reviews, CI diagnosis, local TODOs, or legacy issues
without a linked PRD delivery contract, `implement` means local code/docs
changes plus validation only. Commit, push, draft PR, ready-for-review
transition, Codex review request, issue mutation, merge, and release require
explicit owner authorization or a later `commit`, `push`, `pr`, `review-ready`,
`merge-close`, or `release` mode.
