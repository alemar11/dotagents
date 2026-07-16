# Shared Orchestration Ledger

## Resolution

Use one ledger per overlapping repository/source portfolio under
`~/.cache/dotagents/skills/codex-orchestrator/ledgers/`. Resolve it before
implementation, execution creation, worktree creation, or source mutation.
Validate the required headings, option rows, source fingerprints, active-root
claim, and current adapter evidence. Invalid current ledgers block; missing
ledgers load `ledger-template.md` and create a fresh projection.

## Required Structure

- Scope
- Option Resolution
- Discovery Sources
- Active Root
- Codex Review Wait Registry
- Feature Spec Execution Registry
- Parent Closeout Watch
- Recovery Packet
- Gate Policy
- Workstreams with active, needs-owner, ready-next, blocked, deferred,
  completed, and released states
- Wave Reports
- Runtime Metrics
- Notes

## Active Root Claim

The Markdown section is a projection, not the concurrency primitive. Both
adapters must use the sibling `scripts/orchestrator-claim` artifact, which
serializes overlap checks and writes under one filesystem `flock` in
`~/.cache/dotagents/skills/codex-orchestrator/claims/`. Canonicalize every
repository realpath and source id, then atomically acquire before creating this
ledger, a Goal, run, task, worktree, or any other runtime artifact.

A claim records root id, execution adapter, Git-common-directory repository
identities, checkout evidence, source set, ledger ref, fingerprint, opened and
heartbeat timestamps, and takeover evidence. Linked worktrees of the same Git
repository therefore overlap even when their checkout paths differ. App and CLI
adapters share this namespace. Persist the helper-returned fingerprint and claim
ref in this projection; never infer ownership by reading the Markdown row alone.

An overlapping live claim blocks as `needs-owner`. Takeover requires stale
heartbeat evidence plus `existing_orchestrator_session_takeover_policy=takeover-authorized`.
Never infer takeover from an inaccessible worker or old timestamp alone.
`claim takeover` requires the exact conflicting root ids and fails atomically if
the live conflict set differs. It also requires
`--takeover-policy takeover-authorized`, the `verified-stale` reason, and the
current fingerprint and heartbeat for every expected claim. A
takeover must satisfy the helper's fixed five-minute threshold. Terminal owners
release their own claim; opaque terminal evidence never authorizes replacement.
Every acquisition generates a fresh nonce, so its fingerprint is unique even
when a released root id later reacquires the same scope. Every heartbeat and
release includes that acquire-time expected fingerprint.
Adapter mutations use the helper's ownership lease: it validates that same
fingerprint while holding the authoritative claim-store lock for the complete
mutation, so takeover cannot interleave after the check.
`claim release` also requires terminal or durable handoff evidence and runs
before the projection is marked released.

## Feature Spec Execution Registry

Keep one row per implementation-eligible Feature Spec:

| feature_spec_ref | feature_spec_title | execution_adapter | execution_ref | adapter_evidence_ref | workstream_ids | repository_refs | pull_request_refs | lifecycle_owner | state | last_observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

`execution_adapter` is derived as `codex-app-task` or `codex-cli-session` from
the invoked public skill. App rows point to
their task/Goal projection; CLI rows point to their run/spec manifest and
structured artifact directory. Shared lifecycle logic treats adapter evidence
as opaque until the selected adapter validates it.

At most three rows may be nonterminal. One Feature Spec consumes one slot
across all repositories and internal subagents. A Spec has at most one live
execution ref.

## Workstreams And Waves

Every workstream records source/spec refs, repository and allowed paths,
dependencies, actions, delivery target and permission, issue authority,
execution registry ref, evidence, gates, lifecycle state, and next action.

Every wave records selected Specs, dependency proof, slot count, adapter refs,
capability evidence, changes, validation, delivery evidence, reconciliation,
and recovery update. Worker reports are evidence; only the root changes shared
lifecycle or source status.

## Recovery Packet

The packet is a compact derived projection: option fingerprint, repository
HEAD/status fingerprints, active execution rows, due gates/checks, next action,
and evidence refs. On resume, validate every fingerprint and adapter ref before
mutation. Any mismatch invalidates the packet and triggers full reconciliation.

## Closeout

Before final status, reconcile sources, execution registry, gates, reviews, CI,
and due checks. Require no active execution, ready-next action, unresolved
authorized work, or unverified source mutation. Release the active-root claim
only after terminal evidence or an explicit durable handoff is recorded.
