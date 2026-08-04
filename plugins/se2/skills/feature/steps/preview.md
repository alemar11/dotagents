---
node_id: preview
kind: action
purpose: retain-the-complete-bundle-as-a-local-preview
entry_conditions:
  - preview-mode-is-resolved
inputs:
  - frozen-feature-bundle
  - run_mode
outputs:
  - preview-report
  - non-durable-feature-and-task-refs
transitions:
  - to: complete
    when: preview-report-is-complete
stop_if:
  - hosted-state-would-be-required
side_effects:
  - none
terminal_states: []
---

# Preview

Return the frozen Feature-and-Task bundle as report data. Do not load the G
dependency gate, inspect GitHub, create a dry-run hosted mutation, or claim
current hosted duplicate, collision, or persistence state.
