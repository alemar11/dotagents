# Feature: <feature-name>

## Feature Definition

<Canonical contract for one bounded capability. This is the durable Feature
definition, not a separate Spec artifact.>

## Planning Identity

- feature_id: <stable-feature-identity>
- feature_slug: <lower-kebab-feature-slug>
- source_route: <new-source-or-existing-source>
- repository_identity: <owning-repository-identity>
- affected_repositories: <feature-wide-repository-identities>
- allowed_paths: <smallest-complete-scope>

## Repository Context

- context_sources_read: <sources selected by the repository AGENTS.md hierarchy>
- confirmed_context: <portable facts and conventions used by this definition>
- missing_or_conflicting_context: <none or exact blocker>

## Outcome

<One bounded observable product or system outcome.>

## Non-Goals

- <Explicitly excluded work.>

## Requirements

- <Requirement that the complete Feature must satisfy.>

## Linked Features

| repository_identity | feature_issue_ref | link_reason |
| --- | --- | --- |
| <peer-repository> | <peer-feature-issue-ref> | <shared boundary or proof link> |

## Acceptance Criteria

- [ ] <Unique, individually provable Feature criterion.>

## Validation

- Preferred: <Primary proof.>
- Fallback: <Equivalent proof or None.>
- Failure policy: <Retry budget, fallback, evidence, and terminal outcome when constrained.>

## Safety Constraints

- <Rollback, compatibility, security, or scope constraint.>

## Documentation Updates

- <Required repository document or instruction update, owner, and validation;
  omit this entry when no update is justified.>

## Task Graph

Tasks are attached to this Feature. Task `dependency_ids` are local to this
Feature and repository; Feature links are not Task dependencies.
