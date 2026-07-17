---
name: implement-feature
description: Execute execution-ready Feature Spec bundles in visible Codex App tasks through reviewed, CI-clean, merge-ready-but-unmerged pull requests. Use only when the user explicitly invokes $implement-feature or asks to run Implement Feature in the Codex App.
---

# Implement Feature

## Purpose

Use this Codex-dependent skill only when the owner explicitly invokes
`$implement-feature` or asks to run Implement Feature in the Codex App. It is the
single App-only implementation adapter. It never plans work and never invokes
another orchestrator.

The root owns runtime validation, authorization, the active-root claim,
portfolio persistence, deterministic scheduling, monitoring, and final status.
Exactly one visible App task owns each implementation-eligible Feature Spec
through the fixed terminal result
`pull-request-ready-for-merge-but-not-merged`.

## Mandatory Runtime Surface Gate

This is the first runtime step. Before asking permission, reading source
artifacts, acquiring a claim, creating persistence, or performing any mutation,
verify that the current runtime exposes both visible Codex App task creation and
App-managed worktree binding.

Generic or background subagents, filesystem access, an interactive CLI, and
local skill discovery do not prove this surface. If either App capability is
absent or unverifiable, abort as `unsupported-runtime` without asking
permission, recommending another orchestrator, or creating artifacts.

## Mandatory Run Authorization

After the surface gate, load `references/options.md` and
`references/task-model-policy.md`. Verify the canonical model and allowed
thinking values against both visible-task creation and follow-up steering before
asking permission. If that support is absent or unverifiable, abort as
`unsupported-runtime` without runtime artifacts. Then resolve
`visible_app_task_permission` from the invocation. If it is `not-requested`, ask
the user once whether to create exactly one visible App task per executable
Feature Spec and run the complete fixed implementation flow.

The question must disclose the exact visible-task model, the bounded adaptive
thinking policy and its default, and that the flow may inspect, edit, validate,
commit, push, publish or update pull requests, request and poll current-revision
Codex review, fix findings, wait for CI, prepare tracker closeout, convert draft
pull requests to ready-for-review, move completed local Markdown issue files to
their configured done folder on the delivery branch after substantive proof,
commit and push those moves, rerun the resulting current-head gates, and report
without merging. Continue only with
`visible_app_task_permission=granted-by-authorized-user`. Denial, no answer, or
inability to ask aborts without implementation or runtime artifacts. Generic
delegation or subagent authority never supplies this grant.

The grant is run-scoped. It authorizes the fixed flow over the accepted bundle;
it does not repair incomplete planning, expand scope, merge, release, deploy, or
change target-repository instructions.

## Fixed Implementation Contract

- The only successful App result is
  `pull-request-ready-for-merge-but-not-merged`. Draft-only, commit-only,
  push-only, uncommitted, and merged outcomes are not successful conclusions.
- Current-revision Codex review and CI are mandatory. Neither can be skipped by
  a user option.
- Every terminal PR targets the affected repository's discovered default branch.
  The base is derived and verified, never selected by a user or Feature Spec.
- Every terminal PR has GitHub lifecycle `OPEN` and is verified mergeable for
  its current head/base tuple: no
  conflicts, no unknown or pending mergeability, and every repository-required
  update, approval, and merge-queue eligibility condition is satisfied. The
  task never enqueues or merges it.
- A draft PR is only an implementation vehicle. After substantive
  implementation, validation, and `$autoreview`, convert it to ready-for-review
  (`isDraft=false`) before waiting on repository approvals or evaluating final
  mergeability. That transition is not the terminal result.
- Use only App-managed worktrees. Never create or repair raw Git worktrees,
  rotate the caller checkout, or implement in the root or a background worker.
- Every created, steered, or resumed visible task uses the per-Spec profile
  resolved from `references/task-model-policy.md`; the root never substitutes or
  omits its model or thinking value.
