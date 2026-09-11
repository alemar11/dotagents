# Explore State Contract

Explore owns transient interview and outcome state. It persists no checkpoint
or ledger. Helper identities, activity, results, and failures are external
execution facts; use the host's observations without inventing a parallel
worker-slot state machine.

## Grilling Session

| State | Meaning | Next step |
| --- | --- | --- |
| `not-started` | Context preparation or initial direct exploration is in progress. | Begin informed clarification, or report a blocking dependency. |
| `awaiting-answer` | A material question needs the user's answer. | Continue the interview after the answer; do not create research helpers yet. |
| `refined` | The scope is confirmed. | Investigate remaining questions or synthesize sufficient evidence. |
| `user-stopped` | The user ended the interview before confirmation. | Proceed from the best-supported scope, preserving unconfirmed items. |
| `blocked` | The interview cannot proceed responsibly. | Report overall `failed`. |

Preparation precedes `not-started` to `awaiting-answer`, `refined`, or `blocked`.
Each answer may lead to another `awaiting-answer`, `refined`, `user-stopped`, or
`blocked`. Do not invent questions when existing evidence and user direction
already settle scope. Research delegation begins only after `refined` or
`user-stopped`. A missing required Learn dependency leaves the interview
`not-started` and the overall outcome `failed`.

## Overall outcome

| Outcome | Meaning |
| --- | --- |
| `completed` | The agreed investigation is answered with sufficient evidence and any required independent inspection. |
| `partial` | A useful answer is available, but required evidence or independence remains missing. |
| `failed` | No usable synthesis is possible or a required intake dependency is blocked. |

Select an outcome after resolving launched helpers through completion, failure,
or supported cancellation and evaluating their evidence. Optional helper failure
alone does not imply `partial` when local recovery establishes the required
answer. Missing results never count as evidence. An outstanding interview answer
or active helper is ongoing work, not a terminal outcome. Resume from the
conversation and current evidence when a previously missing input arrives.
