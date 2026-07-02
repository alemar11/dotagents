# Issue Tracker: Local Markdown

PRDs and implementation issues for this repo live as markdown files under
`.scratch/`.

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `tracker_backend` | enum | `local` | `github`, `local` | PRDs and implementation issues are written as local Markdown files. |
| `delivery_mode` | enum | `pull-request` | `pull-request`, `direct-commit` | Implementation publishes from a feature branch and opens a PR. In multi-repo work, every involved repo uses the same branch name and opens its own PR. |

This root `.scratch/` tree is the authoritative local Markdown tracker path. Do
not relocate these feature artifacts under `project-memory/features/` unless the
repo records a custom tracker mode; `project-memory/` remains routing, domain,
and ADR memory.

Feature-planning workflows write PRDs and generated implementation issues to
the configured local Markdown tracker by default after setup, planning identity,
and blockers are resolved. They do not need a separate per-run confirmation to
create those files unless the current request explicitly asks for dry-run or
no-mutation output.

Current-run override: treat any temp, dry-run, rehearsal, or disabled-write
constraint as run-specific behavior. Do not record it as a durable
issue-tracker configuration row.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The PRD is `.scratch/<feature-slug>/PRD.md`
- Implementation issues are `.scratch/<feature-slug>/issues/<NN>-<slug>.md`,
  numbered from `01`
- Implementation issue headings use:
  `<feature-slug>: <NN> <vertical outcome>`
- Completed implementation issues move to
  `.scratch/<feature-slug>/issues/done/<NN>-<slug>.md`
- Create `issues/done/` only when moving the first completed issue into it.
- Issue type is recorded as a `Type:` line near the top of each issue file,
  using the type strings from `project-memory/agents/triage-labels.md`
- Triage state is recorded as a `Status:` line near the top of each issue file,
  using the state strings from `project-memory/agents/triage-labels.md`
- Comments and conversation history append under a `## Comments` heading
- `$plan-feature` owns PRD and generated issue body shape, including `Source
  PRD`, delivery metadata, partial-PRD links, and issue graph validation.
- In multi-context repos or monorepos, feature slugs must include the accepted
  product or workspace slug when needed to avoid collisions, for example
  `customer-portal-weekly-digest` instead of `weekly-digest`.
- When a PRD has an accepted `Planning Identity`, use that `feature_slug`
  rather than deriving a new slug from the PRD title.

## Delivery Defaults

- Default `delivery_mode`: `pull-request`.
- Branch naming: default to `feature/<feature-slug>`.
- PR shape: one draft PR for a single repo or monorepo feature when the work is
  later published. In multi-repo work, every involved repo uses the same branch
  name and opens its own PR. Local issue files are scheduling units and move to
  `issues/done/` only after validation and the configured proof are complete.
- Direct-commit shape: `direct-commit` is delivery proof, not the local issue
  lifecycle. Implement on the current branch, validate, commit, record the
  commit/proof in the issue or ledger, then move the local issue file to
  `issues/done/` unless the current run explicitly asks to keep completed issue
  files in place for inspection.
- Multi-repo PRD shape: use a single PRD only when that is the accepted
  planning source. Otherwise use linked repo-scoped partial PRDs or generated
  issue files; each one names its affected repo and links the siblings that
  define the same feature. A global PRD is not required as durable setup
  configuration.
- Exceptions: `direct-commit` only with explicit maintainer authorization.

## Runtime Boundary

- Tracker setup records artifact routing, delivery-mode defaults, and closeout
  conventions only.
- If an existing setup file contains the legacy worker-authorization setup key,
  treat it as stale state and remove it when touching the file.

Implementation issues created from a PRD usually use `Type: task`. PRD files
do not need `Type:` or `Status:` lines unless the repo chooses to treat PRDs as
local feature issues. Do not add `Status: Draft` to ordinary PRD files;
workflow status belongs on implementation issues or in the tracker convention.

## Completion

When all acceptance criteria pass and validation is complete, move the issue
file from `.scratch/<feature-slug>/issues/<NN>-<slug>.md` to
`.scratch/<feature-slug>/issues/done/<NN>-<slug>.md`.

For `delivery_mode: direct-commit`, commit on the authorized current branch and
record the commit/proof before moving the issue file. Use
`local-done-move-after-proof` as the local markdown closeout mode even when the
delivery mode is `direct-commit`; `direct-commit-closes-issue` is not a local
markdown lifecycle signal.

Do not delete completed issue files. Do not add a `done` status; the
`issues/done/` folder is the completion signal, while `Status:` remains the
triage/workflow state used for active issues. If `issues/done/` does not
exist yet, create it when completing the first issue.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/`, creating the directory if
needed. If a current-run no-mutation override is active, return draft file paths
and bodies instead of writing local tracker files.

## When a skill says "fetch the relevant issue"

Read the referenced markdown file. The user will normally pass the path or
feature/issue number directly.