- Create exactly one visible task per Feature Spec, including a multi-repository
  Spec. The task owns implementation, validation, commits, publication,
  `$autoreview`, current-revision review/fixes, CI, tracker-closeout preparation,
  ready-for-review transition, and terminal merge-ready evidence for every
  affected repository.
- Keep at most three nonterminal Feature Spec tasks. Internal subagents remain
  inside their parent Spec slot and inherited scope.
- This skill never merges a pull request. A later merge request must start a
  separate GitHub workflow.

## Execution-Ready Intake

After authorization, load `references/spec-backed-delivery.md` and perform one
read-only intake. Accept GitHub-hosted or local-Markdown bundles containing a
durable Feature Spec and its complete generated implementation-issue graph.

Each generated issue must contain one canonical `## Execution Contract` with
the source Spec ref, feature slug, affected repositories, allowed paths, shared
per-Spec target branch name, and earlier generated issue dependency ids. Requirements,
acceptance criteria, and validation commands remain authoritative in their
existing issue sections. Read cross-Spec edges only from the parent Feature
Spec's `## Feature Dependencies` table. A Feature Spec body must never persist
`knowledge_delta` or `## Domain Knowledge Handoff`; the exact payload may appear
only in the final issue's `## Domain Knowledge Closeout` when durable closeout
work exists. Normalize every payload target surface to one repository and one
portable repo-relative path, then require that final issue to name the
repository in `affected_repositories` and contain the target path in
`allowed_paths`. An ambiguous or out-of-scope target makes the bundle
`planning-required`; intake never widens execution scope to accept it.
Require the sole closeout owner to be graph-final: in a single Spec it has no
dependents; exclude it and its own `dependency_ids`, derive the no-dependent
terminals in the remaining graph, and require direct dependencies on all of
them. In a multi-repository bundle apply that algorithm only to the unique final
issue of the dedicated integration partial. Its closeout section must carry the
exact `$project-memory` invocation with `memory_slice=domain-memory` and
`domain_operation=implementation-closeout` after integrated behavior is
proven.
Missing, duplicated, early, or graph-incomplete closeout data is
`planning-required`; intake never supplies it from worker doctrine.
For a nonempty accepted delta, terminal closeout requires
`capture_outcome=captured`, every item and named target reconciled, verified
destinations, and documentation-diff proof; `deferred` or `no-durable-change`
blocks the issue. A supplied accepted item rejected or contradicted by landed
behavior also blocks for an owner decision or separately authorized
planning/implementation correction.

Validate stable refs, complete scope, strictly-earlier intra-Spec dependency
IDs, separate acyclic intra-Spec and cross-Spec dependency graphs, affected
repositories, path ownership, acceptance,
validation, GitHub delivery compatibility, and integration gates. Compute
source and issue fingerprints from the authoritative artifacts; do not trust
source-supplied option hashes.
For a local Markdown issue, require its tracker-owning repository in
`affected_repositories` and its exact active plus derived `done/` paths in
`allowed_paths`; both paths must resolve inside an affected Git repository that
the App-managed checkout can expose. For every multi-repository bundle, require
exactly one distinct repo-owned integration Feature Spec with at least one issue
that owns a bounded path change plus cross-repository proof. Its target branch
must equal `<ordinary_target_branch_name>-integration`, derived from the
ordinary partial in the same repository, so a second App-managed task never
needs to bind an already-owned branch.
Across the implementation-eligible Specs in the complete portfolio, require
exactly one Feature Spec owner for each `(repository, target_branch_name)` pair.
Exclude coordination-only parent/global artifacts because they create no task
or App-managed worktree. The same branch name in different repositories is
valid; two executable Specs in the same repository collide even when their paths
are disjoint or dependencies would serialize them. Treat a collision as
`planning-required` before CLAIM. Never serialize around it, rename an authored
branch, or force-bind an App-managed worktree.
Reject retired handoff fields, delivery tuples, review skips, worker action
lists, parallelization fields, and non-App delivery markers as incompatible.

