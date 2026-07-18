# Durable Idea Source Contract

Load this reference in exactly two cases:

- from `idea-discovery.md` for validation-only candidate inspection before
  selection; or
- after the caller explicitly selects one or more durable `source_idea_refs`.

Validation-only discovery may use only durable identity, current-state, and
prior-outcome classification. It must stop before intent normalization,
drafting, coverage projection, or lifecycle reconciliation. An Idea is
tentative source intent for a new Feature Spec, not a Feature Spec itself, an
implementation issue, or another Plan Feature mode.

## Activation And Eligibility

- Keep explicit `source_idea_refs` as the fast path. Accept them only with
  `mode=full-flow` or `mode=spec-only`.
- Reject Idea input with `mode=issues-from-existing-spec`; that mode consumes
  its existing Feature Spec and source section unchanged.
- Treat selected refs as execution data, never as selectable options.
- Reject chat previews, temporary files, and every `proposed-idea:` ref. Only a
  durable, marker-valid artifact can be selected.
- Require explicit user selection before combining multiple Ideas, and require
  their accepted scope to describe one bounded feature. Split unrelated Ideas
  into separate Plan Feature runs.

## Durable Identity And Validation

Resolve exactly one tracker-owning repository for every Idea before drafting.
Use these durable ref shapes:

- GitHub in the current repository: `#<number>`;
- GitHub across repositories: `owner/repository#<number>` or its canonical
  hosted URL;
- local in the current repository: `planning/ideas/<idea-slug>.md`;
- local across repositories:
  `<repository-slug>/planning/ideas/<idea-slug>.md`.

For ordinary planning input, verify that a GitHub Idea is open, carries the
configured `artifact_marker=idea` label, has no native Issue Type, and has at
most one of the mapped `needs-triage` or `needs-info` workflow labels, with no
other mapped canonical workflow-state label. Read the complete body and the
complete comment history, following pagination until every marker-bearing
planning-outcome comment has been inspected.

For a local Idea, verify the canonical path, an H1 beginning `# Idea:`, exactly
one `artifact_marker: idea` line in the header metadata region, no `issue_type`
line, at most one `workflow_state` whose value is `needs-triage` or
`needs-info`, and the complete canonical Idea body.

Perform GitHub source reads through `$gitstack:github-issues` in both write
modes, omitting mutation fields. `write_mode=propose` still validates current
hosted state but never requests a dry-run mutation or surfaces executable
commands.

The Project Memory marker mapping is required only for Idea capture,
discovery, or consumption. A missing mapping blocks only those Idea paths.
Stop with the exact tracker-routing prerequisite; do not invalidate an
unrelated Plan Feature run or silently rewrite Project Memory configuration.

## Prior Outcomes And Consumed State

Before drafting, inspect every canonical planning-outcome record already
attached to the selected Idea. Validate records from oldest to newest as a
monotonic cumulative history within the active planning cycle: every later
successful result must retain all earlier Feature Spec refs and covered
material scope, and must not return previously covered scope to
`remaining_scope`.

- With no prior record, plan from the complete accepted Idea intent.
- With one or more `coverage: partial` records, load and validate every listed
  durable Feature Spec. Require each Spec to link back to the selected Idea,
  derive the cumulatively covered scope from those Specs, and plan only the
  remaining scope unless the user explicitly requests a re-plan. Missing,
  malformed, ambiguous, or unrelated prior refs block the run instead of being
  ignored.
- Absent an explicitly authorized re-plan, any Idea whose latest canonical
  record is `coverage: full` is consumed and is not valid ordinary planning
  input. An open GitHub Idea in that state, or a local full-outcome Idea that
  still carries a workflow state, is reconciliation-pending because state
  cleanup or closeout did not complete; route it only to reconciliation-only
  recovery.
- During reconciliation-only recovery for the same already-published planning
  result, accept a closed, marker-valid, untyped GitHub Idea as already
  reconciled only when its complete canonical full outcome exactly matches the
  verified cumulative authoritative refs and scope. Do not reopen it or
  duplicate its outcome.
- Allow a consumed local Idea as new input only when the user explicitly asks
  to plan it again. Preserve every prior outcome and append a new result only
  after the new run succeeds. A closed GitHub Idea requires separately
  authorized reopening before it can become new planning input.

An authorized re-plan after a full outcome begins a new active planning cycle.
Preserve earlier records as history, but do not fold their refs or scope into
the new cycle unless the new planning result explicitly reuses them. An
explicit re-plan instruction and prior outcome records are execution data, not
selectable options.

## Idea Intent Normalization

