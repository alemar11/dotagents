# Root Bootstrap

Load this reference before persistent state, visible worker tasks, a new Goal,
or repository/provider mutation.

## Load Path

Always load:

- `spec-backed-delivery.md` for source validation and frontier selection;
- `options.md` for scope disclosure and authorization;
- `app-orchestration.md` for current App project, task, and Goal tools.

Load `multi-repo-workspace.md` when the requested bundle spans repositories.
Workers load `baseline-validation.md` inside their managed checkouts. The exact
ordinary start manifest and command are below, so do not load `run-state.md`
during a healthy fresh start; load it only for CLI errors, recovery, or
maintenance.

## Fast-Start Order

1. Resolve the supplied Feature Spec and traverse its complete connected bundle.
2. Validate the bundle unchanged. Select only executable Specs whose authored
   cross-Spec dependencies are already merged and integration-proven. Report
   blocked downstream refs as the next frontier; do not claim them.
3. Require exactly one affected repository per selected executable Spec and one
   unique `(repository_claim, target_branch_name)` owner. Missing or conflicting
   execution data is `planning-required`.
4. Confirm the root exposes `list_projects`, task create/read/wait/message/title
   tools, and Goal get/create/update tools. Call `list_projects` once and map
   every selected repository path to exactly one project ID. Read the current
   root Goal and reject an unrelated or blocked unfinished Goal.
5. Resolve the current GitStack runtime from the loaded App catalog. In parallel
   per repository, prove access, target/default branch existence, current head,
   and conflicting branch or PR identity. Defer CI, review access, rules,
   approvals, mergeability, and queue eligibility.
6. Render the exact sources and fingerprints, repositories/projects, branches,
   paths, validation commands, task titles, Goal objective, and expected PRs.
   Resolve authority through `options.md`.
7. Re-read source revisions and repository heads only when authorization caused
   a user wait, an observation became stale, or drift is otherwise evidenced.
8. Write the exact schema-1 manifest below to a private temporary JSON file and
   call `scripts/run-state --json run start`. Continue only when
   `start_authorized=true`.
9. Create or adopt and read back the root Goal through
   `app-orchestration.md`, then bind it in state.
10. Dispatch up to three canonical non-overlapping assignments immediately.

Independent repository reads, task creation, title observation, and worker
baselines may fan out to the three-task limit. Fan in before each wave receives
implementation authority.

## Start Manifest

Use exactly these fields:

```json
{
  "schema_version": 1,
  "run_id": "019f-example",
  "root_task_id": "019f-root",
  "goal_objective": "Implement the dependency-ready Feature Spec frontier",
  "sources": [
    {
      "kind": "github-issue",
      "ref": "https://github.com/owner/repository/issues/42",
      "sha256": "<sha256-of-accepted-source-body>"
    }
  ],
  "repositories": [
    {
      "repository_claim": "repository:github:owner/repository",
      "repository_path": "/absolute/repository",
      "project_id": "<App-project-id>",
      "default_branch_name": "main",
      "git_common_dir": "/absolute/repository/.git"
    }
  ],
  "assignments": [
    {
      "assignment_id": "spec-01",
      "source_ref": "https://github.com/owner/repository/issues/42",
      "title": "🛠️ Exact authored Feature Spec title",
      "repository_claim": "repository:github:owner/repository",
      "target_branch_name": "feature/example",
      "allowed_paths": ["src/example/**"],
      "acceptance_criteria": ["Observed behavior matches the Spec"],
      "validation_commands": ["literal accepted command"],
      "integration_gates": [],
      "domain_closeout": null
    }
  ]
}
```

`sources` includes the accepted selected Specs and any coordination source
required to understand them. A GitHub issue ref is canonical and lowercase.
For a local source use `kind=local-file`, an absolute regular-file `ref`, and
its exact content SHA-256. The helper rechecks local bytes and claims both path
and filesystem identity.

`repositories` comes from the one authoritative `list_projects` mapping plus
the provider-read default branch. Resolve
`git_common_dir` with `git rev-parse --path-format=absolute --git-common-dir`
inside the mapped repository; the helper stores its filesystem identity. At
task bind, resolve the same value independently inside the managed checkout.
Repository claims, App project IDs, repository paths, and Git common-directory
filesystem identities are one-to-one; any duplicate mapping is invalid.
`assignments` contains exactly one row per selected executable Spec. The helper
rejects two assignments for one source ref, undeclared sources or repositories,
duplicate repository/branch pairs, and noncanonical fields.

The manifest is the recovery packet. Keep source bodies, paths, acceptance,
validation, and optional closeout data there instead of deriving them from old
state after compaction.

Any failure before `run start` proves zero run state, worker task, new Goal,
repository write, or provider mutation.
