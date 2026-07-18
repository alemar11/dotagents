# Complete Bundle Proposal Fixture

Use this fixture to forward-test Plan Feature's single convergent pipeline. The
result contains the complete proposed Feature Spec, every hardened
implementation issue, mapped metadata, relationships, and publication order
without local or hosted writes.

## User Request

```text
Use $plan-feature to plan a feature named "account settings export". Show me
the complete Feature Spec and implementation issues before publishing them.
Do not write files or mutate GitHub.
```

## Resolved Run

```text
write_mode: propose
source_route: new-source

Project Memory facts:
  tracker_backend: github
  repository_layout: single-repository
  issue_type_mappings:
    feature:
      transport: body-field
      tracker_value: "Issue Type: Feature"
    task:
      transport: native-type
      tracker_value: Task
  workflow_state_mappings:
    ready-for-agent:
      transport: label
      tracker_value: ready-for-agent

Planning data:
  feature_slug: account-settings-export
  affected_repositories:
    - current-repository
  allowed_paths:
    - src/account-settings/**
    - tests/account-settings/**
  target_branch_name: feature/account-settings-export
  source_spec_ref: proposed-spec:account-settings-export

knowledge_delta:
  decisions:
    - Account settings export is a user-owned portable archive.
  target_surfaces:
    - current-repository/CONTEXT.md
    - current-repository/project-memory/adr/ADR-account-settings-export.md
  evidence:
    - "Accepted planning decision: account settings export portability."
    - current-repository/src/account-settings/export.ts
planning_blockers: []
```

## Proposed Bundle Summary

- Title: `Feature Spec: Account Settings Export`
- Intended repository: current repository
- Intended tracker: GitHub
- Intended type: canonical `feature` through final-only `body-field` with exact
  tracker value `Issue Type: Feature`
- Proposed source ref: `proposed-spec:account-settings-export`
- Feature dependencies: empty table body
- App compatibility: compatible after publication replaces the proposed source
  ref with a durable hosted ref
- Domain capture: the non-persisted run delta is deferred to the final
  integration issue; the Feature Spec body carries no payload
- Proposed issue ref: `proposed-issue:account-settings-export/01`
- Final proposed issue ref: `proposed-issue:account-settings-export/02`
- Intended tracker metadata after apply: canonical `task` through `native-type`
  value `Task`, and canonical `ready-for-agent` through `label` value
  `ready-for-agent`
- Bundle status: complete proposal, non-durable, and non-executable until a
  later `write_mode=apply` run replaces proposed refs with verified durable refs

## Proposed Bundle Manifest

```text
artifacts:
  - ref: proposed-spec:account-settings-export
    kind: feature-spec
    intended_metadata:
      issue_type:
        canonical: feature
        transport: body-field
        tracker_value: "Issue Type: Feature"
  - ref: proposed-issue:account-settings-export/01
    kind: implementation-issue
    intended_metadata:
      issue_type:
        canonical: task
        transport: native-type
        tracker_value: Task
      workflow_state:
        canonical: ready-for-agent
        transport: label
        tracker_value: ready-for-agent
  - ref: proposed-issue:account-settings-export/02
    kind: implementation-issue
    intended_metadata:
      issue_type:
        canonical: task
        transport: native-type
        tracker_value: Task
      workflow_state:
        canonical: ready-for-agent
        transport: label
        tracker_value: ready-for-agent
relationships:
  - child: proposed-issue:account-settings-export/01
    parent: proposed-spec:account-settings-export
    dependency_ids: none
  - child: proposed-issue:account-settings-export/02
    parent: proposed-spec:account-settings-export
    dependency_ids: 01
publication_order:
  - proposed-spec:account-settings-export
  - proposed-issue:account-settings-export/01
  - proposed-issue:account-settings-export/02
```

The manifest is descriptive proposal metadata. It does not create, label,
attach, enqueue, or otherwise mutate a tracker object.

## Structural Graph Compression Result

