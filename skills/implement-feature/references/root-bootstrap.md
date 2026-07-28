# Root Bootstrap

Root is a lightweight control plane. Before mutation:

1. Read and validate the complete current Feature Spec frontier through
   `feature-spec-contract.md`.
2. Read the current Codex task and `list_projects`. Require the controller task
   to be anchored to one local saved Codex project on the current host and
   record its exact `controller_project_id`; also read its current primary
   folder. The controller project may be multi-folder or unrelated to the
   feature. It is UI/control-plane identity and read-only coordination context
   only: its primary-folder Git defaults never expand scope or grant an
   implementation claim, branch, worker, or PR.
3. Resolve each affected repository's canonical identity. Use
   `github:owner/repository` for GitHub repositories. For local-only repositories,
   resolve `git rev-parse --path-format=absolute --git-common-dir`, stat that
   real directory, and use the exact identity printed by the helper's local
   identity rule. Linked worktrees therefore share one target.
4. Run the worker-project preflight with `list_projects`. Every affected
   repository must map bijectively to one separate local saved Git project on
   the current host whose reported primary folder is exactly that repository
   root and whose independently resolved Git common directory matches the
   canonical repository identity. When the controller project is multi-folder,
   exclude its project ID from worker mapping even when an affected repository
   is its primary folder. Its primary and secondary folder memberships are
   context only and never satisfy the worker-project requirement. The same
   repository may appear in multiple multi-folder projects without becoming
   multiple repository identities or execution targets. Reject remote, non-Git,
   duplicate eligible repo-project, parent-path, and ambiguous worker mappings
   before state; a broad or multi-folder project is never a substitute.
5. Read `tracker_backend` and exact `delivery_type` from each stable contract.
   Check branches and required dependency proof, calculate allowed-path overlap,
   derive worker order, and disclose startup scope. Repository identity never
   substitutes for either transport fact.
6. For every multi-repository Feature Spec Set, validate ephemeral snapshots of
   all authoritative member bodies with
   `scripts/run-state --json feature-spec-set validate --input <absolute-file>`.
   Require one successful result before permission or state and retain only its
   exact `manifest_feature_set` result for the run manifest.
7. For multi-repository combined proof, verify before permission or state only
   the static prerequisites that can exist at that point: every repository maps
   to a separate repo-specific saved local Git project in the ChatGPT App
   capable of creating its ordinary worker and worktree; every combined
   boundary names an ordinary proof owner; and its Integration Execution
   Contract assigns each component either to that proof owner or to the peer
   that owns the component. Do not require access to worktrees that do not
   exist yet.
8. Load `task-model-policy.md`, resolve exactly one worker profile per
   implementation-eligible Feature Spec, and verify destination-host support
   for the canonical model and every allowed thinking value. Include each
   resolved profile and reason in the startup disclosure, but do not write it
   to the run manifest or SQLite.
9. Resolve the startup fields from `options.md`. If every mapping in step 4
   already exists, resolve only `visible_app_task_permission`. If mappings are
   missing, list the exact repository roots in the standard question and
   resolve both `missing_project_action` and
   `visible_app_task_permission` in the one startup authorization interaction.
   With `create-projects`, use Computer Use only for those exact roots, verify
   each selected path before confirmation, then rerun the complete read-only
   saved-project preflight. With `stop`, denied task permission, unavailable
   Computer Use, a locked host, ambiguous selection, or any mismatched
   readback, stop before run state, claim, task, or worktree creation.
10. Write a private manifest containing only coordination identity:

```json
{
  "schema": "implement-feature/run-manifest",
  "schema_version": "3.0.0",
  "runtime_contract_version": "4.1.0",
  "run_id": "run-019f",
  "root_task_id": "019f-root-task",
  "controller_project_id": "controller-task-project-id",
  "repositories": [
    {
      "repository_identity": "github:owner/repository",
      "git_common_dir": "/absolute/repository/.git",
      "project_id": "affected-repository-project-id"
    }
  ],
  "assignments": [
    {
      "assignment_id": "spec-42",
      "source_spec_ref": "owner/repository#42",
      "repository_identity": "github:owner/repository",
      "tracker_backend": "github",
      "delivery_type": "github-pr",
      "title": "🛠️ Exact Feature Spec title",
      "target_branch_name": "feature/example",
      "prerequisite_assignment_ids": []
    }
  ],
  "feature_sets": []
}
```

The Feature Spec Set validator input has the exact protocol
`schema="implement-feature/feature-spec-set-input"` and
`schema_version="1.0.0"`. Its `members` array contains exact objects with
`source_spec_ref`, `affected_repository`, and `body_file`; each body path is an
absolute regular non-symlink file containing the complete current member body.
The command is read-only and emits the canonical member table plus one
`manifest_feature_set` object. Copy that object byte-for-byte into
`feature_sets`; its transient member projection contains `source_spec_ref`,
`repository_identity`, and `repository_key`. Sort multiple set objects
bytewise by `feature_id`; use an empty array for standalone Specs. Keep every
ephemeral input and body snapshot unchanged through successful `run start`,
which revalidates them and compares the current projections to the manifest
before opening SQLite. Pass one repeated
`--feature-spec-set-input <absolute-file>` flag per linked set and no such flag
for standalone Specs. Delete the ephemeral inputs and body snapshots only after
`run start` succeeds. Never persist those bodies, their normalized table text,
responsibilities, criterion text, repository key, or hashes in SQLite.

