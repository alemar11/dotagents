---
name: implement-feature
description: Execute ready Feature Spec bundles in visible ChatGPT desktop app tasks through merge-ready-but-unmerged pull requests. Use only when explicitly invoked.
---

# Implement Feature

## Purpose

Use this Codex-dependent skill only when the owner explicitly invokes $implement-feature
or asks to run Implement Feature in the ChatGPT desktop
app. It is the single App-only implementation adapter: it never plans, repairs
planning artifacts, or invokes another orchestrator.

The root owns authorization, intake, the active-root claim, the ledger,
scheduling, monitoring, and final status. Exactly one visible App task owns each
implementation-eligible Feature Spec through the only successful App result:
`pull-request-ready-for-merge-but-not-merged`.

## Mandatory Runtime Surface Gate

This is the first runtime step. Before asking permission, reading sources,
persistence, or mutation, verify visible ChatGPT desktop app task creation, App-managed worktree
binding, `codex_app__set_thread_title`, live task-title observation, and
`create_goal`, `get_goal`, and `update_goal` in the root plus general visible-task
Goal-tool support. This gate does not create a task to inspect task-local tools.
Filesystem, CLI, local skill, or background-agent access does not prove this
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
  `$autoreview`, Codex review, CI, integration, tracker-closeout, mergeability,
  approval, update, and merge-queue eligibility gates satisfied. Unknown or
  pending evidence blocks. Never enqueue or merge.
- Every terminal PR targets its discovered default branch; the base is derived
  and verified, never selected by the user or source. A draft is only a vehicle;
  convert it to ready-for-review after substantive proof and `$autoreview`, before
  current-revision review and CI. This transition is not the terminal result.
- Use only App-managed worktrees. Never create raw Git worktrees, rotate the
  caller checkout, or implement in the root or a background worker.
- Create exactly one visible task per Feature Spec, including a multi-repository
  Spec, and at most three nonterminal Spec tasks. Every created, resumed, or
  steered task uses the recorded per-Spec model profile.
- After CLAIM, give the calling task the stable root title defined by
  `references/ledger.md`: `👨🏻‍💻 Feature Orchestrator` for one executable Spec
  or `👨🏻‍💻 Multi-Feature Orchestrator` for more than one, with no counter.
- Give every task a root-owned display title: one relevant emoji, one space, and
  the exact authored Feature Spec title. Use `🛠️` only when nothing is clearer;
  the title is UI evidence, not identity.
- The root performs cache maintenance synchronously after CLAIM. It never uses a
  task, Goal, worktree, or internal subagent for cache work.
- This skill never merges a pull request. A later merge request must start a
  separate GitHub workflow.

## Execution-Ready Intake

After authorization, load `references/spec-backed-delivery.md` and perform one
read-only intake of the complete durable Feature Spec and generated-issue graph.
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
planning or tracker artifacts. Report exact failures and that no claim, ledger,
Goal, task, tracker write, or source mutation was created.

## Controller Loop

0. **SURFACE** — prove the required App and Goal surfaces.
1. **AUTHORIZE** — verify the model policy and obtain the fixed-flow grant.
2. **INTAKE** — validate and fingerprint the complete bundle; resolve each task
   profile. Convert verified GitHub `owner/repository#N` refs to
   `https://github.com/owner/repository/issues/N`; use the URL as the claim/task source id while
   preserving the authored ref as evidence.
3. **CLAIM** — load `references/ledger.md`; run
   `scripts/active-root-claim --json doctor`; canonicalize repositories and
   sources; acquire before any other artifact. Qualify local refs as
   `git:<git-common-dir>::ref:<source-ref>`. Never pass GitHub shorthand directly to the
   helper.
4. **CACHE-MAINTENANCE** — load `references/cache-lifecycle.md`; run its doctor
   and fixed 180-day prune once in the root. Warnings are nonblocking.
5. **REGISTER** — create the ledger, authorization/source snapshots, and complete
   Spec registry with the portfolio objective and `portfolio_goal_state=pending`;
   persist `root_task_title`, then set and observe the calling task title. Only
   then reconcile with `get_goal`; otherwise call `create_goal`. Persist active
   evidence. Never set `token_budget`.
