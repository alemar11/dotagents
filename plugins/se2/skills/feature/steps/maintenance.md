---
node_id: maintenance
kind: action
purpose: rehydrate-an-existing-feature-task-bundle-for-canonical-graph-reconciliation
entry_conditions:
  - existing-feature-tasks-and-external-change-indication-are-available
inputs:
  - existing-feature-issue
  - existing-task-issues
  - existing-task-dependency-relationships
  - external-change-indication
  - affected-repositories
  - repository-context
outputs:
  - rehydrated-bundle
  - maintenance-evidence
  - entry_route
  - documentation-update-candidates
transitions:
  - to: feature
    when: current-bundle-is-rehydrated-and-identities-are-retained
  - to: blocked
    when: references-conflict-or-change-indication-is-unclear
stop_if:
  - existing-feature-is-ambiguous
  - current-task-or-dependency-state-cannot-be-reconciled
side_effects:
  - read
  - hosted
terminal_states: []
---

# Maintenance

Use this step only as the alternate entry route for an explicit Feature
maintenance request. Start from the existing Feature issue, its Task issues,
current Task dependency relationships, and the external change indication.

When hosted state must be rehydrated, pass the shared G dependency preflight
before the first hosted read and use the G-owned GitHub issue workflow. Re-read
the authoritative current state and rehydrate one complete transient bundle per
affected repository. Preserve stable Feature and Task identities, record
current Feature attachments and Task dependency edges, and retain the
indication as maintenance evidence. Do not create, update, delete, or comment
on issues in this step.

Rehydrate acceptance-criterion IDs separately from criterion prose. Preserve
every valid existing ID through non-semantic clarification, reordering, and Task
movement. Rehydrate the Feature-owned monotonic Feature and Task acceptance
high-water marks and never recycle an ID at or below them. A legacy criterion
rendered as a Markdown checkbox has no stable ID: report one migration that
assigns fresh IDs in preserved text/order and initializes both high-water marks
from the migrated set. Do not interpret checked or unchecked legacy markers as
acceptance evidence. If bracketed IDs exist without their high-water marks, or a
mark is below a current ID, block instead of inferring missing retirement
history.

Start context discovery from each repository's `AGENTS.md` and follow the
applicable descendant instructions before deciding what additional documents or
code must be read. Record any context-justified documentation update candidate
without imposing a documentation system.

Pass the rehydrated bundle to Feature. The canonical path then reviews the
Feature definition, recalculates vertical Tasks and coverage, validates the
Task dependency graph, and reaches `terminal-operation`. Missing references,
foreign state, conflicts, or an indication that is not specific enough to
justify a change transition to `blocked`.
