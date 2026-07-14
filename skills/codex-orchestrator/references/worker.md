# Worker Reference

Use this reference before creating, naming, messaging, steering, or closing
Codex worker surfaces or subagents.

## Worker Fields

Resolve session worker fields before delegation.
Load `options.md` first. Session selection fields use that registry; this file
owns worker capability and lifecycle fields.

Worker authorization is resolved per workstream and session by the root
orchestrator. Do not read worker assignments, worker-count limits, dispatch
flags, authorization ceilings, publication policy, issue mutation policy,
Feature Spec-specific worker settings, or issue-specific worker settings from
project-memory defaults, tracker templates, generated issues, or draft publish
commands. Any project-memory worker-authorization setup is invalid,
non-authoritative state.

Product surface references: visible Codex App task creation is documented in
<https://developers.openai.com/codex/app/features>, CLI/App subagents are
documented in <https://developers.openai.com/codex/subagents>, and Codex
instruction discovery is documented in
<https://developers.openai.com/codex/guides/agents-md>.
In the current Codex App surface, visible task creation uses `create_thread`.
Use its managed worktree target when a dedicated checkout is required, then
use the returned task identifier for later task operations. Search the current
tool registry before relying on any optional project-selection argument.

Session option fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `work_delegation_policy` | `orchestrator-decides-for-each-implementation-workstream`, `run-all-work-in-current-orchestrator-session`, `orchestrator-decides-with-concurrent-worker-limit` | Whether work may be delegated and whether the authorized user sets a concurrency ceiling. |
| `delegated_worker_visibility` | `orchestrator-decides-between-background-and-visible-workers`, `background-codex-subagents-only`, `visible-codex-app-tasks-only`, `not-applicable` | Which delegated worker types may be used. |
| `visible_app_task_permission` | `not-requested`, `granted-by-authorized-user`, `denied-by-authorized-user` | Permission for visible user-owned App tasks. |
| `unmanaged_git_worktree_fallback_permission` | `not-granted`, `granted-by-authorized-user` | Permission for an unmanaged Git worktree after managed-worktree failure evidence. |

`max_concurrent_delegated_workers` and `max_visible_app_tasks` are numeric/data fields governed by
`options.md`, not prose or boolean option values.

Execution fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `actual_execution_location` | `current-orchestrator-session`, `background-codex-subagent`, `visible-codex-app-task` | Where the workstream actually runs. The current-session value works in both CLI and App. |
| `worker_allowed_actions` | See the canonical list below | Independent action list. Merge and source closeout remain root-owned. |

Worker report fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `worker_status` | `done`, `blocked`, `needs-owner`, `ready-for-review` | Worker report only, not a root closeout decision. |
| `worker_lifecycle` | `integrated`, `retained-for-inspection`, `abandoned`, `handoff-pending` | Root decision about worker output. |
| `source_disposition` | `completed`, `partial`, `blocked`, `needs-owner`, `deferred`, `unchanged` | Source outcome from the worker's perspective. |

Integration fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `branch_expectation` | `feature-branch`, `repository-feature-branch`, `named-target-branch`, `none` | Expected landing target. |
| `integration_method` | `handoff`, `worker-commit`, `patch-apply`, `manual-root`, `pending` | Root integration path. Replace `pending` before lifecycle closeout or record that no output was integrated. |
| `starting_checkout_branch_handling` | `keep-current-branch-checked-out`, `branch-switch-authorized`, `not-applicable` | Whether the checkout where the owner invoked the orchestrator may switch branches during integration or publication. |
| `result_checkout_path` | `worker-worktree`, `integration-worktree`, `caller-checkout`, `not-applicable` | Checkout where commit, push, draft PR publication, and ready-for-review transition will run. |

In a Codex App session, `worker-worktree` and `integration-worktree` mean a
worktree owned by a visible App task whenever the root creates or allocates a
new dedicated checkout. Record the returned App task identifier with the checkout. This
binding does not apply in CLI-only sessions or to an existing owner-supplied
checkout.

## Runtime Tool Mapping

