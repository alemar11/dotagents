# Worker Reference

Use this reference before creating, naming, messaging, steering, or closing
Codex worker surfaces or subagents.

## Worker Fields

Resolve session worker fields before delegation.
Load `options.md` first. Session selection fields use that registry; this file
owns worker capability and lifecycle fields.

Worker authorization is resolved per workstream and session by the root
orchestrator. Do not read worker assignments, worker-count preferences,
dispatch flags, authorization ceilings, publication policy, issue mutation policy,
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
| `visible_app_task_permission` | `not-requested`, `granted-by-authorized-user`, `denied-by-authorized-user` | Explicit consent; the granted value selects mandatory one-visible-task-per-Feature-Spec execution. |
| `implementation_checkout_strategy` | `managed-worktree-per-feature-spec`, `serial-caller-checkout-branches` | Visible-task checkout topology. Managed worktrees are the default; the serial caller-checkout strategy requires exact authorized-user evidence requesting no worktrees. |
| `unmanaged_git_worktree_fallback_permission` | `not-granted`, `granted-by-authorized-user` | Permission for an unmanaged Git worktree after managed-worktree failure evidence. |

Worker surface, count, per-wave parallelism, and serial or parallel sequencing
are orchestrator-derived runtime decisions governed by `options.md`, not
session options or user-provided numeric fields. The granted visible-task
mode is the exception to free surface/count selection: surface is visible and
the mapping is exactly one task per implementation-eligible Feature Spec.
Across all worker surfaces, the root may activate one, two, or three eligible
nonterminal Feature Spec executions, never more. Managed-worktree waves may use
any safe count within that ceiling; serial caller-checkout waves may activate
exactly one. A nested subagent remains inside its parent Feature Spec execution
slot and does not increase the Spec count.

Execution fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `actual_execution_location` | `current-orchestrator-session`, `background-codex-subagent`, `visible-codex-app-task` | Where the workstream actually runs. The current-session value works in both CLI and App. |
| `worker_allowed_actions` | See the canonical list below | Independent action list. Merge and final source closeout remain root-owned; an assigned visible Feature Spec task may own every pre-merge delivery action. |

Visible-task Goal fields are derived runtime state, never session options:

| Field | Values | Meaning |
| --- | --- | --- |
| `task_goal_mode` | `pending`, `active`, `unavailable`, `not-applicable` | Goal establishment state for an orchestrator-created visible task. `unavailable` is valid only when the runtime exposes no Goal tool; background workers use `not-applicable`. |
| `task_goal_status` | `pending`, `active`, `complete`, `blocked`, `not-applicable` | Current task-owned Goal status. `not-applicable` accompanies unavailable Goal mode or a non-visible worker. |
| `task_goal_dispatch_objective_sha256` | 64 lowercase hex characters or `not-applicable` | Root-owned fingerprint of the exact objective sent at dispatch. |
| `task_goal_reported_objective_sha256` | 64 lowercase hex characters, `pending`, or `not-applicable` | Task-reported fingerprint of the objective it established or repeated as fallback. |
| `task_goal_evidence` | Goal tool or task result ref, or `not-applicable` | Root-readable Goal, dispatch, or current task result. |
| `task_goal_missing_tool` | `runtime-goal-tool`, `not-applicable` | Exact missing surface for the unavailable fallback. |

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
| `integration_method` | `handoff`, `worker-commit`, `patch-apply`, `manual-root`, `pending` | Integration path. `manual-root` is invalid in mandatory Feature Spec task mode. Replace `pending` before lifecycle closeout or record that no output was integrated. |
| `starting_checkout_branch_handling` | `keep-current-branch-checked-out`, `branch-switch-authorized`, `not-applicable` | Whether the checkout where the owner invoked the orchestrator may switch branches during integration or publication. |
| `result_checkout_path` | `worker-worktree`, `integration-worktree`, `caller-checkout`, `not-applicable` | Checkout where commit, push, draft PR publication, and ready-for-review transition will run. |

