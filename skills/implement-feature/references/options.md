# Implement Feature Startup Authorization

The behavior-affecting startup fields are:

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `missing_project_action` | `create-projects`, `stop` | When one or more required repositories are not saved Git projects, either authorize creation of exactly the listed projects or stop before state. Omit this field when none are missing. |
| `visible_app_task_permission` | `granted`, `denied` | Permit the disclosed visible Codex worker tasks and ChatGPT-created worktrees for this run. |

After validating the current Feature Spec frontier and completing the read-only
saved-project preflight, disclose the selected Specs, repositories, branches,
expected worker count, ChatGPT-created worktrees, GitHub publication when
applicable, tracker mutation, validation, AutoReview, and the AutoReview-owned
native Codex review only when the derived profile is `high-risk`, plus the exact
terminal boundary: `pr-ready-for-merge-but-not-merged` or
`local-branch-ready`.

When no project is missing, ask once whether to start those visible tasks.
Resolve the answer directly to `visible_app_task_permission`.

When projects are missing, use this standard question in the same startup
authorization interaction:

> To create the visible tasks with managed worktrees, every affected repository
> must be saved as a separate local Git project in the ChatGPT App. These
> projects are missing:
>
> - `<repository>` — `<absolute-path>`
>
> Do you authorize me to create exactly these persistent projects in the
> ChatGPT App through Computer Use and then start the disclosed
> implementation? Project creation is distinct from task creation. Otherwise I
> will stop without creating run state, claims, tasks, or worktrees.

Resolve an affirmative answer to
`missing_project_action=create-projects` and
`visible_app_task_permission=granted`. Resolve a negative answer to
`missing_project_action=stop` and
`visible_app_task_permission=denied`. Emit and persist only these canonical
values in ephemeral controller state; never persist either as repository
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

After the startup interaction grants the required fields, do not ask another
user question. Validation authority,
recovery choices, operational clarifications, blockers, retries within the
durable budget, and continuation are worker decisions. A stable contract change
causes a declarative blocked result, not a question. `denied` stops before run
state, task, worktree, claim, project, or provider mutation.
