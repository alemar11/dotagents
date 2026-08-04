# Implement Run-State Ledger

This reference owns the minimal SQLite WAL checkpoint and recovery ledger for
`se2:implement`. The ledger is not the workflow engine and never replaces
authoritative application, GitHub, Git, or filesystem readback.

The orchestrator is the sole runtime ledger client. Workers communicate
bounded evidence to the orchestrator and never invoke, inspect, or reconcile
the ledger directly.

## Runtime surface

Normal execution uses the shipped standard-library Python artifact at
`scripts/run-state`. The CLI version, runtime contract, and database schema are
independent identities. The initial contract is:

| Domain | Version |
| --- | --- |
| CLI | `1.0.0` |
| Runtime contract | `1.0.0` |
| Database schema | integer `1` |
| JSON envelope | `se2-implement/ledger-envelope` version `1.0.0` |

The default database is:

```text
~/.cache/dotagents/plugins/se2/skills/implement/run-state.sqlite3
```

Create it only through an explicit mutating ledger command. `--help`,
`--version`, `capabilities`, and `doctor` are read-only and must not create the
database, parent directory, WAL, or shared-memory sidecars. Read-only URI
construction must preserve the exact resolved local path.

## Storage and reset policy

Use SQLite persistent WAL journal mode, owner-only directory and database
permissions, a fixed busy timeout, foreign keys, and compare-and-swap revisions
for mutable run and assignment rows. Do not add a filesystem lock. Journal
drift blocks normal commands and read-only diagnosis does not repair it;
`state prepare` is the explicit repair boundary.

Normal and diagnostic commands reject symlinks, directory modes other than
`0700`, database modes other than `0600`, or a runtime CLI/artifact identity
different from the metadata singleton. `state prepare` may repair permissions,
WAL, and runtime identity for the current schema; it never rewrites an
incompatible schema or follows a symlink.

The `runtime_metadata` singleton row is the schema source of truth. Require the
current schema identity plus the exact table definitions, types, nullability,
primary and unique keys, checks, foreign keys, and explicit index definitions.
The shipped schema owns its constraints. There are no migrations,
compatibility aliases, or old-path probes. A detectable mismatch returns
`invalid-state-schema` without changing data.

Reset is an explicit destructive operation requiring the exact confirmation
token documented by `scripts/run-state --help`. It removes only the resolved
ledger database and its SQLite sidecars, then recreates the current schema.
Never reset automatically after a mismatch or error.

## Minimal data model

Keep only five tables:

- `runtime_metadata`: schema, runtime contract, CLI version, and shipped
  artifact identity;
- `runs`: one multi-Feature run, orchestrator identity, coarse checkpoint,
  aggregate status, and revision;
- `feature_claims`: exclusive active ownership from one authoritative GitHub
  Feature to one Implement run, with revision and explicit release state;
- `assignments`: Feature/Task refs, worker identity and worktree, branches,
  SHAs, PR ref, repair identity, contract generation, checkpoint, status, and
  revision;
- `operations`: one idempotency reservation for a side effect, its subject,
  status, receipt ref, and readback ref.

Do not store Feature/Task bodies, prompts, messages, findings, logs, arbitrary
JSON, model/reasoning profiles, code state, or worker technical state.

## Command families

```text
scripts/run-state --version
scripts/run-state --json capabilities
scripts/run-state --json doctor
scripts/run-state --json state prepare
scripts/run-state --json state reset --confirm drop-and-recreate
scripts/run-state --json run start ...
scripts/run-state --json run show ...
scripts/run-state --json run checkpoint ...
scripts/run-state --json feature claim --run-id ... --input ...
scripts/run-state --json feature release --run-id ... --input ...
scripts/run-state --json assignment checkpoint ...
scripts/run-state --json operation begin ...
scripts/run-state --json operation finish ...
```

