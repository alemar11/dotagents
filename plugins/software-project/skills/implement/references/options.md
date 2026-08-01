# Implement Startup Authorization

The behavior-affecting startup fields are:

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `missing_project_action` | `create-projects`, `stop` | When one or more required repositories have no separate repo-specific saved Git project, either authorize creation of exactly the listed projects or stop before state. Omit this field when none are missing. |
| `visible_app_task_permission` | `granted`, `denied` | Permit the disclosed visible Codex worker tasks and ChatGPT-created worktrees for this run. |
| `scope_repair_task_permission` | `granted`, `denied` | Permit a separate visible Plan Feature task only when an active worker later needs a monotonic `allowed_paths` repair. |

After validating the current Feature Spec frontier and completing the read-only
worker-project preflight, disclose the selected Specs, repositories, branches,
expected worker count, ChatGPT-created worktrees, GitHub publication, tracker
mutation, validation, and the native `codex review` command for every worker,
plus the exact
terminal boundary: `pr-ready-for-merge`. For every worker, also disclose the fixed
`gpt-5.6-sol` model and its resolved thinking level: `medium` for routine work,
`high` for complex work, or `xhigh` for risky or cross-system work. An explicit
`$software-project:implement` request to start, implement, or resume the selected Specs
explicitly requests those exact task profiles and resolves
`visible_app_task_permission=granted` without an additional worker-task
creation question. An explicit denial overrides that grant and stops before
mutation.

When no project is missing, use this exact question so permission cannot be
mistaken for an immediate task launch:

> May I create one separate visible Plan Feature task later, only if an
> implementation worker proves that a required path is missing from
> `allowed_paths`? Granting this permission does not create that task now. No
> planner task will be created unless a scope miss occurs.

Resolve that answer directly to `scope_repair_task_permission`. After an
affirmative answer, state exactly: `Planner-task permission recorded; no
planner task has been created.` After a negative answer, state exactly:
`Planner-task permission denied; a future scope miss will block without
creating a planner task.`

When projects are missing, use this standard question in the same startup
authorization interaction:

> To create the visible tasks with managed worktrees, every affected repository
> must have a separate repo-specific local Git project in the ChatGPT App.
> Folders attached to the controller's multi-folder project provide context but
> do not satisfy this worker-project requirement. These projects are missing:
>
> - `<repository>` — `<absolute-path>`
>
> The explicit execution request already authorizes the disclosed worker tasks.
> This answer also controls whether I may create one separate visible Plan
> Feature task later, only if an implementation worker proves that a required
> path is missing from `allowed_paths`. Granting this permission does not create
> that task now. No planner task will be created unless a scope miss occurs.
> Do you also authorize me to create exactly these persistent projects in the
> ChatGPT App through Computer Use? Project creation is distinct from task creation.
> Otherwise I will stop without creating run state, claims, tasks, or worktrees.

Resolve an affirmative answer to
`missing_project_action=create-projects` and
`scope_repair_task_permission=granted`. Resolve a negative answer to
`missing_project_action=stop` and `scope_repair_task_permission=denied`. Do not
change the already resolved
worker-task permission based on the project answer. A user may explicitly grant
worker tasks while denying planner repair tasks; normalize that answer to
`visible_app_task_permission=granted` and
`scope_repair_task_permission=denied`. Emit and persist only these canonical
values in ephemeral controller state; never persist them as repository
configuration.

`create-projects` authorizes only the exact paths listed in the question.
Before confirming each file-picker selection, read back the selected absolute
path and require exact equality with the expected Git root. After creation,
read `list_projects` again and require the saved path and independently resolved
Git common directory to match the expected repository. Ambiguous selection,
inaccessible Computer Use, a locked host, a parent path, or a mismatched
readback stops immediately. Never create a broader substitute such as a parent
root or `/private/tmp`, never silently create another project, and
never treat task permission as project-creation permission.

`granted` covers the full worker lifecycle: implementation, compatible
rewrites, repairs, tests, command approvals through the ChatGPT App,
publication, review fixes, tracker checkboxes, recovery, and final evidence. It
does not authorize merge, deployment, release, post-merge closure, or work
outside the durable contract.

`scope_repair_task_permission=granted` authorizes only the bounded, separate
planner task described in `scope-repair-orchestration.md`; it grants no planning
authority to root or workers. `denied` leaves a later scope request
declaratively blocked and does not trigger another user question.

After the startup interaction grants the required fields, do not ask another
user question. Validation authority,
recovery choices, operational clarifications, blockers, retries within the
durable budget, and continuation are worker decisions. A stable contract change
causes a declarative blocked result, not a question.
`visible_app_task_permission=denied` stops before run state, task, worktree,
claim, project, or provider mutation.
