---
name: implement-feature
description: Execute ready Feature Spec bundles in visible ChatGPT desktop app tasks through merge-ready-but-unmerged pull requests. Use only when explicitly invoked.
---

# Implement Feature

## Purpose

Use this skill only when the owner explicitly invokes $implement-feature in the
ChatGPT desktop app. It is the single App-only implementation adapter and never
plans or repairs planning artifacts.

The root owns intake, the active-root claim, typed run state,
review deadlines, reconciliation, and final status. Exactly one visible App task
owns each implementation-eligible Feature Spec through the only successful App result:
`pull-request-ready-for-merge-but-not-merged`.

## Mandatory Runtime Surface Gate

This is the first runtime step. Before asking permission, reading sources,
persistence, or mutation, verify visible ChatGPT desktop app task creation, App-managed worktree
binding, `codex_app__set_thread_title`, live task-title observation, and
`create_goal`, `get_goal`, and `update_goal` in the root plus general visible-task
Goal-tool support. Goal state must support targeted readback and normal
`pending` to `active` to `complete` progress for both root and worker tasks.
Goal pause/resume and App heartbeat automation are not part of this runtime
contract. This gate does not create a task to inspect task-local tools.
Call `get_goal` once in the root. A `blocked` Goal returns `new-root-required`
before authorization: require a fresh App task; do not read
sources, preflight, claim, create artifacts, or call `create_goal`/`update_goal`.
Prior artifacts stay untouched. CLI/background-agent access does not prove this
surface. If any capability is absent or unverifiable, return
`unsupported-runtime` without asking permission or creating artifacts.

## Mandatory Run Authorization

After the surface gate, load `references/options.md` and
`references/task-model-policy.md`. Verify that visible-task creation and
steering support the exact model and bounded adaptive thinking policy. Otherwise
return `unsupported-runtime` without artifacts.

Resolve `visible_app_task_permission`. When `not-requested`, ask once using the
standard disclosure, exact question, and two fixed answers in
`references/options.md`. Together they disclose the exact visible-task model,
thinking policy, fixed flow, retention, and no-merge boundary. Keep them
adjacent; do not improvise them, expose controller terms, or define the
App-owned free-form response.

Continue only with
`visible_app_task_permission=granted-by-authorized-user`. Denial, silence, or
inability to ask stops without artifacts. Generic delegation or subagent
authority never supplies this grant. The grant covers only the accepted bundle
and fixed execution flow; it does not authorize scope expansion, planning,
merge, release, or deployment.

## Fixed Contract

- Success means real `OPEN`, non-draft, conflict-free pull requests against each
  repository's discovered default branch, at their current heads, with mandatory
  terminal `$autoreview`, Codex review, CI, integration, tracker-closeout,
  mergeability, approval, update, and merge-queue eligibility gates satisfied.
  Unknown or pending evidence blocks except exact 45-minute `timeout-accepted`.
  Never enqueue or merge.
- Every terminal PR targets its discovered default branch; the base is derived
  and verified, never selected by the user or source. A draft is only a vehicle;
  convert it to ready-for-review after substantive proof and terminal
  `$autoreview`, before current-revision review and CI. This transition is not
  the terminal result.
- Use only App-managed worktrees. Never create raw Git worktrees, rotate the
  caller checkout, or implement in the root or a background worker.
- Create exactly one visible task per Feature Spec, including a multi-repository
  Spec, and at most three nonterminal Spec tasks. Every created, resumed, or
  steered task uses the recorded per-Spec model profile.
- After CLAIM, give the calling task the stable root title defined by
  `references/run-state.md`: `👨🏻‍💻 Feature Orchestrator` for one executable Spec
  or `👨🏻‍💻 Multi-Feature Orchestrator` for more than one, with no counter.
- Give every task a root-owned display title: one relevant emoji, one space, and
  the exact authored Feature Spec title. Use `🛠️` only when nothing is clearer;
  the title is UI evidence, not identity.
- The root performs cache maintenance synchronously after CLAIM. It never uses a
  task, Goal, worktree, or internal subagent for cache work.
- This skill never merges a pull request. A later merge request must start a
  separate GitHub workflow.

## Execution-Ready Intake

After authorization, load `references/spec-backed-delivery.md` and take one
read-only snapshot of the durable Spec/issue graph. Derive/preflight deliveries and reuse
the exact bytes for intake and fingerprinting. Proven drift requires refetch
and preflight before CLAIM.
That reference canonically owns accepted fields, graph rules, fingerprints,
scope, local-tracker paths, cross-Spec dependencies, integration partials,
domain-knowledge closeout, and rejected legacy fields. Load
`references/multi-repo-workspace.md` when any Spec affects multiple repositories
or the bundle contains partial and integration Specs, even when each Spec is
single-repository.

