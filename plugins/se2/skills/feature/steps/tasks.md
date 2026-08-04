---
node_id: tasks
kind: action
purpose: decompose-harden-and-reconcile-vertical-task-issues-under-the-feature
entry_conditions:
  - feature-definition-and-feature-identity-are-stable
inputs:
  - feature-definition
  - feature-issue
  - acceptance-criteria
  - feature-scope
  - repository-context
  - documentation-update-plan
  - rehydrated-bundle
  - maintenance-evidence
outputs:
  - tasks
  - acceptance-coverage-candidate
  - documentation-update-ownership
  - task-type-projection
  - task-change-set
transitions:
  - to: task-dependency-graph
    when: every-required-outcome-has-a-vertical-task
  - to: blocked
    when: task-verticality-or-scope-cannot-be-proven
stop_if:
  - candidate-is-only-an-architecture-layer
  - task-would-have-no-independent-outcome
  - individual-task-scope-cannot-be-made-safe
side_effects:
  - none
terminal_states: []
---

# Tasks

Derive the smallest useful set of vertical Task issues from the Feature
definition. A Task is an independently valuable, autonomously verifiable
vertical outcome across every required layer; it is not a technical TODO.

For every candidate:

1. name one observable outcome;
2. assign the smallest complete repository and allowed-path scope;
3. include implementation, integration, and validation layers needed for that
   outcome;
4. define unique acceptance criteria and preferred plus fallback validation;
5. assign any context-justified documentation update to the Feature or the
   smallest Task that owns the behavior change;
6. explain only real Task prerequisites;
7. render one Task using templates/task.md.

Compress redundant candidates before freezing IDs. Retain stable Task
identities, create only justified missing Tasks, and calculate removals only
when the explicit maintenance indication and current state make them safe.
Block on duplicates, stale bodies, conflicting Feature relationships, or an
individual Task scope that cannot be made safe. Report overlap between
otherwise valid Features or Tasks as planning evidence in the Feature Bundle
Report; do not turn it into a Task dependency. The GitHub type `Task` is
publication metadata; Task content, Feature attachment, and the Task dependency
graph remain authoritative.
