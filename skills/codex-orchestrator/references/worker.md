# Worker Reference

Use this reference before creating, naming, messaging, steering, or closing
Codex worker threads or subagents.

## Worker Fields

Resolve session worker fields before delegation.

Worker authorization is resolved per workstream and session by the root
orchestrator. Do not read worker assignments, worker-count limits, dispatch
flags, authorization ceilings, publication policy, issue mutation policy,
PRD-specific worker settings, or issue-specific worker settings from
project-memory defaults, tracker templates, generated issues, or draft publish
commands. If legacy project-memory
worker-authorization setup appears, ignore it as stale, non-authoritative state.

Product surface references: visible Codex App thread creation is documented in
<https://developers.openai.com/codex/app/features>, CLI/App subagents are
documented in <https://developers.openai.com/codex/subagents>, and Codex
instruction discovery is documented in
<https://developers.openai.com/codex/guides/agents-md>.

Session fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `delegated_worker_surface` | `codex-app-thread`, `cli-subagent`, `none` | Worker surfaces approved for the current orchestrator session. `codex-app-thread` allows visible App threads only when the current runtime exposes thread tools and the owner approved that surface. |
| `actual_workstream_surface` | `codex-app-thread`, `cli-subagent`, `no-delegation` | Where the workstream actually runs. Do not present hidden subagents as visible App threads. |
| `worker_authorization` | `inspect`, `implement`, `commit`, `push`, `pr`, `ci-rerun-fix`, `merge-close`, `release` | Capability flags; list every allowed action explicitly. |

Worker report fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `worker_status` | `done`, `blocked`, `needs-owner`, `ready-for-review` | Worker report only, not a root closeout decision. |
| `worker_lifecycle` | `integrated`, `retained-for-inspection`, `abandoned`, `handoff-pending` | Root decision about worker output. |
| `source_disposition` | `completed`, `partial`, `blocked`, `needs-owner`, `deferred`, `unchanged` | Source outcome from the worker's perspective. |

Integration fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `branch_expectation` | `feature-branch`, `repo-feature-branch`, `direct-commit-target`, `none` | Expected landing target. |
| `integration_method` | `handoff`, `worker-commit`, `patch-apply`, `manual-root`, `pending` | Root integration path. Replace `pending` before lifecycle closeout or record that no output was integrated. |
| `caller_checkout_policy` | `preserve-current-branch`, `caller-checkout-approved`, `not-applicable` | Whether the checkout where the owner invoked the orchestrator may switch branches during integration or publication. |
| `publication_checkout` | `worker-worktree`, `integration-worktree`, `caller-checkout`, `not-applicable` | Checkout where commit, push, and draft PR publication will run. |

Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases. Treat older `push-pr` authorization as a legacy alias for
`commit`, `push`, and `pr`, then rewrite touched values to the exact authorized
subset.

The canonical execution values are the worker-surface fields above. In the
owner-facing checkpoint, `Execution mode` is only a display summary inferred
from the selected surfaces and worker split; do not treat it as a separate enum or
source of truth.

Automation creation, updates, and scheduling are explicit-only and
runtime-tool-dependent. Project memory does not store scheduled check timing and
is not standing consent to create, update, or schedule Codex App automations.
The ledger is the monitoring surface: record source status,
worker/workstream status, blockers, `Last Read`, and `Next Check` /
`Next Scan/Check` there. The root may create, update, or schedule an automation
only when the current runtime exposes automation tooling and the current owner
request explicitly asks for an automation, reminder, monitor, recurring run, or
approves a checkpoint that explicitly says `Automation: yes`. If automation
tooling is unavailable, do not imply anything was scheduled; draft the proposed
automation instructions, schedule, and handoff text for owner action.

After the owner approves the session settings, the root chooses the number of
workers and the split across approved surfaces for each implementation wave. The
root may still keep work in the root thread or stop for owner input when source,
repo, dependency, gate, or tool state makes dispatch unsafe.

## Surface Wording Rules

In owner worker-surface wording, `thread` means a visible Codex App thread.
Phrases such as `worker thread`, `new thread`, `separate thread`, `Codex
thread`, `visible thread`, or `use a thread` resolve `delegated_worker_surface`
and `actual_workstream_surface` to `codex-app-thread`. Do not spawn a
`cli-subagent` for a request that says `thread` unless the owner explicitly
approves that fallback after the missing or changed surface is stated.

