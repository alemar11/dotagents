# Study Analysis Report

## Scope

- **Mode:** Read-only planning, research, or analysis
- **Shared run tag:** `[<run-tag>]`
- **Requested orchestrator title:** `Study: [<run-tag>] <short title>`
- **Observed orchestrator title:** `<observed title or unavailable>`
- **Title creation/fallback receipt:** `<creation-time title observation and, if used, title-fallback receipt>`
- **Title evidence source:** `<authoritative observation/unavailable>`
- **Title status/warning:** `<title-verified/title-unverified/title-drift or not-applicable>`
- **Orchestrator stable identity:** `<stable task identity or unavailable>`
- **Host/project/execution:** `<host identity / project identity and path / local>`
- **Requested model/reasoning:** `gpt-5.6-sol / medium`
- **Orchestrator setup state:** `<not-started/ready/creation-failed/structural-verification-failed/settings-drift/settings-unavailable/unresolved-setup>`
- **Settings evidence source:** `<independent task telemetry or unavailable>`
- **Orchestrator task state:** `<authoritatively observed external state or not-applicable>`
- **Orchestrator state reason:** `<reason>`
- **Grilling outcome:** `<not-started/refined/user-stopped/blocked>`
- **Grilling question count:** `<count>`
- **Original requested worker count:** `<count or unspecified>`
- **Planned worker count after cap:** `<0-5>`
- **Created worker count:** `<0-5 stable task identities>`
- **Hard cap applied:** `<yes/no>`
- **Parent notified of cap:** `<yes/no/not-applicable>`
- **Full-capacity mode:** `<yes/no>`
- **Full-capacity source:** `<exact-request/capped-request/orchestrator-selected/not-applicable>`
- **Overall outcome:** `<completed/partial/failed>`
- **Worker archival requests:** `<accepted/partial/failed/unavailable/not-applicable>`
- **Independent archival verification:** `<confirmed/unavailable/failed/not-applicable>`
- **Orchestrator remains unarchived:** `<yes/no>`
- **Changes made:** None — Study never writes code or project files

## Executive summary

Summarize the answer and the most important conclusion in a few sentences.

## Objective

State the question, planning goal, or research target that Study analyzed.

## Refined handoff

Summarize the user-confirmed objective, scope, non-goals, constraints,
decisions, success criteria, evidence expectations, and any unconfirmed items
carried forward after Grilling. Do not reproduce the raw interview transcript.

## Observations

Record directly observed repository paths, documents, external sources, App
task facts, and tool results.

## Inferences

Record conclusions derived from the observations and explain the reasoning.

## Unavailable evidence

State what the run could not verify. Never turn missing telemetry into a
success claim.

## Inspected paths

- `<absolute path or repository-relative path>`

## Research sources

- `<source or "No external sources used">`

## Work breakdown or recommended direction

| Area | Recommendation | Dependencies | Confidence |
| --- | --- | --- | --- |
|  |  |  |  |

Describe the proposed next steps without writing or editing implementation
code.

## Worker slot ledger

| Slot | Assignment | Slot state | Provisional identity | Stable task identity | Creation receipt or error | State reason |
| --- | --- | --- | --- | --- | --- | --- |
| Worker N |  |  |  |  |  |  |

List all planned slots, including `not-started`, `creation-failed`,
`structural-verification-failed`, `settings-drift`, and `unresolved-setup`
slots. Never correlate an unresolved provisional identity by title or preview.

## Task telemetry ledger

| Task | Requested title | Title creation/fallback receipt | Observed title and source | Title status/warning | Stable identity | Host | Project/execution | Requested profile | Settings evidence source | State | State reason/attention evidence | Progress position | Inspection position | Revision/event identity | Error | Terminal evidence source | Archive request receipt | Archive verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Orchestrator |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | not-requested | not-applicable |
| Worker N |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

For terminal evidence, cite the final memo message/turn ID or the structured
state/error/last-message evidence that substitutes for a missing memo.

## Milestone log

| Order | Sender | Recipient | Milestone | Counts or state | Message/event ID | Delivery evidence |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Worker results

| Worker | Stable task identity | Terminal state | Key result |
| --- | --- | --- | --- |
|  |  |  |  |

## Risks and open questions

- **Risk or question:** impact, evidence, and suggested resolution.

## Assumptions

- **Assumption:** basis and effect on the result.

## Confidence

State the overall confidence and what would raise it.

## Next action

State the smallest useful follow-up. If implementation is requested, make
clear that a separate coding workflow is required.
