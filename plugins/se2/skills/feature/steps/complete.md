---
node_id: complete
kind: terminal
purpose: calculate-and-report-the-complete-feature-task-bundle
entry_conditions:
  - feature-tasks-and-task-dependency-graph-are-valid
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
outputs:
  - calculated-feature-bundle
  - terminal-report
  - maintenance-changelog-evidence
transitions: []
stop_if:
  - calculated-bundle-is-incomplete
  - publish-verification-fails
side_effects:
  - none-in-preview
  - github-persistence-in-publish
terminal_states:
  - complete
  - blocked
---

# Complete

Always calculate the complete desired bundle before choosing an operational
mode. For each affected repository, the result includes its Feature definition,
Feature issue, every vertical Task, Feature attachment, Task dependency
relationships, criterion coverage, context evidence, required documentation
updates, GitHub issue state, and topological execution waves. The complete
bundle also includes the linked repository-owned Features.

In the non-writing mode, retain the calculated bundle as report data. In the
publishing mode, publish to GitHub only after explicit authorization:

1. re-read the complete current Feature set, Task state, and dependency state;
2. create or update each repository-owned Feature;
3. link the Feature set with qualified issue references or URLs and verify every
   cross-repository relationship;
4. create or update each Task and attach it to its Feature through the
   parent/sub-issue relation or a canonical issue reference;
5. apply the authorized Feature/Task issue-type projection as publication
   metadata only; never use issue type to derive graph semantics;
6. create, update, or remove local Task dependency relationships according to
   the validated DAG;
7. verify every resulting state after its mutation;
8. for maintenance, add one separate comment to the Feature for every
   significant change, covering the reason, Feature definition changes,
   affected Tasks, and dependency changes, then verify each comment;
9. report retained identities, no-ops, missing operations, changelog evidence,
   and verification evidence.

If a mutation is rejected, timed out, or has uncertain readback, stop with a
blocked terminal report and reconcile current state before any retry. Never
replay an uncertain mutation blindly.

The final report must state the Feature reference, Task references, Task
dependency edges, execution waves, acceptance coverage, readiness evidence,
selected mode, and any unvalidated assumptions.
