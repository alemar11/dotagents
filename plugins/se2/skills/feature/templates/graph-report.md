# Feature Bundle Report

## Operational Evidence

- entry_route: <create-or-maintenance>
- run_mode: <publish-by-default-or-explicit-preview>
- terminal_operation: <publish-or-explicit-preview>
- source_route: <new-source-or-existing-source>
- terminal_state: <complete-or-blocked>
- conceptual_result: <complete-Feature-and-Task-bundle>
- operation_evidence: <frozen-preview-or-hosted-readback>

An omitted `run_mode` is reported as `publish`; `preview` is valid only when
explicitly requested. The `terminal-operation` subgraph owns final mode
selection, publication preflight, hosted checks, mutation, and
reconciliation. It is operational evidence, not a separate conceptual result:
the conceptual result remains the complete Feature-and-Task bundle.

## Repository Runs

| repository_identity | feature_ref | task_count | graph_state |
| --- | --- | --- | --- |
| <repository> | <Feature issue reference> | <number> | <complete-or-blocked> |

## Repository Context

| repository_identity | sources_read | context_evidence | missing_or_conflicting |
| --- | --- | --- | --- |
| <repository> | <sources selected by AGENTS.md hierarchy> | <facts used> | <none or blocker> |

## Feature Set

| repository_identity | feature_issue_ref | feature_type_projection | link_reason |
| --- | --- | --- | --- |
| <repository> | <Feature issue reference> | <Feature-or-not-applicable> | <shared boundary or proof link> |

## Feature Definition

- feature_id: <stable-feature-identity>
- feature_slug: <lower-kebab-feature-slug>
- acceptance_criteria: <complete or missing items>
- documentation_updates: <complete or none>

## Tasks

| task_id | task_issue_ref | feature_ref | vertical_outcome | dependency_ids | type_projection | wave | readiness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <generated-id> | <Task issue reference> | <Feature reference> | <outcome> | <IDs-or-none> | <Task-or-not-applicable> | <wave-number> | <evidence> |

## Task Dependency Graph

<One edge per real Task prerequisite. State why each serialized edge is
necessary. Feature links are not Task dependencies.>

## Execution Waves

- allowed_paths: <smallest-complete path envelope per Feature/Task>
- overlap: <shared-path pairs or none, with affected Features/Tasks>
- theoretical_waves: <Wave 0, Wave 1, and the graph/scope rationale>
- scope_overlap_gates: <shared paths, affected Features or Tasks, any proposed
  order or rebase constraint, and why each gate is not a dependency edge>

## Acceptance Coverage

| feature_criterion | owning_task_ids |
| --- | --- |
| <criterion> | <Task-IDs> |

## Publication Evidence

- calculated_bundle: <complete or missing items>
- feature_attachment: <verified Feature-to-Task evidence>
- task_dependency_relationships: <verified evidence>
- issue_type_projection: <Feature/Task mapping or not-applicable>
- preflight_evidence: <G availability and handoff evidence or not-applicable>
- read_after_write: <publish-only evidence or not-applicable>

## Feature Maintenance Changelog

- change_plan: <not-applicable, proposed, or complete>
- feature_comment_refs: <verified separate comment refs or none>
- significant_changes: <reason, Feature definition changes, Tasks, and dependency changes>

The changelog is a lateral publication output on the Feature issue, not a graph
node or terminal state.

## Blockers and Assumptions

- Blockers: <none or exact blocker>
- Unvalidated assumptions: <none or explicit assumptions>
