# Issue Tracker: Local Markdown

Feature Specs and implementation issues for this repo live as durable Markdown
files under each `planning/features/<feature-slug>/` subtree. The
`planning/tmp/` tree is temporary working space only.

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `tracker_backend` | enum | `local` | `github`, `local` | Feature Specs and implementation issues are written as local Markdown files. |
| `change_delivery_target` | enum | `pull-request-ready-for-merge-but-not-merged` | `local-commit-created-without-pushing`, `changes-pushed-to-target-branch-without-pull-request`, `validated-draft-pull-request-published`, `pull-request-ready-for-merge-but-not-merged` | Exact implementation stopping point. Merge is never implied. |

Durable local tracker artifacts must live under `planning/features/`, not
`planning/tmp/`, `.scratch/`, or `project-memory/features/`. Keep `project-memory/` for
routing, domain, and ADR memory. Keep `planning/tmp/` for dry-run output,
rehearsal files, temporary body files, fingerprints, and comparison snapshots
that are safe to delete after the run.

Feature-planning workflows write Feature Specs and generated implementation issues to
the configured local Markdown tracker by default after setup, planning identity,
and blockers are resolved. Branch only on the canonical `effective_target`:
`configured-tracker` writes tracker files and `local-dry-run` returns draft
paths and bodies without writing them.

A non-mutating run requires a non-`none` `no_mutation_override`,
`no_mutation_output=local-artifacts`, and
`effective_target=local-dry-run`. Do not record these run-scoped rows as
durable issue-tracker configuration.

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
  file, using canonical `bug`, `feature`, or `task`.
- Triage state is recorded as a `workflow_state:` line near the top of each
  issue file, using the canonical values from the Triage option contract.
- The Feature Spec pointer is recorded as `source_spec_ref:` reference data.
- Comments and conversation history append under a `## Comments` heading
- `$plan-feature` owns Feature Spec and generated issue body shape, including
  `source_spec_ref`, delivery metadata, partial Feature Spec links, and issue graph
  validation. Local issue metadata must use canonical `issue_type`,
  `workflow_state`, and `source_spec_ref` fields.
- In multi-context repos or monorepos, feature slugs must include the accepted
  product or workspace slug when needed to avoid collisions, for example
  `customer-portal-weekly-digest` instead of `weekly-digest`.
- When a Feature Spec has an accepted `Planning Identity`, use that `feature_slug`
  rather than deriving a new slug from the Feature Spec title.

## Delivery Defaults

- Default `change_delivery_target`:
  `pull-request-ready-for-merge-but-not-merged`.
- Branch naming: for either pull-request target, default to
  `feature/<feature-slug>`. Commit-only and push-without-PR targets use the exact
  branch carried by scoped authorized-user evidence.
- PR shape: one draft PR for a single repo or monorepo feature when the work is
  later published. In multi-repo work, every involved repo uses the same branch
  name and opens its own PR. Local issue files are scheduling units and move to
  `issues/done/` only after validation and the configured proof are complete.
- Commit-only shape: `local-commit-created-without-pushing` is delivery proof,
  not the local issue lifecycle. Implement on the named branch, validate,
  commit without pushing, record proof, then move the local issue to
  `issues/done/`.
- Push-without-PR shape:
  `changes-pushed-to-target-branch-without-pull-request` validates, commits,
  pushes the named branch, records proof, then moves the local issue to
  `issues/done/`.
- Multi-repo Feature Spec shape: use a single Feature Spec only when that is the accepted
  planning source. Otherwise use linked repo-scoped partial Feature Specs or generated
  issue files; each one names its affected repo and links the siblings that
  define the same feature. A global Feature Spec is not required as durable setup
  configuration.
- Exceptions: either non-PR target requires
  `source=authorized-user-instruction` plus exact feature-scope and target-branch
  evidence, or a `source-spec` row preserving that evidence.
- Local issue completion uses `issue_update_permission=no-issue-changes`;
  delivery proof
  never grants a hosted-style final-commit closure.

## Runtime Boundary

- Tracker setup records artifact routing, delivery-target defaults, and closeout
  conventions only.

Implementation issues created from a Feature Spec usually use `issue_type: task`. Feature Spec
files do not need `issue_type:` or `workflow_state:` lines unless the repo
chooses to treat Feature Specs as local feature issues. Do not add `Status: Draft` to
ordinary Feature Spec files;
workflow status belongs on implementation issues or in the tracker convention.

## Completion

When all acceptance criteria pass and validation is complete, move the issue
file from `planning/features/<feature-slug>/issues/<NN>-<slug>.md` to
`planning/features/<feature-slug>/issues/done/<NN>-<slug>.md`.

For `change_delivery_target: local-commit-created-without-pushing`, commit on
the authorized branch without pushing and record proof before moving the issue
file. For `changes-pushed-to-target-branch-without-pull-request`, additionally
record remote-branch proof. Use
`issue_completion_method=move-local-issue-to-done-after-proof` for both; a
hosted final-commit closing keyword is not a local Markdown lifecycle signal.

Do not delete completed issue files. Do not add a `done` status; the
`done/` folder is the completion signal, while `workflow_state:` remains the
lifecycle state used for active issues. If the feature's `done/` folder does
not exist yet, create it when completing the first issue.

## When a skill says "publish to the issue tracker"

Create or update the durable Feature Spec or issue file under
`planning/features/<feature-slug>/`, creating directories as needed for
`effective_target=configured-tracker`. For
`effective_target=local-dry-run`, return bodies and either the would-be durable
target path or a clearly temporary `planning/tmp/<feature-slug>/...` draft
path without writing local tracker files. Never use a `planning/tmp/` or
`.scratch/` path as a durable `source_spec_ref` or `ready-for-agent`
issue location.

## When a skill says "fetch the relevant issue"

Read the referenced markdown file. The user will normally pass the path or
feature/issue number directly.