For a linked local source, the validator requires the exact
`<feature-id>--<repository-key>/planning/features/<feature-slug>/SPEC.md`
identity and emits
`repository_relative_spec_path=planning/features/<feature-slug>/SPEC.md`.
The qualified prefix is not a directory. Include the validated relative path
in the owning worker bootstrap, and resolve it only inside that assignment's
separately verified repository/worktree.

The manifest deliberately omits raw Spec and issue bodies, checklists, allowed
path text, validation attempts, worker technical state, provider state, and text
hashes. It retains only `feature_id` membership for assignments belonging to a
validated linked set. The authoritative bodies remain at their sources.

The manifest protocol and the runtime contract are independent, bare SemVer
identities; neither is the SQLite database schema integer. `run start` accepts
only the exact named manifest protocol shown above. It records the current
runtime contract, CLI version, and SHA-256 of the shipped `run-state` artifact
on the new run so later mutations can require that exact runtime.

The worker-project preflight and any explicitly authorized project setup finish
before writing the manifest or calling `scripts/run-state`. Project creation is
not worker recovery and task permission alone never authorizes it. Do not create
a broader parent project as a diagnostic step. A failed or partial project
setup is reported exactly and never converted into an active run.

One root task may own only one unfinished run. A second run from that task
starts only after the first is terminal.

Call `scripts/run-state --json run start --manifest <absolute-file>` and append
the unchanged `--feature-spec-set-input <absolute-file>` evidence flags for
every linked set. Immediately before startup, re-read the authoritative member
sources; if any changed, replace the snapshots and repeat validation. A
missing, extra, reordered, validator-invalid, or nonmatching evidence
projection fails before database access. One transaction claims every free
canonical Feature Spec and head branch and leaves only conflicting assignments
in `waiting-for-spec`. With
`tracker_backend=github`, a GitHub URL and `owner/repository#number` normalize
to the same claim identity. With `tracker_backend=local`, the globally
unambiguous repository-scoped Spec path remains local even when the repository
identity is `github:owner/repository`.

When at least one assignment acquires its claim, set and verify the immutable
root title once and schedule every claimed assignment allowed by path and
dependency serialization, without a numeric worker cap. When every assignment
waits, create no worker, worktree, branch, or provider mutation. Never use a
default PR base such as `main` as a head-branch collision: only the
implementation head branch is exclusive.

The root creates each worker as a visible Codex task with
`environment=worktree`, `model=gpt-5.6-sol`, and the assignment's resolved
`thinking=medium|high|xhigh`. The ChatGPT App creates the worktree and assigns
it to that task. Root verifies the task, checkout directory, and Git common
directory; it never runs `git worktree add`. SQLite keeps only checkout identity
needed for coordination, not the worker's technical contents or task profile.
The operation always targets the assignment's recorded repo-specific
`project_id`, never the multi-folder controller project. If task readback does
not resolve to that project and repository identity, reconcile or fail the
operation before bootstrap.

Each full bootstrap carries the canonical operational field
`review_owner=worker|root`. Record its initial value atomically with
`send-bootstrap begin --review-owner worker|root`; begin returns that persisted
owner for the envelope. Root may select itself only
after its own AutoReview doctor succeeds. Prefer the worker when its capability
is already proven. When capability is unknown, record and bootstrap with
`review_owner=worker`; after read-only checkout identity preflight and before
branch or implementation mutation, the worker runs
`<autoreview-skill-root>/scripts/autoreview --json doctor`. A successful doctor
confirms the worker owner. `recovery=reroute-to-capable-root` is a hard handoff:
the worker sends the structured doctor result, root runs the same doctor
immediately, and either performs one reconciled worker-to-root
`set-review-owner` operation whose evidence-only follow-up records
`review_owner=root`, or blocks as `blocked-app-capability` before
implementation. Never copy credentials or try an escalated worker launch after
the reroute result. The owner stays out of the run manifest but is authoritative
SQLite bootstrap-operation state: replay keeps the same operation ID and owner,
duplicate effects are idempotent, a second reroute or root-to-worker reversal
fails closed, and
recovery reads `run show` instead of inferring ownership from conversation
prose.

After the required ordinary workers and worktrees exist, forward-test the
declared distributed execution topology before combined validation. Every
worker must remain isolated to its own worktree. Each component owner proves its
exact HEAD before startup and after shutdown and sends endpoint, health, and
cleanup evidence directly to the worker that owns combined proof. If those
ordinary tasks cannot communicate or expose the required components, record
`blocked-app-capability` for every affected nonterminal assignment and stop that
bundle. Never replace the failed topology with cross-worktree access, root
execution, a hidden task, raw worktrees, copied code, or future manual testing.
