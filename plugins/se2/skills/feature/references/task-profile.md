# Feature Task Profile

This is the skill-owned task profile for a task-managed `se2:feature` run.
Pass the complete profile to the root task preflight; the root preflight
validates its live capabilities but does not own or alter these values.

## Required planner role

The Feature workflow uses one principal planner task:

```yaml
task_profile: feature-planner
roles:
  - role: planner
    model: gpt-5.6-sol
    reasoning: medium
topology: single-planner-task
title_template: "🤖 Plan Feature · <Feature outcome>"
```

The planner owns the current Feature graph run and returns the complete
Feature/Task bundle. The application task is an execution envelope, not a
visible node or transition in the Feature graph.

The title uses the established planner/controller emoji convention. Replace
only `<Feature outcome>` with the short, concrete, deterministic outcome for
the current Feature run.

The `planner` role is required exactly as declared. Do not substitute another
model, lower the reasoning level, or silently introduce additional workers.
If the live runtime cannot verify this profile, fail closed with
`unsupported-runtime` before creating or monitoring the planner task.
