# Root Bootstrap

Root is a lightweight control plane. Before mutation:

1. Read and validate the complete current Feature Spec frontier through
   `spec-backed-delivery.md`.
2. Resolve each repository's canonical identity. Use
   `github:owner/repository` for GitHub repositories. For local-only repositories,
   resolve `git rev-parse --path-format=absolute --git-common-dir`, stat that
   real directory, and use the exact identity printed by the helper's local
   identity rule. Linked worktrees therefore share one target.
3. Map every selected repository path to a current App project. Never treat an
   App project or workspace path as repository identity. One App project may
   serve several Specs in one repository, but must not map to distinct
   canonical repositories.
4. Check branches and dependency merge proof, calculate allowed-path overlap,
   derive the worker order, and disclose the startup scope.
5. Resolve the one `visible_app_task_permission` from `options.md`.
6. Write a private manifest containing only controller identity:

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
      "source_ref": "https://github.com/owner/repository/issues/42",
      "repository_identity": "github:owner/repository",
      "project_id": "current-app-project-id",
      "title": "🛠️ Exact Feature Spec title",
      "target_branch_name": "feature/example"
    }
  ]
}
```

The manifest deliberately omits raw Spec and issue bodies, checklists, allowed
path text, validation attempts, worker technical state, provider state, and text
hashes. Those remain authoritative at their sources.

One root task may own only one unfinished run and lifecycle Goal. A second run
from that task starts only after the first is terminal.

Call `scripts/run-state --json run start --manifest <absolute-file>`. The single
transaction either acquires every canonical repository or none. On success,
create and read back the one root Goal, set the root title/progress, and schedule
up to three disjoint assignments. On conflict, follow the bounded wait path and
create no Goal, worker, worktree, branch, or provider mutation.
