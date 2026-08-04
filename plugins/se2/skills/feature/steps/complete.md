---
node_id: complete
kind: terminal
purpose: report-the-complete-feature-task-bundle-after-operation-verification
entry_conditions:
  - selected-operation-is-preview-or-hosted-publication-is-verified
inputs:
  - feature-definition
  - feature-issue
  - tasks
  - task-dependency-graph
  - acceptance-coverage-map
  - execution-waves
  - readiness-evidence
  - repository-context
  - linked-feature-references
  - feature-type-projection
  - task-type-projection
  - documentation-update-ownership
  - task-change-set
  - task-dependency-change-set
  - maintenance-feature-delta
  - maintenance-evidence
  - run_mode
  - operation-evidence
outputs:
  - calculated-feature-bundle
  - terminal-report
  - maintenance-changelog-evidence
transitions: []
stop_if: []
side_effects:
  - none
terminal_states:
  - complete
---

# Complete

Report the complete desired bundle after the selected terminal operation has
finished. For each affected repository, retain its Feature definition, Feature
issue, every vertical Task, Feature attachment, Task dependency relationships,
criterion coverage, context evidence, required documentation updates, GitHub
issue state, and topological execution waves. The complete bundle also includes
the linked repository-owned Features.

Preview enters this node with a non-durable report artifact. Publish enters this
node only after `reconcile-verify` has independently confirmed every hosted
operation and any maintenance changelog comment. This node has no publication,
retry, or recovery side effect; failures transition to `blocked` from the
operation node that owns the missing evidence.

The final report must state the Feature reference, Task references, Task
dependency edges, execution waves, acceptance coverage, readiness evidence,
selected mode, and any unvalidated assumptions.
