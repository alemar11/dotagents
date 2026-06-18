# Issue Tracker: Local Markdown

PRDs and implementation issues for this repo live as markdown files under
`.scratch/`.

Tracker mode: `local-markdown`
Local PRD path pattern: `.scratch/<feature-slug>/PRD.md`
Local issue path pattern: `.scratch/<feature-slug>/issues/<NN>-<slug>.md`
Done issue path pattern: `.scratch/<feature-slug>/issues/done/<NN>-<slug>.md`
External mutation policy: local files only unless the user explicitly
authorizes a hosted tracker in the current run.

Current-run override: record any temp, dry-run, rehearsal, or no-external
constraint here. Do not treat a current-run override as a durable tracker
preference change unless the user explicitly says to make it persistent.

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
- Each implementation issue body includes `Source PRD:` pointing to
  `.scratch/<feature-slug>/PRD.md`.
- Each implementation issue body should include an `Execution plan` pointer to
  `.scratch/<feature-slug>/execution-plan.md` when local artifact runs are in
  scope.
- Each implementation issue body includes `## Delivery` with issue-level
  `Parallelization` and `Closeout`.
- Each implementation issue body copies the effective PRD `Delivery mode` and
  labels it as feature-level metadata inherited from `Source PRD`, for example
  `Delivery mode: One Feature Branch (feature-level, inherited from Source
  PRD)`. Feature-level means the mode applies to the whole Source PRD feature.
- Add issue-level `Delivery mode` or `Integration mode` exception lines only
  when the issue intentionally differs from the PRD, and include the
  authorization or reason.
- In multi-context repos or monorepos, feature slugs must include the accepted
  product or workspace slug when needed to avoid collisions, for example
  `customer-portal-weekly-digest` instead of `weekly-digest`.
- When a PRD has an accepted `Planning Identity`, use that `feature_slug`
  rather than deriving a new slug from the PRD title.

## Delivery Mode Defaults

- Default delivery mode: **One Feature Branch** for a single project or monorepo in
  this git repo.
- Branch naming: default to `feature/<feature-slug>`.
- PR shape: one draft PR for the feature when the work is later published.
  Local issue files are scheduling units and move to `issues/done/` only after
  validation and the configured proof are complete.
- Exceptions: **One PR Per Issue** only for isolated work; **Direct Commit**
  only with explicit maintainer authorization.

Implementation issues created from a PRD usually use `Type: task`. PRD files
do not need `Type:` or `Status:` lines unless the repo chooses to treat PRDs as
local feature issues. Do not add `Status: Draft` to ordinary PRD files;
workflow status belongs on implementation issues or in the tracker convention.

## Completion

When all acceptance criteria pass and validation is complete, move the issue
file from `.scratch/<feature-slug>/issues/<NN>-<slug>.md` to
`.scratch/<feature-slug>/issues/done/<NN>-<slug>.md`.

Do not delete completed issue files. Do not add a `done` status; the
`issues/done/` folder is the completion signal, while `Status:` remains the
triage/workflow state used for active issues. If `issues/done/` does not
exist yet, create it when completing the first issue.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/`, creating the directory if
needed. If a current-run override disallows external mutation, this local write
target is the effective target only when local file writes are authorized.

## When a skill says "fetch the relevant issue"

Read the referenced markdown file. The user will normally pass the path or
feature/issue number directly.
