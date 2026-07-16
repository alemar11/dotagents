# Full-Flow Propose Fixture

Use this fixture to forward-test the complete planning pipeline without local
or hosted writes.

## User Request

```text
Use $plan-feature to plan a feature named "account settings export". Show me
the complete Feature Spec and implementation issues before publishing them.
Do not write files or mutate GitHub.
```

## Resolved Run

```text
mode: full-flow
write_mode: propose

Project Memory facts:
  tracker_backend: github
  repository_layout: single-repository

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

## Proposed Feature Spec Result

- Title: `Feature Spec: Account Settings Export`
- Intended repository: current repository
- Intended tracker: GitHub
- Intended type: mapped `feature`
- Proposed source ref: `proposed-spec:account-settings-export`
- Feature dependencies: empty table body
- App compatibility: compatible after publication replaces the proposed source
  ref with a durable hosted ref
- Domain capture: the non-persisted run delta is deferred to the final
  integration issue; the Feature Spec body carries no payload
- Proposed issue ref: `proposed-issue:account-settings-export/01`
- Final proposed issue ref: `proposed-issue:account-settings-export/02`
- Intended tracker metadata after apply: mapped type `task`, state
  `ready-for-agent`

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

## Representative Proposed Issue

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

## Spec-Only Delta Persistence Probe

This two-invocation probe prevents a deferred delta from disappearing behind a
durable payload-free Spec:

```text
invocation_1:
  mode: spec-only
  write_mode: apply
  knowledge_delta: nonempty
  writes: none
  durable_source_created: false
  result: blocked non-durable preview with exact delta
  next_action: explicit full-flow run

invocation_2:
  source_from_invocation_1: unavailable
  issues_from_existing_spec: impossible from invocation 1
  rule: never treat the blocked preview as a durable no-delta Spec
```

The same write withholding applies to `write_mode=propose`; that mode already
writes nothing, and the preview remains blocked from later publication. A later
`full-flow` invocation must receive the exact delta again so its final issue can
be the durable owner.

## Expected Pipeline

1. Resolve the two run fields and consume tracker/topology facts from Project
   Memory.
2. Run `$grill-me-with-context` only if the supplied intent and repository
   evidence leave a material blocker; defer domain capture.
3. Produce the complete Feature Spec body and deterministic proposed source
   ref without writing.
4. Split vertical issues, stabilize scope and graph, run one or more
   `$plan-harder` passes per issue, persist only each final stable result,
   validate the graph, and render exactly one Execution Contract per issue.
5. Return bodies, intended repositories, mapped metadata, and topological
   publication order using the deterministic single- or multi-repository
   proposed issue refs from `options.md`. Return no executable publication
   command.
6. State that proposed refs are non-executable and must be replaced by durable
   refs during a later `write_mode=apply` run.

## Expected Publication Order

1. Publish the Feature Spec, or the parent then every repo-scoped
   implementation partial for a multi-repository bundle, and capture each
   globally unambiguous durable ref.
2. Publish the dedicated integration partial after its upstream partial refs
   are durable, then update sibling maps and Feature Dependencies with those
   same qualified refs.
3. Replace every proposed source ref in issue bodies with its owning durable
   ref.
4. Publish ordinary implementation issues in topological order.
5. Publish the final integration/domain-closeout issue last.
6. Attach every generated issue to its owning Feature Spec when supported.

This sequence is descriptive output only; it contains no executable command.

## Failure Conditions

- Any local file or hosted tracker object is created or changed.
- The output exposes more than the two registered run choices.
- A proposed issue is presented as executable before its source ref is durable.
- An applied multi-repository sibling or dependency uses a bare hosted issue
  number or bare repo-relative path.
- A proposed issue body contains an applied `workflow_state` header.
- An issue contains more than one execution projection or omits one of the six
  required normal fields.
- Reverse dependency edges are persisted instead of derived.
- Cross-Feature-Spec dependencies appear in issue dependency IDs.
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
