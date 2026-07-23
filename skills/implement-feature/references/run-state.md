# Run State CLI

`scripts/run-state` is a standard-library Python CLI. Normal execution always
uses this shipped artifact. `CLI_VERSION` is exactly `2.0.0`; SQLite, manifest,
observation, and JSON envelope schemas are integer `2`. This is a hard cut with
no migrations, aliases, importers, legacy readers, or alternate state files.
Every v1 DB or payload is rejected without modification. Schema number `2` does
not authorize another shape: table and column structure must match exactly or
the CLI returns `invalid-state-schema` without deleting or rewriting the user's
DB.

All controllers for the same machine user share:

```text
~/.cache/dotagents/skills/implement-feature/run-state.sqlite3
```

The directory and DB are owner-only. There is no lock file. SQLite
`BEGIN IMMEDIATE` transactions plus the fixed 5000 ms busy timeout are the sole
writer coordination. Local SQLite does not coordinate different machines.

## Stored Data Allowlist

The schema contains only metadata, runs, assignments, canonical Feature Spec
claims, and typed ChatGPT task-operation reconciliation facts. It may retain durable
source refs, tracker backend, delivery type, assignment prerequisites, ChatGPT
project/thread/worktree identity, exact `receipt_ref`/`readback_ref` machine
fields, release reason, normal Git
head/base/ancestry facts, and PR/provider refs only when applicable.

It must not store raw Spec or issue bodies, checklists, issue phases, allowed
path prose, validation attempts, worker technical or domain state, arbitrary
provider payloads, generic request/result JSON, or any text hash. Normal Git
head SHAs remain valid evidence.

## Commands

```bash
scripts/run-state --version
scripts/run-state --json doctor
scripts/run-state --json run start --manifest /absolute/manifest.json
scripts/run-state --json run wait-sweep \
  --run-id RUN --assignment-id ASSIGNMENT --expected-revision N
scripts/run-state --json run show --run-id RUN
scripts/run-state --json run list --status active

scripts/run-state --json claim find \
  --repository-identity github:owner/repository \
  --tracker-backend github \
  --source-spec-ref owner/repository#42
scripts/run-state --json claim reconcile \
  --run-id RUN --assignment-id ASSIGNMENT --expected-revision N \
  --observation /absolute/recovery-observation.json
scripts/run-state --json claim abandon \
  --run-id RUN --assignment-id ASSIGNMENT --expected-revision N \
  --owner-run-id OWNER --owner-assignment-id OWNER_ASSIGNMENT \
  --owner-expected-revision OWNER_N

scripts/run-state --json app-operation begin \
  --run-id RUN --expected-revision N --operation-key KEY \
  --action create-worker --subject-id ASSIGNMENT
scripts/run-state --json app-operation finish \
  --run-id RUN --expected-revision N --operation-key KEY \
  --observation /absolute/observation.json
scripts/run-state --json app-operation list --run-id RUN

scripts/run-state --json assignment ready \
  --run-id RUN --expected-revision N --observation /absolute/ready.json
scripts/run-state --json assignment ready --peer-input \
  --run-id RUN --expected-revision N --observation /absolute/ready.json
scripts/run-state --json assignment block \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT
scripts/run-state --json assignment capability-block \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT
scripts/run-state --json assignment resume \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT
scripts/run-state --json assignment recover \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT \
  --observation /absolute/recovery-observation.json
scripts/run-state --json assignment abort \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT
scripts/run-state --json run finish \
  --run-id RUN --expected-revision N --outcome pr-ready
```

Read commands and `doctor` never write. Every mutation uses one compare-and-swap
revision transaction. JSON stdout is one object with `schema_version`, `ok`,
and `command`; errors add typed `error.code` and `error.message`.

Ready observations always bind assignment/thread/repository/checkout,
`delivery_type`, named head and base branches, head/base SHAs, clean worktree,
base ancestry, current-head validation/AutoReview/Codex-review SHAs, tracker
readback, and the exact prerequisite HEAD map. `github-pr` additionally requires
the provider default branch, canonical PR URL, and provider observation ref;
`local-branch` rejects those fields. Status must be respectively
`pr-ready-for-merge-but-not-merged` or `local-branch-ready`.

The exact common ready-observation fields are:
`schema_version`, `assignment_id`, `thread_id`, `repository_identity`,
`delivery_type`, `head_sha`, `head_branch_name`, `base_branch_name`,
`base_sha`, `checkout_path`, `worktree_clean`, `base_is_ancestor`,
`validation_head_sha`, `autoreview_head_sha`, `codex_review_head_sha`,
`tracker_readback_ref`, `prerequisite_heads`, and `status`. `github-pr`
requires exactly three more fields: `default_branch_name`, `pr_url`, and
`provider_observation_ref`. `local-branch` forbids those three. No other keys
are accepted.

## Claim Identity And Lifecycle

Canonical GitHub repository identity is `github:owner/repository`. Local-only
identity derives from the resolved Git common-directory real path, device, and
inode; linked worktrees intentionally share repository identity.

One assignment owns one claim. Its uniqueness key is canonical repository plus
canonical Feature Spec identity. With `tracker_backend=github`, GitHub
`owner/repository#number` and the exact issue URL normalize to one identity.
With `tracker_backend=local`, the globally unambiguous repository-scoped path
remains local regardless of canonical repository identity. A second uniqueness
constraint prevents active assignments from sharing one implementation head
branch in the same repository; the PR base branch is not part of that
constraint.

`run start` acquires free assignment claims independently. Waiting is tracked
per assignment, so a conflict never prevents sibling claims from starting.
Worker creation and bootstrap require an active run and that assignment's
active claim. A root owns only one unfinished run, and at most three workers may
be live.