For `serial-caller-checkout-branches`, `starting_checkout_branch_handling` must
be `branch-switch-authorized` and `result_checkout_path` must be
`caller-checkout`. Record the original branch and HEAD/status fingerprint, the
Spec's exact target branch, branch creation or verified-resume evidence, and
the final original-branch restoration proof. These are runtime evidence, not
additional user options.

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
available. Goal operations run inside the owning task and currently map to
`create_goal`, `get_goal`, and `update_goal` when exposed. The `/goal` command
is the user-facing equivalent, not a command for the root to type remotely.

The root and each spawned Codex App task may use the internal subagent lifecycle
exposed in that task. This nested use does not authorize the worker to create
or manage visible App tasks.

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

## Visible Task Goal Contract

Every visible Codex App task created by the orchestrator must establish its
own assignment-scoped Goal before it starts inspection, implementation, or
review work. This is automatic behavior derived from visible-task creation,
not a user-configurable option. Internal background subagents are exempt and
remain accountable through their parent task. The owner's explicit
`$codex-orchestrator` invocation authorizes this per-task Goal creation as
part of the selected orchestration workflow.

The root includes this exact behavior in the initial task prompt. The task
searches its current runtime tool registry, then uses `get_goal` to reuse a
matching active Goal or `create_goal` to establish one in its own context. The
root cannot create or complete a Goal on another task's behalf. Use this
objective shape:

```text
Complete <exact Feature Spec title or assigned workstream> through
<change_delivery_target> and every assigned validation and closeout gate.
Continue until that terminal target is achieved or a real blocker stops work.
```

After the task reports the Goal tool result, the root reads the task with
`read_thread`,
compares the reported objective fingerprint with the hash of the exact prompt
objective, and records all five `task_goal_*` evidence fields in the ledger.
Do not advance a visible task beyond `created` while its Goal state is
`pending`. A resumed task reuses its matching active Goal. If it has a
different unfinished Goal, treat that as drift and stop or replace the task;
do not overwrite it. A replacement task creates a new Goal.

The owning task updates its Goal and marks it complete only after the exact
assigned delivery target and gates are satisfied. It may mark the Goal blocked
only under the runtime Goal tool's own blocked-state contract. The root
monitors and records those transitions but never updates the task's Goal.
Record `target-complete` for a completed non-merge-ready delivery target; use
`merge-ready` for the default merge-ready target.

Use `task_goal_mode=unavailable` only when the current task runtime exposes
no Goal tool after registry inspection. In that case, the task repeats the
exact objective in its report with the missing-tool evidence, the root records
`task_goal_status=not-applicable`, and work may continue. An exposed Goal tool
that rejects or fails the operation is not the unavailable fallback: report
the failure and stop or replace the task according to its lifecycle rules.

Before task creation, the root computes
`task_goal_dispatch_objective_sha256` from the exact prompt objective; the
task never supplies or rewrites that field. The task reports
`task_goal_reported_objective_sha256`, and the root requires exact equality
before accepting active or unavailable Goal mode. Pending creation uses
`pending` for the reported hash and the existing technical
`thread-message:` or `goal-create-message:` evidence prefix. The unavailable
fallback uses `thread-read:`. These persisted evidence prefixes map to the
`create_thread`/`send_message_to_thread` and `read_thread` tool boundary; they
are not user-facing orchestration terminology.
For an active Goal, `task_goal_evidence` identifies the Goal tool or task
result and `task_goal_missing_tool=not-applicable`. The unavailable fallback
requires a current `thread-read:` evidence ref from `read_thread` plus
`task_goal_missing_tool=runtime-goal-tool`. Background workers use
`not-applicable` for both hashes and the remaining evidence fields.

## Mandatory Feature Spec Task Mode

When `visible_app_task_permission=granted-by-authorized-user`, apply all of
these rules as one execution contract:

- Create exactly one active visible Codex App task for each
  implementation-eligible Feature Spec selected for dispatch in the current
  wave. A queued or dependency-blocked Spec receives its task when its wave
  starts. Use the canonical Feature Spec ref as the stable assignment key and
  set the task title to the exact Feature Spec title immediately after
  creation. Send the exact assignment and terminal delivery target, then
  require the task to establish its own Goal and report evidence before
  implementation starts.
