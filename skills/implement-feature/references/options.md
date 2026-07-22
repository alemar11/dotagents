# Implement Feature Startup Permission

The sole behavior-affecting option is:

| Field | Values | Meaning |
| --- | --- | --- |
| `visible_app_task_permission` | `granted`, `denied` | Permit the disclosed visible Codex worker tasks and ChatGPT-created worktrees for this run. |

After validating the current Feature Spec frontier, disclose the selected Specs,
repositories, branches, expected worker count, ChatGPT-created worktrees, GitHub
publication when applicable, tracker mutation, validation, AutoReview, Codex
review, and the exact terminal boundary: `pr-ready-for-merge-but-not-merged` or
`local-branch-ready`. Ask once whether to start
those visible tasks. Resolve the answer directly to the canonical value and do
not persist it as repository configuration.

`granted` covers the full worker lifecycle: implementation, compatible rewrites,
repairs, tests, command approvals through the ChatGPT desktop app, publication, review fixes,
tracker checkboxes, recovery, and final evidence. It does not authorize merge,
deployment, release, post-merge closure, or work outside the durable contract.

After `granted`, do not ask another user question. Validation authority,
recovery choices, operational clarifications, blockers, retries within the
durable budget, and continuation are worker decisions. A stable contract change
causes a declarative blocked result, not a question. `denied` stops before run
state, Goal, task, worktree, claim, or provider mutation.
