---
node_id: task-dependency-graph
kind: validation
purpose: recalculate-and-validate-the-task-dependency-dag-coverage-and-waves
entry_conditions:
  - vertical-tasks-have-been-derived
inputs:
  - feature-definition
  - feature-issue
  - tasks
  - acceptance-criteria
  - acceptance-coverage-candidate
  - linked-feature-references
  - repository-context
  - documentation-update-ownership
  - existing-task-dependency-relationships
  - maintenance-evidence
outputs:
  - task-dependency-graph
  - acceptance-coverage-map
  - execution-waves
  - readiness-evidence
  - task-dependency-change-set
transitions:
  - to: complete
    when: task-dag-is-acyclic-covered-and-agent-ready
  - to: blocked
    when: task-dependency-coverage-or-overlap-validation-fails
stop_if:
  - dependency-id-does-not-resolve-to-a-local-task
  - task-dependency-graph-contains-a-cycle
  - feature-criterion-has-no-owning-task
side_effects:
  - none
terminal_states: []
---

# Task Dependency Graph

Recalculate the desired Task dependency graph after Task boundaries and
ownership have stabilized, then reconcile it against current Task dependency
relationships on the maintenance route.

Require:

- every `dependency_id` resolves to a Task under the same Feature and
  repository;
- no self-dependencies, duplicate edges, or cycles;
- every Feature acceptance criterion maps to one or more Tasks;
- every Task has an independent outcome, safe scope, and validation proof;
- path overlap is safely combined or ordered by a necessary Task edge;
- linked Features resolve to the intended repository-owned Feature issues;
- every context-justified documentation update has one owner and validation;
- every Task satisfies readiness without unresolved questions or placeholders.

Feature-to-Task attachment expresses belonging. Dependency edges exist only
between Tasks. Cross-repository Feature links are not Task dependencies and do
not create a cross-repository integration Task.

Derive topological execution waves. Tasks with no unfinished incoming edges
may run in parallel only when their allowed paths do not create unsafe
concurrent edits. Record the reason for every serialized edge and every scope
overlap gate. On maintenance, report added, retained, removed, or changed
Task dependency relationships before Complete reconciles them.