Use `cli-subagent` only when the owner requests or accepts `subagent`, `/agent`,
`CLI worker`, or similar non-thread worker wording, or when the owner left the
surface open and the checkpoint explicitly resolves it to `cli-subagent`.
If owner wording mixes `thread` and `subagent`, treat it as conflicting
surface intent, present the concrete surface choices in the checkpoint, and
wait for approval before dispatch.

If Codex App thread tools are requested but unavailable, stop before dispatch
and report the missing create/read/message thread surface. Do not silently
downgrade to `cli-subagent`; ask for explicit fallback authorization or keep
the work in the root thread.

## Delegation Rules

- Create one worker per independent ownership boundary: repository, package,
  service, path set, or tightly scoped workstream. Repository boundaries are the
  default isolation heuristic, not a quota.
- In multi-repo projects, use one active worker per affected repo per wave by
  default. Add more only when a repo has independent workstreams with clean
  file, contract, test, and validation boundaries.
- In single repos and monorepos, keep shared contracts, dependencies, root
  config, migrations, generated snapshots, broad tests, conflict resolution,
  and final integration in the root thread.
- Stay in root when orchestration overhead dominates, work overlaps heavily, no
  inspectable surface exists, delegation is unauthorized, or remaining work is
  mostly gates, ledger updates, closeout, or publication decisions.
- Do not assign implementation for `Parallelization: depends-on <issue>` until
  root verifies dependency completion. Keep `root-integrated` implementation in
  root; workers may inspect or prove only when root keeps integration ownership.
- Workers may inspect, implement, test, and report only within their authorized
  mode. They must not spawn sub-workers, create threads, manage chats, edit
  ledgers, create active-root claims, decide takeover or handoff, choose branch
  strategy, mutate sources, or delegate their assignment.
- Workers must preserve unrelated local changes and stage only authorized
  paths. Only the root creates, reuses, forks, assigns, renames, messages,
  archives, closes, interrupts, or replaces worker threads.
- When visible Codex App workers provide helper worktrees, preserve the caller
  checkout branch by default. Root-owned integration, validation, commit, push,
  and PR creation should run from the worker worktree or a dedicated integration
  worktree. Switching the caller checkout is allowed only when the checkpoint
  explicitly chooses `caller-checkout-approved`, or when no helper/integration
  checkout is available and the owner approves that fallback.

## Approach Checkpoint

Before dispatching implementation, build a startup approach checkpoint with
session-scoped worker settings. Present it and wait for owner approval. This is
an execution brief, not a generic "can I start?" prompt. The root may do
read-only discovery, planning, source registration, and wave shaping before
approval, but it must not create workers, create visible App threads, start
implementation edits, mutate source state, commit, push, or open PRs until the
checkpoint is owner-approved.

The checkpoint must state its approval scope. For PRD or feature
implementation with a clear generated issue graph, prefer a bounded multi-wave
approval scope that covers all listed source items and dependency-unlocked
waves. Use current-wave-only approval when later workstreams are not yet
specified enough, depend on unresolved owner decisions, or require different
surface, worker split, authorization, or delivery boundaries.

When a bounded multi-wave checkpoint is owner-approved, continue from one wave
to the next without pausing as dependencies are satisfied, as long as later
waves stay inside the recorded source items, approved worker surfaces,
authorization modes, delivery path, and stop conditions. Regenerate the
checkpoint and wait for approval before doing work outside those boundaries.

Start with a short `Approach Summary` paragraph in plain language. Summarize
the session settings, approval scope, starting wave, root-owned coordination,
worker usage, and stop conditions. Keep concrete selected values in the tables;
keep raw internal field names out of the owner-facing checkpoint unless
debugging.

Then use this compact decision table:

