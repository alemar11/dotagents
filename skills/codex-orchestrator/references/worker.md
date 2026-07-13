# Worker Reference

Use this reference before creating, naming, messaging, steering, or closing
Codex worker threads or subagents.

## Worker Fields

Resolve session worker fields before delegation.
Load `options.md` first. Session selection fields use that registry; this file
owns worker capability and lifecycle fields.

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
In the current Codex App surface, project-scoped visible-thread creation uses
`codex_app.list_projects` before `codex_app.create_thread`.

Session option fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `delegation_mode` | `auto`, `disabled`, `bounded` | Whether the root may delegate and whether `worker_limit` bounds delegation. |
| `worker_surface` | `auto`, `root-thread`, `cli-subagent`, `codex-app-thread` | Requested session surface. `codex-app-thread` is a separately created visible App task. |
| `app_thread_consent` | `not-requested`, `granted`, `denied` | Session consent for visible App tasks. |
| `raw_worktree_fallback` | `forbidden`, `owner-approved` | Whether an App session may fall back to a raw Git worktree after managed-worktree failure evidence. |

`worker_limit` and `app_thread_limit` are numeric/data fields governed by
`options.md`, not prose or boolean option values.

Execution fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `actual_workstream_surface` | `root-thread`, `cli-subagent`, `codex-app-thread` | Where the workstream actually runs. Display `root-thread` owner-facing as `root thread (no-delegation)`. Do not present internal subagents as separately created App tasks. |
| `worker_authorization` | `inspect`, `implement`, `commit`, `push`, `pr`, `review-ready`, `ci-rerun-fix`, `release` | Capability flags; list every allowed action explicitly. `review-ready` also requires exact root-listed sub-actions. Merge and source closeout remain root-owned. |

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
| `publication_checkout` | `worker-worktree`, `integration-worktree`, `caller-checkout`, `not-applicable` | Checkout where commit, push, draft PR publication, and ready-for-review transition will run. |

In a Codex App session, `worker-worktree` and `integration-worktree` mean a
worktree owned by a visible App thread whenever the root creates or allocates a
new dedicated checkout. Record the App thread id with the checkout. This
binding does not apply in CLI-only sessions or to an existing owner-supplied
checkout.

## Runtime Tool Mapping

Search the current tool registry before dispatch or lifecycle operations; tool
names are runtime-dependent. In the current surface, internal subagent
operations map to `spawn_agent`, `list_agents`, `send_message`,
`followup_task`, `interrupt_agent`, and `wait_agent`. Separately created App
tasks map to `list_projects`, `create_thread`, `list_threads`, `read_thread`,
`send_message_to_thread`, title/archive/pin, fork, and handoff/status tools.

Do not claim a resume or close operation when the runtime exposes only
follow-up, interrupt, or archive. Read current state first, use the narrowest
available lifecycle operation, and record the actual tool and result. For App
worktree creation, starting state may be the project default, an existing named
branch, or the current working tree when supported; a branch start argument
selects an existing ref and does not name a new branch.

Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases. Treat older `push-pr` authorization as a legacy alias for
`commit`, `push`, and `pr`, then rewrite touched values to the exact authorized
subset.

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
- `checked_at`: timestamp plus the tool, thread metadata, or command that
  produced the evidence.

Do not assume a fork inherits broader permissions than its parent. If a
snapshot changes or an operation fails with permission, network,
authentication, or state-storage evidence, refresh the snapshot once and stop
retrying that operation in the worker. Route it to a capable root when current
scope, authority, and gates permit; otherwise record the blocker. Never copy
credentials into a worker to manufacture capability.

Automation creation, updates, and scheduling require a matching source- or
workstream-scoped `automation_authority=explicit-owner-authorization` row and are
runtime-tool-dependent. Project memory does not store scheduled check timing
and cannot supply that option.
The ledger is the monitoring surface: record source status,
worker/workstream status, blockers, `Last Read`, and `Next Check` /
`Next Scan/Check` there. The root may create, update, or schedule an automation
only when the runtime exposes automation tooling and the matching scoped
option-resolution row records
`automation_authority=explicit-owner-authorization` with owner evidence naming
the exact automation target.
If automation tooling is unavailable, do not imply anything was scheduled;
draft the proposed automation instructions, schedule, and handoff text for
owner action.

The root chooses the number of workers and split for each wave within
`delegation_mode`, `worker_surface`, `worker_limit`, `app_thread_consent`, and
`app_thread_limit`. It may still keep work in the root thread or stop for owner
input when source, repo, dependency, gate, or tool state makes dispatch unsafe.