- Assign every generated issue, affected repository, implementation change,
  integration step, validation run, commit, push, draft PR, Codex-review
  request and poll, feedback disposition and fix, CI repair, parent-closing-
  keyword preparation, and ready transition for that Feature Spec to its one
  task. A multi-repository Spec still has one task and may produce one PR
  per repository.
- Do not split one Feature Spec across multiple active visible tasks and do
  not reuse one visible task for multiple Feature Specs. The root may choose
  serial or parallel starts from the dependency graph and live capacity, but
  it may not change the one-to-one mapping or exceed three nonterminal Feature
  Spec executions across visible tasks, background workers, and root-owned
  execution combined. Internal subagents never consume another Spec slot.
- The root is orchestration-only: register and group sources, resolve authority
  and strategy, create/title/read/message/replace/archive tasks, maintain the
  ledger, reconcile read-only evidence, and report status. It must not edit,
  integrate, validate, commit, push, mutate the PR, request or poll Codex
  review, disposition review feedback, fix review or CI failures, run the
  review closeout workflow, or mark the PR ready for these Specs.
- The assigned task may create and manage any internal background subagent
  topology it finds useful within the inherited scope and action ceiling. It
  remains accountable for integrating those results and reporting their ids,
  scopes, outcomes, and serial or parallel topology to the root.
- If a task drifts from the selected target or closeout sequence, read its
  latest state and send a precise corrective message naming the mismatch,
  expected next state, and preserved authority. If it is stale or fails,
  resume-equivalent or replace it with another visible task for the same
  Feature Spec after recording lifecycle evidence. Keep only one active task
  for the Spec. Never fall back to root-owned or background-only
  implementation, integration, validation, or review; stop as `needs-owner` or
  blocked when no visible replacement can safely continue.
- A mandatory Feature Spec task may not use `autoreview=reroute-to-root`;
  replace the task or record the unavailable gate as a blocker.

### Checkout Strategy

Use `implementation_checkout_strategy=managed-worktree-per-feature-spec` unless
the authorized user explicitly says not to use worktrees. In the default mode,
create the visible task with its managed worktree target before implementation.
Each Spec has an isolated checkout and the root may schedule independent Specs
in parallel when dependencies and capacity permit, up to the run-wide ceiling
of three nonterminal Feature Spec executions.

When an otherwise blocked downstream Spec carries an explicit
`upstream-merge-ready-head` dependency edge, load `stacked-feature-specs.md`
before creating its task or checkout. That reference is the only managed-
worktree exception that may start a downstream Spec from an unmerged upstream
head. Generic `depends-on` relationships remain blocked until their recorded
dependency proof satisfies the ordinary start rule.

Normalize an exact no-worktree instruction to
`implementation_checkout_strategy=serial-caller-checkout-branches`. That value
selects this complete controller flow:

1. Before the first Spec, require an attached branch and record the caller
   checkout's original branch, HEAD, and clean `git status --short`
   fingerprint. A detached or dirty checkout blocks local dispatch; never carry
   its changes onto a Spec branch.
2. Select exactly one implementation-eligible Feature Spec. Verify its
   `target_branch_name` is a valid dedicated feature branch, differs from the
   original branch, and is not assigned to another Feature Spec in the same
   repository during this run. Append its immutable
   Spec/repository/target-branch ownership to the run-wide serial branch-
   assignment registry before switching, and retain that row after completion.
   Reject an uncommitted terminal delivery target because it cannot survive the
   required branch restoration safely.
3. From the resolved baseline, create and switch to that branch. On recovery,
   switch to an existing branch only after proving it belongs to the same Spec
   and matches the recorded baseline. Record the exact Git evidence.
4. Create or resume the Spec's visible task in Local, establish its Goal, and
   keep it as the only active visible Feature Spec task. The root owns only the
   controller Git operations that create, switch, verify, and restore branches;
   the task still owns every implementation, validation, publication, review,
   fix, CI, and ready-transition action.