| Decision | Planned value | Meaning |
| --- | --- | --- |
| Source items | <issue/PR/PRD/checklist refs> | Durable work sources this approval covers. |
| Approval scope | <current wave only OR bounded multi-wave plan through source refs> | Whether approval covers only the first wave or the bounded graph. |
| Session surfaces | <CLI subagents yes/no; visible App threads yes/no; automation yes/no> | PRD-agnostic and issue-agnostic session choices. |
| Execution split | <root-only OR root + workers with count/scope> | Which work stays root-owned and which work is delegated. |
| Workstreams starting now | <count and short names> | Work units that can start immediately. |
| Checkouts | <caller checkout policy; publication checkout> | Where integration/publication will run and whether caller branch is preserved. |
| Authorization modes | <inspect, implement, commit, push, pr, ci-rerun-fix, merge-close, release> | The exact actions allowed by this approval. |
| Delivery and gates | <branch/PR/closeout plus tests/autoreview/CI/integration proof> | Landing path and proof before closeout. |
| Stop condition | <scope/surface/auth/delivery/gate change, blocker, or completion> | When the orchestrator must return to the owner. |

Then include one row per workstream:

| Wave | Workstream | Surface | Scope | Start rule | Allowed actions | Output expected |
| --- | --- | --- | --- | --- | --- | --- |
| <wave> | <name/ref> | <root thread (no-delegation), cli-subagent, or codex-app-thread> | <repo/package/paths> | <independent, depends-on proof, or root-integrated> | <authorization modes and limits> | <patch/report/commit/PR> |

A workstream defines the implementation slice. It creates a worker only when
its `Surface` is `cli-subagent` or `codex-app-thread`; `no-delegation` means
the root orchestrator thread owns that slice directly.

Explicit natural-language acceptance such as `approve`, `go ahead`, `ok
proceed`, or `looks good` approves a blocking checkpoint. If the owner changes
the split, worker surface, authorization, or delivery path, revise the
checkpoint and ask again before dispatch.

For root-only work, do not write `none; root-owned` in the owner-facing
checkpoint. Write `Execution mode: root thread only; no separate workers`,
`Worker surface: no-delegation`, `CLI subagents: no`, and
`Visible App threads: no`. If no automation will be created or updated, write
`Automation: no`.

End every blocking approach checkpoint with this exact text:

> Reply approve to dispatch the approved scope, or send edits to the split, worker surface, authorization, delivery path, approval scope, or stop conditions. I will not start implementation workers or root-owned implementation until you approve.

## Recurring PRD Automation

When the owner asks for a recurring automation that searches for new PRDs and
implements them, the startup checkpoint must say that the two session worker
surface answers apply to every automation run. Ask no additional PRD-specific
worker-surface questions.

Process one PRD at a time. If a PRD stops as `blocked`, `needs-owner`, or
`deferred`, record that PRD's blocker and continue to the next unrelated
eligible PRD in a later run. Stop the automation queue only when the blocker is
systemic, such as missing credentials, unavailable worker/thread tools, broken
tracker access, unsafe repository state shared by multiple PRDs, failing shared
infrastructure, or another general condition that can affect multiple PRDs.

Each automation run starts and ends with the ledger: select the next PRD from
`Next Scan/Check`, source status, dependencies, and blocker state, then write
progress, blockers, proof, or the next check before stopping.

## Delivery Mode Rules

The root passes the effective delivery mode plus whether it is inherited from
`Source PRD` or an issue-level override. `prd-backed-delivery.md` owns the full
delivery/publication/issue-mutation authority model; workers only enforce the
assignment they receive.

For generated implementation issues, the root also passes the validated
`## Orchestrator Handoff` projection. Workers may use the handoff for scope,
start rule, dependencies, validation, and closeout, but they must not treat it
as worker authorization, publication authority, issue mutation authority, or
permission to change branch/PR strategy.

| Mode | Worker handling |
| --- | --- |
| `pull-request` | Root owns the branch/PR shape. In single-repo or monorepo work, workers provide patches, helper-worktree diffs, handoff, or reviewed commits unless root explicitly grants publication modes. In multi-repo work, repo-scoped workers may prepare their repo branch/PR only when `commit`, `push`, and/or `pr` modes are explicitly listed. |
| `direct-commit` | Use only with explicit owner authorization recorded in the prompt and ledger. |

If assigned delivery mode conflicts with repo reality, stop and report
`needs-owner`; do not choose a new branch or PR strategy. Workers may commit,
push, or open a draft PR only when the prompt names the exact repository,
branch/refspec, PR shape, closeout target, and corresponding authorization
modes. `pr` is not a shortcut for commit or push.

## Worker Status Vs Root Lifecycle

Workers report execution status. The root orchestrator decides lifecycle:

