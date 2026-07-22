# Root Bootstrap

Root is a lightweight control plane. Before mutation:

1. Read and validate the complete current Feature Spec frontier through
   `feature-spec-contract.md`.
2. Resolve each repository's canonical identity. Use
   `github:owner/repository` for GitHub repositories. For local-only repositories,
   resolve `git rev-parse --path-format=absolute --git-common-dir`, stat that
   real directory, and use the exact identity printed by the helper's local
   identity rule. Linked worktrees therefore share one target.
3. Map every selected repository path to a saved ChatGPT desktop project. Never
   treat a project or workspace path as repository identity. A multi-repository
   project may serve several canonical repositories only when each worker's
   checkout and Git common directory are independently verified.
4. Read `tracker_backend` and exact `delivery_type` from each stable contract.
   Check branches and required dependency proof, calculate allowed-path overlap,
   derive worker order, and disclose startup scope. Repository identity never
   substitutes for either transport fact.
5. For a dedicated multi-repository integration Spec, prove before permission
   or state that its ChatGPT desktop project can expose every sibling
   ChatGPT-created worktree
   to that visible task. Missing capability evidence blocks before startup.
6. Resolve the one `visible_app_task_permission` from `options.md`.
7. Write a private manifest containing only controller identity:

```json
{
  "schema_version": 1,
  "run_id": "run-019f",
  "root_task_id": "019f-root-task",
  "repositories": [
    {
      "repository_identity": "github:owner/repository",
      "git_common_dir": "/absolute/repository/.git"
    }
  ],
  "assignments": [
    {
      "assignment_id": "spec-42",
      "source_spec_ref": "owner/repository#42",
      "repository_identity": "github:owner/repository",
      "tracker_backend": "github",
      "delivery_type": "github-pr",
      "project_id": "current-app-project-id",
      "title": "🛠️ Exact Feature Spec title",
      "target_branch_name": "feature/example",
      "prerequisite_assignment_ids": []
    }
  ]
}
```

The manifest deliberately omits raw Spec and issue bodies, checklists, allowed
path text, validation attempts, worker technical state, provider state, and text
hashes. Those remain authoritative at their sources.

One root task may own only one unfinished run and lifecycle Goal. A second run
from that task starts only after the first is terminal.

Call `scripts/run-state --json run start --manifest <absolute-file>`. One
transaction claims every free canonical Feature Spec and head branch and leaves
only conflicting assignments in `waiting-for-spec`. With
`tracker_backend=github`, a GitHub URL and `owner/repository#number` normalize
to the same claim identity. With `tracker_backend=local`, the globally
unambiguous repository-scoped Spec path remains local even when the repository
identity is `github:owner/repository`.

When at least one assignment acquires its claim, create and read back the one
root Goal, set title/progress, and schedule up to three disjoint claimed
assignments. When every assignment waits, create no Goal, worker, worktree,
branch, or provider mutation. Never use a default PR base such as `main` as a
head-branch collision: only the implementation head branch is exclusive.

The root creates each worker as a visible Codex task with
`environment=worktree`. The ChatGPT desktop app creates the worktree and assigns
it to that task. Root verifies the task, checkout directory, and Git common
directory; it never runs `git worktree add`. SQLite keeps only checkout identity
needed for coordination, not the worker's technical contents.
