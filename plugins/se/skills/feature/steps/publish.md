---
node_id: publish
kind: action
purpose: freeze-preview-or-publish-and-read-back-semantic-projections
entry_conditions:
  - reviewed-plan-is-clean
  - run-mode-and-authority-are-resolved
inputs:
  - publication_ready_plan
  - run_mode
  - publication_authority
  - existing_plan_evidence
outputs:
  - final_plan_set
  - parent_feature_issue_identities
  - child_macro_task_issue_identities
  - relationship_and_dependency_results
  - removed_dependency_results
  - publication_readback
  - publication_warnings
  - downstream_handoff_status
transitions:
  - to: complete
    when: preview-is-frozen-or-all-required-publication-results-are-reconciled
  - to: blocked
    when: authority-attempt-handoff-or-required-write-cannot-be-reconciled
stop_if:
  - publish-would-silently-downgrade-to-preview
  - a-duplicate-plan-or-issue-would-be-created-after-an-ambiguous-effect
  - a-canonical-dependency-edge-lacks-an-attempt-or-result
  - an-explicitly-requested-downstream-handoff-lacks-a-terminal-result
side_effects:
  - transient
  - hosted
terminal_states: []
---

# Publish

Resolve the operation before effects. `preview` is explicit, local, and
non-durable; freeze the plan with proposed identities and perform no hosted
publication operation. An earlier hosted source read may still have used G
during Intake.

`publish` is the default and requires the installed G dependency and authority
for the exact parent issues, child issues, relationships, dependencies, and
existing-source updates in scope. Never substitute preview when publishing is
blocked.

Before hosted reads or writes, apply the shared
[G dependency preflight](../../../references/codex-dependency-preflight.md).
Immediately before every write, apply
[hosted-content-safety.md](../../../references/hosted-content-safety.md) to the
exact rendered title and body. Route issue operations through the focused
G-owned workflows.

For new-source publication:

1. publish one parent Feature issue per registry member and no container issue;
2. publish every Macro Task as a child of its own parent Feature;
3. after every exact parent and child identity is known, render the final Plan
   Set registry and child mappings, update every parent body in place, and
   preserve each created identity;
4. read back exact identities, final semantic bodies, set membership, and
   parent-child relationships;
5. attempt every Feature dependency and every same-parent Macro dependency as a
   native GitHub `blocked by` projection after all identities are known;
6. read back and record one observable native result for every canonical edge;
7. optionally delegate label and native Issue Type classification after
   semantic publication. Metadata failure never blocks completion.

For existing-source publication, update the same issues with the smallest
semantic patch. Preserve the complete untouched artifact, including labels,
acceptance order, executor-owned progress, and relationships outside the
explicit semantic graph delta. Read back the changed and preserved fields.
Compare the revised body-backed dependency graph with the prior SE-owned graph:
attempt every new desired edge, verify or record `no-op` for every retained
canonical edge, and remove only a prior SE-owned native edge explicitly removed
from the revised plan. Preserve foreign native edges. Record the observable
result for each desired edge and planned removal.
Perform any explicitly requested downstream notification or handoff only after
the update is verified, and reconcile its terminal result before completion.

Issue creation/update identity and semantic-body readback are mandatory. When a
required write is ambiguous, inspect the same intended artifact before any
retry; preserve a discovered identity. Block when it cannot be reconciled.
Confirmed failed, unavailable, or unknown native dependency projections are
warnings when the body-backed graph and required issue projections are
verified. A missing dependency attempt or result, or a missing terminal result
for an explicitly requested downstream handoff, blocks. Do not run a
whole-provider audit when targeted readback already proves the intended
projection.

When one exact hosted Idea is the source, close it as completed only after the
full Plan Set publication is verified and only when that lifecycle mutation is
in scope.
