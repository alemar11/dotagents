# Run State

## Boundary

`scripts/run-state` is the only shipped local helper. It is a standard-library
Python CLI backed by one owner-private SQLite database:

```text
$XDG_STATE_HOME/dotagents/skills/implement-feature/run-state-v1.sqlite3
```

When `XDG_STATE_HOME` is unset, use
`~/.local/state/dotagents/skills/implement-feature/run-state-v1.sqlite3`.
`CLI_VERSION` is `1.0.0`; the only state and JSON schema is integer `1`.
SQLite is the sole writer-coordination surface. Schema bootstrap and every
mutation use explicit bounded transactions; a writer that cannot acquire the
database within ten seconds fails with `state-busy`.
Before the first schema transaction commits, readers treat its private empty
database file as `uninitialized`, never as an unsupported schema.

This is a clean hard cut. The tool never probes a prior filename, cache tree,
schema, or format; never migrates or imports; and never creates a second archive
representation. An unsupported database fails closed.

The helper owns only:

- atomic repository and source claims;
- an exact immutable start manifest and its source fingerprints;
- typed App project, assignment, task/worktree, Goal, and operation identities;
- compare-and-swap revisions and a paginated one-use operation journal;
- a three-live-task ceiling;
- preimplementation abort or successful finish with atomic claim release.

It does not select a frontier, calculate path overlap, load Markdown, run
commands, control the App, inspect Git/GitHub, or judge external evidence.

## Runtime Surface

```bash
scripts/run-state --version
scripts/run-state --json doctor
scripts/run-state --json run start --manifest '<absolute-json>'
scripts/run-state --json run list --status 'active|completed|preimplementation-aborted|all'
scripts/run-state --json run show --run-id '<run-id>'
scripts/run-state --json claim find --claim-key '<claim-key>'

scripts/run-state --json operation begin --run-id '<run-id>' --expected-revision <n> --operation-key '<key>' --owner '<lower-kebab>' --action '<lower-kebab>' --subject-id '<id>' [--head-sha '<sha>'] --request '<absolute-json>'
scripts/run-state --json operation finish --run-id '<run-id>' --expected-revision <n> --operation-key '<key>' --status 'unknown|succeeded|failed' --result '<absolute-json>'
scripts/run-state --json operation show --run-id '<run-id>' --operation-key '<key>'
scripts/run-state --json operation list --run-id '<run-id>' [--after-sequence <n>] [--limit <n>]

scripts/run-state --json goal bind --run-id '<run-id>' --expected-revision <n> --source 'created|adopted' --objective-sha256 '<sha256>'
scripts/run-state --json goal complete --run-id '<run-id>' --expected-revision <n> --objective-sha256 '<sha256>'

scripts/run-state --json task bind --run-id '<run-id>' --expected-revision <n> --observation '<absolute-json>'
scripts/run-state --json task baseline --run-id '<run-id>' --expected-revision <n> --observation '<absolute-json>'
scripts/run-state --json task authorize --run-id '<run-id>' --expected-revision <n> --assignment-id '<id>'
scripts/run-state --json task ready --run-id '<run-id>' --expected-revision <n> --observation '<absolute-json>'
scripts/run-state --json task abort --run-id '<run-id>' --expected-revision <n> --observation '<absolute-json>'

scripts/run-state --json run finish --run-id '<run-id>' --expected-revision <n> --outcome 'completed|preimplementation-aborted'
```

`doctor`, `run show`, `run list`, `claim find`, and operation reads do not
write. Every mutation is one SQLite transaction. A stale revision performs no
partial write. On first use, schema bootstrap is one atomic transaction before
the first mutation transaction. JSON input must be an absolute regular
non-symlink file and is size-bounded.

## Typed App Results

The operation journal accepts all explicit owners and actions, but App lifecycle
actions have one protected identity per subject and exact successful results:

| Action | Subject | Result |
| --- | --- | --- |
| `create-goal` | root task ID | `{status:"active",objective_sha256}` |
| `block-goal` | root task ID | `{status:"blocked",objective_sha256}` |
| `complete-goal` | root task ID | `{status:"complete",objective_sha256}` |
| `create-task` | assignment ID | `{thread_id}` |
| `set-task-title` | assignment ID | `{thread_id,title}` |
| `send-worker-bootstrap` | assignment ID | `{thread_id}` |
| `authorize-implementation` | assignment ID | `{thread_id}` |
| `archive-task` | assignment ID | `{thread_id,status:"archived"}` |
| `resume-goal` (`owner`) | root task ID | `{status:"granted",authorization_ref}` |
| `abandon-run` (`owner`) | root task ID | `{status:"granted",authorization_ref}` |