Search the current tool registry before dispatch or lifecycle operations; tool
names are runtime-dependent. In the current surface, internal subagent
operations map to `spawn_agent`, `list_agents`, `send_message`,
`followup_task`, `interrupt_agent`, and `wait_agent`. Separately created App
tasks map to `create_thread`, `list_threads`, `read_thread`,
`send_message_to_thread`, `set_thread_title`, `set_thread_archived`,
`set_thread_pinned`, `fork_thread`, and `handoff_thread` when those tools are
available.

Do not claim a resume or close operation when the runtime exposes only
follow-up, interrupt, or archive. Read current state first, use the narrowest
available lifecycle operation, and record the actual tool and result. For App
worktree creation, starting state may be the project default, an existing named
branch, or the current working tree when supported; a branch start argument
selects an existing ref and does not name a new branch.

Lower-kebab-case values are canonical. Retired surface and capability values
are invalid input; do not reinterpret or silently upgrade them.

The canonical execution values are the worker-surface fields above. In the
owner-facing execution report, `Execution mode` is only a display summary
inferred from the selected surfaces and worker split; do not treat it as a
separate enum or source of truth.

## Capability Snapshots

The root records a capability snapshot when a worker is created, resumed, or
forked, and refreshes it before the worker performs a network, publication, or
external-mutation action. Record:

- `filesystem`: the reported permission profile and whether the assigned
  checkout is readable/writable as required;
- `network`: available, restricted, or unknown, with read-only probe evidence
  when the action needs network access;
- `gh_auth`: available, unavailable, or not-required;
- `codex_cli`: available, unavailable, or not-required;
- `autoreview`: available, unavailable, or reroute-to-root, using
  `autoreview doctor --json` when applicable;
- `checked_at`: timestamp plus the tool, task metadata, or command that
  produced the evidence.

Do not assume a fork inherits broader permissions than its parent. If a
snapshot changes or an operation fails with permission, network,
authentication, or state-storage evidence, refresh the snapshot once and stop
retrying that operation in the worker. Route it to a capable root when current
scope, authority, and gates permit; otherwise record the blocker. Never copy
credentials into a worker to manufacture capability.

Automation creation, updates, and scheduling require a matching source- or
workstream-scoped `scheduled_automation_change_permission=granted-by-authorized-user` row and are
runtime-tool-dependent. Project memory does not store scheduled check timing
and cannot supply that option.
The ledger is the monitoring surface: record source status,
worker/workstream status, blockers, `Last Read`, and `Next Check` /
`Next Scan/Check` there. The root may create, update, or schedule an automation
only when the runtime exposes automation tooling and the matching scoped
option-resolution row records
`scheduled_automation_change_permission=granted-by-authorized-user` with owner evidence naming
the exact automation target.
If automation tooling is unavailable, do not imply anything was scheduled;
draft the proposed automation instructions, schedule, and handoff text for
owner action.

The root chooses the number of workers and split for each wave within
`work_delegation_policy`, `delegated_worker_visibility`, `max_concurrent_delegated_workers`, `visible_app_task_permission`, and
`max_visible_app_tasks`. It may still keep work in the root session or stop for owner
input when source, repo, dependency, gate, or tool state makes dispatch unsafe.
There is no separate workspace execution mode; serial and parallel owner
requests are resolved through these existing session fields plus the issue
graph, dependency state, and repo/branch/worktree safety.

When the current runtime is the Codex App and the root chooses a new dedicated
worker, integration, or publication worktree, select
`delegated_worker_visibility=visible-codex-app-tasks-only` and create the task
with a worktree target before implementation. Do not run the
implementation through CLI subagents in the caller checkout and move the
integrated diff into a manually created worktree only for publication. If the
App operation is missing, fails, or cannot represent the required starting
state, report that evidence and ask for explicit authority before falling back
to a raw Git worktree. CLI-only sessions may use raw Git worktrees directly.

## Session Option Resolution

Resolve session behavior from the canonical fields in `options.md`. Owner
wording is evidence only: record it in the option-resolution row, normalize it
to one value per field, and never compare downstream behavior against the
phrase. If wording could resolve to more than one `delegated_worker_visibility` or
`work_delegation_policy`, ask for canonical field assignments before dispatch.

