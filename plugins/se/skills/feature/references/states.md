# Feature States

This reference is the human-readable state registry for `se:feature`. It keeps
workflow position separate from plan metadata, durable planning projections,
and external runtime state. The workflow registry and step front matter remain
the structural sources of truth for transitions.

## Workflow nodes

Workflow nodes describe where the planning run is executing. They are
transient and are never Feature, Macro Task, publication, or provider states.

| node | kind | plain description |
| --- | --- | --- |
| `maintenance` | action | Rehydrate an existing published Feature Plan Set for an explicit semantic revision. |
| `intake` | action | Normalize a new Feature request, its source issues, and repository identities. |
| `analysis` | action | Collect repository, boundary, dependency, question, and critic evidence. |
| `clarification` | decision | Present and reconcile the initial material question batch or the one permitted review-generated follow-up batch. |
| `convergence` | action | Resolve the final sibling Feature boundaries and local Macro Task structure. |
| `plan` | action | Compose the Feature Plan Set and each Feature's Macro Task registry. |
| `plan-review` | validation | Critically review the complete draft, reconcile correctable findings, and surface at most one follow-up clarification batch. |
| `plan-validation` | validation | Verify that the planning contract is complete and internally consistent. |
| `plan-publication` | action | Freeze a preview or publish and verify the hosted planning projections. |
| `complete` | terminal | Finish with a frozen preview or a semantic publication verified by read-after-write evidence with one recorded native dependency result per edge. |
| `blocked` | terminal | Stop because a required planning or publication contract needs a specific recovery input. |

`current_node_id` contains exactly one node from this table. The question batch
may wait for the user inside `clarification`; `awaiting-user-input` is not a
separate workflow node and is not terminal `blocked`.

## Plan, report, and domain states

| field or domain | allowed values | lifetime | plain description |
| --- | --- | --- | --- |
| `entry_route` | `create`, `maintenance` | transient and reported | Selects a new plan or an explicit revision of an existing plan. The `maintenance` value is a route; the node with the same name performs that route. |
| `source_route` | `new-source`, `existing-source` | plan and report | Identifies whether planning starts from new intent or an existing published Plan Set. |
| `run_mode` | `preview`, `publish` | transient and reported | Selects the operation. Omission means `publish`; the value describes intent, not its result. |
| `planning_depth` | `simple`, `substantial` | plan and report | Derived during analysis. `simple` is limited to one narrow, fully bounded single-repository outcome with no material product choice; uncertainty selects `substantial`. |
| `clarification_route` | `ask`, `skip-simple`, `skip-complete-brief`, `skip-user-directed` | transient, plan, and report | Controls the transition from analysis. Substantial planning defaults to `ask`; every skip value requires its own evidence and never permits guessing a material decision. |
| `plan_review_round` | `initial`, `post-clarification` | plan and report | Distinguishes the first complete-draft review from the one review allowed after a review-generated clarification batch. Another material question after `post-clarification` blocks. |
| `plan_review_result` | `clean`, `revision-required`, `clarification-required`, `blocked` | plan and report | Records the critic draft-review outcome. Only `clean` may enter Plan Validation; the other values select bounded revision, one follow-up clarification, or terminal blocking. |
| `plan_review_provenance` | `delegated-critic`, `serial-fallback` | plan and report | Records who performed the finished-draft review. `delegated-critic` requires an observed successful assignment; failed, unavailable, ambiguous, or unobserved delegation must be reported as `serial-fallback`. |
| `plan_status` | `planning`, `awaiting-user-input`, `plan-ready`, `published`, `blocked` | plan and report | Summarizes semantic planning progress. A successful preview remains `plan-ready`; `published` requires verified hosted publication. |
| `set_status` | `preview`, `published`, `blocked` | report | Summarizes the Plan Set operation result. It is separate from requested `run_mode`. |
| `feature_status` | `ready`, `blocked` | durable plan projection | Describes whether one Feature member satisfies its planning contract or retains a member-specific blocker. It is not Implement or PR readiness. |
| `macro_status` | `ready`, `blocked` | durable Macro Task projection | Describes whether one Macro Task satisfies its planning contract. It is not an Implement execution gate. |
| `question_status` | `open`, `resolved` | plan and report | Describes whether one material planning question still needs a decision. |
| `question_blocking` | `yes`, `no` | plan and report | States whether the question prevents convergence. A non-blocking open question becomes an explicit assumption. |
| source-map decision | `consolidated`, `separated`, `out-of-scope` | durable plan content | Records how each source issue contributes to the Feature Plan Set. |
| critic disposition | `accepted`, `rejected`, `unresolved` | durable plan content | Records how each independent critic challenge was reconciled. |

`plan-readiness` is validation evidence, not another status enum. Its outcome is
represented by the transition from `plan-validation` and by `plan_status`.

## External execution and hosted states

| field or domain | values | owner | plain description |
| --- | --- | --- | --- |
| planner task wait | `awaiting-user-input` | application runtime | A resumable wait while the question batch is with the user. It remains nonterminal. |
| `goal_status` | `active`, `complete`, `not-available` | goal runtime and report | Reports the optional goal lifecycle. Goal `complete` is not the Feature workflow node `complete`. |
| delegation outcome | `parallel-analysis`, `serial-fallback`, `unavailable`, `unknown` | planner report | Reports how analysis roles were handled. Substantial planning requires the study and critic lenses even when both run through serial fallback. |
| tagger result | values defined by `$g:github-tagger` | `$g:github-tagger` | Records the reconciled classification and application result for each published issue. It may contain zero selected labels and zero selected types and is not Feature or Macro Task semantic state. |
| native dependency result | `verified`, `no-op`, `failed`, `unavailable`, `unknown` | `$g:github-issues` result and Feature report | Records the mandatory native projection attempt for one canonical dependency. Only an absent attempt/result blocks publication; failure does not override the body-backed semantic graph. |
| source Idea close reason | `completed` | hosted issue provider | Used only after the complete Plan Set, all projections, and every tagger handoff have reconciled. |

## Persistence boundary

Feature Plan Set, Feature, Macro Task, and question metadata may be rendered in
durable plan or hosted artifacts. The planning run itself remains transient.
`se:feature` owns no persisted runtime checkpoint, checkpoint status, resume
ledger, or delivery state. Implementation checkpoints such as
`candidate-published` and `delivery-pending` belong to `se:implement`, not this
skill.