When the current runtime is the Codex App and the root chooses a new dedicated
worker, integration, or publication worktree, select `codex-app-thread` and
create the thread with a worktree target before implementation. Do not run the
implementation through CLI subagents in the caller checkout and move the
integrated diff into a manually created worktree only for publication. If the
App operation is missing, fails, or cannot represent the required starting
state, report that evidence and ask for explicit authority before falling back
to a raw Git worktree. CLI-only sessions may use raw Git worktrees directly.

## Session Option Resolution

Resolve session behavior from the canonical fields in `options.md`. Owner
wording is evidence only: record it in the option-resolution row, normalize it
to one value per field, and never compare downstream behavior against the
phrase. If wording could resolve to more than one `worker_surface` or
`delegation_mode`, ask for canonical field assignments before dispatch.

Do not spawn a `cli-subagent` when `worker_surface=codex-app-thread`. If the App
surface is unavailable, require a new canonical selection or keep the work in
`root-thread`; never infer a fallback from wording.

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
- Do not assign implementation with `parallelization=depends-on` until root
  verifies every separately recorded `dependency_ids` entry. Keep
  `parallelization=root-integrated` implementation in root; workers may inspect
  or prove only when root keeps integration ownership.
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
  worktree. Switching the caller checkout is allowed only when the scoped row
  is `caller_checkout_policy=caller-checkout-approved`. An unavailable helper
  checkout does not change that value.
- In the Codex App, if the root decides a new dedicated worktree is needed for
  implementation, integration, or publication, create a visible App thread
  with a worktree environment and bind the checkout to that thread in the
  ledger. Do not create an unowned raw Git worktree merely to preserve the
  caller checkout. This requirement does not apply in CLI-only sessions.

## Startup Option Resolution

Initialize every session with:

```text
delegation_mode=auto
worker_surface=auto
worker_limit=unbounded
app_thread_consent=not-requested
app_thread_limit=unspecified
raw_worktree_fallback=forbidden
```

These defaults authorize internal CLI subagent selection but not visible App
task creation, raw-worktree fallback, or automation mutation. If owner input
changes a default, record the canonical assignment and its evidence in the
ledger `## Option Resolution` table before dispatch.

When visible App tasks may be useful and `app_thread_consent=not-requested`, ask
for these fields rather than offering prose reply shapes:

```text
worker_surface=<auto|root-thread|cli-subagent|codex-app-thread>
app_thread_consent=<granted|denied>
app_thread_limit=<positive integer when granted>
```

Reject incomplete or conflicting combinations using `options.md`. A bare
affirmation is not a value and cannot grant consent or a limit. While a required
field is unresolved, continue only root-owned discovery, source registration,
and wave shaping that does not create workers, edit implementation, mutate
sources, commit, push, or publish.

Do not re-resolve fields for later PRDs or waves while the canonical session
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
| Source items | <issue/PR/PRD/checklist refs> | Durable work sources this report covers. |
| Delivery and gates | <branch/PR/closeout plus tests/autoreview/CI/integration proof> | Landing path and proof before closeout. |
| Stop condition | <scope/surface/auth/delivery/gate change, blocker, or completion> | When the orchestrator must return to the owner. |

Then include one row per workstream. Option fields keep their canonical names
and values; refs and proof stay in separate data columns:

| wave | workstream | actual_workstream_surface | scope | parallelization | dependency_ids | blocked_issue_ids | dependency_reason | dependency_proof | worker_authorization | expected_output |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <wave> | <name/ref> | <root-thread|cli-subagent|codex-app-thread> | <repo/package/paths> | <independent|depends-on|blocks|root-integrated> | <refs|none> | <refs|none> | <reason|none> | <evidence|pending|none> | <modes and limits> | <patch|report|commit|pr> |

A workstream defines the implementation slice. It creates a worker only when
`actual_workstream_surface` is `cli-subagent` or `codex-app-thread`;
`root-thread` means the root orchestrator owns that slice directly.

For root-only work, do not write a prose alias such as `none; root-owned` in
the owner-facing report. Use `actual_workstream_surface=root-thread`. If no
automation will be created or updated, do not mention automation in the report
unless it is relevant to a stop condition.

## Recurring PRD Automation

For a recurring PRD automation, require
the PRD-scoped `automation_authority=explicit-owner-authorization` row and
carry that scoped row plus the canonical session option snapshot into every
run. Ask no PRD-specific worker-surface
question unless a run lacks an applicable canonical field or would exceed its
recorded value.

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

