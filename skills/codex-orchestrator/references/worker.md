# Worker Reference

Use this reference before creating, naming, messaging, steering, or closing
Codex worker threads or subagents.

## Worker Policy

Resolve the ledger worker policy before delegation.

Worker authorization is resolved per workstream and session by the root
orchestrator. Do not read it from project-memory defaults, tracker templates,
generated issues, or draft publish commands. If legacy project-memory
worker-authorization setup appears, ignore it as stale, non-authoritative state.

| Field | Values | Meaning |
| --- | --- | --- |
| `delegated_worker_surface` | `auto`, `codex-app-thread`, `cli-subagent`, `none` | Owner-authorized delegation policy. `auto` chooses among authorized surfaces; in CLI this resolves to `cli-subagent`, while in App it may use visible App threads or subagents. |
| `actual_workstream_surface` | `codex-app-thread`, `cli-subagent`, `no-delegation` | Where the workstream actually runs. Do not present hidden subagents as visible App threads. |
| `max_active_delegated_workers`, `max_active_cli_subagents`, `max_active_codex_app_threads`, `session_wide_delegated_worker_cap` | numbers or `none` | Caps, not quotas. Preserve separate surface caps instead of collapsing them. Title-case ledger labels are display aliases. |
| `worker_authorization` | `inspect`, `implement`, `commit`, `push`, `pr`, `ci-rerun-fix`, `merge-close`, `release` | Capability flags; list every allowed action explicitly. |
| `worker_status` | `done`, `blocked`, `needs-owner`, `ready-for-review` | Worker report only, not a root closeout decision. |
| `worker_lifecycle` | `integrated`, `retained-for-inspection`, `abandoned`, `handoff-pending` | Root decision about worker output. |
| `branch_expectation` | `shared-feature-branch`, `repo-feature-branch`, `issue-branch`, `direct-commit-target`, `none` | Expected landing target. |
| `integration_method` | `handoff`, `worker-commit`, `patch-apply`, `manual-root`, dispatch-time `pending` | Root integration path. Replace `pending` before lifecycle closeout or record that no output was integrated. |
| `source_disposition` | `completed`, `partial`, `blocked`, `needs-owner`, `deferred`, `unchanged` | Source outcome from the worker's perspective. |

Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases. Treat older `push-pr` authorization as a legacy alias for
`commit`, `push`, and `pr`, then rewrite touched values to the exact authorized
subset.

## Delegation Rules

- Create one worker per independent ownership boundary: repository, package,
  service, path set, or tightly scoped workstream. Repository boundaries are the
  default isolation heuristic, not a quota or strict cap.
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
  ledgers, or delegate their assignment.
- Workers must preserve unrelated local changes and stage only authorized
  paths. Only the root creates, reuses, forks, assigns, renames, messages,
  archives, closes, interrupts, or replaces worker threads.

## Delivery Mode Rules

The root passes the effective delivery mode plus whether it is inherited from
`Source PRD` or an issue-level override. `prd-backed-delivery.md` owns the full
delivery/publication/issue-mutation authority model; workers only enforce the
assignment they receive.

| Mode | Worker handling |
| --- | --- |
| `one-feature-branch` | Root owns the shared branch/PR. Worker provides patch, helper-worktree diff, handoff, or reviewed commit unless root explicitly grants publication modes. |
| `one-pr-per-repo` | Repo-scoped worker may prepare that repo branch/PR only when `commit`, `push`, and/or `pr` modes are explicitly listed. |
| `one-pr-per-issue` | Use only for explicitly isolated issue work. |
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
- `patch-apply`: apply a worker diff or patch in the root checkout, then inspect
  conflicts and rerun root gates.
- `manual-root`: reimplement or copy the relevant change in the root checkout
  when the worker output is partial, stale, conflicting, or easier to reproduce
  safely than to apply directly.

For every path, inspect the tracked diff, preserve unrelated local changes,
exclude generated ignored artifacts, rerun the required root gates, and record
the integration method and proof in the ledger. Do not commit, push, merge,
close, release, or mutate external services unless the current authorization
modes and gate state permit it.

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

- `integrated`: output was accepted into the root checkout, root gates passed,
  and the worker can be archived or its helper worktree removed.
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
- Wave: <number>
- Objective: <one concrete outcome>
- Source ID: <stable source id>
- Source ref: <URL, path:line, heading, run id, or ledger item>
- Acceptance criteria: <source-owned completion criteria>
- Closeout target: <issue close, PR reply, file checkbox/patch, CI rerun, ledger status>
- Authorization modes: <one or more of inspect|implement|commit|push|pr|ci-rerun-fix|merge-close|release>
- Allowed paths or surfaces: <paths, branches, PRs, issues, or commands>
- Delivery mode: <one-feature-branch|one-pr-per-repo|one-pr-per-issue|direct-commit> (<feature-level, inherited from Source PRD|issue-level override with authorization>)
- Delivery mode source: <Source PRD path/issue, explicit owner request, or issue-level override reason>
- Publication authority: <none|explicit-owner-authorization|prd-backed-branch-plus-draft-pr|blocked, with reason>
- Issue mutation authority: <none|pr-body-closeout-only|explicit-direct-mutation>
- Parallelization: <independent|depends-on source/workstream|blocks source/workstream|root-integrated>
- Dependencies: <completed source/workstream proof, pending dependency, or none>
- Branch expectation: <shared-feature-branch|repo-feature-branch|issue-branch|direct-commit-target|none>
- Issue integration shape: <shared-feature-branch|repo-pr|issue-pr|direct-commit|inspect-only>
- Root integration method: <handoff|worker-commit|patch-apply|manual-root|pending>
- Report channel: this worker thread only
- Helper checkout/worktree: <path or unknown>
- Heartbeat/next checkpoint: <interval/time or none>
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
  `none`
- Scheduling: current wave assignment, unlock state, and dependency source
- Gate status: pass|fail|blocked|not-applicable with root-verifiable evidence
- Generated artifacts: ignored local files or directories created, or none
- Risks: residual risks, dependency audit warnings, security findings,
  untested adapters, setup gaps, or test gaps
- Next: exact owner or orchestrator action
```

## Heartbeat Checks

When heartbeat monitoring is requested, poll workers at the requested interval
or a conservative default such as five minutes. Read the worker state first
when the worker surface supports it, then ask for status, blocker, validation,
risks, and expected next checkpoint only if the latest state is stale or
insufficient. Do not interrupt a worker with new scope unless the user changed
priority, a contract mismatch was discovered, or a gate failed.

For each heartbeat wave, update the ledger with last-read time, worker status,
validation or proof delta, blocker, risk delta, and next check. If a worker
misses its next checkpoint or produces the same status for two consecutive
heartbeats without new proof, send one focused unblock request. After the next
no-progress check, choose a root-owned action: continue with a reason, steer,
replace, abandon, retain for inspection, classify as `blocked` or
`needs-owner`, or ask the owner.
