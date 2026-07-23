# Run State CLI

`scripts/run-state` is a standard-library Python CLI. Normal execution always
uses this shipped artifact. `CLI_VERSION` is exactly `1.0.0`; SQLite, manifest,
observation, and JSON envelope schemas are integer `1`. This is a breaking hard
cut with no migrations, state copies, aliases, importers, or alternate state
files. Schema number `1` does not authorize another shape: table and column
structure must match exactly or the CLI returns `invalid-state-schema` without
deleting or rewriting the DB.

All controllers for the same machine user share:

```text
~/.cache/dotagents/skills/implement-feature/run-state.sqlite3
```

The directory and DB are owner-only. SQLite transactions use a fixed 5000 ms
busy timeout. There is no filesystem lock. The application-owned,
single-row `runtime_metadata` table is the sole schema and cutover source of
truth:

```sql
CREATE TABLE runtime_metadata (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    schema_version INTEGER NOT NULL CHECK (schema_version >= 1),
    target_schema_version INTEGER,
    CHECK (
        target_schema_version IS NULL
        OR target_schema_version > schema_version
    )
);
```

Exactly one `singleton = 1` row must exist. Normal schema-1 state is
`(schema_version=1, target_schema_version=NULL)`. `PRAGMA user_version` is not
application state and is never read or written. Local coordination does not
span different machines.

## Stored Data Allowlist

The schema contains only runtime metadata, runs, assignments, canonical Feature Spec
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
scripts/run-state --json state prepare
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

Read commands and `doctor` never write. `state prepare` is the explicit
destructive preparation command; every ordinary state mutation uses one
compare-and-swap revision transaction. JSON stdout is one object with
`schema_version`, `ok`, and `command`; errors add typed `error.code` and
`error.message`.

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
  "schema_version": 1,
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

Every task observation uses `schema_version: 1` and
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

`set-root-title` is single-use for each run. Its exact expected title is derived
from the immutable assignment count: `🤖 Feature Orchestrator` for one
assignment and `🤖 Feature Orchestrator · N Features` for two or more.

Unknown or failed observations may include only the authoritative subset
actually observed. Never invent reconciliation references.

## CLI Maintenance

Keep normal execution on `scripts/run-state`; there is no maintenance project
or build output. `CLI_VERSION` remains `1.0.0` and
`STATE_SCHEMA_VERSION` remains `1`. Re-run `--help`,
`--version`, read-only `doctor`, Python compilation, unit/contract tests, and an
isolated lifecycle fixture after changes.

## Hard-Cut Operations

Changing `STATE_SCHEMA_VERSION`, changing SQLite shape, or expanding the
recognized rebuild-source set requires explicit user consent before code or
documentation edits. Every approved change is a breaking hard cut. Never add
`ALTER` upgrades, data-copy migrations, imports, versioned DB filenames, or
state carry-forward.

At runtime, call read-only `doctor` first and then `state prepare`.
For a recognized older DB, `state prepare` validates the old schema and writes
the new runtime's schema number to `target_schema_version` transactionally
while the old schema remains intact. A non-NULL target makes old/current
runtimes reject every new `run start`, while commands needed by already-owned
runs remain available.

If owners remain, invoke preparation with the absolute retained executable:
`state prepare --retained-runtime /absolute/path/to/old/run-state`. It verifies
that executable's approved SHA-256 identity and exact old lineage version, then returns
`waiting-for-schema-drain`. Keep the root turn open and repeat bounded `doctor`
and `state prepare` sweeps. `waiting-for-spec`, `active`, and `blocked` all
count as owners. Do not force-finish, abandon, release, or rewrite claims
merely to complete a cutover. If the retained executable is unavailable or
does not report the exact old version, fail closed and preserve the fence.

When the recognized older DB reports zero owners, `state prepare` begins an
exclusive SQLite transaction and rechecks zero. Inside that same transaction
it drops all application tables, indexes, and triggers; recreates the complete
fresh schema including `runtime_metadata`; inserts the new
`(schema_version=N, target_schema_version=NULL)` singleton; and commits. No
row, claim, operation, or historical evidence is copied. Any failure rolls
back the transaction and restores the complete old logical and file state.

An older runtime that encounters a newer schema fails closed and never
regenerates it. Unknown older versions, unversioned tables, corrupt DBs,
same-number structural drift, unsafe permissions, and symlinks also fail
closed without reset.

Schema 1 and CLI 1.0.0 begin a fresh lineage. No pre-lineage DB is a recognized
rebuild source: verify zero owners with its original runtime, suspend new
invocations, delete the old DB once, then let schema-1 `state prepare`
create the fresh claim domain. For every future approved cut, stage the newer
runtime without replacing the exact old executable needed by active owners.
The newer `state prepare` may set the fence and wait, but old owners must
terminalize through that retained old executable. Replace it only after
`active_owner_runs=0` and successful regeneration. If the old executable is
unavailable, fail closed instead of promising an unexecutable drain.
