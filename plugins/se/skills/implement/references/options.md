# Implement Startup Authorization

The behavior-affecting startup fields are:

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `missing_project_action` | `create-projects`, `stop` | When one or more required repositories have no separate repo-specific saved Git project, either authorize creation of exactly the listed projects or stop before state. Omit this field when none are missing. |
| `visible_app_task_permission` | `granted`, `denied` | Permit every disclosed Codex App task required by this run, including the Implement root, workers, necessary contract-repair Feature tasks, and ChatGPT-created worktrees. |
| `contract_repair_task_permission` | `granted`, `denied` | Internal derived control for all necessary contract-repair Feature tasks; it is resolved together with `visible_app_task_permission` and is not a separate user decision. |

Before creating the root, disclose the root controller task, its exact local
project, and its fixed `gpt-5.6-sol` / `thinking: medium` profile. After
validating the current Feature Spec frontier and completing the read-only
worker-project preflight, disclose the selected Specs, repositories, branches,
expected worker count, ChatGPT-created worktrees, GitHub publication, tracker
mutation, validation, and native review for every worker,
plus the exact
terminal boundary: `pr-ready-for-merge`. For every worker, also disclose the fixed
`gpt-5.6-sol` model and its resolved thinking level: `medium` for routine work,
`high` for complex work, or `xhigh` for risky or cross-system work. An explicit
`$se:implement` request to start, implement, or resume the selected Specs
explicitly requests the root and those exact worker task profiles and resolves
`visible_app_task_permission=granted` and
`contract_repair_task_permission=granted` without an additional root-, worker-,
planner-, or task-creation question. An explicit denial overrides both grants
and stops before mutation. When no project is missing, there is no startup
authorization question.

When projects are missing, use this standard question in the same startup
authorization interaction:

> To create the visible tasks with managed worktrees, every affected repository
> must have a separate repo-specific local Git project in the ChatGPT App.
> Folders attached to the controller's multi-folder project provide context but
> do not satisfy this worker-project requirement. These projects are missing:
>
> - `<repository>` — `<absolute-path>`
>
> The explicit execution request already authorizes every Codex App task required
> by the disclosed run, including the root, workers, and any necessary contract-repair
> Feature task.
> Do you also authorize me to create exactly these persistent projects in the
> ChatGPT App through Computer Use? Project creation is distinct from task creation.
> Otherwise I will stop without creating run state, claims, tasks, or worktrees.

Resolve an affirmative answer to
`missing_project_action=create-projects` and a negative answer to
`missing_project_action=stop`. Do not change the already resolved task
permissions based on the project answer. Emit and persist only these canonical
values in ephemeral controller state; never persist them as repository
configuration.

`create-projects` authorizes only the exact paths listed in the question.
Before confirming each file-picker selection, read back the selected absolute
path and require exact equality with the expected Git root. After creation,
observe the authoritative saved-project inventory again and require the saved
path and independently resolved Git common directory to match the expected
repository. Ambiguous selection,
inaccessible Computer Use, a locked host, a parent path, or a mismatched
readback stops immediately. Never create a broader substitute such as a parent
root or `/private/tmp`, never silently create another project, and
never treat task permission as project-creation permission.

`granted` covers every disclosed task lifecycle: root monitoring,
implementation, compatible rewrites, contract-repair planning, repairs,
tests, command approvals through the ChatGPT App, publication, review fixes,
tracker checkboxes, recovery, and final evidence. It does not authorize merge,
deployment, release, post-merge closure, or work outside the durable contract.

`contract_repair_task_permission=granted` is derived automatically by an explicit
execution invocation and authorizes every necessary separate planner task
described in `contract-repair-orchestration.md`; it grants no planning authority
to root or workers. A `denied` value can only come from an explicit task-
creation denial, leaves a later contract-repair request declaratively blocked, and does
not trigger another user question.

After the preflight and any optional missing-project interaction, do not ask
another user question. Validation authority,
recovery choices, operational clarifications, blockers, retries within the
durable budget, and continuation are worker decisions. A stable contract change
causes a declarative blocked result, not a question.
`visible_app_task_permission=denied` stops before root creation, run state,
worker task, worktree, claim, project, or provider mutation.