The root passes the effective runtime delivery plus its source. Use
`local-only` for ad-hoc or legacy implementation without a PRD delivery
contract. Otherwise pass the PRD-backed mode plus whether it is inherited from
`source_prd_ref` or an issue-level override. `prd-backed-delivery.md` owns the full
delivery/publication/issue-mutation authority model; workers only enforce the
assignment they receive.

For `pull-request`, the root also passes `pr_closeout`. Default it to
`merge-ready`; use `draft-only` only when the option-resolution record contains
owner or source-contract evidence. No-mutation, PR-shape, and merge-authority
evidence cannot alter `pr_closeout`. A draft-only worker receives no
`review-ready` authorization. If the canonical value later changes to
`merge-ready`, the root may assign the ready-for-review sequence from the
existing draft PR.

The root also passes `pr_shape`. PRD-backed work inherits `single-pr` or
`per-repo-pr`; ad hoc `local-only` and `direct-commit` work use `none`. Branch
names, repository refs, and expected PR URLs remain separate data.

For generated implementation issues, the root also passes the validated
`## Orchestrator Handoff` projection. Workers may use the handoff for scope,
start rule, dependencies, validation, and closeout, but they must not treat it
as worker authorization, publication authority, issue mutation authority, or
permission to change branch/PR strategy.

| Mode | Worker handling |
| --- | --- |
| `local-only` | Implement and validate within the assigned paths. Do not commit, push, create or transition a PR, request Codex review, mutate issues, merge, release, or deploy. Missing PRD delivery metadata is expected, not a blocker. |
| `pull-request` | Root owns the branch/PR shape, Codex review disposition, and merge-ready decision. In single-repo or monorepo work, workers provide patches, helper-worktree diffs, handoff, or reviewed commits unless their canonical `worker_authorization` set includes publication modes. In multi-repo work, repo-scoped workers may prepare their repo branch/PR only when `commit`, `push`, `pr`, and/or `review-ready` plus the exact `review_ready_actions` are present. |
| `direct-commit` | Require the scoped delivery option row and ledger evidence to name the exact owner instruction and workstream, and require `branch_name` to equal the authorized target branch. |

If assigned delivery mode conflicts with repo reality, stop and report
`needs-owner`; do not choose a new branch or PR strategy. Workers may commit,
push, open a draft PR, mark a PR ready for review, or request Codex review only
when the prompt names the exact repository, branch/refspec, PR shape, closeout
target, corresponding authorization modes, and, for `review-ready`, exact
sub-actions. `pr` is not a shortcut for commit, push, or `review-ready`.

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

- `handoff`: use `codex_app.handoff_thread` and read completion with
  `codex_app.get_handoff_status`, or use the equivalent inspected worker
  surface when the worker's checkout should become the integration checkout.
- `worker-commit`: accept a worker-prepared commit or branch only when the
  authorization modes include `commit` and the root has reviewed the diff.
- `patch-apply`: apply a worker diff or patch in the explicitly named
  integration checkout, then inspect conflicts and rerun root gates. Prefer a
  worker worktree or dedicated integration worktree when one exists; use the
  caller checkout only when
  `caller_checkout_policy=caller-checkout-approved`.
- `manual-root`: reimplement or copy the relevant change in the explicitly
  named integration checkout when the worker output is partial, stale,
  conflicting, or easier to reproduce safely than to apply directly. Preserve
  the caller checkout unless
  `caller_checkout_policy=caller-checkout-approved`.

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

In a Codex App session, a newly created helper worktree must be owned by a
visible App worker thread. Create the thread through the App worktree target,
record its id/title/path, and use that managed checkout for the assigned work.
If the App cannot create the required worktree, stop before `git worktree add`,
report the exact limitation, and request explicit fallback authority. This rule
does not apply in CLI-only sessions and does not require wrapping an existing
owner-supplied checkout in a new thread.

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
request, source item, linked `source_prd_ref`, publication authority, issue mutation
authority, selected worker surface, dependency state, dirty-worktree state, and
gates. If a worker may edit, commit, push, open a draft PR, mark it ready for
review, and request Codex review, record `implement, commit, push, pr,
review-ready` plus the `mark-ready` and `request-codex-review` sub-actions. If
it may only open a PR from an already-pushed branch, record `pr` only.

- `inspect`: read-only investigation, issue/PR/CI inspection, repo scan, or
  design review. It never permits file edits, staging, publication, or external
  mutation; allowed paths and surfaces only bound where inspection may occur.
