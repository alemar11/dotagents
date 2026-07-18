# Idea Source Forward Scenarios

These read-only fixtures define representative Plan Feature outcomes. They do
not authorize tracker or repository mutation.

## New-Source Local Idea To Complete Applied Bundle

Input:

- no durable `source_spec_ref` exists, so Plan Feature derives the new-source
  route;
- `write_mode=apply`;
- one selected `current-repository/planning/ideas/export-settings.md` Idea;
- no prior planning outcome;
- every material Idea element resolves to `covered` or `excluded`;
- the requested applied bundle contains one Feature Spec, its final hardened
  implementation issues, mapped metadata, and parent/issue relationships.

Expected:

- read and normalize all seven canonical Idea sections;
- publish and verify `planning/features/export-settings/SPEC.md`;
- publish and verify every generated implementation issue, its mapped metadata,
  dependencies, and parent relationship;
- keep the exact Idea ref only in the Spec's `## Source` section;
- wait until the complete applied bundle is durable and verified before
  reconciling the Idea;
- append one canonical local outcome with `coverage: full`, the durable Spec
  ref, cumulative `covered_scope`, and `remaining_scope` containing only
  `none`;
- remove any Idea workflow state and leave the Idea file in place as consumed;
- require no implementation PR or PR merge before consuming the Idea.

## Explicit GitHub Discovery Without Selection

Input:

- an explicit request to list captured Ideas;
- no exact `source_idea_refs`;
- GitHub tracker routing with a configured Idea-marker label.

Expected:

- list and validate open marker-labelled, untyped GitHub Ideas through
  read-only GitStack operations;
- read the complete paginated comment history and classify an open Idea whose
  latest canonical outcome is full as reconciliation-pending, not selectable;
- show qualified refs, Summary, workflow state, and prior outcomes;
- perform no comment, label, type, close, Feature Spec, or issue mutation;
- stop when the user asked only to inspect or has not selected a ref.

## Proposed Idea Ref Is Rejected

Input:

- no durable `source_spec_ref` exists;
- `source_idea_refs` contains `proposed-idea:export-settings`.

Expected:

- reject the proposed ref before drafting or mutation;
- create no Feature Spec, implementation issue, planning outcome, label change,
  or local file;
- require a durable, marker-valid Idea ref before the new-source route can
  continue.

## New-Source Proposal Leaves Idea Unchanged

Input:

- no durable `source_spec_ref` exists, so Plan Feature derives the new-source
  route;
- `write_mode=propose`;
- one selected GitHub Idea.

Expected:

- read and validate current GitHub source state through GitStack with mutation
  fields omitted;
- return a proposed Feature Spec plus a report-only
  `intended_coverage=partial|full`, `intended_covered_scope`, and
  `intended_remaining_scope` projection;
- keep the durable coverage map unchanged and render no canonical planning
  outcome block;
- leave the selected Idea unchanged, including its open/closed state and every
  workflow label;
- perform no GitStack publication, dry-run mutation, outcome comment, label
  change, or close operation.

## Existing-Source Route Rejects Unbound Idea Refs

Input:

- one durable `source_spec_ref` already exists, so Plan Feature derives the
  existing-source route;
- its immutable `## Source` contains one exact `- Source Idea:` ref;
- the invocation also supplies a different or additional `source_idea_refs`
  value.

Expected:

- derive the complete `bound_source_idea_refs` set from the immutable Spec;
- reject the explicit `source_idea_refs` because it is not exactly set-equal to
  the bound refs, before issue generation or mutation;
- preserve the durable Feature Spec and its existing `## Source` evidence
  unchanged;
- perform no Idea read, outcome, workflow-state, or close operation.

## Partial New-Source Publication Retries Through Bound Ideas

Input:

- an earlier `write_mode=apply` run published a Feature Spec whose `## Source`
  contains the selected Idea ref;
- that run failed before every implementation issue and Idea reconciliation
  completed;
- the retry discovers the durable Spec and therefore derives the
  existing-source route;
- the Idea remains open with no outcome for that incomplete bundle.

Expected:

- derive `bound_source_idea_refs` from the immutable Spec without requiring the
  caller to reselect the Idea;
- accept an explicitly repeated `source_idea_refs` value only when it is exactly
  set-equal to the bound set;
- validate the Idea, unchanged Spec, prior outcomes, and coverage without
  drafting from the Idea again;
- converge only the missing issues and relationships;
- after the complete applied bundle verifies, reconcile and close or triage the
  bound Idea in the same retry;
- require no separate third reconciliation invocation.

## Multiple Ideas Stay Bounded

Input:

- three discovered Ideas;
- two describe one bounded export-settings feature;
- one describes unrelated billing work.

Expected:

- require explicit selection;
- allow the two related refs to feed one planning run;
- require a separate Plan Feature run for the billing Idea;
- never publish an unrelated batch of Feature Specs from one run.

## Repeated Partial Planning Becomes Cumulative Full Coverage

Input:

- an open Idea whose older paginated comments contain a canonical partial
  outcome referencing `owner/repository#101`;
- the prior Spec covers export format selection and leaves scheduled delivery
  in `remaining_scope`;
- a new verified Spec `owner/repository#125` covers scheduled delivery.

Expected:

- paginate through the complete comment history before deriving prior state;
- load and validate `owner/repository#101` before drafting;
- plan only the residual scheduled-delivery scope unless re-planning was
  explicitly requested;
- derive cumulative full coverage from both Specs;
- write one canonical full outcome whose lexicographically ordered
  `feature_spec_refs` contain both refs, whose `covered_scope` is cumulative,
  and whose only `remaining_scope` item is `none`;
- close the GitHub Idea only after that outcome and state cleanup verify.

## Conflicting Cumulative Outcome Is Rejected

Input:

- the latest partial outcome carries `feature_spec_refs` containing only
  `owner/repository#101`;
- a candidate successor reuses that same ref set but changes coverage or scope.

Expected:

- reject the candidate as conflicting rather than append or edit history;
- accept an exact latest block only as an idempotent already-applied result;
- accept a genuine later result only when its ref set is a strict superset and
  its covered and remaining scope progress monotonically.

## Reconciliation-Only Recovery

Input:

- the complete applied bundle is already durable and verified;
- the exact canonical full outcome comment exists;
- label cleanup succeeded but the GitHub close operation did not.

Expected:

- enter reconciliation-only recovery before ordinary source validation;
- validate the Idea, outcome block, cumulative Spec refs, and coverage map;
- do not draft, edit, or republish any Feature Spec or implementation issue;
- retry only the missing close operation;
- accept the Idea as complete if a prior retry already closed it with the exact
  matching full outcome.

## Answered Needs-Info Does Not Stay Stale

Input:

- an Idea currently carries `needs-info`;
- the requester supplies the blocking answer;
- a later technical failure prevents planning completion.

Expected:

- write no planning outcome;
- keep the Idea open;
- replace stale `needs-info` with `needs-triage` at terminal reconciliation;
- report the technical blocker.

## Complete Applied Bundle Precedes Idea Closure

Input:

- no durable `source_spec_ref` existed when the new-source route began;
- `write_mode=apply`;
- cumulative Idea coverage is full;
- every requested Feature Spec, implementation issue, metadata mutation, and
  relationship is durable and verified.

Expected:

- wait until the complete applied bundle is durable and verified;
- write the canonical full outcome and close the GitHub Idea at planning
  closeout;
- leave implementation issue and Feature Spec delivery lifecycle to the
  executor;
- do not wait for a future implementation PR or PR merge to close the Idea;
- do not let that later PR merge reopen or otherwise mutate the consumed Idea.
