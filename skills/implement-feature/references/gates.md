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

`dependency-integration` is `task-static`: dispatch only after every cross-Spec
dependency is merged; merge-ready is unfinished. Registered preflight is typed
delivery state, not another gate. Neither requires a PR revision.

Multi-repository completion requires exactly one distinct repo-owned
integration Feature Spec downstream of all implementation partials. It owns a
bounded path change and cross-repository proof and produces a real PR rather
than a no-op validation result.

## Delivery-Revision Gates

Registration binds each delivery's passed GitHub/default-base capability,
`ci_availability`, `preflight_key`, and evidence ref. Only `configured` or
`not-configured` is valid; incomplete inspection blocks before CLAIM. Before
seal, `delivery-preflight-observed` may replace it; after seal, only
post-terminal drift may record change.

For each delivery's current exact repository, PR number and URL, head SHA, base
ref, and merge-base SHA require:

- `publication`: real PR identity, lifecycle `OPEN`, and base equal to that
  repository's currently discovered default branch;
- `codex-review`: mandatory current-revision request with either a clean result,
  or an exact 45-minute pending timeout recorded as `timeout-accepted` with a
  persistent PR warning;
- `ci`, only when `ci_availability=configured`: at least one applicable run or
  status context on the exact head SHA and every required applicable result
  successful;
- `pr-ready`: non-draft exact PR identity after the ready-for-review transition;
- `tracker-closeout`: every applicable closing vehicle prepared at the current
  delivery revision;
- `mergeability`: conflict-free GitHub mergeability plus required base
  freshness, approvals, and merge-queue eligibility.

For `focused-validation`, `full-validation`, and `autoreview`, require a
verified current command receipt from `execution-manifest.md`. Its gate
fingerprint must bind the current bundle, checkout cwd, exact argv, pinned
tools/dependencies, write policy, and outputs. A pre-call manifest or finding
validation failure is not a gate result and consumes no AutoReview budget.

When `ci_availability=not-configured`, do not emit, wait for, poll, or accept a
`ci` gate; report availability, never `passed`. For configured CI, skipped or
neutral counts only when rules prove it optional. Unknown, pending,
dirty/conflicting, stale-required, closed, merged, or blocked truth fails.
Never enqueue or merge.

A draft is only an intermediate vehicle. After substantive implementation,
focused validation, and terminal `$autoreview` evidence, convert it to ready-for-review with
`isDraft=false`; only then obtain approval and final rule evidence. Do not make
draft status a circular prerequisite for mergeability. The transition is not
terminal.

## Task-Revision-Set Gates

The delivery evidence key hashes current revision and preflight keys. The task
revision-set key contains every delivery evidence key. Bind
`scope-acceptance`, `integration-validation`, and optional `domain-closeout` to
that set; bind `focused-validation`, `full-validation`, and `autoreview` per
delivery key. Partial sets fail.

The `autoreview` gate requires terminal `autoreview-observed` evidence for the
current head/base/merge-base; repository or scope drift starts a new lineage.

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

Any delivery revision, preflight fingerprint, CI availability, PR identity,
material diff, repository-rule, tracker
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
rerun final validation and establish terminal `$autoreview` evidence, convert drafts to ready-for-review,
then obtain current-revision review and configured CI, or independently
revalidate explicit `not-configured`, before terminal merge-ready state.
Record closeout as prepared; completion reaches the default branch only after a
later merge. GitHub sources cannot use `source-moved`.

## Staged Terminal Gate

Closeout must not be circular. Use this order:

1. Prove every applicable static, delivery-revision, and task-revision-set gate
   at the current complete revision set; apply `task-terminal-sealed`.
2. Apply `terminal-handoff-recorded` with the unchanged seal fingerprint,
   `pull-request-ready` kind, fixed `external-merge-required` authority, and
   next action.
3. After all tasks, independently reverify current proof and apply
   `portfolio-terminal-verified`.
4. Complete and read back the root Goal; apply `portfolio-goal-completed`.
5. Release and archive through `cache-lifecycle.md`.

The machine-derived terminal projection exposes readiness for each stage.
Review monitoring retains the active claim and cannot satisfy terminal
handoff. Neither the root nor a task merges, performs
post-merge verification, or closes hosted tracker items.

Review request has no skip; every delivery-revision review gate is mandatory.
`timeout-accepted` passes only that gate and is never equivalent to a clean
verdict. It cannot override CI, mergeability, branch rules, approvals, or any
repository-required review state. Surface its warning in terminal evidence, and
require the later merge workflow to re-check late Codex findings.

After a task seal or Goal completion, changed terminal evidence is recorded only
through `post-terminal-drift-recorded`. It records portfolio drift, blocks
portfolio verification or archive, and does not reopen Goals
or resume implementation. Report the owner action; a later correction requires
a separately authorized fresh run.