5. Do not switch branches or dispatch another Spec when the task is merely
   committed, pushed, in draft, waiting for review, fixing feedback, or waiting
   for CI. Wait until it reaches its complete selected delivery target—normally
   a clean current-revision Codex review, passing CI, and merge-ready PR.
6. After terminal task evidence is reconciled, require a clean feature branch,
   switch back to the original branch, and prove its branch, HEAD, and status
   match the recorded baseline. Only then may the next Spec begin.

If any branch preparation, terminal cleanliness, or restoration check fails,
stop the serial lane as `needs-owner` or blocked and never dispatch another
Spec from that state. Do not use a worktree as a
silent fallback after the user selected no worktrees, do not implement on the
original branch, and do not reuse one repository/feature-branch pair for
different Specs.
Internal subagents may explore or review read-only work in parallel, but only
one agent may mutate the caller checkout at a time.

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
scope, authority, and gates permit only outside mandatory Feature Spec task
mode. In mandatory mode, steer or replace the assigned visible task and stop
if no capable visible replacement exists; the root must not take over the
implementation or review action. Never copy credentials into a worker to
manufacture capability.

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

Outside mandatory Feature Spec task mode, the root chooses the worker
surface, number of workers, and serial or parallel split for each wave within
`visible_app_task_permission`, live runtime capacity, and the work graph. In
mandatory mode, the surface and one-task-per-Spec count are fixed. Managed-
worktree mode leaves a one-to-three serial or parallel scheduling choice to the
root; serial caller-checkout mode forces one complete Spec task at a time. The
three-Spec ceiling applies across root-owned execution, background workers, and
visible tasks, not separately to each surface. Each spawned Codex App task may
choose its own internal background subagent topology within its assigned scope;
those subagents share the parent Spec slot.
There is no separate workspace execution mode, delegation toggle, worker-count
field, visibility selector, or parallelism option.

When the current runtime is the Codex App and the selected strategy requires a new dedicated
worker, integration, or publication worktree, require
`visible_app_task_permission=granted-by-authorized-user` and create the task with
a worktree target before implementation. Do not run the
implementation through CLI subagents in the caller checkout and move the
integrated diff into a manually created worktree only for publication. If the
App operation is missing, fails, or cannot represent the required starting
state, report that evidence and ask for explicit authority before falling back
to a raw Git worktree. CLI-only sessions may use raw Git worktrees directly.

Without visible-task consent, the viable App default is root or background
subagent execution inside an existing owner-supplied checkout with non-
overlapping path ownership; do not create a new dedicated worktree. If safe
isolation requires a new checkout, ask for visible-task consent or the exact
raw-worktree fallback permission before dispatch. This checkout rule never
permits Feature Spec implementation to bypass mandatory visible task mode
after consent is granted.

## Session Option Resolution

Resolve session behavior from the canonical fields in `options.md`. Owner
wording is evidence only: record it in the option-resolution row, normalize it
to one value per field, and never compare downstream behavior against the
phrase.

If visible App task tools were authorized but are unavailable, record the
missing create/read/message surface. For Feature Spec implementation, stop
before dispatch or preserve the existing assigned visible task for later
recovery; do not reshape that work into background Codex subagents or root-owned
execution. A raw Git worktree still requires
`unmanaged_git_worktree_fallback_permission=granted-by-authorized-user`, but
that permission changes only checkout management and never waives the required
visible task.

If `implementation_checkout_strategy=serial-caller-checkout-branches` is
selected and Local task creation or branch switching is unavailable, stop with
the exact capability evidence. Neither a managed nor raw worktree is an
authorized fallback for an explicit no-worktree run.

## Delegation Rules

- In mandatory Feature Spec task mode, group by canonical Feature Spec ref,
  not repository, package, issue, or path. One Spec gets one active visible
  task even when it spans multiple repositories or generated issues.
