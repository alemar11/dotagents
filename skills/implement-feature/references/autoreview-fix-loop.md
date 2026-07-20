# AutoReview Fix Loop

AutoReview authority begins only after atomic baseline acceptance and root Goal
activation. Create a scoped local commit with no pending Git-visible changes,
then record the exact committed target and revision.

AutoReview 3.0.0 owns the closed `run-phase` and `reconcile-attempt` operations,
managed controller envelope validation, protocol/evidence 2.0.0, attempt journal
2.1.0, phase packet, prompt/model attempt, evidence, and bounded invalid-output
repair. Implement Feature owns phase/disposition/gate mapping but does not copy
AutoReview request, result, evidence, or attempt field registries.

Run `ledger-cache controller next`. For `execute-autoreview-phase`, AutoReview
prepares a request from the selected phase and immutable target/prior evidence/
hosted obligation. Preparation and validation launch nothing. Immediately
before the phase, `operation start` must atomically issue the generic started
receipt after live claim/CAS/task/revision/checkout and exact controller
equality checks. A second start fails; a controller envelope alone is never
model authority.

One logical model phase has one primary launch plus only the existing bounded
invalid-output repair. The append-only attempt journal records `prepared`,
`model-started`, optional `repair-prepared` and `repair-model-started`, then
`completed` or `failed`. A disposition phase may complete with zero launches.
A second invalid output is consumed-failed. After any launch, interruption or
crash never launches again; `reconcile-attempt` binds the exact original
request, started receipt, attempt id, complete journal, launch count, target,
revision, phase, evidence parent/lineage, and hosted obligation. A recovered
completed attempt returns its exact terminal evidence.

`operation record-result` calls AutoReview's `validate_result_for_request` and
appends one opaque owner result plus normalized orchestration state. The same
result is idempotent; a different terminal result for the same start fails
closed. Terminal clean/composite-clean advances the current-revision AutoReview
gate, `verification-clean` selects the next owner phase, findings select review
fix, interruption stays in reconciliation, and consumed failure requires owner
attention.

Follow AutoReview's evidence-chain contract. Fix verification requires a new
committed head. After first-full fixes reach `verification-clean`, run the only
`terminal-full`. Later accepted findings close through delta evidence as
`terminal-composite-clean`. Never run a third full. If every finding is
rejected, use the no-model `disposition` phase on the unchanged head.

Hosted findings remain one typed obligation bound to exact GitStack request,
provider evidence, accepted finding set, prior evidence tip, source revision,
repository, and PR. AutoReview alone validates consumption. Merge-base-only
change preserves lineage only for the same canonical patch and scope; semantic
target drift still requires explicit owner-authorized lineage reset.

No AutoReview operation grants provider mutation, merge, enqueue, deploy,
Goal, task, or worktree authority.
