# Issue Tracker: GitHub

PRDs and implementation issues for this repo live as GitHub issues. Use
`$github-issues` for GitHub issue lifecycle operations.

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `tracker_backend` | enum | `github` | `github`, `local` | PRDs and implementation issues are written as GitHub issues. |
| `delivery_mode` | enum | `pull-request` | `pull-request`, `direct-commit` | Implementation publishes from a feature branch and opens a PR. In multi-repo work, every involved repo uses the same branch name and opens its own PR. |

GitHub is the authoritative artifact store in this mode. Do not create or keep
repo-local `.scratch/` PRD/issue mirrors, `project-memory/features/` mirrors, or
other local planning copies merely to feed `gh --body-file`. Temporary body
files must live outside the repo and be removed after mutation unless the user
explicitly asks to keep a local mirror.

Feature-planning workflows write to GitHub by default in this mode after setup,
planning identity, and blockers are resolved. They do not need a separate
per-run confirmation to create PRD or generated implementation issues unless the
current request explicitly asks for dry-run or no-mutation output.

## Non-Mutating Runs

If this setup is being used for a temp exercise, validation pass, rehearsal,
dry run, or any workflow where tracker writes are explicitly disabled, do not
mutate GitHub. Use local markdown only when a local dry-run target is configured
or explicitly chosen for that run, or ask `$github-issues` to return draft issue
bodies and exact `gh` commands without executing them.
When returning draft commands before the PRD issue exists, use
`source_prd_ref=draft-prd:<feature-slug>` and publish the PRD first; generated
issue bodies must replace that draft ref with `Source PRD: #<prd-number>` before
hosted mutation.
Treat any non-mutating choice as a current-run override. Do not record it as a
durable issue-tracker configuration row.

## Conventions

Infer the repo from `git remote -v` unless this file records a specific target.
Use `$github-issues` to create, read, edit, comment on, label, type, attach, or
close GitHub issues.

Use `project-memory/agents/triage-labels.md` for type and label mappings. The
default GitHub issue types are:

- `Bug` for `bug`
- `Feature` for `feature`
- `Task` for `task`

The default GitHub workflow-state labels are lowercase tracker values:

- `needs-triage` for `needs-triage`
- `needs-info` for `needs-info`
- `ready-for-agent` for `ready-for-agent`
- `ready-for-human` for `ready-for-human`
- `wontfix` for `wontfix`

If GitHub issue types are disabled or customized for the organization, record
the actual available values or fallback label convention in
`project-memory/agents/triage-labels.md`.

## Delivery Defaults

- Default `delivery_mode`: `pull-request`.
- Branch naming: default to `feature/<feature-slug>`.
- PR shape: one draft PR for a single repo or monorepo feature. In multi-repo
  work, every involved repo uses the same branch name and opens its own PR.
  Generated implementation issues are scheduling units and normally close from
  the relevant PR body.
- Multi-repo PRD shape: use a single PRD only when that is the accepted
  planning source. Otherwise use linked repo-scoped partial PRDs or generated
  issues; each one names its affected repo and links the siblings that define
  the same feature. No central repo, central issue, project label, or global
  PRD is required as durable setup configuration.
- Exceptions: `direct-commit` only with explicit maintainer authorization.

## Runtime Boundary

- Tracker setup records artifact routing, delivery-mode defaults, and closeout
  conventions only.
- If an existing setup file contains the legacy worker-authorization setup key,
  treat it as stale state and remove it when touching the file.

## Title Format

- PRD issue: `PRD: <Feature Name>`
- Implementation issue: `<feature-slug>: <NN> <vertical outcome>`

Use the accepted lowercase kebab-case `<feature-slug>` from `$plan-feature`,
the PRD planning identity, or the PRD source path. Derive it from the PRD title
only when no accepted slug exists. Use two-digit ordering (`01`, `02`, `03`)
for implementation issues so the global issue list remains scannable even
outside the PRD sub-issue view.

## When a skill says "publish to the issue tracker"

Use `$github-issues` to create a GitHub issue.

For feature planning:

- The PRD is a GitHub issue titled `PRD: <Feature Name>` with type `Feature`
  unless the repo maps `feature` to a different value.
- Generated implementation issues are the execution graph. Do not create a
  separate execution-plan issue unless the user explicitly requests a
  non-authoritative summary.
- Implementation issues are GitHub sub-issues of the PRD issue with type
  `Task` unless the repo maps `task` to a different value.
- Implementation issue titles use
  `<feature-slug>: <NN> <vertical outcome>`.
- `$plan-feature` owns PRD and generated issue body shape, including `Source
  PRD`, delivery metadata, partial-PRD links, and issue graph validation.

For triage:

- Existing bug reports should use the mapped `bug` type.
- Existing feature or enhancement requests should use the mapped `feature`
  type.
- Existing maintenance, docs, cleanup, follow-up, or implementation work items
  should use the mapped `task` type.
- Workflow state belongs in the mapped triage labels, not in the GitHub issue
  type.

## Completion

When all acceptance criteria pass and validation is complete, close that
implementation issue from the relevant PR body with a GitHub closing keyword
such as `Closes #<issue-number>`. For the default `pull-request` delivery mode,
the relevant feature or repo PR closes generated implementation issues.
Final-commit closure is allowed only when the issue records `direct-commit` or another
explicit maintainer authorization. The issue closes when that PR or authorized
commit reaches the default branch.

Use closing keywords only for issues actually satisfied by the change. Do not
close the parent PRD issue from a child implementation issue unless the
maintainer explicitly says the whole PRD is complete.

## When a skill says "fetch the relevant issue"

Use `$github-issues` to view the issue and recent comments.