- Outside that mode, create one worker per independent ownership boundary:
  repository, package, service, path set, or tightly scoped workstream.
  Repository boundaries are the default isolation heuristic, not a quota.
- Outside that mode, multi-repo work may use one active worker per affected
  repo per wave when the file, contract, test, and validation boundaries are
  clean. Mandatory mode keeps all repos for one Spec under its assigned task.
- Outside mandatory mode, shared contracts, dependencies, root config,
  migrations, generated snapshots, broad tests, conflict resolution, and final
  integration may stay in the root session. In mandatory mode, the assigned
  task owns those implementation surfaces for its Spec.
- Never keep implementation or review in the root while mandatory mode is
  active. Work that cannot safely run in its assigned visible task remains
  undispatched or blocked.
- Do not assign implementation with `parallelization=depends-on` until root
  verifies every separately recorded `dependency_ids` entry. Outside mandatory
  Feature Spec task mode, keep `parallelization=root-integrated`
  implementation in root; workers may inspect or prove only when root keeps
  integration ownership. Inside mandatory mode, that value still means the
  work must integrate as one unit, but the assigned Feature Spec task is the
  integration surface and the root remains orchestration-only.
- The only dependency that may dispatch from an unmerged head is an explicit
  same-repository `upstream-merge-ready-head` edge that passes
  `stacked-feature-specs.md`. It still uses a distinct downstream task, branch,
  managed worktree, and pull request; it never shares or supersedes the
  upstream task or pull request.
- Workers may inspect, implement, test, and report only within their authorized
  mode. They may create and manage internal background subagents within the
  assigned scope and action set, but those subagents inherit the same authority
  ceiling and must not create visible App tasks, edit ledgers, create active-root
  claims, decide takeover or handoff, choose branch strategy, or mutate sources.
  The parent worker reports nested subagent ids, scopes, outcomes, and topology
  to the root.
- Workers must preserve unrelated local changes and stage only authorized
  paths. Only the root creates, reuses, forks, assigns, renames, messages,
  archives, or replaces visible App tasks. Each task owns the lifecycle of its
  internal subagents.
- When visible Codex App workers provide helper worktrees, preserve the caller
  checkout branch by default. In managed-worktree mandatory mode, task-owned integration,
  validation, commit, push, and PR creation run from its managed worktree. In
  other modes, root-owned publication may use the worker worktree or a dedicated
  integration worktree. Switching the caller checkout is allowed only when the scoped row
  is `starting_checkout_branch_handling=branch-switch-authorized`. An unavailable helper
  checkout does not change that value.
- In the Codex App, if the root decides a new dedicated worktree is needed for
  implementation, integration, or publication, create a visible App task
  with a worktree environment and bind the checkout to that task in the
  ledger. Do not create an unowned raw Git worktree merely to preserve the
  caller checkout. This requirement does not apply in CLI-only sessions.
- In serial caller-checkout mode, the root may create, switch, verify, and
  restore the dedicated Spec branch because those are controller-owned checkout
  operations. It must not edit files, resolve implementation conflicts, commit,
  push, or perform review work. Keep exactly one active Spec task until the full
  target is complete and the original caller branch has been restored.

## Startup Option Resolution

Initialize every session with:

```text
visible_app_task_permission=not-requested
implementation_checkout_strategy=managed-worktree-per-feature-spec
unmanaged_git_worktree_fallback_permission=not-granted
repository_layout=<from project memory, safe repo evidence, or authorized-user instruction>
```

Orchestrator invocation authorizes internal background subagent selection but
not visible App task creation, raw-worktree fallback, or automation mutation.
If owner input changes a default, record the canonical assignment and its
evidence in the ledger `## Option Resolution` table before dispatch.

When visible App tasks may be useful and
`visible_app_task_permission=not-requested`, ask for this field rather than
offering prose reply shapes:

```text
visible_app_task_permission=<granted-by-authorized-user|denied-by-authorized-user>
```

Reject conflicting assignments using `options.md`. A bare affirmation is not a
value and cannot grant permission. While visible-task permission is unresolved,
do not create visible App tasks; continue with root-owned work and internal
background subagents when safe. Stop only when a managed visible worktree is
required and no authorized fallback can represent it.