`assignment ready` validates delivery-specific typed evidence, atomically
records normal Git facts, and releases that assignment's claim.
`--peer-input` instead records the current HEAD for dependent peers, retains
the task and claim, and parks the worker so another assignment can use the
execution slot. Combined ready evidence must reproduce the current exact
prerequisite HEAD vector; drift fails closed. `assignment abort` releases one
claim only before bootstrap
authority. A durable-contract block retains only the affected claim. `run
finish` completes aggregate run state after assignment-level release; claim
release never proves upstream merge or combined behavior.

`assignment resume` is the same-root CAS transition for a recovered
`blocked-durable-contract` or `blocked-app-capability` assignment. It restores
the exact prior `active` or `peer-input-ready` state and requires the retained
claim. A `blocked-by-active-spec` assignment may run `run wait-sweep` again;
`abandoned-recovery-required` may repeat `claim reconcile` with newer
authoritative evidence.

## Recovery Observation

`claim reconcile` accepts exactly:

```json
{
  "schema_version": 2,
  "owner_run_id": "owner-run",
  "owner_assignment_id": "spec-42",
  "owner_expected_revision": 7,
  "repository_identity": "github:owner/repository",
  "tracker_backend": "github",
  "source_spec_ref": "owner/repository#42",
  "worker_state": "active",
  "checkout_state": "present",
  "readback_ref": "authoritative-app-readback-ref"
}
```

`worker_state` is one of `active`, `archived`, `completed`, `not-found`, or
`unknown`; `checkout_state` is `present`, `released`, `not-found`, or `unknown`.
An active worker or present checkout retains the owner. Terminal worker proof
transfers the claim only when the checkout is released or absent and the owner
has no pending or unknown assignment operation. Unknown or unresolved evidence
records `abandoned-recovery-required` on the waiter and retains the owner claim.
Owner and waiter revisions plus the SQLite writer transaction prevent stale
recovery.

When no waiter exists, the owning root uses `assignment recover` with the same
typed observation. Active worker or present checkout preserves the assignment.
Terminal/missing worker plus released/absent checkout and fully reconciled task
operations marks only that assignment `abandoned` and releases its claim. When
every sibling is already terminal and every claim is released, the same root
calls `run finish --outcome abandoned`. Unknown evidence fails closed without
changing ownership.

`claim abandon` is a deliberately separate administrative override. The normal
controller never calls it. It is accepted only after typed reconciliation put
the waiter in `abandoned-recovery-required`; exact current owner and waiter
identities and revisions are mandatory. It preserves artifacts and transfers
only the exact Feature Spec claim. There is no TTL, lease, heartbeat takeover,
or repository-wide claim release.

Typed ChatGPT operation observations carry only action-specific fields plus `receipt_ref` and
`readback_ref` when actually observed. `unknown` preserves ambiguous effects
and cannot be relaunched. Pending or unknown bootstrap delivery forbids worker
archive until independent task inspection proves it failed.

Every task observation uses `schema_version: 2` and
`status: unknown|succeeded|failed`. A succeeded observation requires
`receipt_ref`, `readback_ref`, and exactly these action fields:

| Action | Additional fields |
| --- | --- |
| `create-worker` | `thread_id`, `project_id`, `checkout_path`, `git_common_dir`, `observed_state` |
| `set-worker-title` | `thread_id`, `observed_title` |
| `send-bootstrap` | `thread_id` |
| `send-worker-message` | `thread_id` |
| `set-root-title` | `observed_title` |
| `archive-worker` | `thread_id`, `observed_state` |

Unknown or failed observations may include only the authoritative subset
actually observed. Never invent reconciliation references.

## CLI Maintenance

Keep normal execution on `scripts/run-state`; there is no maintenance project
or build output. `CLI_VERSION` remains `2.0.0` and
`STATE_SCHEMA_VERSION` remains `2`. Re-run `--help`,
`--version`, read-only `doctor`, Python compilation, unit/contract tests, and an
isolated lifecycle fixture after changes.

## Hard-Cut Operations

Before changing the runtime or canonical DB, suspend new invocations and use
the installed v1 runtime to reconcile every pending or unknown operation and
terminalize every v1 controller. Continue only when its read-only `doctor`
reports `active_owner_runs=0` and the repository changes are frozen in a clean
commit.

If the canonical DB is already absent, an uninitialized v1 `doctor` is
equivalent to zero owners even when that older output omits
`active_owner_runs`. In that case, require an already timestamped owner-only v1
archive bound to the frozen v1 commit, do not recreate the canonical DB, and
skip the rename.

Archive the owner-only canonical v1 DB with a timestamped rename, then install
the v2 runtime, documentation, and tests together. Do not use a v2 filename:
the canonical `run-state.sqlite3` path remains the single claim domain. Before
the first v2 write, `doctor` must report `uninitialized`,
`active_owner_runs=0`, and `writes_performed=false`; the first `run start`
creates schema 2.

Use the archive shape
`run-state.sqlite3.v1-YYYYMMDD-HHMMSS.bak`, keep mode `0600`, and record the
exact frozen v1 commit SHA in the cutover evidence. Any later v1 recovery uses
a clean checkout of that immutable commit, never the live v2 script.

Before any v2 run, rollback may restore the frozen v1 code and archived v1 DB
directly. After a v2 run exists, first terminalize every v2 controller, archive
the v2 DB, and only then restore the frozen v1 code and DB. Never run both
versions against separate state files.

`blocked` runs count as active owners for this gate. Rollback is forbidden
until the same root recovers each blocked assignment to an ordinary permitted
terminal outcome. There is no force-finish path that drops post-bootstrap
claims or bypasses unresolved worker/checkouts merely to make rollback
possible.