After the complete bundle passes intake, resolve one visible-task thinking level
per implementation-eligible Feature Spec from
`references/task-model-policy.md`. This is read-only derived runtime evidence,
not Feature Spec data or a user option. Resolve it before CLAIM; incomplete
evidence remains `planning-required` instead of receiving a stronger model
profile.

Never create, repair, regenerate, or publish planning artifacts; infer missing
implementation detail; mutate trackers; or invoke a planning skill during
intake. Missing, contradictory, stale, or non-durable evidence aborts as
`planning-required` before CLAIM. An explicit non-App contract aborts as
`unsupported-app-delivery-target`. Report exact invalid fields and state that
no claim, ledger, Goal, task, tracker write, or source mutation was created.

## Controller Loop

0. **SURFACE** — verify visible task creation and App-managed worktree binding.
1. **AUTHORIZE** — verify and disclose the fixed model plus bounded adaptive
   thinking policy, then obtain the one fixed-flow grant or abort.
2. **INTAKE** — validate and fingerprint the complete bundle read-only, then
   resolve and record each Spec's task profile before CLAIM. Resolve
   each verified GitHub `owner/repository#N` Feature Spec ref to canonical
   `https://github.com/owner/repository/issues/N`; preserve the authored ref as
   authoritative source evidence and use the URL as the claim/task source id.
3. **CLAIM** — run `scripts/orchestrator-claim --json doctor`; canonicalize the
   finalized repositories and source ids; then atomically acquire the claim
   before creating any other runtime artifact. Qualify repository-local source
   refs as `git:<git-common-dir>::ref:<source-ref>` and preserve globally durable
   URI-shaped ids. Never pass GitHub shorthand directly to the helper.
4. **REGISTER** — create the ledger projection, snapshot authorization and
   source fingerprints, and create the portfolio Goal or exact fallback.
5. **PR-PREFLIGHT** — require a GitHub target, authenticated access, branch
   publication, PR create/update capability, current-head review, and a
   discoverable CI path expected to produce at least one applicable result for
   every affected repository. Also require read access to PR lifecycle,
   mergeability/conflicts, branch rules, approvals, base-freshness requirements,
   and merge-queue eligibility; when that evidence cannot be observed, fail
   preflight rather than discovering an unverifiable terminal gate after
   implementation. Discover and fix the terminal PR base as that
   repository's default branch, and verify it again during current-head review.
   Abort as `pr-preflight-failed`; never downgrade.
6. **DISPATCH** — load `references/worker.md`, choose the deterministic ready
   set, adopt and resume any exact task refs carried by takeover, otherwise
   create one managed visible task per selected Spec with its resolved task
   profile, and verify its Goal.
7. **MONITOR** — read current task state, reconcile live evidence, and send only
   precise corrections with the recorded task profile. Never take implementation
   or review back into the root.
8. **GATE** — require the fixed pull-request, review, CI, integration, and
   tracker-closeout gates.
9. **RECONCILE** — refresh sources, claims, dependency merges, task state,
   review waits, ledger evidence, and recovery state; dispatch the next ready
   wave or emit a concrete blocker or durable handoff.

Every wave must produce a state transition, evidence update, owner decision, or
explicit no-progress record.

## Deterministic Scheduling

Treat a Feature Spec as ready only when every upstream ref in its parent
`## Feature Dependencies` table is merged,
its required App-managed checkouts are available, and its affected paths do not
overlap a running or selected Spec. A merge-ready but unmerged upstream does not
make a downstream ready; record the external merge handoff and wait for verified
merge evidence. Early stacking, downstream draft publication against an
upstream branch, rebase promotion, and force-push machinery are unsupported.
If every remaining Spec waits on an external merge, persist that handoff and
release the claim; a later explicit resume reacquires and verifies the merge.

Sort ready candidates by canonical claim/task source id ascending. Greedily select
the first candidates, up to the remaining three-task capacity, whose canonical
`(repository, path)` scopes are pairwise disjoint. Treat missing, wildcard, or
ancestor/descendant path scopes as overlapping. Recompute from live evidence on
every wave; parallelism and task count are never user options.

