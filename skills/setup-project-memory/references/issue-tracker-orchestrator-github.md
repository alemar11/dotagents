# Issue Tracker: GitHub Coordination Repository

Cross-repo PRDs and vertical feature issues live in a configured GitHub
coordination repository. The coordination repository groups and tracks
cross-repo outcomes; actual product code changes still happen in the owning
repos.

Tracker mode: `orchestrator-github`

The coordination repository is the authoritative artifact store in this mode.
Do not create or keep repo-local `.scratch/`, local `projects/.../features/...`,
or `project-memory/features/` mirrors merely to feed `gh --body-file`.
Temporary body files must live outside the repo and be removed after mutation
unless the user explicitly asks to keep a local mirror.

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
not mutate GitHub. Use local orchestrator markdown only when a local dry-run
target is configured or explicitly chosen for that run, or ask `$github-issues`
to return draft issue bodies and exact `gh` commands without executing them.
Record this as a current-run override in
`project-memory/agents/issue-tracker.md`; do not treat it as a durable
coordination backend change unless the user explicitly says so.

## Conventions

- PRD issue title: `PRD: <Feature Name>`
- Execution plan issue title: `Execution plan: <feature-slug>`
- Vertical feature issue title:
  `<feature-slug>: <NN> <vertical outcome>`
- Use the accepted lowercase kebab-case `<feature-slug>` from `$plan-feature`,
  the PRD planning identity, or the PRD source path. Derive it from the PRD
  title only when no accepted slug exists.
- PRD issues use the mapped `feature` issue type when GitHub issue types are
  available.
- Execution-plan issues use the mapped `task` issue type when GitHub issue
  types are available, but they are planning/control artifacts and must not be
  labeled `ready-for-agent`.
- Vertical feature issues use the mapped `task` issue type when available.
- Vertical feature issues are GitHub sub-issues of the PRD parent issue.
- Each vertical feature issue body includes `Source PRD: #<prd-number>`.
- Create or update one dedicated execution-plan issue per PRD and attach it to
  the PRD parent when parent/sub-issues are supported. It must include
  `Source PRD: #<prd-number>`, delivery mode, dependency graph, waves/unlock
  conditions, integration gates, and links to every generated vertical feature
  issue after those issues exist.
- Each vertical feature issue body should include an `Execution plan` pointer to
  the dedicated execution-plan issue, usually `Execution plan: #<number>`. Use
  `execution-plan.md` only when the effective target is a local artifact target
  or an explicitly requested local mirror. Use a PRD comment/body section only
  as a fallback when the execution-plan issue cannot be created or edited.
- Each PRD parent issue and vertical feature issue gets a GitHub label named
  exactly `<project-slug>`. This is a project grouping/search label, not a
  workflow state label.
- The execution-plan issue also gets the same `<project-slug>` label.

Before creating the first issue for a project, use `$github-issues` to ensure
the project label exists. Use `$github-issues` to create the PRD parent issue,
create or update the execution-plan issue, create vertical issues under the
PRD, and attach existing issues to the PRD when needed.

## Delivery Mode Defaults

- Default delivery mode: **One PR Per Repo** for true multi-repo orchestrator work.
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
- `Execution plan: #<plan-number>` pointing to the hosted execution-plan issue
- affected repo list
- `Delivery mode` copied from the PRD and labeled as feature-level metadata
  inherited from `Source PRD`, for example `Delivery mode: One PR Per Repo
  (feature-level, inherited from Source PRD)`. Feature-level means the mode
  applies to the whole Source PRD feature.
- issue-level `Parallelization` and `Closeout`
- explicit `Delivery mode` or `Integration mode` exception lines only when the
  issue intentionally differs from the PRD, with the authorization or reason
  recorded
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