Do not re-resolve fields for later Feature Specs or waves while the canonical session
snapshot remains applicable. Ask again only when a required field is missing or
the next action would cross an independent
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
When visible task permission is granted, every Feature Spec-backed row must use
`visible-codex-app-task`, and every row sharing the same Feature Spec ref must
name the same worker id. The report must also prove that each active visible
worker maps to only one Feature Spec.

For root-only work, do not write a prose alias such as `none; root-owned` in
the owner-facing report. Use `actual_execution_location=current-orchestrator-session`. If no
automation will be created or updated, do not mention automation in the report
unless it is relevant to a stop condition.

## Recurring Feature Spec Automation

For a recurring Feature Spec automation, require
the Feature Spec-scoped `scheduled_automation_change_permission=granted-by-authorized-user` row and
carry that scoped row plus the canonical session option snapshot into every
run. Ask no Feature Spec-specific worker-surface
question unless a run would create a visible App task without an applicable
granted permission row.

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
required by `codex_review_requirement`. For the required path, keep the PR draft
while request and polling actions run; `mark-pull-request-ready` becomes
actionable only after a terminal current-revision review with no unresolved
actionable feedback, completed feedback disposition, validation, and current CI.
An explicit skip still permits
`mark-pull-request-ready` after the remaining gates pass, but not review request
or polling. The refreshed `target_pull_request_ref` must continue to match any
PR-scoped skip evidence.

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
| `validated-draft-pull-request-published` | Root decides branch and PR count. In mandatory mode, the assigned Feature Spec task executes through draft PR publication. |
| `pull-request-ready-for-merge-but-not-merged` | Root decides branch, PR count, and permission. In mandatory mode, the assigned Feature Spec task executes publication, review request and polling, disposition and fixes, CI, parent-closeout preparation, and mark-ready; never merge. |

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
root still reads the latest state and records the lifecycle decision. Outside
mandatory mode it also chooses an integration path and reruns root-owned gates.
Inside mandatory mode it reconciles the task's current proof read-only and
steers the task to finish any missing integration or gate; it never performs
that work itself.
For an assigned visible Feature Spec task, `done` or `ready-for-review` is not
terminal until every PR for the Spec is non-draft and the selected merge-ready
target plus required closeout evidence is reached.

## Visible Task Naming

In mandatory Feature Spec task mode, set the visible task title immediately
after creation to the exact canonical Feature Spec title, including its
`Feature Spec: ` prefix when that is the source title:

```text
<exact Feature Spec title>
```

Do not rename that task for phase or status changes and do not reuse it for
another Spec. Outside mandatory mode, use `<Project>: <short current task>` for
any explicitly authorized visible ad hoc worker. Avoid status-only names such
as `Worker 1`, `Active`, or `Needs review`. Record the Feature Spec ref, exact
source title, worker id, and current task title in the ledger. Use the title
transport encoding from `ledger-template.md` only inside ledger table/token
fields; decode it before setting or comparing the actual App task title.

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
  with the accepted root changes, or create a fresh worker from the current
  root. Keeping overlapping integration in the root is allowed only outside
  mandatory Feature Spec task mode;
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

Outside mandatory Feature Spec task mode, the root orchestrator owns
integration and chooses one path per worker output:

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

In mandatory Feature Spec task mode, the assigned task owns integration in its
selected managed worktree or prepared serial caller-checkout branch and may use
`handoff`, `worker-commit`, or `patch-apply` internally for its nested
subagents. `manual-root` is forbidden. The root reads
the resulting Git/PR/proof state and either accepts the evidence or sends the
task a corrective message; it never applies, copies, reimplements, validates,
or publishes the change itself.

For every path, the owning execution surface inspects the tracked diff,
preserves unrelated local changes, excludes generated ignored artifacts, and
runs the required gates. The root records the integration method, publication
checkout, caller checkout disposition, and proof in the ledger; in mandatory
mode it does so from task evidence without rerunning the work. Do not commit,
push, merge, close, release, or mutate external services unless the current
scoped permissions, worker actions, and gate state permit it.

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