- Candidate issues: `2`.
- Final retained issues: `2`.
- Combined or removed slices: none.
- Removed artificial dependencies: none.
- Retention reasons: issue `01` owns the independently useful authorized archive
  contract and focused proof; issue `02` owns the product download path,
  integrated proof, and final domain closeout.
- Avoided initial `$plan-harder` calls: `0`.
- Gate result: passed. Counts are measurements only and did not determine the
  result.

## Proposed Feature Spec

```markdown
# Feature Spec: Account Settings Export

## Source

- Accepted feature request in the current conversation.
- `src/account-settings/export.ts`

## Planning Identity

- Feature slug: `account-settings-export`.
- Repository layout: `single-repository`.

## Problem

Account owners cannot produce a portable archive of their supported settings.

## Goals

- Let an authorized account owner assemble and download a stable settings
  archive.
- Preserve account ownership boundaries throughout export and download.

## Non-Goals

- Export data that is not part of account settings.
- Deploy or release the feature as part of planning.

## Users And Use Cases

- An account owner downloads their settings for portability or backup.

## Requirements

- Export only settings owned by the requesting account.
- Produce a stable documented archive shape.
- Reject cross-account access to an assembled archive.

## Product / Repository Scope

- Affected repositories: `current-repository`.
- Allowed paths: `src/account-settings/**`, `tests/account-settings/**`,
  `CONTEXT.md`, and `project-memory/adr/**`.
- Shared target branch: `feature/account-settings-export`.

## Feature Dependencies

| upstream_feature_spec_ref | dependency_reason |
| --- | --- |

## Acceptance Criteria

- [ ] An authorized account owner can download a portable settings archive.
- [ ] The archive excludes settings owned by another account.
- [ ] The complete export path has focused integration proof.

## Validation Expectations

- Focused account-settings export contract and integration tests.
- Manual authorized and cross-account download checks as fallback proof.

## Risks

- Archive-shape drift could break portability without contract coverage.

## Open Questions

- None.

## Issue-Splitting Notes

- Build the authorized archive first, then connect download and integrated
  domain-memory closeout.

```

## Proposed Implementation Issue 01

```markdown
# account-settings-export: 01 Assemble the account settings archive

## Execution Contract

| Field | Value |
| --- | --- |
| `source_spec_ref` | `proposed-spec:account-settings-export` |
| `feature_slug` | `account-settings-export` |
| `affected_repositories` | `current-repository` |
| `allowed_paths` | `src/account-settings/**`, `tests/account-settings/**` |
| `target_branch_name` | `feature/account-settings-export` |
| `dependency_ids` | `none` |

## Goal

Allow an account owner to assemble a portable archive of supported account
settings.

## Non-Goals

- Expose the archive through a download endpoint.
- Update durable project-memory surfaces.

## Requirements

- Export only settings owned by the requesting account.
- Produce a stable documented archive shape.

## Implementation Plan

Plan-hardening: final stable $plan-harder issue-hardening pass completed for this issue.

Implement export assembly and authorization together with focused contract
coverage.

## Acceptance Criteria

- [ ] An authorized account owner can assemble the archive.
- [ ] The archive excludes settings owned by another account.

## Validation

- Preferred: focused account-settings export tests.
- Fallback: equivalent repository test runner plus a manual archive assembly.

## Completion

- GitHub tracker: include this issue's closing keyword in the relevant
  implementation PR; closure occurs after merge.
```

## Final Proposed Integration Issue

Proposed issue ref: `proposed-issue:account-settings-export/02`

```markdown
# account-settings-export: 02 Download the archive and close durable context

## Execution Contract

| Field | Value |
| --- | --- |
| `source_spec_ref` | `proposed-spec:account-settings-export` |
| `feature_slug` | `account-settings-export` |
| `affected_repositories` | `current-repository` |
| `allowed_paths` | `src/account-settings/download/**`, `tests/account-settings/**`, `CONTEXT.md`, `project-memory/adr/**` |
| `target_branch_name` | `feature/account-settings-export` |
| `dependency_ids` | `01` |

## Goal

Expose the authorized archive through the product download flow, prove the
integrated behavior, and reconcile the accepted durable contract.

## Non-Goals

- Add unrelated account settings formats.
- Release or deploy the feature.

## Requirements

- Connect the download flow to the archive produced by issue `01`.
- Preserve account ownership checks through the integrated request path.
- Run domain-memory closeout only after integrated behavior is proven.

## Implementation Plan

Plan-hardening: final stable $plan-harder issue-hardening pass completed for this issue.

Implement the download boundary, exercise the complete export path, then hand
the accepted durable delta to Project Memory and verify its documentation diff.

## Acceptance Criteria

- [ ] An authorized account owner can download the portable archive.
- [ ] Another account cannot access that archive.
- [ ] Integrated validation passes before durable context is updated.
- [ ] Project Memory reconciles the accepted delta against landed behavior.

## Validation

- Preferred: focused account-settings export integration tests.
- Fallback: equivalent repository test runner plus a manual authorized and
  cross-account download check.

## Domain Knowledge Closeout

- Required workflow:
  - Invoke `$project-memory` with `memory_slice=domain-memory` and
    `domain_operation=implementation-closeout` after integrated behavior is
    proven.
knowledge_delta:
  decisions:
    - Account settings export is a user-owned portable archive.
  target_surfaces:
    - current-repository/CONTEXT.md
    - current-repository/project-memory/adr/ADR-account-settings-export.md
  evidence:
    - "Accepted planning decision: account settings export portability."
    - current-repository/src/account-settings/export.ts
- Closeout proof:
  - Require `capture_outcome=captured` from Project Memory.
  - Verify every accepted item and required named target, report `CONTEXT.md`
    and `project-memory/adr/ADR-account-settings-export.md` as reconciled
    destinations, and verify the complete documentation diff.
  - Treat `deferred` or `no-durable-change` as blocked for this nonempty delta.

## Completion

- GitHub tracker: include this issue's closing keyword in the relevant
  implementation PR; closure occurs after merge.
```

## Multi-Repository Identity Probe

This second propose-only case proves that two repo-scoped partials and their
first generated issues cannot collide:

```text
project_slug: account-platform
feature_slug: account-settings-export
parent_source_spec_ref: proposed-spec:account-platform/account-settings-export
child_source_spec_refs:
  api: proposed-spec:account-platform/account-settings-export/api
  web: proposed-spec:account-platform/account-settings-export/web
child_issue_refs:
  api: proposed-issue:account-platform/account-settings-export/api/01
  web: proposed-issue:account-platform/account-settings-export/web/01
implementation_target_branches:
  api: feature/account-settings-export
  web: feature/account-settings-export
```

The parent is coordination-only. Each generated implementation issue belongs
to one repo-scoped partial and uses that partial's source ref.

Every multi-repository bundle adds exactly one dedicated integration partial
owned by the repository where a concrete integration change and integrated
validation run:

```text
integration_source_spec_ref: proposed-spec:account-platform/account-settings-export/web/integration
integration_feature_dependencies:
  - upstream_feature_spec_ref: proposed-spec:account-platform/account-settings-export/api
    dependency_reason: Wait for the API implementation partial to merge and prove its contract.
  - upstream_feature_spec_ref: proposed-spec:account-platform/account-settings-export/web
    dependency_reason: Wait for the web implementation partial to merge and prove its product path.
integration_issue_ref: proposed-issue:account-platform/account-settings-export/web/integration/01
integration_issue_dependency_ids: none
integration_target_branch: feature/account-settings-export-integration
knowledge_delta_owner: integration_issue_ref
```

The integration partial is downstream of both implementation partials, so its
whole issue graph waits for their merges. Its issue IDs remain local to the
integration partial; no sibling-partial issue ID is copied into
`dependency_ids`. The integration issue owns a bounded change in the `web`
repository plus the integrated proof, so it can produce a real PR. The
`knowledge_delta_owner` line is present only when a delta exists; the same
integration partial and issue remain mandatory without one.

### Expected Applied Multi-Repository Identity Projection

This is a non-mutating projection of the identities that a later apply run must
persist. Hosted and local refs remain globally unambiguous after proposed refs
are replaced:

```text
github_child_source_spec_refs:
  api: acme/account-api#241
  web: acme/account-web#118
github_integration_source_spec_ref: acme/account-web#119
github_integration_issue_source_spec_ref: acme/account-web#119
github_integration_target_branch: feature/account-settings-export-integration
github_integration_feature_dependencies:
  - upstream_feature_spec_ref: acme/account-api#241
    dependency_reason: Wait for the API implementation partial to merge and prove its contract.
  - upstream_feature_spec_ref: acme/account-web#118
    dependency_reason: Wait for the web implementation partial to merge and prove its product path.
local_child_source_spec_refs:
  api: api/planning/features/account-settings-export/SPEC.md
  web: web/planning/features/account-settings-export/SPEC.md
local_integration_source_spec_ref: web/planning/features/account-settings-export/integration/SPEC.md
local_integration_issue_source_spec_ref: web/planning/features/account-settings-export/integration/SPEC.md
local_integration_target_branch: feature/account-settings-export-integration
local_integration_issue_affected_repositories: web
local_integration_issue_allowed_paths:
  - web/src/account-settings/export-integration/**
  - web/planning/features/account-settings-export/integration/issues/01-prove-integrated-export.md
  - web/planning/features/account-settings-export/integration/issues/done/01-prove-integrated-export.md
local_integration_feature_dependencies:
  - upstream_feature_spec_ref: api/planning/features/account-settings-export/SPEC.md
    dependency_reason: Wait for the API implementation partial to merge and prove its contract.
  - upstream_feature_spec_ref: web/planning/features/account-settings-export/SPEC.md
    dependency_reason: Wait for the web implementation partial to merge and prove its product path.
local_integration_completion_path: web/planning/features/account-settings-export/integration/issues/done/01-prove-integrated-export.md
```

Bare `#<number>` and bare repo-relative paths are not valid sibling identities.
The applied integration Feature Spec and its generated issue are App-compatible
only after these durable refs replace every proposed ref; this projection does
not publish or enqueue them.

### Multi-Repository Apply Transaction Projection

A later multi-repository apply predeclares one recoverable publication
transaction across hosted and local roles before the first mutation:

```text
publication_transaction: plan-feature/account-settings-export/<generated-id>
roles:
  - parent: hosted
  - implementation/api: hosted
  - implementation/web: local
  - integration/web: local
staging_contract:
  applies_to: hosted roles with unknown refs only
  marker: unique transaction and role
  state: explicitly non-executable and not yet a Feature Spec
  excluded_final_content: durable refs and optional final-only body metadata
  predeclared_inputs: role, target, title, reconstructable template and hash, allowed ref slots, and optional exact body-metadata slot/value
  allowed_finalization: replace predeclared durable-ref slots, insert exact body metadata, and remove staging notice
finalization_contract:
  operation: edit
  materialization: compute final bodies and hashes after durable refs are known
  verification: final body hash, qualified refs, metadata, and cross-links
foreign_race_policy: stop
recognized_retry_policy: resume only exact missing label provisioning, hosted create, edit, local-file create, or metadata operations
```

Every role, target, parameterized body-template hash, and allowed ref slot is
known before creation, and the complete templates remain reconstructable.
Final-body hashes are computed only after durable refs exist. Refs returned by
the transaction's own creates are expected state, not a foreign race. Issue
generation starts only after all staging markers are gone and the complete
connected Spec set verifies. A partial failure returns the transaction identity,
role-to-ref map, complete templates and hashes, ref slots, any materialized
final-body hashes, the optional body-metadata slot and value, selected Idea refs
plus verified prior outcome refs,
the complete `knowledge_delta`, completed operations, and exact missing
operations; a hash alone is
insufficient and the retry never creates duplicate roles.

For an all-local bundle, every deterministic ref is resolved and every final
body hash is recorded before the first file create. If a later file create
fails, the exact continuation remains on the new-source route and creates only
missing predeclared paths whose targets and hashes still match. An absent or
mismatched continuation blocks; existing final files are never overwritten or
reinterpreted as a complete immutable bundle.

## Existing Source Derived-Route Probe

When a durable `source_spec_ref` is supplied at intake, derive the
existing-source route: read and validate the source unchanged, skip Feature
Spec drafting and publication, then apply or propose the issue and relationship
remainder. A `proposed-spec:` ref is not durable route evidence.

```text
source_spec_ref: acme/account-settings#88
source_state: durable-and-canonical
source_body_action: read-and-validate-unchanged
feature_spec_drafting: skipped
feature_spec_publication: skipped
reconciliation_outcomes:
  contract_equivalent_existing_issue: retain without regenerating hardening prose
  absent_required_issue: create only operations proven missing
  missing_mapped_metadata_or_parent_attachment: repair only the supported operation
  complete_equivalent_bundle: no-op when the complete bundle already matches
  body_graph_or_conflicting_metadata_mismatch: conflict-stop without rewriting the artifact
```

The route must never rewrite the supplied source or duplicate a verified
artifact. Under `write_mode=propose`, the supplied source remains durable while
new issue and relationship projections remain non-durable and non-executable.

## Durable-Seed Idempotence Probe

Before graph synthesis, Plan Feature enumerates every durable issue and seeds
the candidate graph with contract-equivalent IDs and vertical slices. A
complete durable graph produces no new candidate and reaches the no-op path
without model regeneration. For an incomplete graph, only uncovered Spec scope
may produce a missing slice:

```text
retained_generated_ids: [01, 03]
retained_id_action: fixed; never renumber or regenerate
uncovered_scope: downloadable archive audit event
missing_generated_id: 04
invalid_repair: insert an upstream node that requires changing retained 01 or 03
```

The final source, Project Memory mappings, and complete issue/metadata/parent
state are re-read before proposal, no-op, or mutation. Every create also proves
its exact target remains absent; concurrent drift forces recomputation or a
block instead of duplicate publication.

## Existing Multi-Repository Partial Intake Probe

An existing-source request may begin from any canonical member, not only the
coordination parent:

```text
intake_source_spec_ref: acme/account-web#118
intake_role: implementation-partial
required_connected_set:
  - coordination-parent
  - implementation/api
  - implementation/web
  - integration/web
completion_scope: every implementation-eligible partial in the connected set
```

Plan Feature follows the intake partial's canonical parent, sibling map, and
Feature Dependencies in both directions, validates the complete connected set
unchanged, and converges issues for every implementation-eligible member. A
missing, disconnected, or contradictory member blocks the whole run; success
for only the intake partial is invalid.

## Knowledge Delta Single-Run Probe

Any accepted `knowledge_delta` is carried directly through the same complete
bundle run and persisted only on the final integration issue. The proposed
Feature Spec remains payload-free, while the final proposed issue above carries
the exact delta and its implementation-closeout contract. There is no
successful partial planning result that can strand the delta between
invocations. If an apply fails after a Spec becomes durable but before the final
owner issue verifies, the incomplete result returns an exact continuation
handoff containing `feature_slug`, every staged or durable Spec ref, any
applicable multi-repository publication transaction identity, role map, and
reconstructable templates, the selected Idea and prior-outcome refs, the
complete `knowledge_delta`,
completed operations, and exact missing operations. A retry requires that
handoff to match current state and must not reinterpret omission as
`no-durable-change`.

## Expected Pipeline

1. Resolve the sole run control, `write_mode`, and consume tracker/topology
   facts plus any durable `source_spec_ref` from Project Memory and intake
   evidence.
2. Run `$grill-me-with-context` only if the supplied intent and repository
   evidence leave a material blocker; defer domain capture.
3. Produce the complete Feature Spec body and deterministic proposed source
   ref without writing.
4. Split candidate vertical issues, assign scope plus integration and closeout
   ownership, run structural graph compression, then freeze final IDs.
5. Run one or more `$plan-harder` passes per missing final issue; in this
   new-source proposal every final issue is missing. Persist only each final
   stable result, validate the graph, and render exactly one Execution Contract
   per issue.
6. Return bodies, intended repositories, mapped metadata, and topological
   publication order using the deterministic single- or multi-repository
   proposed issue refs from `options.md`. Return no executable publication
   command.
7. State that proposed refs are non-executable and must be replaced by durable
   refs during a later `write_mode=apply` run.

## Expected Publication Order

1. For this fixture, revalidate the mapped `Task` native type and exact
   `ready-for-agent` label, and retain the exact `Issue Type: Feature`
   `body-field` line as final-body data. An applied run creates only a missing
   exact mapped label before dependent mutation; it never substitutes another
   transport when a mapped native type is unavailable.
2. For one directly created Feature Spec, insert the configured final-only
   `body-field` before computing and publishing the final body. For a
   multi-repository bundle, stage every predeclared hosted role that needs a ref
   while excluding that `body-field`; deterministic local refs are already
   resolved. Capture every globally unambiguous durable ref before finalization.
3. Finalize every hosted staged body using only the predeclared qualified-ref
   substitutions, sibling maps, Feature Dependencies, exact final-only
   `body-field` insertion, and staging-marker removal. Verify each final body
   before applying any mapped native type or label. In a mixed-backend bundle,
   keep local bodies unwritten until this point, then write their deterministic
   paths with final qualified refs and verify the complete connected set.
4. Replace every proposed source ref in issue bodies with its owning durable
   ref.
5. Publish ordinary implementation issues in topological order; after each
   final body verifies, apply mapped `Task` through native type and
   `ready-for-agent` through its exact label.
6. Publish the final integration/domain-closeout issue last.
7. Attach every generated issue to its owning Feature Spec when supported.

This sequence is descriptive output only; it contains no executable command.

## Failure Conditions

- Any local file or hosted tracker object is created or changed.
- The output exposes any selectable run control other than `write_mode`.
- A proposed issue is presented as executable before its source ref is durable.
- Existing-source reconciliation rewrites the source, duplicates an exact
  contract-equivalent match, creates an operation not proven missing, treats a
  complete matching bundle as work, repairs an unsupported relationship, or
  continues after a body, graph, or conflicting-metadata mismatch.
- An applied multi-repository sibling or dependency uses a bare hosted issue
  number or bare repo-relative path.
- A proposed issue body contains an applied `workflow_state` header.
- A proposed Feature Spec body contains the applied `Issue Type: Feature`
  body field, a staged body includes it before ref resolution, or finalization
  fails to insert and verify it before native-type or label mutation.
- An issue contains more than one execution projection or omits one of the six
  required normal fields.
- Reverse dependency edges are persisted instead of derived.
- Cross-Feature-Spec dependencies appear in issue dependency IDs.
- Candidate issues are hardened before the structural graph-compression gate
  passes, or issue count is used as a threshold or cap.
- Compression changes the remaining graph but the final domain-closeout
  owner's terminal dependencies are not recomputed.
- A Feature Spec body persists `knowledge_delta` or a
  `## Domain Knowledge Handoff` section.
- A multi-repository bundle omits its distinct integration partial or emits a
  validation-only integration issue that cannot produce a real PR.
- Domain knowledge is captured during planning or assigned to a docs-only
  issue.
- A `knowledge_delta.target_surfaces` entry falls outside the final closeout
  issue's `affected_repositories` or `allowed_paths`.
- Worker permissions, task counts, checkout paths, or App-session settings
  appear in the Feature Spec or issues.
- A machine-local absolute path appears in a body.
- The response includes an executable publication command.