Do not spawn a background Codex subagent when
`delegated_worker_visibility=visible-codex-app-tasks-only`. If the App
surface is unavailable, require a new canonical selection or keep the work in
`current-orchestrator-session`; never infer a fallback from wording.

If Codex App task tools are requested but unavailable, stop before dispatch
and report the missing create/read/message task surface. Do not silently
downgrade to a background Codex subagent; ask for explicit fallback
authorization or keep
the work in the root session.

## Delegation Rules

- Create one worker per independent ownership boundary: repository, package,
  service, path set, or tightly scoped workstream. Repository boundaries are the
  default isolation heuristic, not a quota.
- In multi-repo projects, use one active worker per affected repo per wave by
  default. Add more only when a repo has independent workstreams with clean
  file, contract, test, and validation boundaries.
- In single repos and monorepos, keep shared contracts, dependencies, root
  config, migrations, generated snapshots, broad tests, conflict resolution,
  and final integration in the root session.
- Stay in root when orchestration overhead dominates, work overlaps heavily, no
  inspectable surface exists, delegation is unauthorized, or remaining work is
  mostly gates, ledger updates, closeout, or publication decisions.
- Do not assign implementation with `parallelization=depends-on` until root
  verifies every separately recorded `dependency_ids` entry. Keep
  `parallelization=root-integrated` implementation in root; workers may inspect
  or prove only when root keeps integration ownership.
- Workers may inspect, implement, test, and report only within their authorized
  mode. They must not spawn sub-workers, create tasks, manage tasks, edit
  ledgers, create active-root claims, decide takeover or handoff, choose branch
  strategy, mutate sources, or delegate their assignment.
- Workers must preserve unrelated local changes and stage only authorized
  paths. Only the root creates, reuses, forks, assigns, renames, messages,
  archives, closes, interrupts, or replaces worker tasks.
- When visible Codex App workers provide helper worktrees, preserve the caller
  checkout branch by default. Root-owned integration, validation, commit, push,
  and PR creation should run from the worker worktree or a dedicated integration
  worktree. Switching the caller checkout is allowed only when the scoped row
  is `starting_checkout_branch_handling=branch-switch-authorized`. An unavailable helper
  checkout does not change that value.
- In the Codex App, if the root decides a new dedicated worktree is needed for
  implementation, integration, or publication, create a visible App task
  with a worktree environment and bind the checkout to that task in the
  ledger. Do not create an unowned raw Git worktree merely to preserve the
  caller checkout. This requirement does not apply in CLI-only sessions.

## Startup Option Resolution

Initialize every session with:

```text
work_delegation_policy=orchestrator-decides-for-each-implementation-workstream
delegated_worker_visibility=orchestrator-decides-between-background-and-visible-workers
max_concurrent_delegated_workers=not-limited-by-authorized-user
visible_app_task_permission=not-requested
max_visible_app_tasks=not-applicable
unmanaged_git_worktree_fallback_permission=not-granted
repository_layout=<from project memory, safe repo evidence, or authorized-user instruction>
```

These defaults authorize internal CLI subagent selection but not visible App
task creation, raw-worktree fallback, or automation mutation. If owner input
changes a default, record the canonical assignment and its evidence in the
ledger `## Option Resolution` table before dispatch.

When visible App tasks may be useful and `visible_app_task_permission=not-requested`, ask
for these fields rather than offering prose reply shapes:

```text
delegated_worker_visibility=<orchestrator-decides-between-background-and-visible-workers|background-codex-subagents-only|visible-codex-app-tasks-only>
visible_app_task_permission=<granted-by-authorized-user|denied-by-authorized-user>
max_visible_app_tasks=<positive integer when permission is granted>
```

Reject incomplete or conflicting combinations using `options.md`. A bare
affirmation is not a value and cannot grant permission or a limit. While a required
field is unresolved, continue only root-owned discovery, source registration,
and wave shaping that does not create workers, edit implementation, mutate
sources, commit, push, or publish.

Do not re-resolve fields for later Feature Specs or waves while the canonical session
snapshot remains applicable. Ask again only when a required field is missing or
the next action would exceed the recorded option values or cross an independent
authority, credential, risk, or gate boundary.

## Execution Report

