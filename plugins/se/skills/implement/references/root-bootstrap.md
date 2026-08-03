# Implement Root Bootstrap

The parent session creates the root/controller task before this protocol runs.
The root is a lightweight control plane and must not invoke `$se:implement`,
create another root, or replace itself. The verified parent identity, host, and
relay instructions are transient handoff context; the stable root task identity
remains the only durable controller identity in `run-state`.

On entry, before the numbered preflight below, the root must:

- independently observe the current task and verify its stable identity, local
  execution, and exact control-plane project;
- independently establish the provenance of the incoming handoff and require
  its parent identity and host/project binding to match the authoritative source
  parent that created or resumed this exact root;
- reject any parent or root identity derived from prompt prose, a title, timing,
  user-supplied text, remembered state, or a manually copied UUID;
- stop as `blocked-parent-identity-provenance` before monitoring, retry,
  run-state access, claims, or any other mutation when source identity,
  provenance, or binding is unavailable, stale, contradictory, or mismatched;
- verify the `gpt-5.6-sol` / medium-reasoning profile when task telemetry exposes
  them; settings drift blocks before workers;
- retain the verified parent task identity only for coarse milestone and
  final-report relay;
  the parent is not a worker, repository, or run-state target;
- keep the root task unarchived and keep the same root for resume/recovery;
- treat the parent-facing final Markdown report as a relay of root evidence, not
  as a second root synthesis.

Before mutation, root follows this numbered preflight:

1. Read `../../../references/workflow-contract.md` and
   `../../../references/ready-gate.md`, then read and validate the complete
   current Feature Spec frontier through `feature-spec-contract.md`. Before
   resolving worker profiles, startup authorization, or writing any run state,
   enforce the ready-for-agent gate against the complete implementation issue
   graph. Read the exact label metadata through the G issue workflow;
   incomplete pagination, stale reads, races, or one missing label stop the
   affected Spec before claims, tasks, or worktrees.
2. Observe the current Codex task and authoritative saved-project inventory.
   When the task has an explicit saved-project binding, require it to identify
   one local saved Codex project on the task's current host and record that
   exact binding as `controller_project_id`; also establish its primary path.
   This direct binding may be multi-folder or unrelated to the feature.

   When task readback omits an explicit saved-project binding, use the
   compatibility fallback only if all of these authoritative facts hold:

   - authoritative task observation establishes a local current host and an
     absolute working directory;
   - that directory resolves to an existing non-symlink directory and is
     exactly the Git
     worktree root reported by `git rev-parse --show-toplevel`;
   - exactly one saved project is local, belongs to that same host, is
     authoritatively identified as Git-backed, and has a canonical path exactly
     equal to the task's canonical working directory;
   - independently resolving the candidate path's absolute Git common directory
     succeeds and exactly matches the current task repository's absolute Git
     common directory; and
   - no second exact-path candidate, parent-path substitution, remote or
     cross-host candidate, non-Git candidate, missing path, symlink alias, or
     Git-common-directory mismatch remains.

   Record that unique candidate's stable project identity as
   `controller_project_id`. One reported project path does not expose the
   complete folder set or folder count, so do not claim that this fallback
   proves a single-folder project. The
   candidate may be a one-folder project or the primary path of a multi-folder
   workspace. Both are safe as controller identity because the controller
   project is UI/control-plane identity and read-only coordination context only:
   its Git defaults never expand scope or grant an implementation claim,
   branch, worker, or PR. Zero, multiple, or unverifiable candidates stop before
   state.
3. Resolve each affected repository's canonical GitHub identity as
   `github:owner/repository` and verify that the saved project points to that
   repository.
4. Run the worker-project preflight against the authoritative saved-project
   inventory. Every affected repository must map bijectively to one separate
   local saved Git project on the current host. Its reported primary folder
   must be exactly that repository root, and its independently resolved Git
   common directory must match the canonical repository identity. Resolve this eligibility independently even
   when step 2 used the same project ID as controller identity: exact-path
   controller resolution is not worker-project evidence. When the controller
   project is multi-folder, exclude its project ID from worker mapping even when
   an affected repository is its primary folder. Its primary and secondary
   folder memberships are context only and never satisfy the worker-project
   requirement. The same repository may appear in multiple multi-folder
   projects without becoming multiple repository identities or execution
   targets. Reject remote, non-Git, duplicate eligible repo-project,
   parent-path, and ambiguous worker mappings before state; a broad or
   multi-folder project is never a substitute.
5. Verify GitHub Issue refs, the fixed GitHub PR delivery, branches, and required
   dependency proof; calculate allowed-path overlap,
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
8. Load `task-model-policy.md`, verify the fixed root profile, resolve exactly
   one worker profile per implementation-eligible Feature Spec, and verify
   destination-host support for the canonical model and every allowed thinking
   value. Include the root profile and each worker profile and reason in the
   startup disclosure, but do not write them to the run manifest or SQLite.
