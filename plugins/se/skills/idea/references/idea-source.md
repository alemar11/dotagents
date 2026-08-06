# Idea Source Handoff

This reference owns the transient source artifact that an explicit Idea
capture may hand to a later Feature planning run. It is not a Feature Plan and
does not authorize an automatic skill invocation.

## Canonical shape

The artifact may contain only these fields:

| Field | Meaning |
| --- | --- |
| source_kind | Always idea-source. |
| candidate_name | Tentative human-readable proposal name. |
| idea_slug | Deterministic lower-kebab proposal slug. |
| repository_identity | One verified tracker-owning repository. |
| summary | Tentative proposal summary. |
| problem_or_opportunity | Observed need or opportunity. |
| proposed_direction | Tentative direction, not an implementation design. |
| expected_value | Anticipated value. |
| known_context_and_constraints | Portable context and constraints. |
| open_questions | Material or unresolved questions. |
| source_evidence | Portable evidence supporting the proposal. |
| idea_ref | Proposed or verified Idea reference. |
| idea_ref_state | proposed-non-durable or verified hosted state. |

## Excluded fields

The artifact must not contain Feature outcome, non-goals, requirements,
acceptance criteria, allowed paths, validation policy, execution units, dependency IDs,
implementation plans, readiness claims, or durable project-memory content.

## Lifecycle

Idea creates this shape only after its local capture bundle is normalized. In
preview, the artifact and its ref remain non-durable. In publish, the hosted
Idea may be verified, but the handoff remains transient.

When Feature Intake receives this artifact, it keeps source_route as
new-source, reloads repository context, preserves open questions as
clarification evidence, and derives all Feature Plan fields independently.
