# Macro Task

The semantic contract is owned by [Feature Planning](../SKILL.md). This issue
is a durable macro-vertical planning projection of one parent Feature
outcome. It is not an optional scope item, a technical execution unit, a
worker assignment, or a separate PR boundary.

## Identity

- parent_feature_issue: <Feature issue reference>
- feature_plan_set_id: <Feature Plan Set identity>
- parent_feature_id: <owning Feature identity>
- macro_task_id: <stable lower-kebab ID>
- macro_task_registry_revision: <revision>
- macro_status: <ready or blocked>

## Macro outcome

<Describe the coherent vertical capability area this Macro Task represents.>

## Scope and criteria

- scope: <macro boundary>
- feature_acceptance_refs: <F-AC-NN list>

## Macro dependency

- blocked_by: <Macro Task IDs owned by the same parent Feature or none>
- dependency_semantics: planning-only; Implement may combine, reorder, or internalize the relation while preserving this outcome and its Feature criteria

Cross-Feature Macro Task references are invalid, even when the parent Features
share a repository. Feature-level dependencies belong in the Feature Plan Set
registry and parent Feature projections.

## Closure

This Macro Task is part of the `parent_feature_id` closed implementation issue
set. The final implementation PR closes this Task together with that parent
Feature, and never closes a sibling Feature or its Tasks, after the PR is
merged.