Owner request and result refs are exactly
`owner:<action>:<run_id>:<operation_key>`. They correlate a typed operation to
the explicit current owner turn; they are not a fabricated App message ID.

The protected GitStack action `ensure-pull-request-ready` uses an assignment ID
subject, requires an exact operation head, and returns
`{pr_url,head_sha,head_branch_name,base_branch_name,default_branch_name,status:"ready-for-review"}`.

`operation begin` authorizes one launch only. An existing key never authorizes
a relaunch. `unknown` preserves ambiguity and may be reconciled only by
finishing the same operation as `succeeded` or `failed`. `operation list` is the
authoritative recovery surface and must be paged until `has_more=false`.

## Task Observations

`task bind` accepts exactly:

```json
{
  "schema_version": 1,
  "assignment_id": "spec-01",
  "thread_id": "019f-worker",
  "observed_title": "🛠️ Exact title",
  "project_id": "<App-project-id>",
  "repository_claim": "repository:github:owner/repository",
  "git_common_dir": "/absolute/repository/.git",
  "checkout_path": "/absolute/worktree",
  "git_top_level": "/absolute/worktree",
  "checkout_branch": "codex/generated-worktree",
  "baseline_head": "<git-head>"
}
```

It requires the active or explicitly resumed bound Goal, exact manifest project/repository identity,
the same independently observed Git common-directory path and filesystem
identity, a checkout not bound to another active assignment, and matching
successful task-create and title operations. `task baseline` accepts `schema_version`,
`assignment_id`, `thread_id`, matching `head_sha`, and `status=passed`, after
the bootstrap message operation. The implementation-authority operation cannot
start while any dispatched baseline remains pending; `task authorize` requires
the passed baseline and matching operation.

`task ready` accepts the exact assignment/thread, provider-read `head_sha`,
`head_branch_name`, `base_branch_name`, `default_branch_name`, canonical PR URL
in the claimed repository, and `status=ready-for-merge`. It requires head branch
equal to the authored target, base equal to the observed default branch, and a
default branch equal to the immutable repository manifest, plus a matching
succeeded `owner=gitstack`, `action=ensure-pull-request-ready`
operation. `task abort` accepts the exact assignment/thread, App
`completed|archived` readback, and observation ref, and is legal only before
implementation authority.

## Finish And Start Over

Successful finish requires every assignment `ready-for-merge`, the exact Goal
observed `completed`, and no pending or unknown operation. Preimplementation
abort requires every created task `terminal-aborted`, all uncreated assignments
still `planned`, no task ever authorized, no unresolved operation, and either
an active Goal or protected owner abandonment of a blocked Goal. Both finish
paths release claims atomically while preserving the run row.

A succeeded protected `block-goal` operation projects `goal.status=blocked`
without changing schema 1 and makes `blocked_resume_authorized=false`. Every new
journaled mutation then fails closed except Goal blocking, task reconciliation,
and protected owner decisions; existing operations remain finishable under the
same key. A later protected `owner/resume-goal` sets that projection to true and
resumes the same run without falsifying the App Goal as active. Repeated epochs require
new block and resume operation keys. Exact completion supersedes both.

A blocked run keeps its claims by default. Before implementation authority,
protected `owner/abandon-run` plus reconciled tasks and operations permits
`preimplementation-aborted` and closes further work authority; after GO,
abandonment and claim release remain forbidden.

There is no `retired` state and no takeover or migration command. Recover an
active schema-1 run from `run show` and the complete operation journal. A fresh
run uses a new run ID and imports nothing.

## JSON And Maintenance

With `--json`, stdout is one object containing `schema_version`, `ok`,
`command`, and command data. Errors contain `error.code` and `error.message`.

Normal execution uses only `scripts/run-state`; there is no maintenance project
or build output. `CLI_VERSION` in the artifact is the one semver source.
Breaking CLI changes reset the major contract, compatible additions bump minor,
and fixes bump patch. Re-run `--help`, `--version`, `--json doctor`, the focused
tests, and an isolated lifecycle fixture after every behavior change.
