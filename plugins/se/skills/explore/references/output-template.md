# Explore Analysis Report

Return the report in the current task or session. Keep detail proportionate
to the investigation; combine related findings where useful. Include the
subagent ledger only when workers were planned.

## Scope

- **Objective and agreed scope:** Summarize the question, constraints, decisions,
  evidence expectations, and unconfirmed items after exploration and Grilling Session. Do not
  reproduce the interview transcript or construct a transfer handoff.
- **Grilling Session outcome:** `<not-started/refined/user-stopped/blocked>`
- **Worker plan:** Original requested count, planned count after the cap,
  created count, and reason for the selected count. State when no workers were
  planned. If capped, record the original request and pre-creation disclosure.
- **Overall outcome:** `<completed/partial/failed>`
- **Changes made:** None

## Executive summary

Summarize the answer and most important conclusion in a few sentences.

## Observations

Record directly observed repository paths, documents, sources, runtime facts,
and worker results.

## Inferences

Record conclusions derived from observations and explain the reasoning.

## Unavailable evidence

State what the run could not verify. Never turn missing evidence into a success
claim.

## Inspected paths

- `<absolute path or repository-relative path>`

## Research sources

- `<source or "No external sources used">`

## Work breakdown or recommended direction

| Area | Recommendation | Dependencies | Confidence |
| --- | --- | --- | --- |
|  |  |  |  |

Describe proposed next steps without writing or editing implementation code.

## Subagent slot ledger

Include every planned slot. When `planned_worker_count=0`, state that no slots
were reserved.

| Slot | Parent controller | Assignment | Slot state | Stable subagent identity | Parent lineage and creation evidence or error | Working-directory context | Requested profile | Profile evidence | Execution state | State reason | Terminal evidence | Key result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Worker N |  |  |  |  |  |  | `<requested model / reasoning from the selected role or explicit override>` |  |  |  |  |  |

List `not-started`, `creation-failed`, `structural-verification-failed`,
`settings-drift`, and `unresolved-setup` slots even when no stable worker
identity exists. Never correlate an uncertain identity through title, label,
assignment text, or timing.

## Worker results

When workers were planned, summarize every completed, failed, unresolved, or
abandoned slot and explain
its effect on the synthesis.

## Risks and open questions

- **Risk or question:** impact, evidence, and suggested resolution.

## Assumptions

- **Assumption:** basis and effect on the result.

## Confidence

State overall confidence and what evidence would raise it.

## Next action

State the smallest useful follow-up. If implementation is requested, make
clear that it requires a separate coding workflow.
