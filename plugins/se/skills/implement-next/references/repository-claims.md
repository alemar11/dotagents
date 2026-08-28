# Repository Claims

The repository-claims registry prevents two Implement Next orchestrators on
the same host from owning overlapping repositories. It does nothing else.

## Identity and scope

Use the GitHub repository database ID in the canonical
`github:<decimal-database-id>` form. The provider key is fixed, and the decimal
ID uses its canonical positive-integer spelling without leading zeroes. Do not
use a GraphQL node ID, another provider spelling, an owner/name display path,
URL, checkout path, project title, or task title as repository identity. One
provider field and serialization prevents aliases for the same repository.

Choose one cryptographically fresh 32-character lowercase hexadecimal
`claim_token` for the complete selected repository set. The token is the
provisional owner's fencing capability: keep it out of logs and ordinary
diagnostics, and pass it only in the initial orchestrator handoff. No command
receipt, inspection, or error discloses it; the acquiring role retains the
value it generated. The repository set is immutable for that orchestrator. A
smaller selection may reuse an existing claim, but no run may add repositories
to its token. To implement a larger graph, hand off or abandon the old run,
release its complete claim, and start a new orchestrator for the newly frozen
set.

The registry stores exactly repository key, claim token, visible-home key,
optional orchestrator task identity, and diagnostic claim time. Use the stable
saved-project identity as `home_project_key`. Use the canonical lower-kebab
sentinel `projectless` only for the warned fallback where no suitable visible
project exists.

Claims are host-local. They do not coordinate another machine and have no TTL,
heartbeat, automatic expiry, or automatic stale-owner recovery.

## CLI

The shipped `scripts/repository-claims` CLI uses this default database:

`~/.cache/dotagents/plugins/se/skills/implement-next/repository-claims.sqlite3`

Its relevant operations are:

- `doctor`: verify an existing registry without creating one;
- `acquire`: atomically reserve the full repository set provisionally;
- `bind`: attach the observed orchestrator task identity to the full claim;
- `inspect`: read redacted claims or select by repository key;
- `release`: remove one complete bound claim or abandon a provisional claim
  from its original fenced acquisition context.

Use `--help`, command help, and JSON output rather than inferring arguments.
The CLI owns schema, transaction, permission, and error details. `acquire`,
`bind`, and `release` read the exact fencing token from protected standard input;
never place it in process arguments, environment variables, command text, or a
shared file. `inspect` filters by repository key and never accepts or returns a
token.

## Acquisition and task creation

1. Freeze the full repository set and visible home before acquisition.
2. Acquire all keys in one operation. Never loop over repositories.
3. On `acquired`, create exactly one orchestrator. Put the opaque claim token,
   frozen repository keys, selected Feature references, and visible home key
   in its initial handoff together with an explicit binding barrier. The task
   may observe its own stable identity but must not create workers or perform
   Git, GitHub, or other role-owned effects yet. Bind only after independently
   observing the handoff correlation and stable task identity. Read back the
   complete bound claim, then release the same task from the barrier with that
   matching confirmation.
4. On `reuse-bound`, inspect and resume the identified orchestrator only after
   confirming that the complete claim still names that stable task identity.
5. On `reconcile-provisional`, the original acquiring invocation still holds
   the fencing token. Determine from visible task history whether creation
   occurred. Bind the matching task if proved. It may abandon provisionally
   only when task creation was never attempted or an attempted creation is
   authoritatively terminal as not applied. A point-in-time absence of a
   visible task is not sufficient proof. When one creation attempt is proved
   not applied, keep the provisional claim and use the registered
   `claim-repositories -> claim-repositories` edge for at most one new task
   creation attempt. A second non-application blocks rather than looping.
6. On overlap, mixed ownership, or a foreign claim, do not create another
   orchestrator. Route the request to the existing owner when one claim covers
   the selection; otherwise report the ownership conflict.

Another invocation never releases a provisional claim that it merely observes,
even when no task is currently visible. Never retry task creation merely
because its immediate receipt, title, project grouping, or current activity is
unclear.

## Release and recovery

Release is always for the exact complete token group. A bound release requires
the matching orchestrator task identity. `--abandon-provisional` requires the
original fencing token and asserts that task creation was never attempted or
that its exact attempted effect is authoritatively terminal as not applied.
Queued, active, interrupted, or ambiguous creation cannot be abandoned. Lost
provisional fencing context fails closed for manual inspection; it never
becomes an inferred release. There is no partial release, force release, token
expansion, repair command, or automatic takeover.

For a stale bound owner, first inspect the recorded task and current Git and
GitHub state. Reuse the task when safe. Before any bound release, independently
observe the orchestrator and every worker it created as stopped and unable to
perform further repository or hosted effects. Queued, active, interrupted, or
unknown actors retain the claim. If the user explicitly abandons or hands off a
quiescent run, release using its exact binding and report that the registry no
longer protects the old orchestrator. Corruption blocks mutation; preserve the
database for manual inspection rather than guessing a repair.

The registry may remain claimed while work is blocked because that
orchestrator is still the single resumable owner. This is intentional
serialization, not execution progress.
