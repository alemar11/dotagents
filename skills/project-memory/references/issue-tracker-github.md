# Issue Tracker: GitHub

PRDs and implementation issues for this repo live as GitHub issues. Use
`$gitstack:github-issues` for GitHub issue lifecycle operations.

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `tracker_backend` | enum | `github` | `github`, `local` | PRDs and implementation issues are written as GitHub issues. |
| `delivery_mode` | enum | `pull-request` | `pull-request`, `direct-commit` | Implementation publishes from a feature branch and opens a PR. In multi-repo work, every involved repo uses the same branch name and opens its own PR. |

GitHub is the authoritative artifact store in this mode. Do not create or keep
repo-local `.scratch/` PRD/issue mirrors, `project-memory/features/` mirrors, or
other local planning copies merely to feed `gh --body-file`. Temporary body
files must live outside the repo and be removed after mutation. Create a
persistent mirror only when the canonical Plan Feature rows contain
`local_mirror=requested` and a validated `local_mirror_path`.

Feature-planning workflows write to GitHub by default in this mode after setup,
planning identity, and blockers are resolved. Branch only on the canonical
`effective_target`: `configured-tracker` writes to GitHub,
`draft-publish-commands` returns exact draft commands, and `local-dry-run`
returns non-executable local artifacts.

## Non-Mutating Runs

Require a non-`none` `no_mutation_override` before either non-mutating target.
For `effective_target=local-dry-run`, return local paths and bodies without
writing GitHub. For `effective_target=draft-publish-commands`, ask
`$gitstack:github-issues` for draft issue bodies and exact `gh` commands without
executing them.
When returning draft commands before the PRD issue exists, use
`source_prd_ref=draft-prd:<feature-slug>` and publish the PRD first; generated
issue bodies must replace that draft ref with `source_prd_ref: #<prd-number>` before
hosted mutation.
Treat `no_mutation_override`, `no_mutation_output`, and the derived
non-mutating target as run-scoped rows. Do not record them as durable
issue-tracker configuration.

## Conventions

Infer the repo from `git remote -v` unless this file records a specific target.
Use `$gitstack:github-issues` to create, read, edit, comment on, label, type, attach, or
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
- Branch naming: for `delivery_mode=pull-request`, default to
  `feature/<feature-slug>`. For `delivery_mode=direct-commit`, use the exact
  target branch carried by the scoped owner evidence.
- PR shape: one draft PR for a single repo or monorepo feature. In multi-repo
  work, every involved repo uses the same branch name and opens its own PR.
  Generated implementation issues are scheduling units and normally close from
  the relevant PR body.
- Multi-repo PRD shape: use a single PRD only when that is the accepted
  planning source. Otherwise use linked repo-scoped partial PRDs or generated
  issues; each one names its affected repo and links the siblings that define
  the same feature. No central repo, central issue, project label, or global
  PRD is required as durable setup configuration.
- Exceptions: `delivery_mode=direct-commit` requires
  `source=owner-instruction` plus exact feature-scope and target-branch
  evidence, or a `source-prd` row preserving that evidence. Final-commit issue
  closure additionally requires a separate
  `issue_mutation_authority=explicit-direct-mutation` row whose owner evidence
  explicitly authorizes that closeout for the same scope, target, and branch.

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

Use `$gitstack:github-issues` to create a GitHub issue.

For feature planning:

- The PRD is a GitHub issue titled `PRD: <Feature Name>` with type `Feature`
  unless the repo maps `feature` to a different value.
- Generated implementation issues are the execution graph. Do not create a
  separate execution-plan issue. A requested non-authoritative summary remains
  a response view and is not tracker publication.
- Implementation issues are GitHub sub-issues of the PRD issue with type
  `Task` unless the repo maps `task` to a different value.
- Implementation issue titles use
  `<feature-slug>: <NN> <vertical outcome>`.
- `$plan-feature` owns PRD and generated issue body shape, including
  `source_prd_ref`, delivery metadata, partial-PRD links, and issue graph
  validation. `Source PRD` is a read-only legacy migration alias.

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
Final-commit closure is allowed only for
`closeout_mode=direct-commit-closes-issue` with
`issue_mutation_authority=explicit-direct-mutation` and exact separately scoped
authorization evidence. The issue closes when that authorized
commit reaches the default branch.

Use closing keywords only for issues actually satisfied by the change. Do not
add the parent PRD closing keyword from an individual child issue. For a
whole-PRD final feature or integration PR, the root delivery orchestrator may
add that parent keyword only after its review and all PRD closeout gates pass.

## When a skill says "fetch the relevant issue"

Use `$gitstack:github-issues` to view the issue and recent comments.
