# Codex App Orchestration Ledger

## Resolution

Use one ledger per overlapping repository/source portfolio under
`~/.cache/dotagents/skills/codex-orchestrator/ledgers/`. Resolve it before
implementation, task creation, managed-worktree creation, or source mutation.
Validate the required headings, option rows, source fingerprints, active-root
claim, and current task evidence. Invalid current ledgers block; missing
ledgers load `ledger-template.md` and create a fresh projection.

## Required Structure

- Scope
- Option Resolution
- Discovery Sources
- Active Root
- Codex Review Wait Registry
- Feature Spec Task Registry
- Parent Closeout Handoff
- Recovery Packet
- Gate Policy
- Workstreams with active, needs-owner, ready-next, blocked, deferred,
  completed, and released states
- Wave Reports
- Runtime Metrics
- Notes

## Active Root Claim

The Markdown section is a projection, not the concurrency primitive. Use
`scripts/orchestrator-claim`, which serializes overlap checks and writes under
one filesystem `flock` in
`~/.cache/dotagents/skills/codex-orchestrator/claims/`. Canonicalize every
repository realpath and source id, then atomically acquire before creating this
ledger, a Goal, task, managed worktree, or any other runtime artifact.

A claim records root id, Git-common-directory repository identities, checkout
evidence, source set, ledger ref, fingerprint, opened and heartbeat timestamps,
and takeover evidence. Linked worktrees of the same Git repository therefore
overlap even when their checkout paths differ. All App runs share this
namespace. Persist the helper-returned fingerprint and claim ref in this
projection; never infer ownership by reading the Markdown row alone.

An overlapping live claim blocks as `needs-owner`. Takeover requires stale
heartbeat evidence plus
`existing_orchestrator_session_takeover_policy=takeover-authorized`. Never infer
takeover from an inaccessible task or old timestamp alone. `claim takeover`
requires the exact conflicting root ids and fails atomically if the live
conflict set differs. It also requires `--takeover-policy takeover-authorized`,
the `verified-stale` reason, and the current fingerprint and heartbeat for every
expected claim. A takeover must satisfy the helper's fixed five-minute
heartbeat threshold. Terminal owners release their own claim; opaque terminal
evidence never authorizes replacement.

Every acquisition generates a fresh nonce, so its fingerprint is unique even
when a released root id later reacquires the same scope. Every heartbeat and
release includes that acquire-time expected fingerprint. Mutations use the
helper's ownership lease: it validates the same fingerprint while holding the
authoritative claim-store lock for the complete mutation, so takeover cannot
interleave after the check. `claim release` requires terminal or durable
handoff evidence and runs before the projection is marked released.

## Feature Spec Task Registry

Keep one row per implementation-eligible Feature Spec:

| feature_spec_ref | feature_spec_title | task_ref | task_evidence_ref | workstream_ids | repository_refs | pull_request_refs | lifecycle_owner | state | last_observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Each row points to one visible App task, its assignment Goal, and its managed
checkout evidence. At most three rows may be nonterminal. One Feature Spec
consumes one slot across all repositories and internal subagents. A Spec has at
most one live task ref.

## Workstreams And Waves

Every workstream records source/spec refs, repository and allowed paths,
dependencies, actions, delivery target and permission, issue authority, task
registry ref, evidence, gates, lifecycle state, and next action.

Every wave records selected Specs, dependency proof, slot count, task refs,
capability evidence, changes, validation, delivery evidence, reconciliation,
and recovery update. Task reports are evidence; only the root changes ledger
lifecycle or source status.

## Recovery Packet

The packet is a compact derived projection: option fingerprint, repository
HEAD/status fingerprints, active task rows, due gates/checks, next action, and
evidence refs. On resume, validate every fingerprint and task ref before
mutation. Any mismatch invalidates the packet and triggers full reconciliation.

## Closeout

Before final status, reconcile sources, task registry, gates, reviews, CI, and
due checks. Require no active task, ready-next action, unresolved authorized
work, or unverified source mutation. Release the active-root claim only after
terminal evidence or an explicit durable handoff is recorded.
