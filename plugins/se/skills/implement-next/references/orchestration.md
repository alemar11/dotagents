# Implement Next Orchestration

Load this reference for graph scheduling, multi-repository topology, resume,
worker concurrency, pull-request stacks, claim conflicts, or workflow
transitions. `SKILL.md` owns the workflow node registry; this reference owns
the condition for every declared edge.

## Workflow transition conditions

| from | to | when |
| --- | --- | --- |
| intake | claim-repositories | Every exact selected parent Feature, its body-backed dependencies, repository identities, and visible home are resolved without a material user choice. |
| intake | deferred | A material semantic choice remains that the caller can resolve. |
| intake | blocked | The selection is invalid, cyclic, unreadable, or cannot be mapped to authoritative repositories. |
| claim-repositories | claim-repositories | One orchestrator-creation attempt is authoritatively proved not applied; retry task creation once under the same provisional claim. |
| claim-repositories | reconcile | The complete claim is independently acquired or reused, correlated to one stable orchestrator identity, bound, and read back. |
| claim-repositories | blocked | Claim overlap, provisional task effects, binding, or orchestrator identity cannot be reconciled safely. |
| reconcile | schedule | At least one selected Feature remains unfinished and current authoritative evidence supports another scheduling decision. |
| reconcile | release-claims | The caller explicitly requested handoff or abandonment and every task created by the orchestrator is independently quiescent. |
| reconcile | complete | Every selected Feature has a current exact-HEAD pull request whose applicable required validation, review, and CI gates pass with no unresolved blocker, or is proved already incorporated into its integration base, and no explicit release is pending. |
| reconcile | deferred | Safe continuation requires a material semantic decision or additional user authority. |
| reconcile | blocked | Required capability, identity, ownership, or effect evidence remains unavailable or ambiguous. |
| schedule | deliver-feature | One or more dependency-ready Features are not already assigned to an independently observed active lane and have verified bases, topology, and trustworthy worker targets. |
| schedule | reconcile | No new assignment should start because only active lanes remain or until a bounded authoritative refresh observes a material Git, pull-request, review, CI, task, or Feature change. |
| schedule | deferred | The only responsible continuation requires a material user decision or authority. |
| schedule | blocked | Unfinished work has no responsible ready, refresh, or user-decision path. |
| deliver-feature | reconcile | A worker returns exact completion, partial progress, correction, or blocker evidence; concurrent returns reconcile independently. |
| release-claims | complete | Exact whole-group release is independently verified. |
| release-claims | blocked | Release cannot be proved exact and safe. |

`schedule -> reconcile` is a change-driven wait loop, not a busy poll. Terminal
nodes have no outgoing transitions. A resumed invocation starts at `intake` and
reconstructs its continuation through `claim-repositories -> reconcile`; task
history or a claim row never acts as a persisted current-node pointer.

## Orchestrator placement

The orchestrator is the visible owner of one caller-selected Feature graph or
set. Use the single involved saved project as its home. For a graph spanning
several projects, prefer the current associated project when it visibly groups
the whole run; otherwise use the caller-selected coordination project. Ask
only when several plausible homes remain. The workers still run in their
repository projects and isolated worktrees. A projectless orchestrator is only
a warned fallback; use `projectless` as its visible-home claim key. It does not
change repository ownership.

Freeze all repository identities before acquisition. Version 1 does not expand
a live claim because independent multi-repository expansion can deadlock and
can make the intended visible home ambiguous.

## Task metadata and worker targets

Set display titles when tasks are created:

- orchestrator: `🤖 Implement · <Feature or graph name>`;
- worker: `🛠 <repository> · <current Feature>`.

Best-effort rename a reused worker for its current Feature. Titles and project
grouping are diagnostics, never identity, correctness evidence, or a reason to
retry or replace a task.

Use the configured model and reasoning defaults unless the caller explicitly
requests another profile. If a caller makes a profile acceptance-critical,
verify it or report that it cannot be established; otherwise profile metadata
does not gate delivery.

Resolve one integration branch per repository before scheduling. A
repository-qualified caller override wins; otherwise use the authoritative
provider default. Reject a missing, ambiguous, inaccessible, or
wrong-repository selection without fallback. Through the applicable G-owned
branch transport, refresh that upstream branch and read its full remote tip.
Freeze the branch and SHA for the current bootstrap wave, reread them before
each standalone or stack-root bootstrap, and recompute unstarted work if the tip
changes. Never infer a base from the current checkout, a stale tracking ref,
project metadata, or a branch name alone.

Before any fresh worker mutation, independently observe its actual stable
repository identity, remote, isolated worktree, current branch, and full
starting SHA. Require an exact match with its handoff. A fresh worker then
establishes the intended Feature head branch from that verified integration
base or prerequisite HEAD and reads back the branch and initial HEAD before
content writes. Missing or mismatched evidence stops that lane.

Before reassigning a clean worker, first verify the prior Feature's expected
head branch and current HEAD and prove its worktree clean and unambiguous. Then
switch through G-owned branch transport to the next Feature's independently
verified integration base or prerequisite HEAD, read back that starting branch
and SHA, create the new Feature head, and read back its initial HEAD before
content writes. A same-Feature resume instead remains on its expected head
branch, verifies current HEAD, and preserves inspected dirty work. Saved-project
placement, task title, and prior dialogue never substitute for these facts.