## Atomic Claim And Takeover

Use `scripts/orchestrator-claim` as the sole active-root authority. Persist the
acquire-time claim fingerprint, heartbeat while active, and provide that
fingerprint for every heartbeat and release. Release only after terminal proof
or an explicit durable handoff is recorded.

An overlapping live claim aborts as `needs-owner`. Takeover is exceptional:
perform read-only discovery first. Verify the helper's five-minute
stale-heartbeat threshold and capture the exact conflicting root ids,
fingerprints, heartbeat snapshots, complete repository/source scopes, ledgers,
and recorded visible task refs. Read live App state to prove that every recorded
task is still addressable and can be resumed after a bounded stop; when no task
was created, verify that absence from both ledger and live App state. A stale
heartbeat alone is never task-stop evidence.

Then resolve `stale_claim_takeover_permission`; if missing, ask a separate
question naming the roots, complete scopes, and tasks and disclosing that a
grant will interrupt or terminate those exact tasks, verify they are
non-mutating and resumable, replace the complete claims, and adopt the same task
refs. Denial creates no task mutation. Only after
`granted-by-authorized-user` may the root stop the tasks through the App runtime.
If any task cannot be stopped, verified non-mutating, or kept resumable, abort as
`needs-owner` without takeover.

The candidate claim must cover every repository and source owned by every
replaced root; partial-root takeover is invalid. Supply one
`--expected-task-termination <root-id>=<evidence-ref>` per conflict, where the
evidence identifies the complete stopped-and-resumable task set or proves that
the root created none. Also supply one
`--expected-task-adoption <root-id>=<absolute-json-path>` whose validated
per-Spec entries cover every claimed source exactly once and contain the exact
task ref, Goal evidence, and managed-checkout map, or explicit no-task evidence.
Every entry also carries the exact profile resolved before CLAIM, including a
no-task Spec awaiting a later dispatch wave.
This file is runtime evidence, not a user option:

```text
scripts/orchestrator-claim --json claim takeover \
  --takeover-permission granted-by-authorized-user \
  --expected-task-termination <root-id>=<evidence-ref> \
  --expected-task-adoption <root-id>=<absolute-json-path> \
  --takeover-reason verified-stale ...
```

The helper atomically writes a recoverable prepared-takeover journal before it
deletes any prior claim. That journal remains an ownership record through
partial deletion and finalization, and the candidate permanently embeds every
full replaced-claim snapshot plus the validated per-Spec adoption data. Across
the complete candidate, every recorded task ref and managed
`(repository, checkout)` pair must have exactly one Spec owner. Each recorded
checkout must still be on its stated target branch and its baseline revision
must resolve as a commit. On an interrupted takeover, inspect `claim status` and idempotently run
`claim recover-takeover --root-id <candidate-root> --expected-transaction-id
<transaction-id>`; a changed snapshot blocks without deleting remaining claims.
Status queried by a replaced root reports the prepared transaction and its
candidate recovery root even when that replaced claim was already deleted.

After acquisition, rebuild or verify the new ledger registry from the embedded
adoption data, adopt those exact tasks, and resume them as needed. Never create a
new task for a Spec that has recorded or embedded task evidence; if adoption or
resume fails, stop as blocked. The helper detects legacy schema-3 and schema-4 claims
read-only; an exact legacy owner may retire one only with `claim retire-legacy`,
its stored fingerprint, and terminal or durable-handoff evidence. Never migrate
or silently delete a legacy active claim. A terminal current owner releases its
own claim; takeover is never a retry alias.

## Task, Ledger, And Recovery

Load `references/ledger.md` during CLAIM and `references/worker.md` before task
creation, resume, read, or steering. The canonical ledger lives under
`~/.cache/dotagents/skills/implement-feature/ledgers/` and records only
authorization evidence, source fingerprints, claim ownership, task/Goal and
managed-checkout state, the resolved per-Spec task profile, PR/review/CI proof,
recovery state, and external handoffs.