`feature claim` atomically claims the complete non-empty `feature_refs` input
set or changes nothing; an active claim from another run returns
`feature-already-claimed`. Canonicalize an issue ref to one
`owner/repository#number` identity before lookup or storage, including an
equivalent GitHub issue URL. `feature release` accepts the complete active claim
set and expected revision for every member, verifies the run is at
`release-claims`, every assignment is delivery-ready at `final-verify`, and no
operation remains pending or unknown, then releases the whole set in one
transaction. It never releases one Feature independently. Preserve claims for
resumable blocked or deferred runs. Never infer release from task or PR state
without terminal reconciliation.

An assignment may be created or moved only while its `feature_ref` has an
active claim owned by the same run. A released, missing, or foreign claim
blocks the checkpoint; assignment state never establishes Feature ownership.
Feature, Task, and repository identity are immutable after creation, and
`contract_generation` may stay unchanged or advance by exactly one.

`run checkpoint` and `assignment checkpoint` accept only documented,
allowlisted fields and one expected revision. They record durable boundaries,
not every graph transition. A run can become `complete` only after at least one
Feature claim has been released, at least one assignment exists, every
assignment is delivery-ready at `final-verify`, and all operations are resolved.
An empty run can never complete. `operation begin` is idempotent for one
`run_id, action, subject_id`; duplicate calls return the original operation.
Beginning a side effect requires an active run and the assignment's active
Feature claim; a released or reclaimed claim makes the old run ineligible.
`operation finish` records authoritative `applied`, `not-applied`, `unknown`,
or `blocked` evidence. Every result requires authoritative readback;
`applied` and `unknown` also require the originating receipt. A recorded
`unknown` may be refined to one definitive result after reconciliation, while
a definitive result is immutable.

Treat a bounded application-task title adjustment as an application side
effect. Before applying it, reserve an operation with
`action=task-title-adjust` and a stable subject derived from the exact task
identity alone. Retain the exact requested title in the operation's referenced
effect evidence. Bind worker and Contract Repair planner reservations to their
assignment; the orchestrator owns every reservation and readback. Finish the
operation from the adjustment evidence and authoritative title observation.
On resume, reconcile a pending or `unknown` reservation and never begin a
second adjustment for that subject, even when Contract Repair changes the task
outcome or canonical title. This usage reuses the existing operations contract
and requires no schema, runtime-contract, envelope, or CLI-version change.

Delivery topology does not add a table or assignment field. Reconstruct it from
the authoritative Task dependency graph, assignment `base_branch`, `base_sha`,
`head_branch`, `candidate_sha`, live PR state, and operation evidence. Before a
stacked child publication, reserve the normal publication effect and a separate
child-bound operation with `action=stack-link`. Use a stable subject derived
from repository identity, verified parent PR, child branch, and candidate SHA
so the reservation exists before the G-owned workflow attempts the link.

After the worker returns, finish the publication and stack-link operations
independently. Store the G receipt by reference and require an authoritative
parent/child readback reference. A confirmed PR with an ambiguous link records
publication as `applied` and stack-link as `unknown`; it never replays PR
creation or linking without reconciliation. This usage requires no schema,
runtime-contract, envelope, or CLI-version change.

## Recovery boundary

On resume, read the last ledger checkpoint, then independently observe current
application tasks, worktrees, repositories, Feature/Task issues, PRs, and
reviews. For stacked assignments, also re-read parent/child bases, full heads,
stack order, and link state. Reconcile differences before another side effect.
Ledger text never proves external state.

For title recovery, the current display title can verify a match but cannot
prove whether a missing or different title was never adjusted. When the
operation reservation or retained attempt evidence is missing or ambiguous,
do not adjust again; preserve the task and report the shared title warning.

A ledger failure blocks only a new side effect or recovery step that requires
durable idempotency. It does not prevent ordinary live dialogue or read-only
observation. Do not mirror messages or routine milestones into SQLite.

## CLI maintenance

Keep normal execution on `scripts/run-state`. The script constant `CLI_VERSION`
is the semver source of truth. Use a major bump for breaking commands or JSON,
a minor bump for backward-compatible commands or stored capabilities, and a
patch bump for compatible fixes. Verify the shipped artifact with `--help`,
`--version`, `--json doctor`, focused tests, destructive-path guards, and a
temporary-database fixture.