- `implement`: local code/docs changes plus focused validation, but no staging,
  commit, push, PR, merge, release, or external mutation. Allowed paths and
  surfaces bound the edits but cannot grant another capability mode.
- `commit`: may stage and create local commits for the assigned paths in the
  exact repository and branch/worktree named by the root. It assumes edits are
  separately allowed by `implement` or by explicit assignment text. It does not
  permit push, PR creation/update, merge, release, or issue mutation. Commit
  messages must not use GitHub closing keywords such as `closes`, `fixes`, or
  `resolves` unless `closeout_mode=direct-commit-closes-issue` and the scoped
  authorization evidence names that issue; use non-closing references such as
  `Refs #123` when a reference is useful.
- `push`: may push only the exact assigned branch or explicit refspec after the
  required validation and publication-safety checks. It does not permit local
  commits unless `commit` is also listed, and it does not permit PR
  creation/update, PR-body closeout keywords, merge, release, or direct issue
  mutation.
- `pr`: may create or update the assigned draft PR for the exact branch and
  closeout target after required validation and publication-safety checks. This
  is the first mode that may place GitHub closing keywords such as `Closes #123`
  in a PR body when the generated issue's closeout path calls for PR-body
  closure. A worker must not add or remove the parent PRD closing keyword; that
  post-review mutation and its reviewed-head revalidation are root-owned. This
  mode does not permit local commits or push unless those modes are also listed,
  and it does not authorize ready-for-review transition, Codex review request,
  merge, release, or direct issue mutation.
- `review-ready`: umbrella capability for exact root-listed PR-review
  sub-actions: `mark-ready`, `request-codex-review`, `poll-codex-review`, and
  `post-root-supplied-disposition`. A worker may perform only the listed
  sub-actions for the assigned PR. Before `request-codex-review`, run the
  GitStack status check for the assigned head. If the result shows the assigned
  head is stale, the root must refresh the assignment to the PR's current SHA
  and the worker must rerun `reviews check` for that refreshed SHA. Request only
  when that same-SHA check returns `not_requested` or `stale` with
  `head_is_current=true`. Immediately before requesting, re-read the PR head and
  stop if it changed or the ledger already records a request for that SHA. Root
  retry or fresh-review wording cannot bypass the refreshed check or authorize
  a second request for an unchanged head. Reuse `clean`/`findings` and poll
  `acknowledged`/`pending`. Posting a disposition requires
  root-supplied text and supporting evidence; evaluating Codex feedback,
  deciding whether fixes are needed, and accepting residual risk remain
  root-owned unless the root also explicitly lists the needed `implement`,
  `commit`, or `push` modes. It does not permit code edits, commits, pushes,
  asking Codex to fix issues with a cloud task, merge, release, or direct issue
  mutation unless those modes or instructions are also explicitly listed.
- `ci-rerun-fix`: rerun checks, inspect CI logs, and diagnose or verify a known
  PR or branch when the root assignment names the failing checks. Any edits,
  commits, or pushes for CI repair also require the corresponding `implement`,
  `commit`, and `push` modes plus publication-safety gates.
- `release`: tag, release, publish, or package promotion only with explicit
  owner approval and the release gate satisfied.

Merge, direct issue closeout, labels, and root-authored discussion mutations
are not worker modes. They remain root-owned actions with their own recorded
authority. A legacy worker assignment containing `merge-close` is invalid;
stop as `needs-owner` instead of executing or silently translating it.

## Prompt Template

