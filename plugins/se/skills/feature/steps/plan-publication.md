---
node_id: plan-publication
kind: action
purpose: preview-or-publish-the-feature-plan-set-and-macro-projections
entry_conditions:
  - plan-validation-is-ready
inputs:
  - feature-plan
  - feature-plan-set-registry
  - macro-task-registry
  - plan-publication-content
  - run-mode-request
  - source-route
  - source-idea-identity
outputs:
  - frozen-plan
  - feature-plan-set-projection
  - macro-task-projection
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

For preview, freeze the complete Feature Plan Set, its Feature registry, every
local Macro Task registry, and all proposed parent/child projections as local
report data and do not inspect hosted state for a new source. For publish,
load the shared G dependency preflight and apply
[hosted-content-safety.md](../../../references/hosted-content-safety.md)
immediately before every hosted write.

Publish one parent issue per Feature member through the G-owned hosted issue
workflow. Never publish a Feature Plan Set container or integration issue.
Then publish one child issue per Macro Task, link each child to its own parent
Feature issue, and project Feature-level and macro-local planning `blocked_by`
values into the set manifest, parent Feature bodies, and child Task bodies. Do
not invent a provider-native blocker relation. Update every parent Feature
projection with the final set membership, exact parent issue refs, local child
issue refs, and registry after all parent and child identities are known.

After every final parent and child projection, relation, and exact identity are
verified, invoke `$g:github-tagger` separately for each exact issue with
`mutation_mode=apply` and both labels and native type requested. Feature must
not choose, suggest, or preset label names or type values, including `Feature`
or `Task`. Instruct the tagger to select the smallest relevant set of existing
labels, with zero labels valid when none is pertinent, and zero or one
available native issue type, with zero valid when none is pertinent. Record
each tagger result in the publication evidence.

Labels and native issue types remain optional publication metadata. A readable
catalog with no confident match, an empty catalog, unavailable metadata, zero
selected values, unchanged values, or a reconciled partial or failed metadata
write does not block semantic publication. The handoff itself must still
return one terminal, reconciled result per issue. A missing result or an
indeterminate mutation blocks completion because final provider state is not
known. Never use labels, type, or their availability as Feature, Macro Task,
relation, or completion authority.

The set registry maps `feature_id` to exactly one parent Feature issue and
`(parent_feature_id, macro_task_id)` to exactly one child Task issue. Every
parent projection must carry the same `feature_plan_set_id` and revision. A
Feature-level dependency may cross repositories; a Macro Task dependency may
not cross parent Features, even in the same repository.

For an existing-source maintenance route, reuse the exact Plan Set identity,
Feature identities, parent Feature issues, and stable Macro Task identities
from authoritative readback. Reconcile the existing sibling parent/child
projections in place and never create a second Feature, a container issue, or
a duplicate child set from local assumptions.

Do not create technical execution-unit issues, technical dependency IDs,
execution waves, or worker assignments here. Macro Task issues are durable
planning projections and are not one-to-one execution units.

Verify every parent Feature issue, every child Task, every parent/child
relation, every Feature identity, every parent issue ref, every registry
`blocked_by` value, shared set identity/revision, and the final set registry
with authoritative read-after-write evidence. Verify every tagger handoff has
a reconciled result and retain its independently read-back final labels and
type when it attempted a mutation. Publication is not complete while a Feature
or Macro Task lacks its exact hosted identity, a Feature-level edge points
outside the set, a Macro edge crosses a parent Feature, sibling projections
disagree, or a tagger result remains unresolved; an empty optional metadata
assignment alone never blocks completion.

Verify every hosted operation with authoritative read-after-write evidence.
Retain the calculated plan when publication fails and report the smallest
recovery input. Do not silently downgrade a default publish to preview.

When one exact hosted Idea is the source, close that Idea with reason
completed only after the complete Feature Plan Set, every sibling Feature,
every Macro Task projection, the final registry, all authoritative readbacks,
and every required tagger handoff reconcile. Preview and ambiguous source
identity never close an Idea.