This section applies only to `managed-worktree-per-feature-spec` and authorized
raw-worktree fallback. Under `serial-caller-checkout-branches`, do not create a
helper worktree; use the clean caller checkout and serial branch-rotation flow.

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

- `integrated`: output was accepted into the chosen integration checkout and
  required gates passed. In mandatory mode those gates were executed by the
  assigned task and reconciled read-only by the root. The worker can then be
  archived or its helper worktree removed.
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
- `request-codex-review`: request review only after the current-revision preflight;
- `poll-codex-review`: run the one bounded GitStack waiter for the existing
  request for that revision; never implement caller-owned check/sleep polling;
- `post-review-disposition`: post the assigned task's evidence-backed
  disposition for feedback on its current PR and head;
- `rerun-ci`: rerun named checks and inspect their result;
- `fix-ci-failure`: edit and validate the named CI repair scope;
- `publish-release`: perform the exact authorized release operation.

`create-local-commit` never permits closing keywords unless
`issue_completion_method=final-commit-closing-keyword` and the independent
issue-update permission names the same issue. `request-codex-review` and
`poll-codex-review` are valid only with
`codex_review_requirement=required-on-current-pull-request-head`. An explicit
review skip may still allow `mark-pull-request-ready`. Report the initial
GitStack observation and later fingerprint or terminal transitions; unchanged
waiter attempts are not worker progress and must not trigger repeated reports.

Merge, direct issue updates, labels, and final source closeout are not worker
actions. They remain root-owned with their own permission rows. In mandatory
mode, `post-review-disposition` and authorized parent-closing-keyword changes
are part of the assigned task's pre-merge PR closeout; the root must not post
them for the task. Any retired capability value is invalid and stops as
`needs-owner`; never translate it silently.

## Prompt Template

