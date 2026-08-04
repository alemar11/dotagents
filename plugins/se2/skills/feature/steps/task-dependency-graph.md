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
  - feature-acceptance-high-water
  - task-acceptance-high-water
  - linked-feature-references
  - repository-context
  - documentation-update-ownership
  - existing-task-dependency-relationships
  - maintenance-evidence
outputs:
  - task-dependency-graph
  - acceptance-coverage-map
  - allowed_paths
  - overlap
  - execution-waves
  - scope-overlap-gates
  - readiness-evidence
  - task-dependency-change-set
transitions:
  - to: terminal-operation
    when: task-dag-is-acyclic-covered-and-agent-ready
  - to: blocked
    when: task-dependency-coverage-or-scope-validation-fails
stop_if:
  - dependency-id-does-not-resolve-to-a-local-task
  - task-dependency-graph-contains-a-cycle
  - feature-criterion-has-no-owning-task
  - acceptance-criterion-id-is-missing-duplicate-or-ambiguous
  - acceptance-high-water-is-missing-invalid-or-decreases
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
- every Feature acceptance-criterion ID maps to one or more Task IDs and one or
  more Task acceptance-criterion IDs that prove its complete observable outcome;
- every `F-AC-NN` ID is unique within its Feature and every `T-AC-NN` ID is
  unique across the complete Task set under that Feature;
- the Feature body owns monotonic Feature and Task acceptance high-water marks,
  every current or retired ID is at or below its matching mark, and neither
  mark decreases during maintenance;
- every Task has an independent outcome, safe scope, and validation proof;
- path overlap is identified through `allowed_paths` and every external
  scope-overlap gate is recorded separately from dependency IDs;
- linked Features resolve to the intended repository-owned Feature issues;
- every context-justified documentation update has one owner and validation;
- every Task satisfies readiness without unresolved questions or placeholders.

Feature-to-Task attachment expresses belonging. Dependency edges exist only
between Tasks. Cross-repository Feature links are not Task dependencies and do
not create a cross-repository integration Task.

Calculate theoretical topological execution waves. Tasks with no unfinished
incoming edges may be proposed in parallel only when their `allowed_paths` do
not identify unsafe concurrent edits. Record the reason for every serialized
edge and every scope-overlap gate, including shared paths, affected Features or
Tasks, any proposed order or rebase constraint, and why the gate is not a
logical dependency edge. This node reports planning evidence for the
Implement handoff; it does not claim paths, serialize workers, inspect current
base/HEAD state, or rebase a worker. On maintenance, report added, retained,
removed, or changed Task dependency relationships before Terminal Operation
reconciles the selected publication mode.
