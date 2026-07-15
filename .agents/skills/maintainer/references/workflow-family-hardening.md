# Workflow Family Hardening

Use this playbook when representative executions expose a recurring ownership,
authority, handoff, closeout, correctness, or runtime-efficiency defect across
connected skills or plugins.

## Evidence Boundary

- Use `$skill-audit` when portfolio or session evidence is required. A
  reproducible test failure, supplied log, or observed live failure may be
  sufficient for its own claim. All evidence gathering remains read-only;
  Maintainer owns edits only after the finding is accepted for implementation.
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

3. Compare intended ownership with the representative trace. Classify each
   finding as `contract defect`, `missing regression`, `tool/runtime drift`,
   `efficiency defect`, or `operator-only`.
4. Choose the smallest connected target set. Keep unrelated packages out even
   when they appear in the same session.
5. If the fix changes public package identity, removes/merges a package, or
   substantially redistributes responsibility, route through `$skill-creator`
   or `$plugin-creator` first, then use `package-lifecycle.md`.
6. Update the owning contracts and add regression proof that tests normalized
   behavior rather than wording alone.
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
