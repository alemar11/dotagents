# Issue Tracker: Local Markdown

Feature Specs and implementation issues for this repo live as durable Markdown
files under each `planning/features/<feature-slug>/` subtree.

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `tracker_backend` | enum | `local` | `github`, `local` | Feature Specs and implementation issues are routed to local Markdown files. |

Project Memory stores only tracker routing and conventions. Implementation
delivery, branch/PR strategy, and executor permissions belong to Feature Specs
and executing workflows.

## Publication

- `write_mode=apply`: create or update durable Feature Spec and issue files at
  their canonical paths.
- `write_mode=propose`: return proposed bodies, canonical target paths,
  metadata, relationships, and publication order without writing files.

Proposed output may use `source_spec_ref=proposed-spec:<feature-slug>` for one
Feature Spec,
`source_spec_ref=proposed-spec:<project-slug>/<feature-slug>` for a
multi-repository parent, or
`source_spec_ref=proposed-spec:<project-slug>/<feature-slug>/<repository-slug>`
for a repo-scoped implementation partial, or
`source_spec_ref=proposed-spec:<project-slug>/<feature-slug>/<repository-slug>/integration`
for a dedicated integration partial until that Feature Spec is written. A
proposed ref and any `planning/tmp/` artifact are non-executable and must never
be used as a durable `ready-for-agent` source.

Applied single-repository refs use the repo-relative durable path. Applied
multi-repository partials prefix that path with the owning repository slug,
using the canonical `<repository-slug>/<repo-relative-spec-path>` shape. For
example,
`source_spec_ref=<repository-slug>/planning/features/<feature-slug>/SPEC.md` or
`source_spec_ref=<repository-slug>/planning/features/<feature-slug>/integration/SPEC.md`.
Use the same qualified refs in repo-to-child mappings, sibling links, and
Feature Dependencies. A bare repo-relative path is invalid across sibling
repositories because identical tracker paths can exist in more than one child.

## Conventions

- One feature per directory: `planning/features/<feature-slug>/`
- The Feature Spec is `planning/features/<feature-slug>/SPEC.md`
- A dedicated integration partial in the same repository is
  `planning/features/<feature-slug>/integration/SPEC.md`; its issues are
  `planning/features/<feature-slug>/integration/issues/<NN>-<slug>.md` and its
  completed issues move under the matching `integration/issues/done/`
  subtree. It never reuses the implementation partial's `SPEC.md` or
  `issues/` paths.
- Implementation issues are
  `planning/features/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Implementation issue headings use:
  `<feature-slug>: <NN> <vertical outcome>`
- Completed implementation issues move to
  `planning/features/<feature-slug>/issues/done/<NN>-<slug>.md`
- Create `planning/features/<feature-slug>/issues/done/` only when moving the
  first completed issue into it.
- Issue type is recorded as an `issue_type:` line near the top of each issue
  file, using the canonical value loaded from `triage-labels.md` and the
  repository mapping.
- Workflow state is recorded as a `workflow_state:` line near the top of each
  issue file, using the canonical value loaded from `triage-labels.md` and the
  repository mapping.
- In a Plan-generated implementation issue, the Feature Spec pointer is
  recorded only in the canonical `## Execution Contract` `source_spec_ref`
  row, never as duplicate header metadata.
- Comments and conversation history append under a `## Comments` heading.
- `$plan-feature` owns Feature Spec and generated issue body shape, including
  `source_spec_ref`, affected repositories and paths, dependency ids, planning
  identity, partial Feature Spec links, and graph validation.
- App-compatible generated issues include the Git repository that owns the
  tracker file in `affected_repositories` and include both the exact active
  issue path and exact derived `done/` path in `allowed_paths`. Both paths must
  resolve inside that repository. A tracker artifact at a non-Git workspace root
  or outside every affected Git repository is non-App-executable; do not invent
  a tracker owner.
- In scoped-context monorepos, include the accepted product or
  workspace slug when needed to avoid collisions.
- When a Feature Spec has an accepted Planning Identity, use its
  `feature_slug` rather than deriving a new slug from the title.

Durable local tracker artifacts live under `planning/features/`, not
`planning/tmp/`, `.scratch/`, or `project-memory/features/`. Keep
`project-memory/` for routing, domain, and ADR memory. Temporary artifacts are
caller-owned working data and never durable source references.

Implementation issues created from a Feature Spec normally use
`issue_type: task`. Feature Spec files do not need `issue_type:` or
`workflow_state:` unless the repo intentionally treats them as local feature
issues. Do not add `Status: Draft`; workflow state belongs on implementation
issues or in tracker convention.

## Completion Convention

After the consuming implementation workflow provides substantive acceptance,
integration, and any required knowledge-closeout proof, move the issue on the
delivery branch from
`planning/features/<feature-slug>/issues/<NN>-<slug>.md` to
`planning/features/<feature-slug>/issues/done/<NN>-<slug>.md`.

For a dedicated integration partial, move the issue from
`planning/features/<feature-slug>/integration/issues/<NN>-<slug>.md` to
`planning/features/<feature-slug>/integration/issues/done/<NN>-<slug>.md`.
Derive the completion target from the owning issue subtree; never move an
integration issue into the ordinary feature's `issues/done/` directory.

Do not delete completed issue files or add a `done` status. The `done/` folder
is the completion signal; `workflow_state:` remains the lifecycle state for
active issues. Create the folder on demand when completing the first issue.
Commit and push the move as part of the delivery change set, then rerun final
validation, review, and CI gates invalidated by the new head. Until the later PR
merge lands that path on the default branch, closeout is prepared rather than
globally completed.

Project Memory records this local tracker lifecycle but does not choose the
implementation stopping point or prescribe its delivery proof.

## Publish And Fetch

For `write_mode=apply`, create or update the durable artifact under
`planning/features/<feature-slug>/`, creating directories as needed. For
`write_mode=propose`, return the would-be durable path and body without writing
it. A dedicated integration partial uses the distinct `integration/` subtree
in the evidence-derived owner repository; it does not require a coordination
repository.

To fetch an issue, read the referenced Markdown file. The user normally passes
the path or feature/issue number directly.