- Worker status: `done`, `blocked`, `needs-owner`, `ready-for-review`
- Root lifecycle: `integrated`, `retained-for-inspection`, `abandoned`,
  `handoff-pending`

Do not equate a worker saying `done` with the workstream being complete. The
root still needs to inspect the latest state, choose an integration path, rerun
root-owned gates, and record the lifecycle decision in the ledger.

## Visible Thread Naming

For visible Codex App worker threads, set the thread title immediately after
creation and whenever the material assignment changes:

```text
<Project>: <short current task>
```

Examples:

- `livekit-vision: BE preview API`
- `dotagents: GitHub skill audit`
- `mobile: CI rerun fix`

Keep names short and task-specific. Avoid status-only names such as `Worker 1`,
`Active`, or `Needs review`. Record the worker id and title in the ledger.

## Read-Before-Steer

Before sending a new instruction, changing a title, archiving, interrupting,
closing, replacing, or handing off a worker, read its latest state with the
available thread/subagent inspection tool. Base any steering message on the
current worker status, files touched, blockers, validation, risks, and next
checkpoint.

Do not send broad new scope into a worker without recording why the existing
scope changed. If the latest state is unavailable, stop and report the missing
inspection surface instead of guessing.

## Multi-Wave Resync

Before reusing a worker for a second or later wave, or before changing a worker
to overlapping scope, reconcile the worker with root-integrated state:

- read the worker's latest state and identify its current branch, checkout,
  worktree, dirty files, generated ignored artifacts, validation, and remaining
  risks;
- identify root-integrated changes accepted since the worker's assignment,
  especially changes from other workers that touch the same files, contracts,
  fixtures, or docs;
- either hand the worker to a current checkout, send a precise resync brief
  with the accepted root changes, create a fresh worker from the current root,
  or keep the overlapping integration in the root thread;
- do not ask a stale worker to keep editing overlapping files until the resync
  path is explicit in the ledger.

If a worker still has unintegrated output from a previous assignment, integrate
or intentionally abandon that output before adding unrelated new scope. When
preserving previous worker changes is required, state that requirement in the
new prompt and ask the worker to report any overlap or conflict.

Prefer creating a fresh worker when the old one is stale, its checkout drift is
unclear, or the new scope overlaps accepted root changes enough that resync
would be harder to reason about than replacement.

## Worker Output Integration

The root orchestrator owns integration. Choose and record one integration path
per worker output:

- `handoff`: use `codex_app.handoff_thread` or the equivalent inspected worker
  surface when the worker's checkout should become the integration checkout.
- `worker-commit`: accept a worker-prepared commit or branch only when the
  authorization modes include `commit` and the root has reviewed the diff.
- `patch-apply`: apply a worker diff or patch in the explicitly named
  integration checkout, then inspect conflicts and rerun root gates. Prefer a
  worker worktree or dedicated integration worktree when one exists; use the
  caller checkout only when the approach checkpoint approved that branch switch.
- `manual-root`: reimplement or copy the relevant change in the explicitly
  named integration checkout when the worker output is partial, stale,
  conflicting, or easier to reproduce safely than to apply directly. Preserve
  the caller checkout unless it was approved as the integration checkout.

For every path, inspect the tracked diff, preserve unrelated local changes,
exclude generated ignored artifacts, rerun the required root gates, and record
the integration method, publication checkout, caller checkout disposition, and
proof in the ledger. Do not commit, push, merge, close, release, or mutate
external services unless the current authorization modes and gate state permit
it.

## Generated Artifacts

Workers may create local ignored artifacts while validating work, such as
dependency directories, build outputs, caches, virtual environments, screenshots,
or coverage files. The worker final report must list those artifacts separately
from tracked source changes.

Generated ignored artifacts are not automatically a failure, but they are part
of closeout. The root orchestrator decides whether they are removed, retained
for inspection, or left inside a worker-owned helper worktree. Never treat
ignored artifacts as proof that tracked changes are clean; inspect tracked
status and diffs explicitly.

## Helper Worktrees

Treat Codex App worker worktrees and other worker checkouts as temporary helper
surfaces by default, but not as disposable until closeout. A helper worktree may
contain tracked changes, generated artifacts, logs, screenshots, test evidence,
branches, patches, or context that the root needs before final status.

