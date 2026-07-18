# Idea Template

Use this template only after the candidate's name, owner, queue intent, and
source evidence are resolved. Preserve tentative language. Record unknowns as
unknowns instead of inventing requirements or decisions.

## Canonical Content

```markdown
# Idea: <Name>

artifact_marker: idea

## Summary

<One concise description of the proposal.>

## Problem or Opportunity

<The observed need, pain point, opportunity, or motivation.>

## Proposed Direction

<The tentative direction discussed, without turning it into a detailed plan.>

## Expected Value

<The outcome or benefit the proposal may provide.>

## Known Context and Constraints

- <Accepted context or constraint.>

## Open Questions

- <Unresolved question, or `None recorded.`>

## Source

- <Portable conversation, document, issue, or repository evidence.>
```

The canonical template above is the dormant default and intentionally omits a
workflow state. Insert `workflow_state: needs-triage` immediately after the
artifact marker only when the user explicitly queues this Idea for evaluation.
The local header metadata region starts after the H1 and ends at the first
`##` heading. It must contain exactly one
`artifact_marker: idea`, zero or one workflow-state line, and no `issue_type`
line. The consumed Project Memory marker and state mappings must use
`local-header`.

For GitHub, the issue title supplies `# Idea: <Name>`. Render the same seven
`##` sections in the issue body, but omit local header metadata. Apply the
configured `idea` marker and optional `needs-triage` state as labels instead.
Do not set a native Issue Type.

## Content Boundaries

- Keep the exact section order shown above.
- Use `None recorded.` rather than deleting an empty optional section.
- Keep source evidence portable: hosted links, repo-relative or
  repository-qualified paths, issue refs, or a concise conversation
  description. Do not publish developer-machine absolute paths.
- Do not include `## Planning Outcomes` during capture. A later planning
  workflow may append that section when it has a verified durable result.
- Do not add goals, non-goals, acceptance criteria, implementation steps,
  dependencies, delivery policy, readiness claims, domain-memory handoffs, or
  Feature Spec fields.