```text
You are a Codex worker for the <portfolio> portfolio.

Scope:
- repository: <repo path or owner/repo>
- workstream: <short name>
- workstream_ids: <all generated issue/workstream ids for this Feature Spec, or one bounded id>
- workstream_repository_refs: <comma-separated canonical repository refs>
- feature_spec_ref: <canonical Feature Spec URL/path/ref or not-applicable>
- feature_spec_title: <exact canonical Feature Spec title or not-applicable>
- feature_spec_task_assignment: <required|not-applicable>
- lifecycle_owner: <visible-feature-spec-task|bounded-worker>
- codex_review_poll_owner: <visible-feature-spec-task|assigned-worker|not-applicable>
- root_implementation_fallback: <forbidden|not-applicable>
- visible_app_task_permission: <not-requested|granted-by-authorized-user|denied-by-authorized-user>
- implementation_checkout_strategy: <managed-worktree-per-feature-spec|serial-caller-checkout-branches>
- actual_execution_location: <current-orchestrator-session|visible-codex-app-task|background-codex-subagent>
- worker_id: <id or pending>
- worker_title: <title or pending>
- task_goal_objective: <exact assignment-scoped outcome through the selected delivery target>
- task_goal_mode: <pending|active|unavailable|not-applicable>
- task_goal_status: <pending|active|complete|blocked|not-applicable>
- task_goal_dispatch_objective_sha256: <root-computed 64-lowercase-hex or not-applicable>
- task_goal_reported_objective_sha256: <task-reported 64-lowercase-hex, pending, or not-applicable>
- task_goal_evidence: <goal tool/task result ref or not-applicable>
- task_goal_missing_tool: <runtime-goal-tool|not-applicable>
- worker_evidence: authorization_state=<authorized-by-invocation|authorized-user-consented|not-authorized>;
  status=<used|unavailable|attempt-failed|root-owned-fallback>;
  evidence=<tool/session/failure>; parallelism=<parallel|sequential|root-owned|simulated>
- internal_subdelegation: allowed-within-assigned-scope; evaluate whether bounded
  internal background subagents would materially help this assignment; use them
  when useful, otherwise proceed directly; report nested subagent ids, scopes,
  outcomes, and parallel or sequential topology
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
- parent_closeout_merge_base: <closeout-qualified SHA or none>
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
- caller_checkout_original_branch: <branch|per-repository-checkpoints|not-applicable>
- caller_checkout_target_branch: <exact Spec branch|not-applicable>
- caller_checkout_branch_evidence: <baseline HEAD/status plus create/switch/resume proof|not-applicable>
- caller_checkout_restore_state: <pending|restored|not-applicable>
- caller_checkout_restore_evidence: <branch and HEAD/status proof|pending|not-applicable>
- report_channel: this worker surface only
- helper_checkout: <path or unknown>
- next_ledger_check: <time/action or none>
- forbidden_actions: no visible App task creation or management, no sibling or
  root-worker management, no ledger edits, no unrelated cleanup, no commit/push/PR/Codex-review
  request/release unless the exact action is listed; no merge or direct
  source closeout under any worker action set; no duplicate Codex-review request when
  GitStack reports a terminal result or active request for the assigned revision;
  no work on another Feature Spec.

Context:
- Owner request: <summary>
- Current ledger status: <summary>
- Known blockers or assumptions: <bullets>
- Selected gates: <gate names from references/gates.md>
- Required proof: <tests, live proof, CI, autoreview, docs, screenshots>
- Known root-integrated changes since assignment: <bullets or none>

Execution:
1. If this is a visible Codex App task, establish or resume the exact
   `task_goal_objective` with the runtime Goal tool before doing assigned
   work. Report its state and evidence; if no Goal tool exists, report the exact
   objective and unavailable-tool fallback instead.
2. Inspect the current state before editing.
3. Preserve unrelated uncommitted changes. In serial caller-checkout mode,
   verify that this task is on its exact dedicated Spec branch and do not
   create, switch, or reuse another branch.
4. If editing, run focused validation.
5. Run or request autoreview when required by the gate.
6. Stop and report if blocked by access, ambiguous owner intent, unsafe state,
   missing dependency, worker-reported risk, or a gate that cannot be
   satisfied.

Final report:
- Status: done|blocked|needs-owner|ready-for-review
- Source disposition: completed|partial|blocked|needs-owner|deferred|unchanged
- Changes: files or external objects touched
- Validation: commands run and outcomes
- Delivery: selected delivery target, branch or PR used, closeout path, and PR links or
  `none`; include ready-for-review state, Codex review policy/state, publication
  checkout, checkout strategy, caller-checkout branch preparation/restoration
  evidence, and caller checkout disposition
- Feature Spec task: exact Feature Spec ref/title, visible task id/title,
  lifecycle ownership, task Goal objective/mode/status/evidence, PR refs,
  Codex-review polling state, drift corrections, and whether the selected
  target is fully reached
- Worker evidence: canonical `visible_app_task_permission`, `actual_execution_location`, and
  `authorization_state`; worker id or session evidence; unavailable or failed
  tool evidence; nested subagent ids/scopes/outcomes; fallback reason; and
  whether execution was parallel, sequential, root-owned, or simulated
- Scheduling: current wave assignment, unlock state, and dependency source
- Gate status: pass|fail|blocked|not-applicable with root-verifiable evidence
- Generated artifacts: ignored local files or directories created, or none
- Risks: residual risks, dependency audit warnings, security findings,
  untested adapters, setup gaps, or test gaps
- Next: exact owner or orchestrator action
```

Use `caller_checkout_original_branch=per-repository-checkpoints` whenever
`workstream_repository_refs` contains more than one repository. Each original
branch, HEAD, and clean-status fingerprint then comes exclusively from that
repository's serial caller-checkout checkpoint.

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
no-progress check, choose an orchestration action: continue with a reason,
steer, replace, abandon, retain for inspection, classify as `blocked` or
`needs-owner`, or ask the owner. In mandatory mode, none of those choices may
transfer implementation, integration, validation, PR mutation, or review work
to the root or a background-only worker.
