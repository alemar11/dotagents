---
node_id: plan-publication
kind: action
purpose: preview-or-publish-the-complete-feature-plan
entry_conditions:
  - plan-validation-is-ready
inputs:
  - feature-plan
  - plan-publication-content
  - run-mode-request
  - source-route
  - source-idea-identity
outputs:
  - frozen-plan
  - run_mode
  - publication-evidence
  - source-idea-lifecycle-evidence
transitions:
  - to: complete
    when: explicit-preview-is-frozen-or-publish-is-verified
  - to: blocked
    when: publish-operation-or-readback-cannot-be-verified
stop_if:
  - plan-is-not-ready
  - publication-target-is-ambiguous
side_effects:
  - preview-is-local-only
  - publish-is-hosted-and-authorized-by-the-explicit-request
terminal_states: []
---

# Plan Publication

Resolve run_mode exactly once after plan validation. An omitted mode means
publish. Preview is valid only when explicitly requested.

For preview, freeze the complete plan as local report data and do not inspect
hosted state for a new source. For publish, load the shared G dependency
preflight and [hosted-content-safety.md](../../../references/hosted-content-safety.md)
immediately before the first hosted operation. Publish one Feature issue per
repository-owned plan member through the G-owned issue workflow. The Feature
issue body is the durable textual plan; do not create execution-unit issues,
dependency IDs, execution waves, or worker assignments here.

Verify every hosted operation with authoritative read-after-write evidence.
Retain the calculated plan when publication fails and report the smallest
recovery input. Do not silently downgrade a default publish to preview.

When one exact hosted Idea is the source, close that Idea with reason
completed only after the Feature Plan publication and its authoritative
readback succeed. Preview and ambiguous source identity never close an Idea.