9. Resolve the startup fields from `options.md`. The explicit execution request
   resolves both `visible_app_task_permission=granted` and
   `contract_repair_task_permission=granted` for the disclosed root, workers, and
   necessary contract-repair Feature tasks unless the user explicitly denies task
   creation. If mappings are missing, list the exact repository roots in the
   standard question and resolve only `missing_project_action` in the one
   project-creation interaction.
   With `create-projects`, use Computer Use only for those exact roots, verify
   each selected path before confirmation, then rerun the complete read-only
   saved-project preflight. With `stop`, denied task permission, unavailable
   Computer Use, a locked host, ambiguous selection, or any mismatched
   readback, stop before run state, claim, task, or worktree creation.
10. Write a private manifest containing only coordination identity:

```json
{
  "schema": "implement-feature/run-manifest",
  "schema_version": "5.0.0",
  "runtime_contract_version": "2.0.0",
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
      "title": "🛠️ Implement Feature · Exact Feature Spec title",
      "target_branch_name": "feature/example",
      "prerequisite_assignment_ids": []
    }
  ],
  "feature_sets": []
}
```

Each assignment `title` is the complete canonical worker-task title
`🛠️ Implement Feature · <Feature Spec title>`; the runtime rejects a bare or differently
prefixed title.

The Feature Spec Set validator input has the exact protocol
`schema="implement-feature/feature-spec-set-input"` and
`schema_version="2.0.0"`. Its `members` array contains exact objects with
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

On recovery, reread the controller task and projects. A direct binding must
still identify the recorded controller project. An omitted explicit binding
must reproduce every step-2 fallback predicate and resolve the same recorded
project ID; otherwise stop rather than replacing the controller identity.

One root task may own only one unfinished run. A second run from that task
starts only after the first is terminal.

Call `scripts/run-state --json run start --manifest <absolute-file>` and append
the unchanged `--feature-spec-set-input <absolute-file>` evidence flags for
every linked set. Immediately before startup, re-read the authoritative member
sources; if any changed, replace the snapshots and repeat validation. A
missing, extra, reordered, validator-invalid, or nonmatching evidence
projection fails before database access. One transaction claims every free
canonical Feature Spec and head branch and leaves only conflicting assignments
in `waiting-for-spec`. GitHub issue URLs and `owner/repository#number` normalize
to the same claim identity.

When at least one assignment acquires its claim, attempt the immutable root
title once when the live title operation is exposed, record any title warning
in the run report, and schedule every claimed assignment allowed by path and
dependency serialization, without a numeric worker cap. If that operation is
not exposed, record `root-title-unverified` and continue.
When every assignment waits, create no worker, worktree, branch, or provider
mutation. Never use a
default PR base such as `main` as a head-branch collision: only the
implementation head branch is exclusive.

The root creates each worker as a visible Codex task in an isolated worktree,
using `gpt-5.6-sol` and the assignment's resolved medium, high, or extra-high
reasoning profile. Before the one creation attempt, root resolves the exact
repository project and host from authoritative App state and requests the
canonical worker title when supported. The ChatGPT App creates the isolated
checkout and assigns it to that task. Root independently observes the created
task and verifies its stable identity, project, host, execution mode, state,
title, checkout directory, Git common directory, project binding, and
operational state in the
`create-worker` observation. Title evidence is recorded separately from the
structural worker proof. If creation does not yield the exact title, root
records `set-worker-title`, applies the exact canonical title at most once to
the stable task identity, then independently verifies the title again when
possible. A
missing or different title records `title-unverified` or `title-drift` and does
not prevent bootstrap once task identity, project, checkout, Git common
directory, and operational state are verified. Root never runs `git worktree
add` and never retries a title mutation blindly.

SQLite keeps only checkout identity and typed task readback needed for
coordination, not the worker's technical contents or task profile. The
operation always targets the assignment's recorded repo-specific `project_id`,
never the multi-folder controller project. If task readback does not resolve to
that project or repository identity, reconcile or fail the operation before
bootstrap. A missing, normalized-to-different, or unverifiable title is a
telemetry warning only; it does not authorize cleanup or block bootstrap. Root
does not retry the title operation to repair drift. An inspection error never proves
absence and retains the claim. An all-aborted pre-bootstrap run finishes as
`preimplementation-aborted`; if a sibling implementation already started,
every sibling must become terminal and the mixed run finishes as `abandoned`,
not as successful delivery.

Each full bootstrap has one fixed execution policy: the worker owns native
review. After read-only checkout identity preflight and before branch or
implementation mutation, the worker verifies that the current live runtime can
perform native review with the exact worker model and resolved medium, high, or
extra-high reasoning profile. An unavailable or unusable profiled review
capability is reported as `blocked-app-capability` before editing;
root records the evidence and does not take over the review. The bootstrap
contains no review-owner choice or reroute field, and replay keeps only the
same operation ID and `bootstrap_id`. Never copy credentials or try an
escalated launch.

After the required ordinary workers and worktrees exist, forward-test the
declared distributed execution topology before combined validation. Every
worker must remain isolated to its own worktree. Each component owner proves its
exact HEAD before startup and after shutdown and sends endpoint, health, and
cleanup evidence directly to the worker that owns combined proof. If those
ordinary tasks cannot communicate or expose the required components, record
`blocked-app-capability` for every affected nonterminal assignment and stop that
bundle. Never replace the failed topology with cross-worktree access, root
execution, a hidden task, raw worktrees, copied code, or future manual testing.
