# Study Analysis Report

Include the common sections below, then exactly one surface-specific controller
section and exactly one matching worker ledger. Omit inapplicable App fields
from CLI reports rather than filling the report with placeholders.

## Scope

- **Mode:** Read-only planning, research, or analysis
- **Study surface:** `<app-task/cli-session>`
- **Worker transport:** `<app-task/subagent/none>`
- **Shared run tag:** `[<run-tag>]`
- **Controller location:** `<separate visible App Study task/current CLI session>`
- **Controller profile:** `<gpt-5.6-sol / medium/current CLI profile inherited or unavailable>`
- **Grilling outcome:** `<refined/user-stopped/blocked>`
- **Grilling question count:** `<count>`
- **Original requested worker count:** `<count or unspecified>`
- **Planned worker count after cap:** `<0-5>`
- **Created worker count:** `<0-5 stable identities>`
- **Hard cap applied:** `<yes/no>`
- **User notified of cap before creation:** `<yes/no/not-applicable>`
- **Full-capacity mode:** `<yes/no>`
- **Full-capacity source:** `<exact-request/capped-request/controller-selected/not-applicable>`
- **Overall outcome:** `<completed/partial/failed>`
- **Changes made:** None — Study never writes code or project files

## App controller and lifecycle

Include this section only for `study_surface=app-task`.

- **Requested controller title:** `Study: [<run-tag>] <short title>`
- **Observed controller title:** `<observed title or unavailable>`
- **Title request/fallback evidence:** `<evidence>`
- **App title state:** `<title-verified/title-unverified/title-drift/not-applicable>`
- **Stable controller task identity:** `<identity or unavailable>`
- **Host/project/execution:** `<host / saved project identity and path / direct local>`
- **Requested profile:** `gpt-5.6-sol / medium`
- **Controller setup state:** `<not-started/pending-setup/ready/creation-failed/structural-verification-failed/settings-drift/settings-unavailable/unresolved-setup>`
- **Profile evidence source:** `<authoritative observation or unavailable>`
- **Controller task state and reason:** `<observed state / reason>`
- **Parent monitoring outcome:** `<final report returned/blocker>`
- **Worker archival requests:** `<accepted/partial/failed/unavailable/not-applicable>`
- **Independent archival verification:** `<confirmed/unavailable/failed/not-applicable>`
- **Controller remains unarchived:** `<yes/no>`

## CLI controller

Include this section only for `study_surface=cli-session`.

- **Controller:** Current invoking CLI session
- **Working directory:** `<absolute current working directory>`
- **Model/reasoning handling:** Current session profile retained
- **Observed current profile:** `<model/reasoning or unavailable>`
- **Separate App Study task created:** No
- **Controller synthesis source:** `<direct analysis plus subagent results/direct analysis only>`

## Executive summary

Summarize the answer and most important conclusion in a few sentences.

## Objective

State the question, planning goal, or research target that Study analyzed.

## Refined handoff

Summarize the user-confirmed or best-supported objective, outcome, scope,
non-goals, constraints, decisions, terminology, success criteria, evidence
expectations, and any unconfirmed items carried forward after Grilling. Do not
reproduce the raw interview transcript.

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

## Worker slot ledger

Include every planned slot. When `planned_worker_count=0`, state that no slots
were reserved.

| Slot | Transport | Assignment | Slot state | Stable identity | Creation evidence or error | Requested profile | Profile evidence | Execution state | State reason | Terminal evidence | Key result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Worker N |  |  |  |  |  | `gpt-5.6-luna / max` |  |  |  |  |  |

List `not-started`, `creation-failed`, `structural-verification-failed`,
`settings-drift`, and `unresolved-setup` slots even when no stable worker
identity exists. Never correlate an uncertain identity through title, label,
assignment text, run tag, or timing.

## App task telemetry ledger

Include this section only for `study_surface=app-task`. Include the controller
and every stable App worker task.

| Task | Requested title | Observed title and source | App title state | Stable identity | Host | Project/execution | Requested profile | Profile evidence | Task state | State reason or attention evidence | Error | Terminal evidence | Archive request | Archive verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Controller |  |  |  |  |  |  | `gpt-5.6-sol / medium` |  |  |  |  |  | not-requested | not-applicable |
| Worker N |  |  |  |  |  |  | `gpt-5.6-luna / max` |  |  |  |  |  |  |  |

## CLI subagent ledger

Include this section only for `study_surface=cli-session`. Include every stable
subagent; App title, task, saved-project, and archival fields do not belong in
this ledger.

| Slot | Stable subagent identity | Parent lineage evidence | Working-directory context | Requested profile | Profile evidence | Execution state | State reason or attention evidence | Error | Terminal evidence | Key result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Worker N |  |  |  | `gpt-5.6-luna / max` |  |  |  |  |  |  |

## Worker results

Summarize every completed, failed, unresolved, or abandoned slot and explain
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
