# Repository Claims

The repository-claims registry prevents two Implement orchestrators on
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
diagnostics. The acquiring role retains the value it generated. Pass it only
in the initial handoff when a separate orchestrator must be created; an
invoking task that becomes the orchestrator retains it without projecting it
into a prompt, record, or diagnostic. No command receipt, inspection, or error
discloses it. The repository set is immutable for that orchestrator. A smaller
selection may reuse an existing claim, but no run may add repositories to its
token. To implement a larger graph, hand off or abandon the old run, release
its complete claim, and start a new orchestrator for the newly frozen set.

The registry stores exactly repository key, claim token, visible-home key,
optional orchestrator task identity, and diagnostic claim time. Use the stable
saved-project identity as `home_project_key`. Use the canonical lower-kebab
sentinel `projectless` only for the warned fallback where no suitable visible
project exists.

Claims are host-local. They do not coordinate another machine and have no TTL,
heartbeat, automatic expiry, or automatic stale-owner recovery.

## CLI

The shipped `scripts/repository-claims` CLI uses this default database:

`~/.cache/dotagents/plugins/se/skills/implement/repository-claims.sqlite3`

Its relevant operations are:

- `doctor`: verify an existing registry without creating one;
- `acquire`: atomically reserve the full repository set provisionally;
- `bind`: attach the observed orchestrator task identity to the full claim;
- `inspect`: read redacted claims or select by repository key;
- `release`: remove one complete bound claim or abandon a provisional claim
  from its original fenced acquisition context.

Use `--help`, command help, and JSON output rather than inferring arguments.
In JSON mode, every argument-parser or runtime failure returns one structured
error envelope with exit code `2`, writes no stderr, and creates no registry for
an invalid request. Help and version remain ordinary successful output.
The CLI owns schema, transaction, permission, and error details. `acquire`,
`bind`, and `release` read the exact fencing token from protected standard input;
never place it in process arguments, environment variables, command text, or a
shared file. `inspect` filters by repository key and never accepts or returns a
token.

## Acquisition and task creation

1. Freeze the full repository set and visible home before acquisition.
2. Acquire all keys in one operation. Never loop over repositories.
3. On `acquired`, use the invoking task as the orchestrator only when it is
   already visible in the intended home and its stable identity and exact
   Feature-selection correlation are independently observed. Bind that exact
   identity, read back the complete claim, and only then permit workers, Git,
   GitHub, or other role-owned effects. The task retains the fencing token in
   its acquiring context; it does not send itself a token-bearing handoff.
4. When the invoking task cannot satisfy that reuse path, create exactly one
   separate orchestrator. Put the opaque claim token, frozen repository keys,
   selected Feature references, and visible home key in its initial handoff
   together with an explicit binding barrier. The task may observe its own
   stable identity but must not create workers or perform Git, GitHub, or other
   role-owned effects yet. Bind only after independently observing the handoff
   correlation and stable task identity. Read back the complete bound claim,
   then release the same task from the barrier with that matching confirmation.
5. On `reuse-bound`, inspect and resume the identified orchestrator only after
   confirming that the complete claim still names that stable task identity.
6. On `reconcile-provisional`, the original acquiring invocation still holds
   the fencing token. Determine from visible task history whether creation
   occurred. Bind the matching task if proved. It may abandon provisionally
   only when task creation was never attempted or an attempted creation is
   authoritatively terminal as not applied. A point-in-time absence of a
   visible task is not sufficient proof. When one creation attempt is proved
   not applied, keep the provisional claim and use the registered
   `claim-repositories -> claim-repositories` edge for at most one new task
   creation attempt. A second non-application blocks rather than looping.
7. On overlap, mixed ownership, or a foreign claim, do not create another
   orchestrator. Route the request to the existing owner when one claim covers
   the selection; otherwise report the ownership conflict.

Another invocation never releases a provisional claim that it merely observes,
even when no task is currently visible. Never retry task creation merely
because its immediate receipt, title, project grouping, or current activity is
unclear.

## Release and recovery

Release is always for the exact complete token group. A bound release requires
the matching orchestrator task identity and is permitted only as that
orchestrator's final external effect after successful delivery, or after an
explicitly authorized handoff or abandonment. Preserve the final outcome
evidence across release and inspect every selected repository as unclaimed
before reporting completion. A failed or ambiguous release or readback blocks;
it never becomes inferred success.

`--abandon-provisional` requires the original fencing token and asserts that
task creation was never attempted or that its exact attempted effect is
authoritatively terminal as not applied. Queued, active, interrupted, or
ambiguous creation cannot be abandoned. Lost provisional fencing context fails
closed for manual inspection. There is no partial release, force release, token
expansion, repair command, or automatic takeover.

For successful delivery, first prove every worker and candidate reviewer
stopped and every Git, GitHub, review, and CI mutation terminal. The bound
orchestrator may remain active only to perform and verify its final release; it
must perform no later external effect. For release by another invocation during
handoff or abandonment, independently observe the old orchestrator and every
task it created as stopped and unable to perform further repository or hosted
effects.

For a stale bound owner, first inspect the recorded task and current Git and
GitHub state. Reuse the task when safe. Queued, active, interrupted, or unknown
actors retain the claim. Corruption blocks mutation; preserve the database for
manual inspection rather than guessing a repair.

The registry remains claimed while delivery is blocked or deferred because
that orchestrator is still the single resumable owner. A successfully delivered
run never retains ownership after verified completion. Claim retention is
serialization, not execution progress.