Before dispatching implementation for each source batch, present a non-blocking
execution report. This report is not an approval prompt and must not ask the
owner to confirm before dispatch. The root may continue after displaying it as
long as the source batch stays inside the recorded option snapshot, delivery
authority, gates, and stop conditions.

Start with a short `Execution Summary` paragraph in plain language. Summarize
the starting wave, root-owned coordination, worker usage, and stop conditions.
Keep concrete canonical values in the tables. A display summary may make them
readable, but it must not introduce another option name or value.

Then use this compact decision table:

| Decision | Planned value | Meaning |
| --- | --- | --- |
| Source items | <issue/PR/Feature Spec/checklist refs> | Durable work sources this report covers. |
| Delivery and gates | <branch/PR/closeout plus tests/autoreview/CI/integration proof> | Landing path and proof before closeout. |
| Stop condition | <scope/surface/auth/delivery/gate change, blocker, or completion> | When the orchestrator must return to the owner. |

Then include one row per workstream. Option fields keep their canonical names
and values; refs and proof stay in separate data columns:

| wave | workstream | actual_execution_location | scope | parallelization | dependency_ids | blocked_issue_ids | dependency_reason | dependency_proof | worker_allowed_actions | expected_output |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <wave> | <name/ref> | <current-orchestrator-session|background-codex-subagent|visible-codex-app-task> | <repo/package/paths> | <independent|depends-on|blocks|root-integrated> | <refs|none> | <refs|none> | <reason|none> | <evidence|pending|none> | <explicit action list> | <patch|report|commit|pull-request> |

A workstream defines the implementation slice. It creates a worker only when
`actual_execution_location` is `background-codex-subagent` or
`visible-codex-app-task`;
`current-orchestrator-session` means the root orchestrator owns that slice directly.

For root-only work, do not write a prose alias such as `none; root-owned` in
the owner-facing report. Use `actual_execution_location=current-orchestrator-session`. If no
automation will be created or updated, do not mention automation in the report
unless it is relevant to a stop condition.

## Recurring Feature Spec Automation

For a recurring Feature Spec automation, require
the Feature Spec-scoped `scheduled_automation_change_permission=granted-by-authorized-user` row and
carry that scoped row plus the canonical session option snapshot into every
run. Ask no Feature Spec-specific worker-surface
question unless a run lacks an applicable canonical field or would exceed its
recorded value.

Process one Feature Spec at a time. If a Feature Spec stops as `blocked`, `needs-owner`, or
`deferred`, record that Feature Spec's blocker and continue to the next unrelated
eligible Feature Spec in a later run. Stop the automation queue only when the blocker is
systemic, such as missing credentials, unavailable worker/task tools, broken
tracker access, unsafe repository state shared by multiple Feature Specs, failing shared
infrastructure, or another general condition that can affect multiple Feature Specs.

Each automation run starts and ends with the ledger: select the next Feature Spec from
`Next Scan/Check`, source status, dependencies, and blocker state, then write
progress, blockers, proof, or the next check before stopping.

## Change Delivery Target Rules

The root passes the exact `change_delivery_target`, its
`delivery_decision_origin`, `change_delivery_permission`, derived
`delivery_allowed_actions`, and supporting branch or PR data. Ad hoc work
defaults to `validated-changes-left-uncommitted`; Feature Spec-backed work
inherits its exact target. Workers enforce only the actions they receive.

`validated-draft-pull-request-published` stops after validated draft
publication and never grants review actions.
`pull-request-ready-for-merge-but-not-merged` may grant only the review actions
required by `codex_review_requirement`. An explicit skip still permits
`mark-pull-request-ready`, but not review request or polling. The refreshed
`target_pull_request_ref` must continue to match any PR-scoped skip evidence.

For generated implementation issues, the root also passes the validated
`## Orchestrator Handoff` projection. Workers may use the handoff for scope,
start rule, dependencies, validation, and closeout, but they must not treat it
as worker authorization, delivery permission, issue-update permission, or
permission to change branch/PR strategy.

