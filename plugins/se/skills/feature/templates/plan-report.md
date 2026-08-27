# Feature Plan Report

## Run

- entry_route: <create or maintenance>
- source_route: <new-source or existing-source>
- run_mode: <preview or publish>
- planning_depth: <simple or substantial>
- clarification_route: <ask, skip-simple, skip-complete-brief, or skip-user-directed>
- plan_status: <planning, awaiting-user-input, plan-ready, published, or blocked>
- goal_status: <active, complete, or not-available>

## Feature Plan Set

- feature_plan_set_id: <set identity>
- feature_plan_set_revision: <revision>
- set_status: <preview, published, or blocked>

| feature_id | repository | parent Feature issue | Feature blocked_by | feature_status |
| --- | --- | --- | --- | --- |
| <feature-id> | <repository> | <issue reference or local preview> | <Feature ID or none> | <ready or blocked> |

### Feature members

| feature_id | repository | Feature Plan issue | outcome | feature_status |
| --- | --- | --- | --- | --- |
| <feature-id> | <repository> | <issue reference or local preview> | <outcome> | <ready or blocked> |

### Macro Tasks

| Feature ID | Feature issue | parent_feature_id | macro_task_id | child Task issue | F-AC refs | blocked_by | macro_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <feature-id> | <Feature issue> | <feature-id> | <macro-01> | <issue reference or local preview> | <F-AC-01> | <local macro ID or none> | <ready or blocked> |

## Source and boundary evidence

- source issues:
- consolidation decision:
- separate or out-of-scope sources:
- linked Feature members and repositories:
- Feature Plan Set identity and revision:
- Feature-level dependency graph:

## Analysis

- intent analysis:
- repository context:
- boundary analysis:
- critic findings:
- accepted assumptions:
- risks:

## Question batch

- clarification_route_evidence: <depth evidence, brief coverage and critic finding, or explicit user direction>

For a question-free route, report an empty batch and its validated exception;
do not emit the placeholder row below.

| id | question | question_blocking | question_status | answer | evidence |
| --- | --- | --- | --- | --- | --- |
| Q-01 | <decision> | <yes or no> | <open or resolved> | <answer or none> | <source> |

## Critic plan review

- plan_review_round:
- plan_review_result:
- plan_review_provenance:
- findings and planner dispositions:
- bounded revision and re-review evidence:
- review-generated question IDs:

## Plan content

- problem statement:
- desired outcome:
- scope:
- non-goals:
- Feature acceptance criteria by Feature:
- Feature registry and parent issue mapping:
- local Macro Task registries and macro dependencies:
- validation intent:
- Implement handoff:

## Operation evidence

- critic plan-review evidence:
- plan-validation:
- publication:
- read-after-write:
- parent Feature publication and set readback:
- Macro Task child publication and local registry readback:
- Feature-level dependency readback:
- native Feature dependency attempt and `blockedBy`/`blocking` result:
- native same-parent Task dependency attempt and `blockedBy`/`blocking` result:
- delegated tagger result per issue, including final labels and type:
- source-Idea lifecycle:
- blockers:
