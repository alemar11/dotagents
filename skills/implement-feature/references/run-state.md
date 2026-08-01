# Run State CLI

`scripts/run-state` is a standard-library Python CLI. Normal execution always
uses the shipped artifact. CLI release `7.0.1` implements the breaking runtime
contract `8.0.0` over database schema `7`. Worker creation now atomically
verifies the final task title and rejects the retired post-creation rename
operation. Externally owned scope repair and contract generations remain in
place while path and dependency serialization stay controller invariants; the
runtime does not add per-file claims. The
controller's saved project remains explicit control-plane identity, each
affected repository maps bijectively to its own saved project, and assignments
inherit that normalized binding. There are no command aliases or compatibility
flags.

Four version domains are deliberately independent:

| Domain | Current identity | Meaning |
| --- | --- | --- |
| CLI | `7.0.1` | User-facing commands and executable behavior |
| Runtime contract | `8.0.0` | Coordination semantics required by an active run |
| Database schema | integer `7` | Exact SQLite tables, columns, indexes, and constraints |
| JSON protocols | independently named and versioned | Exact machine payload or envelope shape |

SemVer identities are bare values without a `v` prefix. Database schema numbers
are integers, never SemVer. `scripts/run-state --json capabilities` is the
machine-readable registry for these identities and protocols:

| Protocol | `schema` | Version |
| --- | --- | --- |
| CLI envelope | `implement-feature/cli-envelope` | `3.0.0` |
| Run manifest | `implement-feature/run-manifest` | `4.0.0` |
| Feature Spec Set input | `implement-feature/feature-spec-set-input` | `2.0.0` |
| Codex task-operation observation | `implement-feature/app-operation-observation` | `4.0.0` |
| Scope-repair observation | `implement-feature/scope-repair-observation` | `1.0.0` |
| Delivery-ready observation | `implement-feature/delivery-ready-observation` | `3.0.0` |
| Recovery observation | `implement-feature/recovery-observation` | `3.0.0` |
| Assignment-resume observation | `implement-feature/assignment-resume-observation` | `2.0.0` |

Every payload carries the exact string `schema_version` listed for its
`schema`. An exact-key protocol change to a field name, type, required key, or
closed enum is breaking and requires that protocol's major bump unless a real
capability-negotiation contract is introduced first.

All controllers for the same machine user share:

```text
~/.cache/dotagents/skills/implement-feature/run-state.sqlite3
```

The directory and DB are owner-only. SQLite transactions use a fixed 5000 ms
busy timeout. There is no filesystem lock. The application-owned,
single-row `runtime_metadata` table is the sole schema source of truth:

```sql
CREATE TABLE runtime_metadata (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    schema_version INTEGER NOT NULL CHECK (schema_version = 7)
);
```

Exactly one `singleton = 1` row must exist. Normal current state is
`(schema_version=7)`. The integer stored here is not the CLI, runtime-contract,
or JSON protocol version. Schema number `7` does not authorize an alternate
shape: every table, column, index, and constraint must match exactly or the CLI
returns `invalid-state-schema` without deleting or rewriting the DB. `PRAGMA
user_version` is not application state and is never read or written. Local
coordination does not span different machines.

Every run records `runtime_contract_version`, `runtime_cli_version`, and
`runtime_artifact_sha256`. Commands that mutate or coordinate that run require
the exact current executable to match all three pins. `run show` and `run list`
remain available for diagnosis when it does not. An executable with the same
SemVer but different bytes is not the retained runtime for that run.

## Stored Data Allowlist

The schema contains only runtime metadata, runs, normalized run-repository
bindings, assignments, canonical Feature Spec claims, typed Codex
task-operation reconciliation facts, and single-use operation markers. It may
retain durable source refs, linked
`feature_id` membership, assignment
prerequisites, Codex controller/repository project identity, thread/worktree
identity, exact `receipt_ref`/`readback_ref` machine fields, release reason,
normal Git head/base/ancestry facts, contract generation, opaque scope repair
identity and authoritative repair readback, and PR/provider refs only when
applicable. GitHub Issues and GitHub PRs are fixed workflow boundaries, not
stored provider or delivery selectors.