| `change_delivery_target` | Worker handling |
| --- | --- |
| `validated-changes-left-uncommitted` | Edit and validate only. Do not commit, push, create or transition a PR, request review, mutate issues, merge, release, or deploy. |
| `local-commit-created-without-pushing` | Require `create-local-commit`; never include `push-target-branch` or PR actions. |
| `changes-pushed-to-target-branch-without-pull-request` | Require the exact target branch plus `create-local-commit` and `push-target-branch`; never create a PR. |
| `validated-draft-pull-request-published` | Root owns branch and PR count. Grant only the actions needed through draft PR publication. |
| `pull-request-ready-for-merge-but-not-merged` | Root owns branch, PR count, review disposition, and the ready-for-merge decision. Grant only exact publication and review actions; never merge. |

If the assigned delivery target conflicts with repository reality, stop and report
`needs-owner`; do not choose a new branch or PR strategy. Workers may commit,
push, open a draft PR, mark a PR ready for review, or request Codex review only
when the prompt names the exact repository, branch/refspec, PR shape, closeout
target, and corresponding explicit actions. A pull-request action is never a
shortcut for commit, push, mark-ready, or review actions.

## Worker Status Vs Root Lifecycle

Workers report execution status. The root orchestrator decides lifecycle:

- Worker status: `done`, `blocked`, `needs-owner`, `ready-for-review`
- Root lifecycle: `integrated`, `retained-for-inspection`, `abandoned`,
  `handoff-pending`

Do not equate a worker saying `done` with the workstream being complete. The
root still needs to inspect the latest state, choose an integration path, rerun
root-owned gates, and record the lifecycle decision in the ledger.

## Visible Thread Naming

For visible Codex App worker tasks, set the task title immediately after
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
available task/subagent inspection tool. Base any steering message on the
current worker status, files touched, blockers, validation, risks, and next
check.

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
  or keep the overlapping integration in the root session;
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

- `handoff`: use `handoff_thread` when available, then inspect the returned
  handoff state or re-read the task with the available status/read tool. Use
  the equivalent inspected worker surface when its checkout should become the
  integration checkout.
- `worker-commit`: accept a worker-prepared commit or branch only when the
  exact `worker_allowed_actions` include `create-local-commit` and the root has
  reviewed the diff.
- `patch-apply`: apply a worker diff or patch in the explicitly named
  integration checkout, then inspect conflicts and rerun root gates. Prefer a
  worker worktree or dedicated integration worktree when one exists; use the
  caller checkout only when
  `starting_checkout_branch_handling=branch-switch-authorized`.
- `manual-root`: reimplement or copy the relevant change in the explicitly
  named integration checkout when the worker output is partial, stale,
  conflicting, or easier to reproduce safely than to apply directly. Preserve
  the caller checkout unless
  `starting_checkout_branch_handling=branch-switch-authorized`.

For every path, inspect the tracked diff, preserve unrelated local changes,
exclude generated ignored artifacts, rerun the required root gates, and record
the integration method, publication checkout, caller checkout disposition, and
proof in the ledger. Do not commit, push, merge, close, release, or mutate
external services unless the current scoped permissions, worker actions, and
gate state permit it.

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

In a Codex App session, a newly created helper worktree must be owned by a
visible App worker task. Create the task through the App worktree target,
record its id/title/path, and use that managed checkout for the assigned work.
If the App cannot create the required worktree, stop before `git worktree add`,
report the exact limitation, and request explicit fallback authority. This rule
does not apply in CLI-only sessions and does not require wrapping an existing
owner-supplied checkout in a new task.

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
  required follow-up hidden only in the worker task.
- `handoff-pending`: the worker's checkout or task is the intended next
  integration surface; record the pending action and owner decision needed.

Do not remove or archive a worker before reading its latest state. Do not remove
a helper worktree that contains unreviewed tracked work, unreported artifacts,
or the only copy of evidence needed for a gate. Once all useful output is
integrated or intentionally abandoned, remove or archive helper surfaces when
that cleanup is safe and available, or record why they remain.

## Worker Allowed Actions

Record every permitted action independently for the exact workstream. Actions
are not a cumulative ladder: `push-target-branch` does not permit a commit, and
`create-or-update-pull-request` does not permit either one.

Canonical actions:

- `inspect-files`: read-only investigation within named paths or objects;
- `edit-files`: change named files only;
- `run-validation`: run the named local proof;
- `create-local-commit`: stage authorized paths and create a local commit on
  the named branch, without pushing;
