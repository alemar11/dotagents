# Typed Next-Action Controller

After registration, run only:

```text
scripts/ledger-cache --json controller next --ledger <absolute-ledger> --root-id <root-id> --expected-claim-fingerprint <64hex>
```

The read-only result is bound to the live claim, ledger generation and state
fingerprint, task observation, delivery revision, and App-managed checkout.
Changed or released authority fails closed. Repeating against unchanged state
is byte-for-byte read-only.

## Exclusive Routing

The controller registry in `scripts/ledger-cache` is the sole canonical mapping
from action to `required_contracts`. The returned list is exhaustive and final.
Load exactly those paths; never add, remove, reorder, or conditionally select a
contract from prose. Every branch predicate—including recovery kind, owned
operation, reply/resolve eligibility, and closeout stage—is resolved from
validated typed state before the response is emitted.

Each writable action names exactly one phase packet contract sufficient for its
phase-specific inputs and evidence. The typed `packet_template` and helper
validator own the generic envelope, common binding arguments, CAS, and result
shape; Markdown packet contracts do not reproduce them.

Missing files, unexpected paths, duplicate contracts, stale content, excessive
contract counts/bytes, or a response that differs from the live registry fails
closed before action or mutation. Callers never choose a phase, contract set,
packet event, owner operation, or transition.

## Contract Loading And Cache

Key transient context reuse by exact absolute installation/worktree path plus
content SHA-256. Reuse only when that key is certainly still live in the
current prompt context. This is a prompt optimization, never caller authority,
ledger state, recovery evidence, or persisted truth.

Compaction, uncertain retention, recovery/takeover, changed bytes, or changed
path invalidates the transient cache. Reload only the current response's
complete set. A file change between response validation and action execution
is stale authority and fails closed. Never preload a later phase.

## Controller 2.0.0 Envelope

Every response has exactly `ok`, `command`, `controller_schema_version`,
`tool_version`, `ledger_schema_version`, `ledger`, `portfolio_key`, `root_id`,
`binding`, `decision`, `phase`, `target`, `action`, `action_owner`,
`packet_template`, `allowed_transitions`, `completion_criterion`, `blockers`,
`required_contracts`, and `projection_fingerprint`.

The controller never launches a task or model, mutates a provider, grants Goal
or worktree authority, or selects merge, enqueue, deploy, or post-merge work.
Its template is validated selection data, not launch authority.
The registered GitStack installation evidence is immutable controller context;
the controller never replaces it with source-checkout or caller-provided data.

Owned GitStack and AutoReview actions expose only their owner/operation identity,
immutable authority binding, generic evidence descriptors, accepted result,
and closed outcome-to-next-phase rows. Provider receipts, prose, transport,
model attempts, owner schemas, and result details remain owned by those tools.

## Started And Result Boundary

Preparation and owner validation are read-only. Immediately before a physical
mutation, waiter, or AutoReview launch, call `operation start`. The bridge
reruns the owner validator, requires exact live controller equality, revalidates
claim/CAS/task/revision/checkout authority, and atomically records one generic
started receipt. A second start returns `reconcile-required`; recovery reads the
original request and receipt and never relaunches or reposts.

`operation record-result` invokes the owner's request-correlated validator,
requires the exact start and current binding, and records the opaque owner
result plus normalized orchestration outcome. Identical replay is idempotent;
a different result fails closed. Terminal reconciliation appends a linked
superseding result and never rewrites history.

Unknown owners, operations, schemas, outcomes, mappings, or result bindings fail
closed. GitStack retains its exact 45-minute deadline and single waiter.
AutoReview retains one logical phase, one primary launch, at most one invalid-
output repair, and reconciliation without relaunch.