Normalize each selected Idea into transient planning evidence without editing
the source body:

| Idea section | Planning use |
| --- | --- |
| `Summary` | Concise source intent and problem framing. |
| `Problem or Opportunity` | Candidate `Problem`, users, and use cases. |
| `Proposed Direction` | Tentative requirements, scope, and non-goals that still require evidence or explicit acceptance. |
| `Expected Value` | Candidate goals and outcomes; never acceptance criteria by itself. |
| `Known Context and Constraints` | Scope, requirements, risks, dependencies, and validation constraints. |
| `Open Questions` | Planning blockers or clarification inputs. |
| `Source` | Portable evidence to verify and cite. |

Do not silently promote tentative direction, expected value, or assumptions to
accepted requirements. Resolve material uncertainty through repository
evidence or clarification.

Maintain a transient per-Idea coverage map for every material accepted element:

| Coverage state | Meaning |
| --- | --- |
| `covered` | Represented by one or more durable Feature Specs, with the owning Spec ref and section known. |
| `excluded` | Explicitly resolved as outside the feature and represented as a non-goal or rejected direction. |
| `deferred` | Intentionally left for a later planning run and named as remaining scope. |
| `blocked` | Cannot be resolved without specific requester information or contradictory evidence. |

These four states describe durable planning coverage. Before publication, a
draft section or non-goal is only a candidate destination. It becomes
`covered` or `excluded` for terminal reconciliation only after the owning
Feature Spec has a verified durable ref and section.

With `write_mode=propose`, or whenever another branch returns only a
non-durable preview, keep the durable map unchanged and build a separate
report-only intended projection. Map every material element to a proposed Spec
section, proposed non-goal, remaining-scope item, or blocking question. Derive
`intended_coverage=partial|full`, `intended_covered_scope`, and
`intended_remaining_scope` only when no blocker remains. Proposed refs and
sections never satisfy durable `covered` or `excluded`, and the intended
projection must not create a canonical outcome block or lifecycle mutation.

Derive the terminal result cumulatively across verified prior Specs and the
new durable Spec set:

- `full`: every material element is `covered` or `excluded`; no `deferred` or
  `blocked` element remains;
- `partial`: at least one material element is newly or previously `covered`, at
  least one is `deferred`, and none is `blocked`;
- waiting for information: at least one element is `blocked`; withhold the
  requested durable result rather than recording partial coverage.

Use the coverage map to produce concise, source-grounded `covered_scope` and
`remaining_scope` lists. Do not persist the internal map in a Feature Spec or
generated implementation issue.

## Feature Spec Projection

- Preserve every captured Idea section unchanged in its source artifact.
- Draft the Feature Spec from the normalized Idea evidence, repository and
  Project Memory evidence, and accepted clarification results.
- Render each consumed ref as `- Source Idea: <durable-ref>` in the Feature
  Spec's existing `## Source` section.
- In a multi-repository bundle, place a source ref in every parent or partial
  Feature Spec whose scope derives from that Idea. Do not copy an unrelated ref
  merely because it belongs to the same planning run.
- Keep Idea refs and coverage maps out of generated implementation issues and
  their `## Execution Contract`; `source_spec_ref` remains the sole planning
  parent for those issues.

## Per-Idea Exit Reconciliation

For `write_mode=apply`, determine durable coverage independently for each
selected Idea and reconcile state once when the Plan Feature run exits. For
`write_mode=propose`, derive only the independent intended projection. Do not
add or remove workflow labels while an interactive clarification question is
still active.

| Run outcome for one Idea | Applied durable result |
| --- | --- |
| Waiting for one specific requester answer | Keep the Idea open, add `needs-info`, and remove `needs-triage`. |
| Failure before a previously requested answer was supplied | Preserve the Idea's previous state and report the blocker. |
| Failure after a supplied answer resolved `needs-info` | Keep the Idea open, replace stale `needs-info` with `needs-triage`, and report the technical blocker. |
| Cumulative durable planning covers only part of the Idea | Record a canonical partial outcome, keep the Idea open, add `needs-triage`, and remove `needs-info`. |
| Cumulative durable planning fully covers the Idea | Record a canonical full outcome, clear `needs-triage` and `needs-info`, then close the GitHub Idea as completed or mark the local Idea consumed. |
| `write_mode=propose` | Report `intended_coverage`, `intended_covered_scope`, `intended_remaining_scope`, and intended transitions only; leave durable coverage unchanged and request no GitStack mutation. |