Require exactly one Feature Spec owner for every implementation-bundle
`(repository, target_branch_name)` pair. Coordination-only parent/global
artifacts create no task. The same branch name in different repositories is
valid; two executable Specs in the same repository collide even when paths are
disjoint. Return `planning-required` before CLAIM; never serialize around the
collision, rename the branch, or force-bind an App-managed worktree.

Validate stable refs, scope, earlier-only dependencies, acyclic intra- and
cross-Spec graphs, repositories, allowed paths, acceptance, validation, GitHub
delivery compatibility, and integration gates. Resolve each accepted Spec's
task profile before CLAIM. Missing or contradictory evidence is
`planning-required`; an explicit non-App target is
`unsupported-app-delivery-target`. Never create, repair, publish, or mutate
planning or tracker artifacts. Report exact failures and that no claim, run state,
Goal, task, tracker write, or source mutation was created.

## Controller Loop

0. **SURFACE** — prove the required App and Goal surfaces; reject a blocked root
   Goal as `new-root-required`.
1. **AUTHORIZE** — verify the model policy and obtain the fixed-flow grant.
2. **SNAPSHOT** — acquire the complete bundle once as temporary data; prepare
   its canonical bundle and delivery set.
3. **DELIVERY-PREFLIGHT** — with `references/execution-manifest.md`,
   prepare/run/verify `delivery-preflight` manifest. Require GitHub push/PR
   access, read access to PR lifecycle,
   mergeability/conflicts, and policy visibility; classify CI as `configured`
   or `not-configured`. Unknown or blocked capability returns
   `delivery-preflight-failed` with zero artifacts. `not-configured` is valid.
4. **INTAKE** — validate/fingerprint the snapshot; resolve profiles and require
   deliveries equal preflight. Convert verified GitHub `owner/repository#N` to
   `https://github.com/owner/repository/issues/N`; use the URL as the claim/task
   source id while preserving the authored ref as evidence.
5. **CLAIM** — load `references/run-state.md`; run
   `scripts/active-root-claim --json doctor`; canonicalize repositories and
   sources; acquire before any other artifact. Qualify local refs as
   `git:<git-common-dir>::ref:<source-ref>`. Never pass GitHub shorthand directly to the
   helper.
6. **CACHE-MAINTENANCE** — load `references/cache-lifecycle.md`; run its doctor
   and fixed 180-day prune once in the root. Warnings are nonblocking.
7. **REGISTER** — call `ledger create` with authorization/sources, complete Spec
   registry, repository deliveries, preflight/CI, fresh portfolio objective,
   and `portfolio_goal_state=pending`; persist `root_task_title`, then set and
   observe the calling task title. Reconcile with `get_goal`; otherwise call
   `create_goal`. Persist active evidence. Never set `token_budget`.
8. **DISPATCH** — load `references/worker.md`; choose the deterministic static
   ready set; adopt/create one managed task per Spec with its profile; observe
   title, Goal tools/objective, and complete delivery checkout map before
   advancing beyond `created`.
9. **MONITOR** — after one full post-dispatch snapshot, consume compact deltas
   until material transition, attention, heartbeat, or workflow deadline. Steer
   with the recorded profile; never pull worker work into root.
10. **GATE** — load `references/gates.md` and
   `references/codex-review-closeout.md`; apply task-static,
   delivery-revision, and complete task-revision-set evidence at its canonical
   scope.
11. **RECONCILE** — read the smallest ledger projection, refresh changed external
    evidence, atomically apply events, then dispatch, reconcile the fixed review
    wait, or advance one staged closeout transition.

An unchanged controller observation timeout performs only a required claim
heartbeat. It creates no run-state event or no-progress record. Use a full task
read only for startup verification, anomaly or blocker diagnosis, and independent terminal
verification. The worker owns the single bounded provider wait; the root never
polls the same provider in parallel. If the exact review is still pending at
the 45-minute deadline, persist the required warning evidence and continue
under the explicit `timeout-accepted` result. Root and worker Goals remain
active until their normal terminal completion.

## Scheduling

A Spec is ready when every upstream ref is merged, static gates pass, and its
registered paths do not overlap a running/selected Spec. Managed checkouts are
post-creation evidence; requiring them here would deadlock dispatch. A merge-ready but
unmerged upstream does not make a downstream ready. Record the dependency wait
and exact external merge action. If all work waits on it, retain the claim and
active state and require explicit same-root resume; do not fabricate a review
schedule, handoff, or release.

