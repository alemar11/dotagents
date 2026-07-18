# Issue Tracker: GitHub

Feature Specs, implementation issues, and captured Ideas for this repo live as
GitHub issues.
Use `$gitstack:github-issues` for GitHub issue lifecycle operations.

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `tracker_backend` | enum | `github` | `github`, `local` | Feature Specs, implementation issues, and Ideas are routed to GitHub. |

GitHub is the authoritative artifact store in this mode. Project Memory stores
only tracker routing and conventions; implementation delivery, branch/PR
strategy, and executor permissions belong to Feature Specs and executing
workflows.

Do not create repo-local planning mirrors merely to feed hosted mutations.
Temporary body files must live outside the repo and be removed after use.

## Publication

- `write_mode=apply`: use `$gitstack:github-issues` to create or update issues,
  relationships, types, and labels. Normalize each write to
  `mutation_mode=apply`, the exact repository/issue target, and one canonical
  `issue_operation`, then verify hosted state.
- `write_mode=propose`: return proposed titles, bodies, metadata,
  relationships, and publication order without mutating GitHub or returning
  executable commands.

When proposed output precedes the hosted Feature Spec, use
`source_spec_ref=proposed-spec:<feature-slug>` for one Feature Spec,
`proposed-spec:<project-slug>/<feature-slug>` for a multi-repository parent, or
`proposed-spec:<project-slug>/<feature-slug>/<repository-slug>` for each
repo-scoped implementation partial. A dedicated integration partial uses
`proposed-spec:<project-slug>/<feature-slug>/<repository-slug>/integration`.
Order the proposal so each owning Feature Spec is created before its issues.
Before hosted child creation, replace that proposed ref in the child's canonical
`## Execution Contract` `source_spec_ref` row with the owning
`#<spec-number>` for a single-repository bundle, or with
`owner/repository#<spec-number>` or its canonical hosted URL for a
multi-repository partial. Use the same globally qualified identity in
repo-to-child mappings, sibling links, and cross-repository Feature Dependency
rows. Never treat a proposed ref as an executable source, use a bare issue
number across repositories, or add a duplicate header field.

On apply, a dedicated integration partial is a second hosted Feature Spec in
its evidence-derived owner repository. Give it the distinct title
`Feature Spec: <Feature Name> - Integration`, retain
`Partial role: integration` in its Planning Identity, and use its own hosted
issue number, expressed as an `owner/repository#<number>` ref or canonical
hosted URL, as the durable `source_spec_ref`. It must not reuse the ordinary
implementation partial's title, body identity, or issue number. Selecting an
integration owner does not require a coordination repository.

## Conventions

Infer the repo from `git remote -v` unless this file records a specific target.
Use `$gitstack:github-issues` to create, read, edit, comment on, label, type,
attach, or close GitHub issues.

For a mutation, pass `mutation_mode=apply`, the exact repository/issue target,
and one canonical `issue_operation`. A read or proposal supplies no mutation
authority and must not be upgraded at this boundary.

Load canonical issue types and workflow states only from
`references/triage-labels.md`, then use the concrete tracker mappings in
`project-memory/config/triage-labels.md`. This tracker reference does not repeat
that registry. If GitHub issue types are disabled or customized for the
organization, record the actual available values or fallback label convention
in the repository mapping file.

Load canonical artifact markers from the same registry and repository mapping.
If the `idea` marker mapping is missing, block only Idea capture and Idea-source
consumption; Feature Spec and implementation-issue workflows remain valid.

## Title Format

- Feature Spec issue: `Feature Spec: <Feature Name>`
- Integration Feature Spec issue: `Feature Spec: <Feature Name> - Integration`
- Implementation issue: `<feature-slug>: <NN> <vertical outcome>`
- Idea issue: `Idea: <Name>`

Use the accepted lowercase kebab-case `<feature-slug>` from `$plan-feature`,
the Feature Spec planning identity, or the Feature Spec source path. Derive it
from the title only when no accepted slug exists. Use two-digit ordering
(`01`, `02`, `03`) for implementation issues.

## Idea Capture

Represent a durable Idea as an open, untyped GitHub issue titled
`Idea: <Name>`. Apply the repository mapping for `artifact_marker: idea`, whose
default tracker value is the `idea` label, and leave the native GitHub Issue
Type unset.

A dormant Idea has the marker label and no workflow-state label. An Idea that
is queued for evaluation or waiting on requester input may carry exactly one
Idea-compatible mapped workflow-state label from `triage-labels.md`. Those
states are mutually exclusive; no other canonical workflow state is valid for
an Idea. Project Memory setup configures these mappings but does not create
Idea issues.

## Feature Planning

- Resolve every artifact's issue type by role from
  `references/triage-labels.md` and the repository mapping immediately before
  publication. Do not hard-code canonical or tracker-specific type values in
  this reference.
- Publish the Feature Spec as a GitHub issue titled
  `Feature Spec: <Feature Name>`.
- Publish a dedicated integration partial, when present, as a separate GitHub
  issue titled `Feature Spec: <Feature Name> - Integration`, with
  `Partial role: integration` in its body.
- Treat generated implementation issues as the execution graph. Do not create
  a separate execution-plan issue.
- Publish implementation issues as sub-issues of the Feature Spec with titles
  using the format above.
- `$plan-feature` owns Feature Spec and generated issue body shape, including
  `source_spec_ref`, affected repositories and paths, dependency ids, planning
  identity, partial Feature Spec links, and graph validation.
- For multi-repo planning, use one accepted parent when appropriate or link
  repo-scoped partial Feature Specs and issues. Do not persist a coordination
  repo or global project label as setup configuration.

## Existing Issue Classification

When a caller classifies an existing issue, load the canonical issue types,
workflow states, and their selection semantics from
`references/triage-labels.md`, then resolve their concrete GitHub mappings from
`project-memory/config/triage-labels.md`. Workflow state belongs in the mapped
labels, not the GitHub issue type. This reference defines no additional type or
state values.

## Completion Convention

Use a GitHub closing keyword only when the consuming implementation workflow
has proved that the referenced issue is satisfied. The issue closes when the
closing change reaches the default branch. Do not close a parent Feature Spec
from an individual child issue; a final integration change may close it only
after all Feature Spec gates pass.

This implementation-proof convention applies to Feature Specs and
implementation issues. A source Idea follows the separate Plan Feature
consumption contract: after the complete requested planning result is durable
and verified, Plan Feature may close an Idea that it determined was fully
covered, retaining the Idea marker and recording the authoritative Feature
Spec refs. A partially covered Idea remains open.

Project Memory records this tracker convention but does not choose the
implementation stopping point, grant issue-mutation authority, or prescribe a
branch/PR workflow.

## Fetch

Use `$gitstack:github-issues` to view the issue and recent comments.
