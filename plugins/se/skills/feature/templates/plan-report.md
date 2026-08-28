# Feature Plan Report

## Result

- feature_plan_set_id: <set identity>
- feature_plan_set_revision: <revision>
- source_route: <new-source or existing-source>
- run_mode: <publish or preview>
- plan_status: <preview, published, or blocked>

## Feature registry

| feature_id | repository | parent Feature issue | blocked_by | status |
| --- | --- | --- | --- | --- |
| <feature-id> | <repository> | <hosted identity or proposed preview ref> | <Feature IDs or none> | <ready or blocked> |

## Macro Task registries

| parent_feature_id | macro_task_id | child Task issue | F-AC refs | blocked_by | status |
| --- | --- | --- | --- | --- | --- |
| <feature-id> | <macro-id> | <hosted identity or proposed preview ref> | <F-AC refs> | <same-parent Macro IDs or none> | <ready or blocked> |

## Planning evidence

- sources and repository context:
- boundary and consolidation decisions:
- acceptance criteria by Feature:
- material questions and answers:
- accepted assumptions and risks:
- review method, findings, and dispositions:
- structural review result:

## Operation evidence

- semantic issue and body readback:
- final parent-body reconciliation:
- parent-child relationship readback:
- Feature dependency attempts and native results:
- same-parent Macro dependency attempts and native results:
- explicitly removed prior SE-owned dependency results:
- optional classification results:
- existing-source preservation evidence:
- downstream handoff status:
- warnings:

## Implementation handoff

<Summarize the implementation-neutral outcome, same-repository stack intent,
cross-repository scheduling intent, F-ACs, Macro outcomes, and validation intent.>

## Blocker

<When blocked, provide the exact blocker, retained identities, and smallest
recovery input. Omit this section on complete preview or publication.>