`app_operation_markers` contains one durable reservation for each
`(run_id, action, subject_id)` in `SINGLE_USE_ACTIONS`. The reservation is
created with `ON CONFLICT DO NOTHING` before the corresponding typed row in
`app_operations`; a duplicate returns the original `operation_id` and must be
reconciled or replayed through that operation. The marker is deliberately a
small idempotency key, not a generic provider payload or a second operation
state machine.

Script-level validation explains whether a transition is allowed, while the
final SQL mutation repeats the expected revision or state as a predicate. Each
guarded mutation must affect exactly one row; otherwise the transaction fails
closed with a conflict error.

It must not store raw Spec or issue bodies, checklists, issue phases, allowed
path prose, validation attempts, worker technical or domain state, arbitrary
provider payloads, generic request/result JSON, or any text hash. Normal Git
head SHAs remain valid evidence.

## Commands

```bash
scripts/run-state --version
scripts/run-state --json capabilities
scripts/run-state --json doctor
scripts/run-state --json feature-spec-set validate \
  --input /absolute/feature-spec-set-input.json
scripts/run-state --json state prepare
scripts/run-state --json run start --manifest /absolute/manifest.json \
  --feature-spec-set-input /absolute/feature-spec-set-input.json
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
  --run-id RUN --expected-revision N \
  --action create-worker --subject-id ASSIGNMENT
scripts/run-state --json app-operation observation template \
  --action send-bootstrap --status unknown
scripts/run-state --json app-operation observation create \
  --run-id RUN --expected-revision N --operation-id OPERATION \
  --launch-count 1 --status unknown --readback-ref READBACK \
  --output /absolute/new-observation.json
scripts/run-state --json app-operation finish \
  --run-id RUN --expected-revision N --operation-id OPERATION \
  --observation /absolute/observation.json
scripts/run-state --json app-operation replay \
  --run-id RUN --expected-revision N --operation-id OPERATION
scripts/run-state --json app-operation list --run-id RUN

scripts/run-state --json assignment ready-observation template \
  --review-profile standard \
  --readiness-mode terminal
scripts/run-state --json assignment ready-observation create \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT \
  --readiness-mode terminal \
  --thread-id THREAD --repository-identity github:owner/repository \
  --head-sha HEAD --head-branch-name feature/example \
  --base-branch-name main --base-sha BASE \
  --checkout-path /absolute/checkout \
  --worktree-clean --base-is-ancestor \
  --validation-head-sha HEAD --autoreview-head-sha HEAD \
  --review-candidate-head-sha CANDIDATE --review-profile standard \
  --default-branch-name main --pr-url https://github.com/owner/repository/pull/44 \
  --provider-observation-ref PROVIDER \
  --tracker-readback-ref TRACKER \
  --output /absolute/new-ready-observation.json
scripts/run-state --json assignment ready \
  --run-id RUN --expected-revision N --observation /absolute/ready.json
scripts/run-state --json assignment block \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT
scripts/run-state --json assignment capability-block \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT
scripts/run-state --json assignment scope-block \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT
scripts/run-state --json app-operation begin \
  --run-id RUN --expected-revision N \
  --action create-scope-repair-task --subject-id ASSIGNMENT
scripts/run-state --json assignment scope-repair-observation template
scripts/run-state --json assignment scope-repair-observation create \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT \
  --repair-outcome applied \
  --implementation-issue-ref owner/repository#43 \
  --planning-thread-id PLANNER_THREAD \
  --planning-result-ref PLANNER_RESULT \
  --authoritative-readback-ref SOURCE_READBACK \
  --output /absolute/new-scope-repair-observation.json
scripts/run-state --json app-operation begin \
  --run-id RUN --expected-revision N \
  --action send-scope-revision --subject-id ASSIGNMENT \
  --scope-repair-observation /absolute/scope-repair-observation.json
scripts/run-state --json assignment resume \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT \
  --observation /absolute/assignment-resume-observation.json
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
the `implement-feature/cli-envelope` protocol fields, `ok`, `command`,
`cli_version`, and `runtime_contract_version`; errors add typed `error.code`
and `error.message`. With `--json`, argument-parser failures such as missing
required flags, invalid enum values, and unknown arguments use that same typed
error envelope instead of unstructured argparse usage output.

The manifest accepted by `run start` has exactly the protocol fields
`schema="implement-feature/run-manifest"` and
`schema_version="4.0.0"`, `runtime_contract_version="8.0.0"`, and the
`run_id`, `root_task_id`, `controller_project_id`, `repositories`,
`assignments`, and `feature_sets` described in
`root-bootstrap.md`. The CLI rejects integer protocol versions and unknown or
additional top-level keys. For each linked set, `run start` also requires one
repeated `--feature-spec-set-input` path. It revalidates the complete current
bodies before opening SQLite and requires the sorted validator projections to
equal `feature_sets` exactly. Standalone manifests use an empty `feature_sets`
array and no evidence flags.

`feature-spec-set validate` is a pure read command. Its input uses the exact
`implement-feature/feature-spec-set-input` protocol and contains at least two
member objects with exact `source_spec_ref`, `affected_repository`, and
absolute `body_file` fields. It parses each complete member body, requires the
same canonical lowercase UUID, distinct lower-kebab repository keys, one exact
normalized Feature Spec Set table, exact self rows, globally unique owned
criterion/proof IDs, and responsibility cells that own precisely those IDs.
Every owned ID in a responsibility cell is an exact inline-code token; the
validator rejects unbackticked text, malformed prefix/suffix matches, and
unidentified acceptance checklist items. An Integration Execution Contract
requires at least one canonical Proof ID.
Applied refs cannot use `proposed-spec:`. Success emits a sorted canonical
projection and a `manifest_feature_set` containing only `feature_id`,
`source_spec_ref`, `repository_identity`, and `repository_key`. It never
creates or mutates the database, and neither the bodies, normalized table,
responsibility text, criterion text, nor hashes enter persistent state.
## Observation Builders

`app-operation observation template`, `assignment scope-repair-observation
template`, and `assignment ready-observation template` return descriptors:
protocol
constants, required fields, optional fields, and the closed-key rule. They are
not payload placeholders and cannot be passed to `finish` or `ready`.

The corresponding `create` commands are pure builders. They read the named run
and assignment or operation, verify the expected revision and exact runtime
pin, derive the protocol constants and designated identity fields, validate all
caller-supplied independent readback facts, and write one bare protocol
payload. In particular, the ready builder derives the fixed GitHub PR transport
and status while repository, task, checkout, branch, and evidence facts remain
caller-supplied observations. They never mutate SQLite.
The output must be an absolute path to a new file in an existing directory. The
builder creates it atomically with mode `0600`, follows no output symlink, and
never overwrites an existing path.

`app-operation finish` remains the sole consumer and state mutator for an
app-operation observation. `assignment ready` remains the sole consumer and
state mutator for a delivery-ready observation. `assignment resume` is the sole
consumer of an assignment-resume observation. Each revalidates the complete
payload inside its write transaction; successful builder output does not
reserve or advance state.

The scope-repair builder requires a `blocked-scope-repair` assignment and the
successful recorded planner task. It derives run, assignment, current contract
generation, repair ID, and source Spec ref. The caller supplies the exact
`repair_outcome=applied|no-op`, implementation issue, planner task, planner
result, and authoritative complete-source readback. `send-scope-revision begin`
is its sole consumer.

The app-operation builder accepts only the action/status fields described by
its descriptor through `--receipt-ref`, `--readback-ref`, `--thread-id`,
`--project-id`, `--checkout-path`, `--git-common-dir`, `--observed-title`,
and `--observed-state`. It also requires `--launch-count` copied from the
authorizing `begin` or `replay` result; it does not derive the launch
generation. A stale count is rejected before any observation file is written.
The builder derives `bootstrap_id`; for `send-scope-revision` it derives
`scope_revision_id` and `contract_generation`.

For a successful `create-worker`, `observed_state` is the literal Codex task
state and accepts `active` or `idle`. Exact `observed_title` equality proves
that the created task is titled atomically and permits bootstrap. A different
title still records the truthful successful creation receipt and worker binding,
but `finish` returns `effect_warning=worker-title-drift` and
`cleanup_required=archive-worker`; bootstrap is rejected so root can archive
the pre-bootstrap task. Successful `archive-worker` readback includes the exact
recorded `checkout_path` and proves that no file, directory, or symlink remains
there before `assignment abort` may release only its claim. Only `ENOENT` or
`ENOTDIR` proves absence; permission, I/O, and every other inspection error
blocks cleanup and retains the claim.
When every assignment remains pre-bootstrap, the all-aborted run finishes as
`preimplementation-aborted`. When a sibling already started, every sibling must
reach a terminal delivery or abandoned state and the mixed run finishes as
`abandoned`, never as successful delivery. For a successful `archive-worker`,
it accepts `archived` or
`completed`. The template exposes these closed values under
`field_constraints`, so callers do not infer them from the UI label.
`create-scope-repair-task` likewise accepts only `active|idle`.

Both ready-observation commands require
`--readiness-mode terminal|peer-input`; the selected value is stored in the
payload. The ready builder accepts repeated
`--prerequisite-head ASSIGNMENT_ID=GIT_SHA` flags. `high-risk` requires
`--codex-review-head-sha`; `standard` rejects it and emits JSON `null`.
GitHub PR delivery requires `--default-branch-name`, `--pr-url`, and
`--provider-observation-ref`.
`peer-input` applies the dependent-assignment validation that the consumer
later repeats. `assignment ready` has no readiness flag: it derives the
mutation exclusively from the observation's `readiness_mode`, preventing the
builder and consumer from selecting different outcomes.

## Codex Task-Operation Identity And Replay

`app-operation begin` generates an opaque `operation_id` in `op-*` form; callers
never choose or replace one. That ID is the durable logical operation identity.
The returned positive `launch_count` identifies one authorized execution
generation: begin creates generation `1`, and every accepted replay increments
it. For `send-bootstrap`, begin also derives the stable `bootstrap_id` in
`bootstrap-*` form. The operation has no review-owner choice: AutoReview is
always worker-owned, while root remains an orchestrator and evidence verifier.
Every result authorizes only its reported generation.

`create-scope-repair-task` binds the assignment's current repair ID and contract
generation and returns the exact expected planner title
`🧭 Scope Repair · <Feature Spec title>`. `send-scope-revision` consumes the
verified scope-repair observation, stores the next generation, and derives a stable
`scope_revision_id` from the operation ID and target generation. Replays keep
all three identities unchanged.

An app-operation observation uses the named app-operation protocol and carries
exactly its `operation_id`, current `launch_count`, and
`status: unknown|succeeded|failed` plus permitted evidence. `finish` rejects a
response from an earlier generation even when its logical `operation_id`
matches. A succeeded observation requires both `receipt_ref` and independent
`readback_ref` plus the exact action-specific fields below:

The exact common fields are `schema`, `schema_version`, `operation_id`,
`launch_count`, and `status`; no observation may omit the launch generation.

| Action | Additional fields |
| --- | --- |
| `create-worker` | `thread_id`, `project_id`, `checkout_path`, `git_common_dir`, `observed_title`, `observed_state` |
| `create-scope-repair-task` | `thread_id`, `project_id`, `observed_state`, `observed_title` |
| `send-bootstrap` | `thread_id`, `bootstrap_id` |
| `send-scope-revision` | `thread_id`, `scope_revision_id`, `contract_generation` |
| `send-worker-message` | `thread_id` |
| `set-root-title` | `observed_title` |
| `archive-worker` | `thread_id`, `checkout_path`, `observed_state` |

Unknown or failed observations may carry only the authoritative action subset
actually observed. A bootstrap observation always identifies the derived
`bootstrap_id`; a scope-revision observation always identifies the derived
revision ID and contract generation. `failed` requires authoritative
`readback_ref`, while `unknown` may omit it until readback exists. Never invent
reconciliation references or classify an immediate tool error alone as proof
that an effect did not happen.

Finishing the same observation for the same launch generation again is
idempotent: it leaves the revision unchanged, reports `already_applied=true`,
and returns the same logically derived `replay_authorized` value that the
stored observation permits. The identical-evidence check uses the normalized
stored facts and does not depend on whether a previously verified
`checkout_path` or `git_common_dir` still exists. A different `launch_count` or
conflicting terminal evidence fails closed.

An `unknown` observation may be refined to another terminal status, but every
fact already recorded by that generation's unknown observation is carried
forward unchanged; the refinement may add facts and may not erase or replace
prior receipt, readback, identity, path, provider, Git, or observed-state
evidence.

`app-operation replay` always preserves the logical `operation_id`, increments
`launch_count`, returns `launch_authorized=true`, and permits one new
generation. Its action-specific gates are:

| Action | Replay gate |
| --- | --- |
| `send-bootstrap` | Prior generation is `unknown` or `failed` with `readback_ref`; the same `bootstrap_id` is preserved and worker deduplication contains ambiguity |
| `send-scope-revision` | Prior generation is `unknown` or `failed` with `readback_ref`; the same repair, revision ID, and target generation are preserved and worker deduplication contains ambiguity |
| `create-worker` | Prior generation is `failed` and `readback_ref` authoritatively proves no worker was created |
| `create-scope-repair-task` | Prior generation is `failed` and `readback_ref` authoritatively proves no planner task was created |
| `set-root-title` | Prior generation is `failed` and `readback_ref` authoritatively proves the title was not changed |
| `archive-worker` | Prior generation is `failed` and `readback_ref` authoritatively proves the worker was not archived or completed |
| `send-worker-message` | Never replayable |

Bootstrap and scope revision have exactly-once logical effect end to end: their
transport calls may be repeated while the worker accepts the stable logical
identity once by the rules in `worker-execution.md`. Other replayed operations depend on
authoritative proof that the preceding generation had no effect; they do not
claim downstream deduplication.

`set-root-title` has one logical `operation_id` for each run; an authorized
failed/no-effect replay is another launch generation of that same operation.
Its expected title is derived from the immutable assignment count:
`🤖 Implement Feature · 1 Spec` for one assignment and
`🤖 Implement Feature · N Specs` for two or more.

## Delivery-Ready Observation

Ready observations always bind assignment/thread/repository/checkout, named head
and base branches, head/base SHAs, clean worktree, base ancestry, current-head
validation and AutoReview SHAs, the first coherent review-candidate SHA, the
derived review profile, its conditional native Codex-review SHA, GitHub issue
readback, the GitHub default branch, canonical PR URL, provider observation ref,
and the exact prerequisite HEAD map. Status is always `pr-ready-for-merge`.

The exact common ready-observation fields are:
`schema`, `schema_version`, `assignment_id`, `thread_id`, `repository_identity`,
`readiness_mode`, `head_sha`, `head_branch_name`,
`base_branch_name`,
`base_sha`, `checkout_path`, `worktree_clean`, `base_is_ancestor`,
`validation_head_sha`, `autoreview_head_sha`, `review_candidate_head_sha`,
`review_profile`, `codex_review_head_sha`,
`tracker_readback_ref`, `prerequisite_heads`, and `status`. Every observation
also requires exactly `default_branch_name`, `pr_url`, and
`provider_observation_ref`. No other keys are accepted.

`review_profile` is exactly `standard` or `high-risk`, derived by AutoReview.
For `standard`, `codex_review_head_sha` must be JSON `null`. For `high-risk`,
it must equal `review_candidate_head_sha`, proving that AutoReview's one native
Codex review inspected the same initial candidate as its structured full pass.
After accepted fixes, `validation_head_sha` and `autoreview_head_sha` bind the
final `head_sha`; `review_candidate_head_sha` remains the immutable initial
candidate linked through AutoReview's evidence chain.

`readiness_mode` is exactly `terminal` or `peer-input`. `terminal` records the
GitHub PR terminal assignment state and releases its claim.
`peer-input` records `peer-input-ready`, retains the worker and claim, and is
valid only when another assignment depends on that assignment. The builder
validates the selected mode read-only; `assignment ready` reads it from the
payload, repeats its validation in the write transaction, and performs the
corresponding mutation without a caller-side mode flag.

## Claim Identity And Lifecycle

Canonical repository identity is `github:owner/repository`.

One assignment owns one claim. Its uniqueness key is canonical repository plus
canonical GitHub Feature Spec identity. GitHub `owner/repository#number` and the
exact issue URL normalize to one identity. A second uniqueness constraint
prevents active assignments from sharing one implementation head
branch in the same repository; the PR base branch is not part of that
constraint.

`run start` acquires free assignment claims independently. Waiting is tracked
per assignment, so a conflict never prevents sibling claims from starting.
Worker creation and bootstrap require an active run and that assignment's
active claim. A root owns only one unfinished run, and the coordinator imposes
no numeric live-worker limit.

`assignment ready` validates delivery-specific typed evidence and atomically
records normal Git facts. With `readiness_mode=terminal` it releases that
assignment's claim. With `readiness_mode=peer-input` it instead records the
current HEAD for dependent peers, retains the task and claim, and parks the
worker for later peer repair. Combined ready evidence must reproduce the current
exact prerequisite HEAD vector; drift fails closed. `assignment abort` releases
one claim only before bootstrap authority. A durable-contract block retains only
the affected claim. `run finish` completes aggregate run state after
assignment-level release; claim release never proves upstream merge or combined
behavior.

`assignment scope-block` retains the worker and claim, records
`blocked-scope-repair`, and creates one opaque repair ID at
`contract_generation=1`. GitHub planning proceeds through the separate
planner operation. A successful
`send-scope-revision` restores the exact pre-block state and atomically advances
to generation `2`; any later `scope-block` returns `full-replan-required`.
Overlap checks remain root-owned and are deliberately not stored as file
claims.

`assignment resume` is the same-root CAS transition for a recovered
`blocked-durable-contract` or `blocked-app-capability` assignment. It restores
the exact prior `active` or `peer-input-ready` state and requires the retained
claim plus a strict assignment-resume observation. That closed payload binds
`run_id`, `assignment_id`, the exact current `run_revision`, the current
`blocked_state`, the matching `recovered_state`, and `readback_ref`. Durable
contract recovery requires `blocked-durable-contract` plus
`durable-contract-restored`; capability recovery requires
`blocked-app-capability` plus `app-capability-restored`. A stale, unrelated, or
cross-reason observation fails before transition. The authoritative durable
source or Codex capability/task readback remains opaque data in
`readback_ref`, which the transition stores on the retained claim. Entering
either blocked state clears any older recovery ref. A `blocked-by-active-spec`
assignment may run `run wait-sweep` again;
`abandoned-recovery-required` may repeat `claim reconcile` with newer
authoritative evidence.