## Scheduling

Derive the ready frontier from the body-backed Feature Plan Set registry and
declared dependency graph plus live delivery evidence. Native GitHub
`blockedBy` or reciprocal `blocking` observations are diagnostic only: they
never add, remove, repair, reverse, or gate a body-declared edge. Inspect every
declared prerequisite whether it is selected or not; selection never expands
implicitly. An unselected prerequisite is satisfied only when current
authoritative evidence proves its implementation is already incorporated into
the intended base or its current candidate meets the same dependency and
topology rules. Otherwise block the dependent and report the missing
prerequisite without starting extra work. The orchestrator decides concurrency;
the graph never forces parallel work.

Exclude every Feature already assigned to an independently observed active
worker lane from the ready frontier. If only active lanes remain, take the
change-driven `schedule -> reconcile` path after a bounded wait or authoritative
refresh. Never create or recall a second lane for the same active Feature.

A cross-repository dependent becomes ready when every declared prerequisite
has a verified published pull request at its current exact HEAD plus the
contract and validation evidence needed to implement the dependent safely, or
is already incorporated into the intended base. Apply this rule to selected
and unselected prerequisites alike. Merge is unnecessary unless the Feature
contract itself requires merged or deployed behavior. A cross-repository edge
never changes either pull request's base.

A current prerequisite candidate does not unblock its dependent while an
applicable check on that exact HEAD is confirmed failing. Pending checks are
non-blocking. Bypass a confirmed failure only when G-owned diagnosis verifies
it as exclusively infrastructure or flaky and unrelated to candidate
correctness.

Prefer one active lane per repository. Add a lane only when ready Features are
genuinely independent, the repository can support concurrent isolated changes,
and the latency benefit exceeds the integration cost. Serialize when work
overlaps, a dependency supplies code or API needed by its child, or one lane is
enough to preserve momentum.

Reassign a worker to a different Feature only when its prior work is committed,
its worktree is clean and unambiguous, and the next base is known. Resume the
same Feature in the same task and worktree after inspecting and preserving its
uncommitted work. A worker reassigned to another Feature switches to a new
verified starting point and branch under the protocol above, then returns new
exact evidence. Never treat the old Feature title or dialogue as current
implementation state.

## Pull-request graph

Use one branch and one pull request per Feature delta.

- A same-repository dependency creates a stack while its prerequisite remains a
  current candidate. Branch the child from the verified parent branch or HEAD
  after the current-head check rule above, and target the child's pull request
  at the immediate parent branch. When every required same-repository
  prerequisite exact HEAD is already incorporated into the verified integration
  base, make the dependent a new stack root from and against that integration
  base; never target a merged or deleted parent branch.
- A cross-repository dependency affects readiness only. Each repository keeps
  a standalone pull request against its own integration base.
- Independent same-repository Features remain sibling branches. If
  implementation discovers a semantic ancestry dependency absent from the
  body-backed Feature graph, stop the affected work for Feature graph or user
  reconciliation instead of inventing a stack edge.

For same-repository fan-in, choose one immediate parent only when that
candidate already contains every required prerequisite HEAD. Otherwise stop
the dependent for Feature graph reconciliation; never omit a prerequisite or
invent a multi-base pull request.

If a stack parent changes, identify every descendant whose ancestry or
validation depends on it, restack those branches in order, and revalidate the
affected exact HEADs. Do not infer readiness from an older parent SHA.

Before every handoff to a G-owned workflow, the orchestrator or worker making
that handoff runs the shared
[codex-dependency-preflight.md](../../../references/codex-dependency-preflight.md).
Before any hosted pull-request, review, or stack write, that same role applies
the shared
[hosted-content-safety.md](../../../references/hosted-content-safety.md)
contract to the final rendered content. Carry both obligations in every worker
handoff that permits G-owned work; an orchestrator check never substitutes for
the worker's own check.

## Resume and replacement

Reconstruct current truth in this order:

1. authoritative Feature issue content and dependency relations;
2. current repository branches, commits, and worktrees;
3. current pull-request, review, and CI state;
4. visible Codex task history and worker handoffs;
5. the repository registry only for orchestrator ownership.

The registry does not prove that a worker is running, a branch is clean, a PR
exists, or validation passed. Reconcile those facts from their owners.

Recall the same worker for a repair, rebase, or review fix when its task and
worktree remain trustworthy. Create a replacement lane only when the old lane
is unavailable or unsafe and current Git state is independently understood.
Replacing a worker does not replace the orchestrator or alter the claim.

For an ambiguous task or provider effect, inspect current authoritative state
once. Continue from a proved effect, retry only after proved non-application,
and stop on unresolved ambiguity. Do not introduce an operation journal to
make an uncertain effect appear known.

A worker may replace an invalid or unavailable evidence command with a
platform-correct command when outcome, scope, acceptance criteria,
dependencies, and non-goals remain unchanged. Record the substitution and
continue in the same task and worktree. Material semantic drift requires user
direction; a validation-only correction never requires a new claim,
orchestrator, or worker.
