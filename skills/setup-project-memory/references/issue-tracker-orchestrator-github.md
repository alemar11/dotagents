# Issue Tracker: GitHub Coordination Repository

Cross-repo PRDs and vertical feature issues live in a configured GitHub
coordination repository. The coordination repository groups and tracks
cross-repo outcomes; actual product code changes still happen in the owning
repos.

Tracker mode: `orchestrator-github`

## Required Configuration

Record the coordination repository in `project-memory/agents/issue-tracker.md`:

```text
Coordination repo: <owner>/<repo>
Project label format: <project-slug>
```

Use `$github-issues` with the configured coordination repository. GitHub issue
commands must target `--repo <owner>/<repo>` unless the current checkout is
the coordination repository.

## Non-Mutating Runs

If this setup is being used for a temp exercise, validation pass, rehearsal,
dry run, or any workflow where external GitHub mutation is not authorized, do
not mutate GitHub. Use local orchestrator markdown for that run, or ask
`$github-issues` to return draft issue bodies and exact `gh` commands without
executing them. Record this as a current-run override in
`project-memory/agents/issue-tracker.md`; do not treat it as a durable
coordination backend change unless the user explicitly says so.

## Conventions

- PRD issue title: `PRD: <Feature Name>`
- Vertical feature issue title:
  `<feature-slug>: <NN> <vertical outcome>`
- Use the accepted lowercase kebab-case `<feature-slug>` from `$plan-feature`,
  the PRD planning identity, or the PRD source path. Derive it from the PRD
  title only when no accepted slug exists.
- PRD issues use the mapped `feature` issue type when GitHub issue types are
  available.
- Vertical feature issues use the mapped `task` issue type when available.
- Vertical feature issues are GitHub sub-issues of the PRD parent issue.
- Each vertical feature issue body includes `Source PRD: #<prd-number>`.
- Each PRD parent issue and vertical feature issue gets a GitHub label named
  exactly `<project-slug>`. This is a project grouping/search label, not a
  workflow state label.

Before creating the first issue for a project, use `$github-issues` to ensure
the project label exists. Use `$github-issues` to create the PRD parent issue,
create vertical issues under the PRD, and attach existing issues to the PRD
when needed.

## Delivery Topology Defaults

- Default topology: **One PR Per Repo** for true multi-repo orchestrator work.
- Branch naming: default to `feature/<feature-slug>` in each affected repo
  unless that repo has a stricter branch policy.
- PR shape: one draft PR per affected repo, all linked from the coordination
  PRD or vertical feature issue.
- Integration proof: cross-repo validation is required before coordination
  issues close. Repo PR links may be placeholders before implementation, but
  completion requires real PR links or equivalent proof.
- Exceptions: **One Feature Branch** only when all affected work is actually in
  one git repo; **One PR Per Issue** only for isolated work; **Direct Commit**
  only with explicit maintainer authorization.

## Orchestrator Issue Content

Generated vertical feature issues should include:

- `Source PRD: #<prd-number>` for searchability and backlinks
- affected repo list
- issue-level `Parallelization`, `Closeout`, and only explicit
  `Topology override` or `Integration mode` lines when the issue intentionally
  differs from the PRD. Full branch and PR strategy is inherited from
  `Source PRD`.
- cross-repo contract or interface notes
- integration gates by name or link and validation proof needed before closure
- repo-local PR links or implementation child issue links when they exist;
  placeholders are allowed before implementation when the issue is otherwise
  ready, but real PR links or equivalent proof are required before completion
- completion rule for the coordination issue
- project label applied: `<project-slug>`

Repo-local child issues are optional in v1. Create them only when a repo needs
its own implementation queue item for ownership, review, or CI. When child
issues live in other repos, attach them to the coordination issue using issue
URLs.

## Completion

Close a vertical feature issue only after all acceptance criteria pass,
validation is complete across the affected repos, and cross-repo integration
proof is recorded. Repo-local implementation PRs should link back to the
coordination issue, but do not close the PRD parent issue from a single repo PR
unless the maintainer explicitly says the whole PRD is complete.

Use closing keywords only for issues actually satisfied by the change.
