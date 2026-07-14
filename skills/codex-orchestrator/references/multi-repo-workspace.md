# Multi-Repo Workspace Flow

Load this reference only when `repository_layout=multi-repository-workspace` or a
registered source/handoff has `workspace_context=multi-repository-workspace`.
Do not load it for ordinary `single-repository` or `monorepo` work.

## Ownership Model

- The parent workspace owns parent/global Feature Specs, generated issue graph
  expansion, orchestration ledgers, worker dispatch, dependency gates,
  cross-repo integration gates, parent issue/spec closeout, and final status.
- Repo-scoped partial Feature Specs are owned by the child repository that
  publishes or stores them.
- Each child repository owns its code, `AGENTS.md`, `CONTEXT.md`, optional
  `TRANSLATION.md`, `project-memory`, validation, branches, commits, PRs, and
  repo-local tracker closeout.
- Parent tracker mode and child tracker mode are independent. Parent local
  tracking does not downgrade a child GitHub tracker, and child GitHub tracking
  does not force parent workspace artifacts into GitHub.

## Worktree Layout

Prefer this layout for child-repo helper worktrees when the parent path is
safe:

```text
<workspace-parent>/.worktrees/<repo-name>/<spec-or-issue-slug>/
```

Before creating it, prove that `<workspace-parent>/.worktrees/` is outside any
tracked Git checkout or ignored by the parent checkout. If that cannot be
proven, use a cache/temp path such as
`~/.cache/dotagents/skills/codex-orchestrator/worktrees/<workspace-slug>/<repo-name>/<spec-or-issue-slug>/`
or stop for an owner-approved safe location. Do not dirty a parent coordination
checkout just to create helper worktrees.

The original child checkout remains the source of truth for remotes, default
branch, and project memory. Worker implementation runs in the helper worktree.

## Dispatch And Parallelism

Execution ordering is derived, not separately configured:

- Default behavior is `work_delegation_policy=orchestrator-decides-for-each-implementation-workstream` plus graph-shaped waves.
- A serial owner request means dispatch one workstream at a time, or use
  `work_delegation_policy=run-all-work-in-current-orchestrator-session` when worker separation is unnecessary.
- A parallel authorized-user request means apply the resolved
  `work_delegation_policy`, `max_concurrent_delegated_workers`,
  `visible_app_task_permission`, and `max_visible_app_tasks` values to
  graph-shaped waves.
- Dependencies, dirty worktrees, overlapping path sets, missing authority, and
  repo/branch/worktree conflicts override requested parallelism.

Safe parallelism requires every active worker to have a unique
`(repo, branch, worktree)` tuple. Same repo plus same branch must serialize,
block, or fail safely through Git's branch ownership checks. Never force a
second worktree checkout of a branch already used by another active worktree.

## Codex App Workers

In a Codex App session, visible worker tasks may remain parent-project-bound
when the App project is the parent workspace. Child repo isolation still comes
from the assigned Git worktree. Record:

- visible worker task id/title;
- parent App workspace root;
- child repo path;
- helper worktree path;
- branch;
- Git top-level;
- proof that the original child checkout stayed clean unless explicitly
  authorized otherwise.

If native child-root worker binding becomes available, treat it as a
worker-launch adapter improvement. It must not change Feature Spec, project
memory, dependency, or closeout contracts.

## Integration And Closeout

- Root verifies every worker report from current filesystem/Git evidence before
  dispatching dependent work.
- Root-owned integration gates run after the relevant child worker wave
  completes.
- Child issues close through their child tracker and delivery rules.
- Parent local issues move to `issues/done/` only after child proof and
  cross-repo integration proof.
- Parent GitHub Feature Specs/issues close only after all child outcomes,
  integration proof, and required PR/review/closeout gates pass.
- Local/no-remote closeout remains conservative: completed local work does not
  move a pull-request-mode issue to done unless exact owner-scoped local
  closeout authority is present.