Before archiving, removing, abandoning, or handing off a helper worktree, read
the latest worker state, inspect tracked changes and ignored artifacts, and
record whether useful output was `integrated`, `retained-for-inspection`,
`abandoned`, or left `handoff-pending`. The root orchestrator decides
whether the helper surface is archived, removed, retained, abandoned, or handed
off; workers only report facts and recommendations.

## Worker Closeout

After a worker reports `done`, `ready-for-review`, `blocked`, or `needs-owner`,
the root orchestrator decides the worker lifecycle state before final owner
status:

- `integrated`: output was accepted into the chosen integration checkout, root
  gates passed, and the worker can be archived or its helper worktree removed.
- `retained-for-inspection`: output or artifacts are intentionally kept for
  owner/root review; record what remains and why.
- `abandoned`: output was not used; record the reason and confirm there is no
  required follow-up hidden only in the worker thread.
- `handoff-pending`: the worker's checkout or thread is the intended next
  integration surface; record the pending action and owner decision needed.

Do not remove or archive a worker before reading its latest state. Do not remove
a helper worktree that contains unreviewed tracked work, unreported artifacts,
or the only copy of evidence needed for a gate. Once all useful output is
integrated or intentionally abandoned, remove or archive helper surfaces when
that cleanup is safe and available, or record why they remain.

## Authorization Modes

Record one or more authorization modes for the specific workstream. Modes are
capability flags, not a cumulative ladder. The root derives them from the owner
request, source item, linked `Source PRD`, publication authority, issue mutation
authority, selected worker surface, dependency state, dirty-worktree state, and
gates. If a worker may edit, commit, push, and open a draft PR, record
`implement, commit, push, pr`. If it may only open a PR from an already-pushed
branch, record `pr` only.

- `inspect`: read-only investigation, issue/PR/CI inspection, repo scan, or
  design review. No file edits unless explicitly listed in allowed surfaces.
- `implement`: local code/docs changes plus focused validation, but no staging,
  commit, push, PR, merge, release, or external mutation unless explicitly
  listed in allowed surfaces.
- `commit`: may stage and create local commits for the assigned paths in the
  exact repository and branch/worktree named by the root. It assumes edits are
  separately allowed by `implement` or by explicit assignment text. It does not
  permit push, PR creation/update, merge, release, or issue mutation. Commit
  messages must not use GitHub closing keywords such as `closes`, `fixes`, or
  `resolves` unless the source explicitly authorizes final-commit closure; use
  non-closing references such as `Refs #123` when a reference is useful.
- `push`: may push only the exact assigned branch or explicit refspec after the
  required validation and publication-safety checks. It does not permit local
  commits unless `commit` is also listed, and it does not permit PR
  creation/update, PR-body closeout keywords, merge, release, or direct issue
  mutation.
- `pr`: may create or update the assigned draft PR for the exact branch and
  closeout target after required validation and publication-safety checks. This
  is the first mode that may place GitHub closing keywords such as `Closes #123`
  in a PR body when the generated issue's closeout path calls for PR-body
  closure. It does not permit local commits or push unless those modes are also
  listed, and it does not authorize merge, release, or direct issue mutation.
- `ci-rerun-fix`: rerun checks, inspect CI logs, and diagnose or verify a known
  PR or branch when the root assignment names the failing checks. Any edits,
  commits, or pushes for CI repair also require the corresponding `implement`,
  `commit`, and `push` modes plus publication-safety gates.
- `merge-close`: merge, close, label, comment, or otherwise mutate GitHub state
  only with explicit owner approval.
- `release`: tag, release, publish, or package promotion only with explicit
  owner approval and the release gate satisfied.

## Prompt Template