If requester input resumes planning, remove `needs-info` only as part of the
next terminal reconciliation. If planning is intentionally deferred after the
answer or fails for a non-requester reason, reconcile to `needs-triage`. The two
workflow states are mutually exclusive.

For `spec-only`, a planning result is durable only after every requested
Feature Spec is published and verified. For `full-flow`, wait until every
Feature Spec, implementation issue, metadata mutation, and relationship in the
requested result is durable and verified. A blocked or partially published run
never records coverage or closes an Idea.

## Canonical Planning Outcome

Use one visible, machine-recognizable block per successful planning result. A
GitHub outcome is the complete body of one new comment:

```markdown
## Planning Outcome
<!-- plan-feature:idea-outcome -->
coverage: <partial|full>
feature_spec_refs:
- <globally unambiguous durable ref>
covered_scope:
- <concise cumulative covered outcome>
remaining_scope:
- <concise residual outcome, or `none` for full coverage>
```

For a local Idea, append the same fields under a new
`### Planning Outcome` subsection inside one append-only
`## Planning Outcomes` section. Use the same marker immediately after the
subheading.

Canonicalization rules:

- keep the field order above and use exactly one marker per record;
- require `coverage` to be `partial` or `full`;
- deduplicate `feature_spec_refs` and order them lexicographically;
- order scope items by their first appearance in the Idea body;
- require at least one durable ref and one `covered_scope` item;
- require at least one real `remaining_scope` item for `partial`;
- require the single `remaining_scope` item `none` for `full`;
- use cumulative refs and scope, including every verified prior partial result
  in the active planning cycle;
- treat an exact latest block as already applied and do not append it again;
- accept a later result only when its cumulative ref set is a strict superset
  of the previous result, its scope progression is monotonic, and at least one
  previously remaining material element becomes covered or excluded;
- treat the same cumulative ref set with different coverage or scope, any
  missing prior ref, or any covered-to-remaining regression as a conflict and
  block rather than editing or duplicating history;
- reject prose-only outcomes, missing markers, reordered fields, and retired
  one-line outcome syntax instead of translating aliases.

Do not add outcome records during capture, discovery, clarification, proposal
mode, or before the complete requested planning result passes its publication
checkpoint.

## Reconciliation-Only Recovery

When the planning result is already durable but source reconciliation was
interrupted, run this recovery branch before ordinary source validation and
before the Feature Spec phase. The verified durable result refs and intended
per-Idea coverage are recovery evidence, not a new mode or option.

1. Read the current Idea, every canonical outcome, and all referenced Specs.
2. Require the intended cumulative outcome to match the verified durable Spec
   set and coverage map exactly.
3. Treat an exact canonical outcome as already written. Retry only missing
   label, comment, local-record, or close operations.
4. Accept an already-closed GitHub Idea only for an exact matching full outcome
   and treat it as complete. Never reopen it during recovery.
5. When selected Ideas have mixed completion state, skip verified completed
   sources and resume only the missing operations for the others.
6. Stop on any source-body, marker, outcome, or ref mismatch. Do not draft,
   republish, or rewrite Feature Specs during source-only recovery.

## Backend Mutations

Before a GitHub `write_mode=apply` reconciliation that adds a workflow state,
resolve the exact configured label for that state and verify that the label
exists in every affected repository. When a required mapping exists but its
concrete label does not, create and verify only that exact configured label
through `$gitstack:github-issues` before mutating any affected Idea:

```text
mutation_mode=apply
issue_operation=create-label
target=owner/repository
```

Do not provision a label merely to clear an absent state. If required-label
provisioning fails, preserve current hosted state, report the exact missing
operation, and resume from verified tracker state. In `write_mode=propose`,
report any required label creation as intended output but request no mutation.

For GitHub `write_mode=apply`, write and verify the canonical outcome comment
first, reconcile `needs-triage` and `needs-info` second, and close a fully
covered Idea last. Use `$gitstack:github-issues` for each exact operation,
verify state after every mutation, and retry only operations proven missing.
Retain the `idea` marker when closing.

For local `write_mode=apply`, leave every captured section unchanged, create
`## Planning Outcomes` only when the first durable outcome is ready, and append
one non-duplicated canonical subsection per successful planning result. Update
only the optional `workflow_state` header according to the exit table. The Idea
file stays at its canonical path; a latest canonical full outcome marks it
consumed.

Apply lifecycle operations only for explicitly selected `source_idea_refs`.
Delay every coverage outcome and closeout until the complete requested planning
result passes its final publication checkpoint. If source reconciliation
partially fails, preserve verified completed operations, report exact missing
operations, and enter reconciliation-only recovery on resume.