## Recovery Observation

`claim reconcile` accepts exactly:

```json
{
  "schema": "implement-feature/recovery-observation",
  "schema_version": "3.0.0",
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

The same named recovery protocol is used by `assignment recover`; the owner
fields then name that exact run, assignment, and expected revision. Pending or
unknown app operations still fail recovery closed. Pending or unknown bootstrap
delivery also forbids worker archive until independent task inspection provides
the typed observation required by the operation lifecycle above.

## CLI Maintenance

Keep normal execution on `scripts/run-state`; there is no maintenance project
or build output. `CLI_VERSION` remains `7.0.1`,
`RUNTIME_CONTRACT_VERSION` remains `8.0.0`;
`DATABASE_SCHEMA_VERSION` is integer `7`; each protocol entry remains at
the independently named identity declared above. Re-run `--help`, `--version`,
read-only `capabilities`, `doctor`, and `feature-spec-set validate`, plus Python
compilation and the remaining executable verifier checks after changes.

Version each domain for its own contract:

- bump the CLI patch for a compatible executable fix, minor for a compatible
  command/capability addition, and major for a breaking command surface;
- bump the runtime-contract patch or minor only for semantics that remain
  compatible with active runs, and major for incompatible coordination or
  replay semantics;
- bump one JSON protocol independently, with a major bump for any incompatible
  exact-key/type/enum change;
- increment the database schema integer for any SQLite shape change, regardless
  of which SemVer identity also changes.

Because runs pin the exact CLI version and artifact digest, even a compatible
new executable does not take over mutation of an already active run. Keep the
exact shipped artifact available until its pinned runs are terminal; this is
runtime identity pinning, not database-schema compatibility.

## Hard-Cut Operations

Changing `DATABASE_SCHEMA_VERSION` or changing SQLite shape requires explicit
user consent before code or documentation edits. Every approved change is a
breaking hard cut. Never add
`ALTER` upgrades, data-copy migrations, imports, versioned DB filenames, or
state carry-forward.

At runtime, call read-only `capabilities` and `doctor` first and then
`state prepare`. The shipped runtime accepts only schema 7. An empty database
is initialized with the exact current tables, columns, indexes, constraints,
and singleton metadata row. An existing database must already match that exact
shape; any other schema number, historical shape, unversioned table set,
corruption, unsafe permission, symlink, or same-number structural drift fails
closed without migration, reset, deletion, or row carry-forward. There is no
legacy schema registry, target-schema fence, retained-runtime cutover, or
automatic recovery path for an older database.
