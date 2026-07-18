# Implement Feature Gates

## Authorization And Managed Checkout

Require `visible_app_task_permission=granted-by-authorized-user` before CLAIM.
The disclosed grant covers the fixed inspect-through-ready flow for the
accepted bundle, not scope expansion, merge, release, deployment, post-merge
closure, or target-repository instruction changes.

Before edits, apply one `managed-checkouts-observed` event containing every
registered delivery exactly once. Require an App-managed isolated checkout,
matching repository, target branch, Git top-level, baseline revision, and
isolation proof for every delivery. Missing, duplicated, shared, unmanaged, or
non-isolated checkout evidence blocks. Never create raw Git worktrees, rotate
the caller checkout, or transfer implementation to the root.

## Static Dispatch Gates

`dependency-integration` is a `task-static` gate. Dispatch only after every
cross-Spec dependency is verified merged; a merge-ready upstream is still
unfinished. `pr-preflight` is a `delivery-static` gate and must pass separately
for every affected repository. Neither static gate requires a PR revision, so
pending tasks can become dispatch-ready before publication.

Multi-repository completion requires exactly one distinct repo-owned
integration Feature Spec downstream of all implementation partials. It owns a
bounded path change and cross-repository proof and produces a real PR rather
than a no-op validation result.

## Delivery-Revision Gates

For each delivery's current exact repository, PR number and URL, head SHA, base
ref, and merge-base SHA require:

- `publication`: real PR identity, lifecycle `OPEN`, and base equal to that
  repository's currently discovered default branch;
- `codex-review`: mandatory current-revision request with every actionable
  finding resolved;
- `ci`: at least one applicable run or status context on the exact head SHA and
  every required applicable result successful;
- `pr-ready`: non-draft exact PR identity after the ready-for-review transition;
- `tracker-closeout`: every applicable closing vehicle prepared at the current
  delivery revision;
- `mergeability`: conflict-free GitHub mergeability plus required base
  freshness, approvals, and merge-queue eligibility.

Zero applicable CI results is a `ci-unavailable` blocker. Skipped or neutral
evidence counts only when repository rules prove it is not required. Unknown,
pending, dirty/conflicting, behind-when-update-required, closed, merged, or
otherwise blocked state never passes. Never enqueue or merge.

A draft is only an intermediate vehicle. After substantive implementation,
focused validation, and `$autoreview`, convert it to ready-for-review with
`isDraft=false`; only then obtain approval and final rule evidence. Do not make
draft status a circular prerequisite for mergeability. The transition is not
terminal.

## Task-Revision-Set Gates

The canonical revision-set key contains one current revision for every
delivery. Bind `scope-acceptance`, `integration-validation`, and optional
`domain-closeout` to that complete set. Bind `focused-validation`,
`full-validation`, and `autoreview` to each delivery revision. A partial set
cannot pass.

## Domain Knowledge Closeout Gate

When the final issue carries a nonempty accepted `knowledge_delta`, invoke
`$project-memory` with `memory_slice=domain-memory` and
`domain_operation=implementation-closeout` only after integration proof.
Require `capture_outcome=captured`, every supplied accepted item still
supported and durably represented, every required named target reconciled,
named verified destinations, and complete documentation-diff verification. An
unresolved, rejected, or landed-behavior-contradicted item,
`capture_outcome=deferred`, or `capture_outcome=no-durable-change` blocks domain
closeout and terminal `merge-ready` pending an owner decision or separately
authorized correction.

Any delivery revision, PR identity, material diff, repository-rule, tracker
delivery, evidence-target, or documentation change invalidates the affected
delivery-revision gates and every task-revision-set gate. Apply new evidence
through typed events; never patch state.

## Tracker Closeout

For GitHub, arm every generated implementation issue in its owning delivery PR.
Arm each implementation-eligible Feature Spec in its designated default-branch
whole-Spec closeout PR only after its gates pass. The final integration
partial's default-branch PR may arm an accepted hosted parent/global Feature
Spec only after every partial gate passes. Use fully qualified refs across
repositories and leave hosted items open until merge.

For local Markdown, complete substantive acceptance, integration proof, and
the domain knowledge closeout gate when present. Only then move each issue from
its exact active path to its predeclared `done/` path in the owning delivery.
`source-moved` requires current task-revision-set proof and an unchanged body
fingerprint; it marks that tracker delivery dirty and invalidates the current
revision set, then commit and push the move, establish a newer tuple through
`revision-observed`, and bind current committed/published lifecycle through
`delivery-observed`. Only that newer published observation clears dirt. Then
rerun final validation and `$autoreview`, convert drafts to ready-for-review,
then obtain current-revision review and CI before terminal merge-ready state.
Record closeout as prepared; completion reaches the default branch only after a
later merge. GitHub sources cannot use `source-moved`.

## Staged Terminal Gate

Closeout must not be circular. Use this order:

1. Prove every applicable static, delivery-revision, and task-revision-set gate
   at the current complete revision set; apply `task-terminal-sealed`.
2. Complete and read back that worker Goal; apply `task-goal-completed`.
3. Apply `terminal-handoff-recorded` with the unchanged seal fingerprint,
   `pull-request-ready` kind, fixed `external-merge-required` authority, and
   next action.
4. After all tasks, independently reverify current proof and apply
   `portfolio-terminal-verified`.
5. Complete and read back the root Goal; apply `portfolio-goal-completed`.
6. Release and archive through `cache-lifecycle.md`.

The machine-derived terminal projection exposes readiness for each stage.
Review monitoring retains the active claim and cannot satisfy terminal
handoff. Neither the root nor a task merges, performs
post-merge verification, or closes hosted tracker items.

Review has no skip; every delivery-revision review gate is mandatory.

After a task seal or Goal completion, changed terminal evidence is recorded only
through `post-terminal-drift-recorded`. It records portfolio drift, blocks
portfolio verification or archive, and does not reopen Goals
or resume implementation. Report the owner action; a later correction requires
a separately authorized fresh run.
