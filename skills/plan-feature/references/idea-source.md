# Durable Idea Source Contract

Load this reference only when the caller supplies one or more
`source_idea_refs`. An Idea is source intent for a new Feature Spec, not a
Feature Spec itself and not another Plan Feature mode.

## Eligibility

- Accept `source_idea_refs` only with `mode=full-flow` or `mode=spec-only`.
- Reject them with `mode=issues-from-existing-spec`; that mode consumes its
  existing Feature Spec and source section unchanged.
- Treat the refs as execution data, never as selectable options.
- Require explicit user selection before combining multiple Ideas, and require
  their accepted scope to describe one bounded feature. Split unrelated Ideas
  into separate Plan Feature runs.
- Reject chat previews, temporary files, and every `proposed-idea:` ref. Only a
  durable, marker-valid artifact can be consumed.

## Durable Identity And Validation

Resolve exactly one tracker-owning repository for every Idea before drafting.
Use these durable ref shapes:

- GitHub in the current repository: `#<number>`;
- GitHub across repositories: `owner/repository#<number>` or its canonical
  hosted URL;
- local in the current repository:
  `planning/ideas/<idea-slug>.md`;
- local across repositories:
  `<repository-slug>/planning/ideas/<idea-slug>.md`.

For normal planning input, verify that a GitHub Idea is open, carries the
configured `artifact_marker=idea` label, has no native Issue Type, and has at
most one of the mapped `needs-triage` or `needs-info` workflow labels, with no
other mapped canonical workflow-state label. For a local Idea, verify the
canonical path, an H1 beginning `# Idea:`, exactly one
`artifact_marker: idea` line in the header metadata region, no `issue_type`
line, and at most one `workflow_state` whose value is `needs-triage` or
`needs-info`.

Perform GitHub source reads through `$gitstack:github-issues` in both write
modes, omitting mutation fields. `write_mode=propose` still validates current
hosted state but never requests a dry-run mutation or surfaces executable
commands.

The Project Memory marker mapping is required only for Idea capture or Idea
consumption. A missing mapping blocks only Idea capture or Idea consumption.
Stop with the exact tracker-routing prerequisite;
do not invalidate an unrelated Plan Feature run or silently rewrite Project
Memory configuration.

## Consumed And Recovery State

A closed GitHub Idea is not valid input for a new planning run. During recovery
of source reconciliation for the same already-published planning result,
however, accept a closed, marker-valid, untyped Idea as already reconciled only
when its existing planning-outcome comment records `coverage=full` and the
exact same authoritative `feature_spec_refs`. Do not reopen it, duplicate the
comment, or reject the remaining Ideas merely because this operation already
completed.

A local Idea containing a `coverage: full` entry in `## Planning Outcomes` is
already consumed and is not valid input for an ordinary new planning run.
Allow it only when either:

- source reconciliation is resuming and the entry contains the exact same
  authoritative Feature Spec refs, in which case treat the operation as
  already complete; or
- the user explicitly asks to plan the consumed Idea again, in which case
  preserve all prior outcome entries and append a new result only after the new
  run succeeds.

An explicit local re-plan instruction is source data, not another selectable
option. A closed GitHub Idea requires a separately authorized reopen before it
can become new planning input.

## Feature Spec Projection

- Preserve every captured Idea section unchanged.
- Render each consumed ref as `- Source Idea: <durable-ref>` in the Feature
  Spec's existing `## Source` section.
- In a multi-repository bundle, place a source ref in every parent or partial
  Feature Spec whose scope derives from that Idea. Do not copy an unrelated
  ref merely because it belongs to the same planning run.
- Keep Idea refs out of generated implementation issues and their
  `## Execution Contract`; `source_spec_ref` remains the sole planning parent
  for those issues.

## Per-Idea Exit Reconciliation

Determine coverage independently for each selected Idea. Reconcile state once
when the Plan Feature run exits; do not add or remove workflow labels while an
interactive clarification question is still active.

| Run outcome for one Idea | Applied durable result |
| --- | --- |
| Waiting for one specific requester answer | Keep the Idea open, add `needs-info`, and remove `needs-triage`. |
| Technical, configuration, validation, or publication failure | Preserve the Idea's previous state and report the blocker. |
| Durable planning result covers only part of the Idea | Link the result, keep the Idea open, add `needs-triage`, and remove `needs-info`. |
| Durable planning result fully covers the Idea | Link the result, clear `needs-triage` and `needs-info`, then close the GitHub Idea as completed or record a full local outcome. |
| `write_mode=propose` | Report intended transitions only; perform read validation but request no GitStack mutation. |

If requester input resumes planning, remove `needs-info` only as part of the
next terminal reconciliation. If planning is intentionally deferred after the
answer, reconcile to `needs-triage`. The two workflow states are mutually
exclusive.

For `spec-only`, a planning result is durable only after every requested
Feature Spec is published and verified. For `full-flow`, wait until every
Feature Spec, implementation issue, metadata mutation, and relationship in the
requested result is durable and verified. A blocked or partially published run
never records coverage or closes an Idea.

## Backend Mutations

Before a GitHub `write_mode=apply` reconciliation that adds a workflow state,
resolve the exact configured label for that state and verify that the label
exists in every affected repository. A dormant Idea moving to `needs-info`
requires the configured `needs-info` label; a dormant Idea receiving partial
coverage requires the configured `needs-triage` label. When a required mapping
exists but its concrete label does not, create and verify only that exact
configured label through `$gitstack:github-issues` before mutating any affected
Idea:

```text
mutation_mode=apply
issue_operation=create-label
target=owner/repository
```

Do not provision a label merely to clear an absent state. If required-label
provisioning fails, preserve the Idea's prior state, report the exact missing
operation, and resume from verified tracker state. In `write_mode=propose`,
report any required label creation as an intended transition but request no
mutation.

For GitHub `write_mode=apply`, add one comment containing
`coverage=<partial|full>` and every resulting authoritative
`feature_spec_refs` value relevant to that Idea. Use
`$gitstack:github-issues` for the exact comment, label, and close operations,
verify state after each mutation, and retry only missing operations after an
ambiguous or partial failure. Write and verify the outcome comment first,
reconcile `needs-triage` and `needs-info` second, and close a fully covered Idea
last. Retain the `idea` marker when closing. This ordering ensures that any
already-closed source carries the recovery evidence required above.

For local `write_mode=apply`, leave every captured section unchanged and add an
append-only `## Planning Outcomes` section after them. Add one non-duplicated
entry per successful planning result using
`- coverage: <partial|full>; feature_spec_refs: <durable-ref>[, <durable-ref>]`.
Treat an exact matching entry as already applied. Update only the optional
`workflow_state` header according to the exit table. The Idea file stays at its
canonical path.

Apply lifecycle operations only for explicitly selected `source_idea_refs`.
A terminal exit waiting for one requester answer may reconcile the affected
Ideas to `needs-info` before a planning result exists. Delay every coverage
backlink, `needs-triage` partial result, and full-consumption closeout until the
complete requested planning result passes its final publication checkpoint,
then apply the already-decided outcome separately to each Idea. If source
reconciliation itself partially fails, preserve verified completed operations,
report exact missing operations, and resume only those operations.
