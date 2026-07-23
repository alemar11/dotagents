# Root Bootstrap

Root is a lightweight control plane. Before mutation:

1. Read and validate the complete current Feature Spec frontier through
   `feature-spec-contract.md`.
2. Resolve each repository's canonical identity. Use
   `github:owner/repository` for GitHub repositories. For local-only repositories,
   resolve `git rev-parse --path-format=absolute --git-common-dir`, stat that
   real directory, and use the exact identity printed by the helper's local
   identity rule. Linked worktrees therefore share one target.
3. Run the saved-project preflight with `list_projects`. Every selected
   repository must map to a saved project whose path is exactly that repository
   root and whose independently resolved Git common directory matches the
   canonical repository identity. A non-Git coordination workspace is not a
   substitute, because worktree creation targets the selected project's Git
   root. Never infer a child repository from a workspace project and never
   treat a project or workspace path as repository identity.
4. Read `tracker_backend` and exact `delivery_type` from each stable contract.
   Check branches and required dependency proof, calculate allowed-path overlap,
   derive worker order, and disclose startup scope. Repository identity never
   substitutes for either transport fact.
5. For multi-repository combined proof, verify before permission or state only
   the static prerequisites that can exist at that point: every repository maps
   to a saved ChatGPT desktop project capable of creating its ordinary worker
   and worktree; every combined boundary names an ordinary proof owner; and its
   Integration Execution Contract assigns each component either to that proof
   owner or to the peer that owns the component. Do not require access to
   worktrees that do not exist yet.
6. Resolve the startup fields from `options.md`. If every mapping in step 3
   already exists, resolve only `visible_app_task_permission`. If mappings are
   missing, list the exact repository roots in the standard question and
   resolve both `missing_project_action` and
   `visible_app_task_permission` in the one startup authorization interaction.
   With `create-projects`, use Computer Use only for those exact roots, verify
   each selected path before confirmation, then rerun the complete read-only
   saved-project preflight. With `stop`, denied task permission, unavailable
   Computer Use, a locked host, ambiguous selection, or any mismatched
   readback, stop before run state, claim, task, or worktree creation.
7. Write a private manifest containing only controller identity:

```json
{
  "schema_version": 2,
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

The saved-project preflight and any explicitly authorized project setup finish
before writing the manifest or calling `scripts/run-state`. Project creation is
not worker recovery and task permission alone never authorizes it. Do not create
a broader parent project as a diagnostic step. A failed or partial project
setup is reported exactly and never converted into an active run.

One root task may own only one unfinished run. A second run from that task
starts only after the first is terminal.

Call `scripts/run-state --json run start --manifest <absolute-file>`. One
transaction claims every free canonical Feature Spec and head branch and leaves
only conflicting assignments in `waiting-for-spec`. With
`tracker_backend=github`, a GitHub URL and `owner/repository#number` normalize
to the same claim identity. With `tracker_backend=local`, the globally
unambiguous repository-scoped Spec path remains local even when the repository
identity is `github:owner/repository`.

When at least one assignment acquires its claim, set and verify the immutable
root title once and schedule up to three disjoint claimed assignments. When
every assignment waits, create no worker, worktree, branch, or provider
mutation. Never use a default PR base such as `main` as a head-branch collision:
only the implementation head branch is exclusive.

The root creates each worker as a visible Codex task with
`environment=worktree`. The ChatGPT desktop app creates the worktree and assigns
it to that task. Root verifies the task, checkout directory, and Git common
directory; it never runs `git worktree add`. SQLite keeps only checkout identity
needed for coordination, not the worker's technical contents.

After the required ordinary workers and worktrees exist, forward-test the
declared distributed execution topology before combined validation. Every
worker must remain isolated to its own worktree. Each component owner proves its
exact HEAD before startup and after shutdown and sends endpoint, health, and
cleanup evidence directly to the worker that owns combined proof. If those
ordinary tasks cannot communicate or expose the required components, record
`blocked-app-capability` for every affected nonterminal assignment and stop that
bundle. Never replace the failed topology with cross-worktree access, root
execution, a hidden task, raw worktrees, copied code, or future manual testing.
