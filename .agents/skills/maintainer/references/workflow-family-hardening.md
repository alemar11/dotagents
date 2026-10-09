# Workflow Family Hardening

Use this playbook when routine maintenance finds a cross-skill contract
inconsistency, representative executions expose a connected workflow defect,
or the user explicitly requests workflow hardening.

## Evidence Boundary

- Use local repository checks and supplied runtime evidence when portfolio or
  session evidence is required. A reproducible test failure, supplied log, or observed live failure may be
  sufficient for its own claim. All evidence gathering remains read-only;
  Maintainer applies concrete repairs within routine maintenance or an explicit
  repair request. Findings from a review-only run remain proposals. Structural
  decisions and unresolved changes to intended behavior require specific
  authority; continue independent repairs.
- Start with current repo state and cheap history, then memory summaries. Inspect
  at least one representative raw session before claiming runtime misuse,
  missed invocation, incorrect routing, or excessive cost.
- Treat a user correction, failed gate, repeated workaround, or live-state
  mismatch as evidence. Do not convert a one-off operator mistake into doctrine
  unless the contract made the mistake likely or recurrence is demonstrated.

## Workflow

1. Name the connected workflow and the concrete failed or wasteful outcome.
2. Build a compact ownership matrix:

   | Surface | Required owner |
   | --- | --- |
   | Input/source of truth | package or tracker that owns acceptance |
   | Decision/authority | skill or user contract allowed to decide |
   | Mutation | skill or tool allowed to write |
   | Handoff | producer fields and consumer obligations |
   | Validation | proof owner and required gates |
   | Closeout | lifecycle owner and terminal evidence |

3. Compare intended ownership across the contracts and any representative trace.
   Classify each finding as `contract defect`, `missing regression`, `tool/runtime drift`,
   `efficiency defect`, or `operator-only`.
4. Choose the smallest connected target set. Keep unrelated packages out even
   when they appear in the same session.
5. If the fix changes public package identity, removes/merges a package, or
   substantially redistributes responsibility, propose it unless specifically
   authorized. For an authorized reshape, use `$skill-creator` or
   `$plugin-creator` first, then targeted maintenance in
   [skill-upgrade.md](skill-upgrade.md).
6. Update the owning contracts. Use affected behavioral regression tests for
   executable changes; validate prose contracts statically and add a bounded
   scenario only when static inspection leaves a meaningful uncertainty.
7. Select validation lanes from `validation-matrix.md`. Use bounded disposable
   repositories for high-risk composed workflows when static contracts cannot
   prove routing, mutation, recovery, or closeout behavior.

## Runtime Efficiency

- Separate startup inventory cost, invoked instruction/reference cost, tool
  output, and whole-run cost.
- Capture full state once, then carry paths/refs, fingerprints, changed
  sections, focused hunks, proof results, and failed-gate excerpts.
- Report exact phase deltas only for uncontaminated counters. For interleaved or
  unavailable counters, label the interval or report `unavailable`; never
  estimate a completion metric.
- Efficiency changes must not weaken authority, safety, validation, or closeout.

## Branch Report Additions

Add the evidence used, ownership matrix, accepted findings, contract and
regression changes, and deferred findings to the common final report owned by
`release-checklist.md`.
