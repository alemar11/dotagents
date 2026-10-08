# Explore State Contract

Explore owns transient interview and outcome state. It persists no checkpoint
or ledger. Helper identities, activity, results, and failures are external
execution facts; use the host's observations without inventing a parallel
worker-slot state machine.

## Grilling Session

| State | Meaning | Next step |
| --- | --- | --- |
| `not-started` | Context preparation or initial direct exploration is in progress. | Assess whether user decisions need clarification, or report a blocking dependency. |
| `not-needed` | The request and existing conversation settle intent and scope; no material user decision remains. | Investigate remaining factual questions or synthesize sufficient evidence without user confirmation. |
| `awaiting-answer` | A material question needs the user's answer. | Continue the interview after the answer; do not create research helpers yet. |
| `refined` | The scope is confirmed. | Investigate remaining questions or synthesize sufficient evidence. |
| `user-stopped` | The user ended the interview before confirmation. | Proceed from the best-supported scope, preserving unconfirmed items. |
| `blocked` | The interview cannot proceed responsibly. | Report overall `failed`. |

Preparation precedes `not-started` to `not-needed`, `awaiting-answer`, `refined`,
or `blocked`. Use `not-needed` only after assessing the request against initial
evidence; it records that no interview occurred, not a user-confirmed brief.
Each answer may lead to another `awaiting-answer`, `refined`, `user-stopped`, or
`blocked`. Do not invent questions when existing evidence and user direction
already settle scope. Research delegation begins only after `not-needed`,
`refined`, or `user-stopped`. If later evidence exposes a material user decision,
stop dependent investigation and transition to `awaiting-answer`; preserve
independent work already in flight and create no new helpers during the
interview. A missing required Learn dependency leaves the interview
`not-started` and the overall outcome `failed`. Missing Grilling Session causes
`blocked` only when an interview is required; it does not affect `not-needed`.

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
