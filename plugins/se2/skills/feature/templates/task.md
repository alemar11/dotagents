# Task: <feature-slug> <NN> <vertical-outcome>

## Feature

- feature_issue_ref: <durable-or-proposed-feature-ref>

## Execution Contract

| Field | Value |
| --- | --- |
| feature_ref | <Feature issue reference> |
| feature_slug | <lower-kebab-feature-slug> |
| repository_identity | <owning-repository-identity> |
| allowed_paths | <smallest-complete-safe-path-envelope> |
| target_branch_name | <target-branch-data> |
| dependency_ids | <earlier-generated-task-IDs-or-none> |

## Goal

<One independently valuable, vertical Task outcome.>

## Non-Goals

- <Excluded work.>

## Context

<Relevant Feature requirements, evidence, and dependency reasons. Do not repeat
dependency IDs as prose.>

## Repository Context

- context_sources_read: <sources selected by the repository AGENTS.md hierarchy>
- applicable_conventions: <facts this Task must preserve>

## Cross-Repository Notes

<Linked Feature references and the exact contract needed from them. Tasks and
Task dependencies remain repository-local; do not create an integration Task.>

## Requirements

- <Requirement this Task must satisfy.>

## Implementation Plan

<Concise planning-time recommendation across every layer required by the
vertical outcome. The executor may simplify it without changing the accepted
goal, scope, constraints, or criteria.>

## Acceptance Criteria

- [ ] <Unique, individually provable Task criterion.>

## Validation

- Preferred: <Primary proof.>
- Fallback: <Equivalent proof or None.>
- Failure policy: <Retry budget, fallback, evidence, and terminal outcome when constrained.>

## Safety Constraints

- <Compatibility, migration, rollback, security, or concurrency constraint.>

## Documentation Updates

- <Required repository document or instruction update owned by this Task;
  omit when no update is justified.>

## Readiness

This Task is agent-ready only when the Feature definition, vertical outcome,
allowed paths, acceptance criteria, validation, dependency IDs, and graph
readiness evidence are complete. Do not place unresolved questions or
placeholders in an agent-ready Task.
