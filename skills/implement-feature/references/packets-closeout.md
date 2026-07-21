# Terminal Closeout Event Contract

Load only for task seal, terminal handoff, portfolio verification, root Goal
completion, or post-terminal drift. `ledger-cache` owns the generic envelope,
common bindings, CAS, canonical encoding, and typed template. This file owns
terminal event inputs and evidence.

| event | phase-specific inputs and evidence |
| --- | --- |
| `task-sealed` | Task, complete current revision-set key, derived seal fingerprint, and independent proof. |
| `handoff-recorded` | Task, unchanged seal, `pull-request-ready`, `external-merge-required`, exact evidence, and next external merge action. |
| `portfolio-verified` | Independent current portfolio verification fingerprint and evidence. |
| `portfolio-goal-completed` | Matching `goal_evidence_ref`, `completion_evidence_ref`, and unchanged `verification_fingerprint`. |
| `terminal-drift-recorded` | Affected task/delivery, seal, drift fingerprint, bounded reason, and evidence. |

Seal requires every current applicable gate. Handoff requires the unchanged
seal. Portfolio verification requires every handoff. Goal completion requires
unchanged portfolio verification: call root `update_goal` with
`status=complete`, require matching readback, then record its event.
Post-terminal drift is the only later
terminal mutation; it blocks subsequent closeout and never reopens a Goal.
