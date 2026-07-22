# Run State CLI

`scripts/run-state` is a standard-library Python CLI. Normal execution always
uses this shipped artifact. `CLI_VERSION` is exactly `1.0.0`; SQLite, manifest,
observation, and JSON envelope schemas are integer `1`. This is a fresh
breaking design with no migrations, aliases, importers, legacy readers, or
alternate state files.

All controllers for the same machine user share:

```text
~/.cache/dotagents/skills/implement-feature/run-state.sqlite3
```

The directory and DB are owner-only. There is no lock file. SQLite
`BEGIN IMMEDIATE` transactions plus the fixed 5000 ms busy timeout are the sole
writer coordination. Local SQLite does not coordinate different machines.

## Stored Data Allowlist

The schema contains only metadata, runs, assignments, canonical Feature Spec
claims, and typed App-operation reconciliation facts. It may retain durable
source refs, App project/thread/worktree identity, receipts/readbacks, release
reason, and coarse Git head, PR, or provider observation refs.

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
scripts/run-state --json assignment block \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT
scripts/run-state --json assignment abort \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT
scripts/run-state --json run finish \
  --run-id RUN --expected-revision N --outcome pr-ready
```

Read commands and `doctor` never write. Every mutation uses one compare-and-swap
revision transaction. JSON stdout is one object with `schema_version`, `ok`,
and `command`; errors add typed `error.code` and `error.message`.

## Claim Identity And Lifecycle

Canonical GitHub repository identity is `github:owner/repository`. Local-only
identity derives from the resolved Git common-directory real path, device, and
inode; linked worktrees intentionally share repository identity.

One assignment owns one claim. Its uniqueness key is canonical repository plus
canonical Feature Spec identity. GitHub `owner/repository#number` and the exact
issue URL normalize to `github:owner/repository#number`. Local refs use the
globally unambiguous repository-scoped Feature Spec path. A second uniqueness
constraint prevents active assignments from sharing one implementation head
branch in the same repository; the PR base branch is not part of that
constraint.

`run start` acquires free assignment claims independently. Waiting is tracked
per assignment, so a conflict never prevents sibling claims from starting.
Worker creation and bootstrap require that assignment's active claim and the
root's active Goal. A root still owns only one unfinished run and one lifecycle
Goal, and at most three workers may be live.

`assignment ready` atomically records final evidence and releases that
assignment's claim. `assignment abort` releases one claim only before bootstrap
authority. A durable-contract block retains only the affected claim. `run
finish` completes aggregate run state after assignment-level release; claim
release never proves upstream merge or integration.

## Recovery Observation

`claim reconcile` accepts exactly:

```json
{
  "schema_version": 1,
  "owner_run_id": "owner-run",
  "owner_assignment_id": "spec-42",
  "owner_expected_revision": 7,
  "repository_identity": "github:owner/repository",
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

`claim abandon` is a deliberately separate administrative override. The normal
controller never calls it. It is accepted only after typed reconciliation put
the waiter in `abandoned-recovery-required`; exact current owner and waiter
identities and revisions are mandatory. It preserves artifacts and transfers
only the exact Feature Spec claim. There is no TTL, lease, heartbeat takeover,
or repository-wide claim release.

Typed App observations carry only action-specific fields plus `receipt_ref` and
`readback_ref` when actually observed. `unknown` preserves ambiguous effects
and cannot be relaunched. Pending or unknown bootstrap delivery forbids worker
archive until readback proves it failed.

## CLI Maintenance

Keep normal execution on `scripts/run-state`; there is no maintenance project
or build output. `CLI_VERSION` remains `1.0.0` while this fresh schema remains
in development, and `STATE_SCHEMA_VERSION` remains `1`. Re-run `--help`,
`--version`, read-only `doctor`, Python compilation, unit/contract tests, and an
isolated lifecycle fixture after changes.
