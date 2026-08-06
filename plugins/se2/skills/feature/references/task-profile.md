# Feature Planning Task Profile

This is the skill-owned task profile for a task-managed se2:feature run.
Pass the complete profile to the root task preflight. The root preflight
verifies the required planner role and records optional runtime capabilities;
it does not select or rewrite these values.

## Required planner role

    task_profile: feature-planner
    roles:
      - role: planner
        required: true
        model: gpt-5.6-sol
        reasoning: medium
        topology: single-planner-task
    optional_roles:
      - role: analysis-worker
        model: gpt-5.6-sol
        reasoning: medium
        topology: bounded-readonly-analysis
      - role: critic-analyst
        model: gpt-5.6-sol
        reasoning: medium
        topology: independent-first-principles-analysis
    topology: planner-with-optional-analysis-workers
    title_template: "📚 Plan Feature · <Feature outcome>"

The planner owns the application task, the Feature graph, the question batch,
the reduction of worker evidence, the canonical textual plan, and the final
publication report. The application task is an execution envelope, not a
Feature graph node.

Optional roles are capability-conditioned. When delegation is available, the
planner may run bounded analysis-worker assignments with distinct analytical
responsibilities and one independent critic assignment. When delegation is
unavailable, the planner performs those analyses serially. This fallback is
part of the Feature profile and does not create a replacement task.

The critic-analyst receives the original intent and source set without the
planner draft or context-derived requirements during its first pass. It is
read-only, records evidence and speculation separately, and cannot publish,
edit the plan, or ask the user directly.

The planner must use the invoking session's exact saved local project and
local environment. It must not create or use a Git worktree, isolated
checkout, or task fork. If that destination cannot be independently verified,
stop before creating, resuming, or monitoring the planner task.

The title uses the established planner emoji convention. Replace only
Feature outcome with a short, deterministic outcome. A title is display
metadata, never task identity or recovery evidence.

The planner role is required exactly as declared. Do not substitute another
model or reasoning level. Optional workers may fall back to the parent, but
the planner has no automatic model or destination fallback. If the live
runtime cannot verify the planner profile, stop with unsupported-runtime.

## Optional goal and delegation facts

When goal tools are available, create or adopt one goal for the whole Feature
Plan run after required task preflight is ready. Keep it active while the
question batch waits for the user and complete it only after preview or
verified publication. Goal unavailability is reported and does not block the
plan.

Record delegation as one of:

- parallel-analysis: bounded optional roles were dispatched and observed;
- serial-fallback: the planner completed the same roles without delegation;
- unavailable: the runtime could not provide delegation and the parent
  fallback was used;
- unknown: capability evidence was insufficient and no delegated role was
  claimed.
