# AutoReview Fix Loop

AutoReview authority begins only after atomic implementation baseline
acceptance and root Goal activation. Baseline-only workers may not reserve an
action, prepare an attempt, or make a model call.

Load before the first AutoReview reservation and again after AutoReview or a
hosted Codex review returns an accepted finding.

Create a clean scoped local commit before push. Record
`committed-revision-observed` with a stable `review_target_key` for
repository/base/review scope and a `committed_revision_key` for exact head plus
canonical reviewed patch. PR identity is separate publication fact: pushing
the same commit attaches the PR to the existing lineage and never triggers a
second review.

Run `ledger-cache autoreview next`; it alone returns the next action, managed
packet, allowed transitions, completion criterion, blockers, current state
fingerprint, and reservation event. Apply that event atomically before launch.
Workers never choose mode, phase, parent, prompt, or local fallback. AutoReview
also scans active schema-11 ledgers, so omitting managed flags cannot escape the
reservation requirement.

Reservations are generation/state-fingerprint bound, one-use, and have no TTL.
Release is allowed only before model launch. Attempts append `prepared`, then
`model-started` only after successful `Popen`, then `completed` or `failed`.
Once model-started is durable, relaunch is forbidden. Invalid output consumes
the attempt as failed. A valid candidate is quarantined with an immutable
operation file; the producer runs the real ledger apply path in dry-run mode
before handoff. Interrupted apply reuses the exact candidate bytes and stable
operation id.

Follow AutoReview's `references/evidence-chain.md` on the committed branch.
Create finding drafts without ids and run AutoReview's `findings prepare`
operation; it alone validates authoritative finding fields and generates the
canonical ids. Prepare each supported AutoReview invocation as an
`execution-manifest` command, then run and verify its receipt before recording
evidence.
The manifest's fixed 60-minute outer deadline supervises the AutoReview and
nested Codex process group only. AutoReview v2 remains the semantic model-attempt
authority. On outer timeout, output limit, cancellation, interruption, or
cleanup failure, reconcile the existing typed attempt. If `model-started` is
durable, never relaunch or reserve a replacement model call. Manifest liveness
does not alter that attempt or reset any provider-review deadline.
Batch accepted fixes, commit a substantive revision, run focused proof,
then use `fix-verification`; delta rounds have no numeric cap but each must
advance the head. After first-full fixes reach `verification-clean`, run the
only `terminal-full`. Later accepted findings, including terminal-full or PR
review findings, close through delta evidence as `terminal-composite-clean`.
Never run a third full in one lineage; no revision progress becomes
`needs-owner`. Record every helper result through `autoreview-observed` using
the strict packet registry.
If every open finding is rejected, use AutoReview's no-Codex `disposition`
phase on the unchanged head instead of inventing a fix revision.

Hosted findings first create one typed obligation bound to the exact GitStack
request receipt, observation, provider evidence, accepted finding-set artifact,
prior evidence tip, source committed revision, repository, and PR. Inline
findings retain their real comment ids; summary-only findings use an empty id
list. The obligation is consumed exactly once by focused fix verification.
Repeated hosted finding cycles after `terminal-composite-clean` remain in the
same lineage.

A merge-base SHA change alone does not reset lineage. Preserve continuity only
when review scope and canonical reviewed patch fingerprint are equivalent.
Semantic target drift requires `autoreview-lineage-reset-authorized` with
explicit owner authority bound to the exact prior evidence fingerprint and
next target/revision keys, then one new initial full. Reparenting, aliases,
legacy adoption, migration, hand-authored fingerprints, deadline resets, and
extra full reviews are rejected.
