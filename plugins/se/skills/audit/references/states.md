# Audit States

This reference is the human-readable state registry for `se:audit`. It keeps
the Audit workflow separate from observed session state, coverage, graph
conformance, and finding lifecycle. The registry in `SKILL.md` remains the
structural source of truth for transitions.

## Workflow nodes

| node | kind | plain description |
| --- | --- | --- |
| `intake` | action | Freeze the explicit audit scope, stopping policy, and monitoring objective. |
| `capability-check` | validation | Establish which live sessions can be inventoried and read responsibly. |
| `discover` | action | Freeze the initial cohort of active candidate sessions and the coverage boundary. |
| `attribute` | validation | Retain only sessions with direct task-visible evidence of SE use. |
| `observe` | action | Read selected sessions and advance their evidence frontiers. |
| `assess` | validation | Compare observations with active skill contracts and classify evidence-backed findings. |
| `monitor-decision` | decision | Decide whether to continue monitoring or return a terminal report. |
| `refresh` | action | Perform one bounded wait or authoritative state refresh before observing again. |
| `reported` | terminal | Return a complete or explicitly partial read-only report. |
| `blocked` | terminal | Stop because no responsible audit result can be established from the available inventory, contract, or evidence. |

`reported` does not imply complete coverage. `blocked` describes the Audit
run's inability to produce a responsible report; it does not describe a
monitored session or an SE workflow being audited.

## Audit report and evidence states

All values in this table are transient report data. Audit persists none of
them.

| field or domain | allowed values | plain description |
| --- | --- | --- |
| monitoring objective | `active` | Remains active across bounded waits until the cohort is terminal or empty, or the user stops the audit. |
| coverage | `complete`, `partial` | `complete` requires an exhausted stable inventory across every available continuation and relevant host/project partition, deduplicated by stable session identity. Any capped, unstable, or untraversable boundary is `partial` with the omission boundary reported. |
| report completeness | `complete`, `partial` | States whether the terminal report is complete or intentionally partial, independently of entering `reported`. |
| contract baseline | `verified`, `contract-baseline-unverified` | States whether the selected session's exact loaded SE contract was established. The unverified value limits contract-derived conclusions. |
| graph conformance | `confirmed`, `compatible-unobserved`, `indeterminate`, `violated` | Classifies the evidence for one workflow node or transition. |
| finding status | `provisional`, `confirmed`, `resolved`, `withdrawn` | Tracks one finding from tentative evidence through confirmation or retirement. Finding `confirmed` is separate from graph-conformance `confirmed`. |
| finding priority | `P0`, `P1`, `P2`, `P3` | Orders findings from catastrophic or audit-blocking impact through clarity and polish. |
| finding category | `skill-bug`, `graph-violation`, `graph-design-improvement`, `runtime-limitation`, `repository-condition`, `user-choice` | Identifies the root-cause ownership of a finding. Feedback is reported separately and is not a finding category. |
| regression flag | `true`, `false` | Records whether a prior verified baseline proves that the behavior regressed. |

The terminal cohort, absence of attributable sessions, and an explicit user
stop are stopping conditions, not additional workflow nodes.

## Observed external session states

Audit records exact runtime labels and does not rename provider-owned state.

| observed state | Audit interpretation |
| --- | --- |
| `active` or `inProgress` | The selected session is nonterminal, so monitoring continues. `inProgress` is preserved external syntax. |
| stalled | No progress is visible, but the selected session remains nonterminal. |
| waiting for input or input-waiting | The selected session is resumable and nonterminal. |
| `inactive` at discovery | Exclude the session from the initial cohort. This label alone is not proof of terminal completion. |
| terminal | Stop monitoring that session only when its authoritative runtime or active skill contract establishes terminality. |

## Persistence boundary

Live application state is authoritative and every Audit workflow, report,
finding, coverage, and evidence state is transient. `se:audit` owns no operation
mode, persisted runtime checkpoint, checkpoint status, resume ledger, report
file, or durable audit artifact.