- `push-target-branch`: push only the named branch or exact refspec;
- `create-or-update-pull-request`: create or update the named PR, including
  authorized closing keywords in its body;
- `mark-pull-request-ready`: transition the named draft PR to ready;
- `request-codex-review`: request review only after the current-head preflight;
- `poll-codex-review`: wait for or inspect the existing request on that head;
- `post-root-provided-review-response`: post only root-supplied disposition text;
- `rerun-ci`: rerun named checks and inspect their result;
- `fix-ci-failure`: edit and validate the named CI repair scope;
- `publish-release`: perform the exact authorized release operation.

`create-local-commit` never permits closing keywords unless
`issue_completion_method=final-commit-closing-keyword` and the independent
issue-update permission names the same issue. `request-codex-review` and
`poll-codex-review` are valid only with
`codex_review_requirement=required-on-current-pull-request-head`. An explicit
review skip may still allow `mark-pull-request-ready`.

Merge, direct issue updates, labels, source closeout, and root-authored
discussion mutations are not worker actions. They remain root-owned with their
own permission rows. Any retired capability value is invalid and stops as
`needs-owner`; never translate it silently.

## Prompt Template

```text
You are a Codex worker for the <portfolio> portfolio.

Scope:
- repository: <repo path or owner/repo>
- workstream: <short name>
- delegated_worker_visibility: <orchestrator-decides-between-background-and-visible-workers|not-applicable|visible-codex-app-tasks-only|background-codex-subagents-only>
- actual_execution_location: <current-orchestrator-session|visible-codex-app-task|background-codex-subagent>
- worker_id: <id or pending>
- worker_title: <title or pending>
- worker_evidence: authorization_state=<authorized-by-invocation|authorized-user-consented|not-authorized>;
  status=<used|unavailable|attempt-failed|root-owned-fallback>;
  evidence=<tool/session/failure>; parallelism=<parallel|sequential|root-owned|simulated>
- wave: <number>
- objective: <one concrete outcome>
- source_id: <stable source id>
- source_ref: <URL, path:line, heading, run id, or ledger item>
- acceptance_criteria: <source-owned completion criteria>
- closeout_target: <local acceptance criteria plus validation, issue close, PR reply, file checkbox/patch, CI rerun, or ledger status>
- worker_allowed_actions: <one or more canonical actions from Worker Allowed Actions>
- capability_snapshot: filesystem=<profile/evidence>; network=<available|restricted|unknown>; gh_auth=<available|unavailable|not-required>; codex_cli=<available|unavailable|not-required>; autoreview=<available|unavailable|reroute-to-root>; checked_at=<time/evidence>
- allowed_paths_or_surfaces: <paths, branches, PRs, issues, or commands>
- change_delivery_target: <validated-changes-left-uncommitted|local-commit-created-without-pushing|changes-pushed-to-target-branch-without-pull-request|validated-draft-pull-request-published|pull-request-ready-for-merge-but-not-merged>
- delivery_decision_origin: <safe-default-for-ad-hoc-work|inherited-from-feature-spec|overridden-by-implementation-issue|specified-by-authorized-user>
- delivery_decision_origin_evidence: <source ref or authorization evidence>
- delivery_permission_source_issue_ref: <issue:<NN>|not-applicable>
- issue_update_permission_source_issue_ref: <issue:<NN>|not-applicable>
- temporary_source_execution_permission: <not-granted|granted-by-authorized-user>
- completion_evidence_policy: <require-live-system-evidence|allow-simulated-evidence-by-authorized-user-exception>
- orchestrator_handoff: <canonical handoff fields, or not-applicable for ad hoc work>
- domain_closeout: <not-applicable|implementation-closeout>
- domain_closeout_data: <exact decisions, target surfaces, evidence, and `$project-memory domain-memory` operation or none>
- change_delivery_permission: <not-required-for-uncommitted-changes|not-granted|granted-for-selected-target>
- change_delivery_permission_evidence: <option-resolution or source-contract evidence>
- delivery_gate_status: <ready|blocked|not-applicable>
- delivery_allowed_actions: <derived canonical action list>
- codex_review_requirement: <required-on-current-pull-request-head|explicitly-skipped-by-authorized-user|not-needed-for-selected-delivery-target>
- codex_review_requirement_evidence: <default or scoped authorized-user-instruction evidence>
- pull_request_count_strategy: <one-pull-request-total|one-pull-request-per-repository|no-pull-request>
- issue_completion_method: <feature-pull-request-closing-keyword|repository-pull-request-closing-keyword|final-commit-closing-keyword|move-local-issue-to-done-after-proof|no-issue-completion>
- issue_update_permission: <no-issue-changes|pull-request-closing-keyword-only|direct-issue-updates-explicitly-authorized>
- parent_spec_applicability: <required|deferred-vehicle|not-applicable>
- parent_spec_applicability_reason: <whole-spec-final-pr|non-default-base|partial-pr|ad-hoc|local-tracker|no-parent|draft-pull-request-target|other-reason>
- parent_spec_closeout: <not-applicable|pending-review|pending-closeout|deferred-to-default-branch|armed|closed|blocked>
- parent_spec_ref: <issue ref or none>
- parent_closeout_vehicle: <PR ref, pending, or none>
- parent_closeout_head: <closeout-qualified SHA or none>
- parent_closeout_base: <branch or none>
- default_branch: <branch or none>
- pr_body_evidence: <URL/fingerprint or none>
- parent_closeout_watch: <not-applicable|root-monitoring|owner-handoff|automation-handoff|complete>
- parent_closeout_watch_evidence: <watch packet, automation id, or none>
- codex_review: <not-applicable|not-requested|requested|received|passed|skipped|blocked>
- codex_review_evidence: <request head/object; GitStack checker status; result head/kind/object; verified provider; terminal status; disposition>
- parallelization: <independent|depends-on|blocks|root-integrated>
- dependency_ids: <source/workstream ids or none>
- blocked_issue_ids: <source/workstream ids or none>
- dependency_reason: <reason or none>
- dependency_proof: <completed proof, pending, or none>
- branch_expectation: <feature-branch|repository-feature-branch|named-target-branch|none>
- target_branch_name: <exact branch or not-applicable>
- integration_method: <handoff|worker-commit|patch-apply|manual-root|pending>
- starting_checkout_branch_handling: <keep-current-branch-checked-out|branch-switch-authorized|not-applicable>
- result_checkout_path: <worker-worktree path|integration-worktree path|caller-checkout path|not-applicable>
- report_channel: this worker surface only
- helper_checkout: <path or unknown>
- next_ledger_check: <time/action or none>
- forbidden_actions: no subdelegation, no ledger edits, no unrelated cleanup,
  no worker/task management, no commit/push/PR/Codex-review
  request/release unless the exact action is listed; no merge or direct
  source closeout under any worker action set; no duplicate Codex-review request when
  GitStack reports a terminal result or active request for the assigned head.

Context:
- Owner request: <summary>
- Current ledger status: <summary>
- Known blockers or assumptions: <bullets>
- Selected gates: <gate names from references/gates.md>
- Required proof: <tests, live proof, CI, autoreview, docs, screenshots>
- Known root-integrated changes since assignment: <bullets or none>

Execution:
1. Inspect the current state before editing.
2. Preserve unrelated uncommitted changes.
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
- Delivery: selected delivery target, branch or PR used, closeout path, and PR links or
  `none`; include ready-for-review state, Codex review policy/state, publication
  checkout, and caller checkout disposition
- Worker evidence: canonical `delegated_worker_visibility`, `actual_execution_location`, and
  `authorization_state`; worker id or session evidence; unavailable or failed
  tool evidence; fallback reason; and whether execution was parallel,
  sequential, root-owned, or simulated
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
expected next check only if the latest state is stale or insufficient. Do
not interrupt a worker with new scope unless the user changed priority, a
contract mismatch was discovered, or a gate failed.

For each progress check, update the ledger with last-read time, worker status,
validation or proof delta, blocker, risk delta, and next check. If a worker
misses its next check or produces the same status for two consecutive
checks without new proof, send one focused unblock request. After the next
no-progress check, choose a root-owned action: continue with a reason, steer,
replace, abandon, retain for inspection, classify as `blocked` or
`needs-owner`, or ask the owner.
