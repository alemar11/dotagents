# Issue Tracker: Local Markdown

Feature Specs and implementation issues for this repo live as durable Markdown
files under each `planning/features/<feature-slug>/` subtree. Captured Ideas
live as durable Markdown files under `planning/ideas/`.

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `tracker_backend` | enum | `local` | `github`, `local` | Feature Specs, implementation issues, and Ideas are routed to local Markdown files. |

Project Memory stores only tracker routing and conventions. Implementation
delivery, branch/PR strategy, and executor permissions belong to Feature Specs
and executing workflows.

## Publication

- `write_mode=apply`: create or update durable Feature Spec, implementation
  issue, and Idea files at their canonical paths.
- `write_mode=propose`: return proposed bodies, canonical target paths,
  metadata, relationships, and publication order without writing files.

Proposed output may use `source_spec_ref=proposed-spec:<feature-slug>` for one
Feature Spec or
`source_spec_ref=proposed-spec:<feature-id>/<repository-key>` for a linked
multi-repository member. A
proposed ref and any `planning/tmp/` artifact are non-executable and must never
be used as a durable `ready-for-agent` source.

Applied single-repository refs use the repo-relative durable path. Applied
multi-repository members prefix that path with the shared Feature ID and the
owning member's stable repository key, using the canonical
`<feature-id>--<repository-key>/planning/features/<feature-slug>/SPEC.md` shape.
The lower-kebab key is at most 48 characters, unique inside the linked set,
persisted in the member's Planning Identity, and frozen with membership.
For example,
`source_spec_ref=<feature-id>--<repository-key>/planning/features/<feature-slug>/SPEC.md`.
Use the same qualified refs in every member's `Feature Spec Set` and Feature Dependencies.
A bare repo-relative path is invalid across repositories because
identical tracker paths and repository names can exist in unrelated sets.
The qualified ref is a portable set identity, not a physical file path. Decode
it only after the member body proves the exact same Feature ID and repository
key: strip exactly the leading `<feature-id>--<repository-key>/`, yielding
`planning/features/<feature-slug>/SPEC.md`. Resolve that remainder only inside
the separately verified owning repository root. Never join the qualified prefix
to a filesystem root, infer a repository root from it, or use one repository's
decoded path in another repository.

## Conventions

- One feature per directory: `planning/features/<feature-slug>/`
- The Feature Spec is `planning/features/<feature-slug>/SPEC.md`
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
  repository mapping. Require transport `local-header`.
- Workflow state is recorded as a `workflow_state:` line near the top of each
  issue file, using the canonical value loaded from `triage-labels.md` and the
  repository mapping. Require transport `local-header`.
- In a Plan-generated implementation issue, the Feature Spec pointer is
  recorded only in the canonical `## Execution Contract` `source_spec_ref`
  row, never as duplicate header metadata.
- Comments and conversation history append under a `## Comments` heading.
- `$plan-feature` owns Feature Spec and generated issue body shape, including
  `source_spec_ref`, affected repositories and paths, dependency ids, planning
  identity, linked Feature Spec Set refs, and graph validation.
- App-compatible generated issues include the Git repository that owns the
  tracker file in `affected_repositories` and include both the exact active
  issue path and exact derived `done/` path in `allowed_paths`. Both paths must
  resolve inside that repository. A tracker artifact outside every affected Git
  repository is non-App-executable; do not invent
  a tracker owner.
- In scoped-context monorepos, include the accepted product or
  repository scope slug when needed to avoid collisions.
- When a Feature Spec has an accepted Planning Identity, use its
  `feature_slug` rather than deriving a new slug from the title.

### Idea Files

- Store one captured Idea at `planning/ideas/<idea-slug>.md`.
- Use the heading `# Idea: <Name>`.
- In the header metadata region, require exactly one
  `artifact_marker: idea`, zero `issue_type` lines, and zero or one
  `workflow_state` line.
- When present, the Idea workflow state must be one of the two Idea-compatible
  states defined by `triage-labels.md`; the states are mutually exclusive.
- Project Memory setup configures the mapping but never creates an Idea file or
  the `planning/ideas/` directory.

Durable local tracker artifacts live under `planning/features/` or
`planning/ideas/`, not `planning/tmp/`, `.scratch/`, or
`project-memory/features/`. Keep
`project-memory/` for routing, domain, and ADR memory. Temporary artifacts are
caller-owned working data and never durable source references.

Implementation issues created from a Feature Spec normally use
`issue_type: task`. Applied Feature Spec files use the configured local-header
mapping for canonical `feature` and never receive `workflow_state:`. Do not add
`Status: Draft`; workflow state belongs on implementation issues or in tracker
convention.

## Completion Convention

After the consuming implementation workflow provides substantive acceptance,
integration, and any required knowledge-closeout proof, move the issue on the
delivery branch from
`planning/features/<feature-slug>/issues/<NN>-<slug>.md` to
`planning/features/<feature-slug>/issues/done/<NN>-<slug>.md`.

Do not delete completed issue files or add a `done` status. The `done/` folder
is the completion signal; `workflow_state:` remains the lifecycle state for
active issues. Create the folder on demand when completing the first issue.
Commit the move on the declared delivery branch, then rerun every final
validation and review gate invalidated by the new head. A `github-pr` executor
also pushes it and satisfies provider gates; a `local-branch` executor performs
no push or PR and reaches local-branch-ready on the named branch. Project Memory
does not choose between them.

Project Memory records this local tracker lifecycle but does not choose the
implementation stopping point or prescribe its delivery proof.

## Publish And Fetch

For `write_mode=apply`, create or update the durable artifact under
`planning/features/<feature-slug>/`, creating directories as needed. For
`write_mode=propose`, return the would-be durable path and body without writing
it.

For an authorized Idea-capture `write_mode=apply`, create the durable artifact
at `planning/ideas/<idea-slug>.md`; Project Memory setup alone never authorizes
that write. An Idea proposal returns its would-be path and body without writing
it.

To fetch an issue, read the referenced Markdown file. The user normally passes
the path or feature/issue number directly.