```text
You are a Codex worker for the <portfolio> portfolio.

Scope:
- repository: <repo path or owner/repo>
- workstream: <short name>
- worker_surface: <auto|root-thread|codex-app-thread|cli-subagent>
- actual_workstream_surface: <root-thread|codex-app-thread|cli-subagent>
- worker_id: <id or pending>
- worker_title: <title or pending>
- worker_evidence: authorization_state=<authorized-by-invocation|owner-consented|not-authorized>;
  status=<used|unavailable|attempt-failed|root-owned-fallback>;
  evidence=<tool/session/failure>; parallelism=<parallel|sequential|root-owned|simulated>
- wave: <number>
- objective: <one concrete outcome>
- source_id: <stable source id>
- source_ref: <URL, path:line, heading, run id, or ledger item>
- acceptance_criteria: <source-owned completion criteria>
- closeout_target: <local acceptance criteria plus validation, issue close, PR reply, file checkbox/patch, CI rerun, or ledger status>
- worker_authorization: <one or more of inspect|implement|commit|push|pr|review-ready|ci-rerun-fix|release>
- review_ready_actions: <mark-ready|request-codex-review|poll-codex-review|post-root-supplied-disposition or not-applicable>
- capability_snapshot: filesystem=<profile/evidence>; network=<available|restricted|unknown>; gh_auth=<available|unavailable|not-required>; codex_cli=<available|unavailable|not-required>; autoreview=<available|unavailable|reroute-to-root>; checked_at=<time/evidence>
- allowed_paths_or_surfaces: <paths, branches, PRs, issues, or commands>
- delivery_mode: <local-only|pull-request|direct-commit>
- delivery_source: <runtime-default|feature-level-inherited|issue-level-override|owner-instruction>
- delivery_source_evidence: <source ref or authorization evidence>
- scope_transfer_ref: <issue:<NN>|not-applicable>
- issue_mutation_transfer_ref: <issue:<NN>|not-applicable>
- temporary_source_execution: <forbidden|owner-approved>
- completion_proof_policy: <live-required|synthetic-accepted>
- orchestrator_handoff: <canonical handoff fields, or not-applicable for ad hoc work>
- domain_closeout: <not-applicable|implementation-closeout>
- domain_closeout_data: <exact decisions, target surfaces, evidence, and `$project-memory domain-memory` operation or none>
- publication_authority: <none|explicit-owner-authorization|prd-backed-pull-request|blocked>
- publication_authority_evidence: <option-resolution or source-contract evidence>
- pr_closeout: <merge-ready|draft-only|not-applicable>
- pr_closeout_evidence: <option-resolution evidence>
- pr_shape: <single-pr|per-repo-pr|none>
- closeout_mode: <feature-pr-closes-issue|repo-pr-closes-issue|direct-commit-closes-issue|local-done-move-after-proof|not-applicable>
- issue_mutation_authority: <none|pr-body-closeout-only|explicit-direct-mutation>
- parent_prd_applicability: <required|deferred-vehicle|not-applicable>
- parent_prd_applicability_reason: <whole-prd-final-pr|non-default-base|partial-pr|ad-hoc|local-tracker|no-parent|draft-only|other-reason>
- parent_prd_closeout: <not-applicable|pending-review|pending-closeout|deferred-to-default-branch|armed|closed|blocked>
- parent_prd_ref: <issue ref or none>
- parent_closeout_vehicle: <PR ref, pending, or none>
- parent_closeout_head: <reviewed SHA or none>
- parent_closeout_base: <branch or none>
- default_branch: <branch or none>
- pr_body_evidence: <URL/fingerprint or none>
- parent_closeout_watch: <not-applicable|root-monitoring|owner-handoff|automation-handoff|complete>
- parent_closeout_watch_evidence: <watch packet, automation id, or none>
- codex_review: <not-applicable|not-requested|requested|received|passed|blocked>
- codex_review_evidence: <request head/object; GitStack checker status; result head/kind/object; verified provider; terminal status; disposition>
- parallelization: <independent|depends-on|blocks|root-integrated>
- dependency_ids: <source/workstream ids or none>
- blocked_issue_ids: <source/workstream ids or none>
- dependency_reason: <reason or none>
- dependency_proof: <completed proof, pending, or none>
- branch_expectation: <feature-branch|repo-feature-branch|direct-commit-target|none>
- branch_name: <exact branch or not-applicable>
- integration_mode: <single-repo-pr|repo-pr|direct-commit|not-applicable>
- integration_method: <handoff|worker-commit|patch-apply|manual-root|pending>
- caller_checkout_policy: <preserve-current-branch|caller-checkout-approved|not-applicable>
- publication_checkout: <worker-worktree path|integration-worktree path|caller-checkout path|not-applicable>
- report_channel: this worker thread only
- helper_checkout: <path or unknown>
- next_ledger_check: <time/action or none>
- forbidden_actions: no subdelegation, no ledger edits, no unrelated cleanup,
  no worker/thread/chat management, no commit/push/PR/Codex-review
  request/release unless this mode explicitly permits it; no merge or direct
  source closeout under any worker mode; no duplicate Codex-review request when
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
- Delivery: runtime delivery, branch or PR used, closeout path, and PR links or
  `none`; include ready-for-review state, Codex review state, publication
  checkout, and caller checkout disposition
- Worker evidence: canonical `worker_surface`, `actual_workstream_surface`, and
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