Sort ready candidates by canonical claim/task source id ascending. Greedily
select up to the remaining three-task capacity with pairwise disjoint canonical
`(repository, path)` scopes. Treat missing, wildcard, and ancestor/descendant path
scopes as overlapping. Recompute from live evidence each wave; task count and
parallelism are not options.

## Claim, Takeover, And Recovery

`scripts/active-root-claim` is the sole ownership authority. Persist the claim
fingerprint, heartbeat while active, and use it for heartbeat and terminal
release. Review waits and dependency waits retain ownership.

An overlapping live claim returns `needs-owner`. For a stale claim, perform
  read-only discovery first and load the takeover contract in
  `references/run-state.md`. Before asking or stopping tasks, use the helper's
read-only status evidence to prove every conflicting heartbeat is at least its
fixed five-minute stale threshold. A stale heartbeat alone is never task-stop evidence.
Then resolve `stale_claim_takeover_permission` as specified by
`references/options.md`. A separate grant must name the complete repository/source scopes,
and tasks and disclose same-task interruption, verification, replacement, and
adoption. Denial creates no task mutation. Only after
`granted-by-authorized-user` may the root stop the tasks through the App runtime and
run `scripts/active-root-claim --json claim takeover`; partial-root takeover is
invalid.

The helper writes a prepared-takeover journal before it deletes any prior claim;
the journal remains an ownership record and embeds each full replaced-claim
snapshot plus validated per-Spec adoption data. Recover through `claim status`
and `claim recover-takeover`; adopt those exact tasks. Never create a new task
for a Spec that has recorded or embedded task evidence. The helper accepts only
current schema-5 claims and fails closed on unsupported claim or takeover state
without migration, retirement, or deletion.

Missing candidate state is created only from complete claim-embedded task/no-task
and delivery-checkout mappings. Creation binds that exact claim. Never add an
adoption event, rebind an existing state, or infer identity.

Before task creation, resume, read, or steering, load `references/worker.md`.
Every new task calls `create_goal` for its exact assignment. Recovery calls
`get_goal`, verifies the recorded objective and evidence, and resumes the same
visible task; never create another Goal or replacement task. Workers report
evidence; only the root changes portfolio state.

On manual resume, load `references/recovery-validation.md` before mutation and
revalidate the runtime surface, claim, source fingerprints, repositories, root
and task titles, Goals, managed checkouts, gates, and review waits. Archived run
states are cold evidence, never recovery input.

## Delivery And Final Report

Before terminal work, load `references/gates.md` and
`references/codex-review-closeout.md`. The visible task owns implementation,
validation, publication, `$autoreview`, current-revision review/fixes, CI when
configured, tracker closeout, and merge-ready proof; the root only verifies and
never enqueues or merges. On accepted AutoReview or PR findings, also load
`references/autoreview-fix-loop.md` before fixes.

For a local source, after current task-set acceptance/integration/domain proof,
move only predeclared refs in their deliveries. The move dirties delivery state
and invalidates old evidence. Commit/push, observe the new revision, rerun
validation and terminal `$autoreview`, convert drafts to
ready-for-review, obtain current-revision review, then configured CI or explicit
`not-configured` terminal revalidation, and terminal proof.
Hosted and local issues remain open until a later default-branch merge.

For pre-CLAIM aborts, report evidence and zero mutation. Otherwise return
run-state-derived source/title/task/Goal/checkout proof, changes, validation,
commits, PRs/revisions, CI, domain/tracker closeout, current-head mergeability
and repository-rule evidence, captured domain-closeout evidence, review
warnings, blockers, recovery freshness,
and next action.

After root-title revalidation, close out only in this order:
`task-terminal-sealed`, worker Goal/readback, `task-goal-completed`,
`terminal-handoff-recorded`, `portfolio-terminal-verified`, root Goal/readback,
`portfolio-goal-completed`, release and archive. Failure retains active state.

An exact Codex review that remains pending after the fixed 45-minute wait is not
reported as clean. Post a persistent warning on the PR, persist its reference as
`timeout-accepted`, warn the user in the final report, and continue the
remaining gates. Review request failure, access uncertainty, findings, and
missing request evidence remain blockers. A later merge workflow must re-check
late Codex findings before merge.
Post-terminal drift blocks archive and never reopens Goals or implementation.

## Reference Routing

`run-state.md` owns commands, projections, and transitions;
`run-state-packets.md` owns event fields before writes; `execution-manifest.md`
owns bundles plus supported command manifests and receipts.
Load `review-thread-resolution.md` only for inline finding ids or stored receipts.