Every created or resumed task establishes its assignment-scoped Goal before
work. Record an exact objective fallback only if that task runtime exposes no
Goal tool. Worker reports are evidence; only the root changes portfolio state.
A stale or failed task is read, recorded, and resumed in that same visible App
task. If the original task cannot be resumed, abort as blocked; never create a
replacement task for the same Spec.

The same rule applies after takeover. A replaced root's recorded task mapping is
continuation state, not permission to spawn again. Adopt and resume the exact
original task or block.

On resume, load `references/recovery-validation.md` and revalidate the runtime
surface, claim, source fingerprints, repositories, task/Goal evidence, managed
checkouts, gates, and review waits before mutation. Incompatible pre-hard-cut
ledgers are not migrated.

## Delivery And Final Report

Load `references/gates.md` before accepting terminal merge-ready state and
`references/codex-review-closeout.md` before requesting or waiting for review.
The visible task owns the entire pre-merge loop. The root verifies that every
affected repository has a real `OPEN`, non-draft PR at its current head, mandatory
review is dispositioned, CI passes, actionable feedback is resolved, integration
proof exists, tracker closeout is prepared, and current GitHub mergeability is
conflict-free and satisfies required update, approval, and merge-queue
eligibility conditions against the repository's discovered default branch.
Unknown or pending mergeability blocks; neither root nor task enqueues or merges.

Derive tracker closeout from the source: arm every generated implementation
issue's GitHub closing keyword in its owning PR and arm every
implementation-eligible Feature Spec in its designated default-branch
whole-Spec closeout PR after that Spec's gates pass. In a multi-repository
bundle with an accepted hosted parent/global Feature Spec, the final integration
partial's default-branch PR also arms that parent's fully qualified ref only
after every partial gate passes. Use fully qualified refs across repositories.
For a local
source, after substantive acceptance, integration, and any knowledge closeout,
move completed Markdown issue files to the configured done folder on the
delivery branch, commit and push the moves, rerun final validation and
`$autoreview`, convert draft PRs to ready-for-review, then obtain
current-revision review and CI before declaring terminal merge-ready state. The move
is prepared closeout until a later default-branch merge lands it. Hosted issues
also remain open until that later merge. Neither root nor task performs merge,
post-merge verification, or final tracker closure.

For a pre-claim abort, report intake evidence and explicitly state that no
runtime artifacts or mutations were created. Otherwise return ledger-derived
source fingerprints, task/Goal and checkout evidence, changes, validation,
commits, PR URLs, exact reviewed revisions, CI state, captured domain-closeout
evidence when present, prepared tracker closeout, current-head mergeability and
repository-rule evidence, blockers, recovery
freshness, and the next external action. Release the claim
after terminal proof or the recorded durable handoff.

## References

- `references/options.md`: the two run-scoped authorization fields.
- `references/task-model-policy.md`: fixed visible-task model and bounded
  per-Spec thinking selection.
- `references/spec-backed-delivery.md`: accepted bundle and Execution Contract.
- `references/ledger.md`: compact claim, task, gate, and recovery persistence.
- `references/worker.md`: fixed visible-task assignment and actions.
- `references/multi-repo-workspace.md`: managed multi-repository execution.
- `references/gates.md`: fixed PR-ready proof gates.
- `references/codex-review-closeout.md`: mandatory review wait and closeout.
- `references/recovery-validation.md`: resume-time hard-cut validation.
- `references/runtime-efficiency.md`: delta evidence for later waves.

## Claim Helper Maintenance

`scripts/orchestrator-claim` is the only supported atomic-claim artifact. Its
`__version__` is the command-contract version. After changes, run `--help`,
`--version`, `--json doctor`, the competing-root tests, and the focused App
contract suite. Use major versions for breaking command or JSON contracts.