```text
You are a Codex worker for the <portfolio> portfolio.

Scope:
- Repository: <repo path or owner/repo>
- Workstream: <short name>
- Worker surface: <codex-app-thread|cli-subagent>
- Worker ID/title: <id/title or pending>
- Worker evidence: requested=<none|cli-subagent|codex-app-thread>;
  approved=<true|false>; actual=<root|cli-subagent|codex-app-thread>;
  status=<used|unavailable|attempt-failed|root-owned-fallback>;
  evidence=<tool/session/failure>; parallelism=<parallel|sequential|root-owned|simulated>
- Wave: <number>
- Objective: <one concrete outcome>
- Source ID: <stable source id>
- Source ref: <URL, path:line, heading, run id, or ledger item>
- Acceptance criteria: <source-owned completion criteria>
- Closeout target: <issue close, PR reply, file checkbox/patch, CI rerun, ledger status>
- Authorization modes: <one or more of inspect|implement|commit|push|pr|ci-rerun-fix|merge-close|release>
- Allowed paths or surfaces: <paths, branches, PRs, issues, or commands>
- Delivery mode: <pull-request|direct-commit> (<feature-level, inherited from Source PRD|issue-level override with authorization>)
- Delivery mode source: <Source PRD path/issue, explicit owner request, or issue-level override reason>
- Orchestrator handoff: <source PRD; feature slug; affected repos/product scope; scope; start rule; validation; closeout, or none for ad hoc work>
- Publication authority: <none|explicit-owner-authorization|prd-backed-branch-plus-draft-pr|blocked, with reason>
- Issue mutation authority: <none|pr-body-closeout-only|explicit-direct-mutation>
- Parallelization: <independent|depends-on source/workstream|blocks source/workstream|root-integrated>
- Dependencies: <completed source/workstream proof, pending dependency, or none>
- Branch expectation: <feature-branch|repo-feature-branch|direct-commit-target|none>
- Issue integration shape: <feature-pr|repo-pr|direct-commit>
- Root integration method: <handoff|worker-commit|patch-apply|manual-root|pending>
- Caller checkout policy: <preserve-current-branch|caller-checkout-approved|not-applicable>
- Publication checkout: <worker-worktree path|integration-worktree path|caller-checkout path|not-applicable>
- Report channel: this worker thread only
- Helper checkout/worktree: <path or unknown>
- Next ledger check: <time/action or none>
- Forbidden actions: no subdelegation, no ledger edits, no unrelated cleanup,
  no worker/thread/chat management, no commit/push/PR/merge/release unless this
  mode explicitly permits it.

Context:
- Owner request: <summary>
- Current ledger status: <summary>
- Known blockers or assumptions: <bullets>
- Selected gates: <gate names from references/gates.md>
- Required proof: <tests, live proof, CI, autoreview, docs, screenshots>
- Known root-integrated changes since assignment: <bullets or none>

Execution:
1. Inspect the current state before editing.
2. Preserve unrelated worktree changes.
3. If editing, run focused validation.
4. Run or request autoreview when required by the gate.
5. Stop and report if blocked by access, ambiguous owner intent, unsafe state,
   missing dependency, worker-reported risk, or a gate that cannot be
   satisfied.

Final report:
- Status: done|blocked|needs-owner|ready-for-review
- Source disposition: completed|partial|blocked|needs-owner|deferred|unchanged
- Changes: files or external objects touched
- Validation: commands run and outcomes
- Delivery: delivery mode, branch or PR used, closeout path, and PR links or
  `none`; include publication checkout and caller checkout disposition
- Worker evidence: requested, approved, and actual surface; worker id or session
  evidence; unavailable or failed tool evidence; fallback reason; and whether
  execution was parallel, sequential, root-owned, or simulated
- Scheduling: current wave assignment, unlock state, and dependency source
- Gate status: pass|fail|blocked|not-applicable with root-verifiable evidence
- Generated artifacts: ignored local files or directories created, or none
- Risks: residual risks, dependency audit warnings, security findings,
  untested adapters, setup gaps, or test gaps
- Next: exact owner or orchestrator action
```

## Ledger-Driven Progress Checks

Before every owner-facing progress update, read the ledger and summarize the
current wave, active workstreams, worker status, blockers, proof changes, and
`Next Check` / `Next Scan/Check`. Do not report progress from memory when the
ledger is available.

When a worker or workstream is due for a check, read the worker state first when
the surface supports it, then ask for status, blocker, validation, risks, and
expected next checkpoint only if the latest state is stale or insufficient. Do
not interrupt a worker with new scope unless the user changed priority, a
contract mismatch was discovered, or a gate failed.

For each progress check, update the ledger with last-read time, worker status,
validation or proof delta, blocker, risk delta, and next check. If a worker
misses its next checkpoint or produces the same status for two consecutive
checks without new proof, send one focused unblock request. After the next
no-progress check, choose a root-owned action: continue with a reason, steer,
replace, abandon, retain for inspection, classify as `blocked` or
`needs-owner`, or ask the owner.