6. **PR-PREFLIGHT** — for every repository prove GitHub access, branch/PR
   publication, current-head review, CI expected to produce at least one
   applicable result, and read
   access to PR lifecycle, mergeability/conflicts, branch rules, approvals,
   base-freshness, and merge-queue eligibility. Discover the default base.
   Otherwise return `pr-preflight-failed`; never downgrade.
7. **DISPATCH** — load `references/worker.md`; choose the deterministic ready
   set; adopt exact takeover tasks or create one managed visible task per Spec
   with its recorded profile; set and observe its title; verify that exact task's Goal tools
   and assignment Goal before advancing beyond `created`.
8. **MONITOR** — reconcile live task evidence and steer precise corrections with
   the recorded profile. Never pull implementation or review into the root.
9. **GATE** — load `references/gates.md` and
   `references/codex-review-closeout.md`; require every fixed terminal gate.
10. **RECONCILE** — refresh sources, claim, merged dependencies, tasks, review
    waits, ledger, and recovery; dispatch another wave or record the blocker or
    durable handoff.

Every wave must produce a transition, evidence update, owner decision, or
explicit no-progress record. After the first wave, load
`references/runtime-efficiency.md` when delta evidence can avoid redundant
reads without weakening a freshness gate.

## Scheduling

A Spec is ready only when every upstream ref in its parent
`## Feature Dependencies` table is merged, its managed checkouts are available,
and its paths do not overlap a running or selected Spec. A merge-ready but
unmerged upstream does not make a downstream ready. Record the external merge handoff; if all work
waits on it, release through a durable handoff and require an explicit resume.

Sort ready candidates by canonical claim/task source id ascending. Greedily
select up to the remaining three-task capacity with pairwise disjoint canonical
`(repository, path)` scopes. Treat missing, wildcard, and ancestor/descendant path
scopes as overlapping. Recompute from live evidence each wave; task count and
parallelism are not options.

## Claim, Takeover, And Recovery

`scripts/active-root-claim` is the sole ownership authority. Persist the claim
fingerprint, heartbeat while active, and use it for heartbeat and release.
Release only after terminal proof or a recorded durable handoff.

An overlapping live claim returns `needs-owner`. For a stale claim, perform
read-only discovery first and load the takeover contract in
`references/ledger.md`. Before asking or stopping tasks, use the helper's
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

Before task creation, resume, read, or steering, load `references/worker.md`.
Every new task calls `create_goal` for its exact assignment. Recovery calls
`get_goal`, verifies the recorded objective and evidence, and resumes the same
visible task; never create another Goal or replacement task. Workers report
evidence; only the root changes portfolio state.

On resume, load `references/recovery-validation.md` before mutation and
revalidate the runtime surface, claim, source fingerprints, repositories, root
and task titles, Goals, managed checkouts, gates, and review waits. Archived
ledgers are cold evidence, never recovery input.

## Delivery And Final Report

Before review or terminal acceptance, load `references/gates.md` and
`references/codex-review-closeout.md`. The visible task owns implementation,
validation, commits, publication, `$autoreview`, current-revision review/fixes,
CI, tracker-closeout preparation, ready-for-review transition, and merge-ready
proof for every affected repository. The root verifies the evidence and never
enqueues or merges.

For a local source, after substantive acceptance, integration, and domain
closeout, move issues to the configured done folder, commit and push, rerun
validation and `$autoreview`, convert drafts to ready-for-review, obtain
current-revision review, then CI and terminal merge-ready proof. Hosted and local
issues remain open until a later default-branch merge.

For pre-CLAIM aborts, report the evidence and zero-mutation result. Otherwise
return ledger-derived source fingerprints, title, task/Goal and checkout proof,
changes, validation, commits, PR URLs, reviewed revisions, CI, captured
domain-closeout evidence, prepared tracker closeout, current-head mergeability
and repository-rule evidence, blockers, recovery freshness, and next action.

Before terminal release, revalidate exact root-title evidence; every task and the
root then call `update_goal` with `status=complete`. Persist
`portfolio_goal_state=complete` and its evidence, then run the complete terminal
release/archive sequence in `references/cache-lifecycle.md`. A
failed title, completion, or evidence write retains the claim and active ledger. A
resumable handoff uses that reference's complete durable-handoff release and
retains its ledger and active nonterminal Goals. Recovery may finish only a fully
revalidated completion, release, or archive transition; it never resumes
implementation after terminal proof.

## Reference Routing

Use the load predicates above. When loading `references/ledger.md`, also load
`references/ledger-template.md`.
