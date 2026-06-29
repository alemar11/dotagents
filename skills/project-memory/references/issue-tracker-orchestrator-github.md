# Issue Tracker: GitHub Coordination Repository

Cross-repo PRDs and vertical feature issues live in a configured GitHub
coordination repository. The coordination repository groups and tracks
cross-repo outcomes; actual product code changes still happen in the owning
repos.

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `tracker_mode` | enum | `orchestrator-github` | `orchestrator-github` | GitHub coordination issues are the authoritative cross-repo planning store. |
| `tracker_writes` | enum | `prompt` | `disabled`, `prompt`, `auto` | Whether coordination-repo writes are disabled, confirmation-gated, or automatic. |
| `coordination_repo` | repo | `<owner>/<repo>` | GitHub `owner/repo` | Repository where PRDs and vertical feature issues are created. |
| `project_label_format` | label-pattern | `<project-slug>` | GitHub label text | Project grouping label applied to PRDs and vertical issues. |
| `delivery_mode` | enum | `one-pr-per-repo` | `one-pr-per-repo`, `one-feature-branch`, `one-pr-per-issue`, `direct-commit` | Default delivery shape for true multi-repo work. |

The coordination repository is the authoritative artifact store in this mode.
Do not create or keep repo-local `.scratch/`, local `projects/.../features/...`,
or `project-memory/features/` mirrors merely to feed `gh --body-file`.
Temporary body files must live outside the repo and be removed after mutation
unless the user explicitly asks to keep a local mirror.

## Required Configuration

Record `coordination_repo` and `project_label_format` in the configuration
table in `project-memory/agents/issue-tracker.md`.

Use `$github-issues` with the configured coordination repository. GitHub issue
commands must target `--repo <owner>/<repo>` unless the current checkout is
the coordination repository.

## Non-Mutating Runs

If this setup is being used for a temp exercise, validation pass, rehearsal,
dry run, or any workflow where tracker writes are explicitly disabled, do not
mutate GitHub. Use local orchestrator markdown only when a local dry-run target
is configured or explicitly chosen for that run, or ask `$github-issues` to
return draft issue bodies and exact `gh` commands without executing them.
When returning draft commands before the PRD issue exists, use
`source_prd_ref=draft-prd:<project-slug>/<feature-slug>` and publish the PRD
first; generated issue bodies must replace that draft ref with
`Source PRD: #<prd-number>` before hosted mutation.
Record this as a current-run `tracker_writes: disabled` override in
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
- Default workflow-state labels are lowercase tracker values:
  `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and
  `wontfix`.
- Vertical feature issues are GitHub sub-issues of the PRD parent issue.
- Each vertical feature issue body includes `Source PRD: #<prd-number>`.
- Generated vertical feature issues are the execution graph. Do not create a
  separate execution-plan issue unless the user explicitly requests a
  non-authoritative summary.
- Each PRD parent issue and vertical feature issue gets a GitHub label named
  exactly `<project-slug>`. This is a project grouping/search label, not a
  workflow state label.

Before creating the first issue for a project, use `$github-issues` to ensure
the project label exists. Use `$github-issues` to create the PRD parent issue,
create vertical issues under the PRD, and attach existing issues to the PRD
when needed.

## Delivery Defaults

- Default `delivery_mode`: `one-pr-per-repo` for true multi-repo orchestrator work.
- Branch naming: default to `feature/<feature-slug>` in each affected repo
  unless that repo has a stricter branch policy.
- PR shape: one draft PR per affected repo, all linked from the coordination
  PRD or vertical feature issue.
- Integration proof: cross-repo validation is required before coordination
  issues close. Planning artifacts may contain expected repo PR slots or
  pre-implementation placeholders, but completion requires `$codex-orchestrator`
  to record real PR links or equivalent proof.
- Exceptions: `one-feature-branch` only when all affected work is actually in
  one git repo; `one-pr-per-issue` only for isolated work; `direct-commit` only
  with explicit maintainer authorization.

## Runtime Policy Boundary

- Tracker setup records artifact routing, delivery-mode defaults, and closeout
  conventions only.
- `project-memory/agents/orchestration-policy.md` records optional
  `$codex-orchestrator` auto-dispatch bounds, allowed worker surfaces, caps,
  authorization ceilings, monitoring defaults, and stop-for-owner rules.
- `$codex-orchestrator` resolves actual worker capability modes per workstream
  and session from the owner request, source item, linked `Source PRD`,
  publication authority, issue mutation authority, orchestration policy,
  selected worker surface, dependencies, dirty-worktree state, and gates.
- If an existing setup file contains the legacy worker-authorization setup key,
  treat it as stale state and remove it when touching the file. Do not copy it
  into PRDs, generated issues, draft commands, ledgers, or worker prompts.

## Orchestrator Issue Content

Generated vertical feature issues should include:

- `Source PRD: #<prd-number>` for searchability and backlinks
- affected repo list
- `Delivery mode` copied from the PRD and labeled as feature-level metadata
  inherited from `Source PRD`, for example `Delivery mode: one-pr-per-repo
  (feature-level, inherited from Source PRD)`. Feature-level means the mode
  applies to the whole Source PRD feature.
- issue-level `Parallelization` and `Closeout`
- explicit `Delivery mode` or `Integration mode` exception lines only when the
  issue intentionally differs from the PRD, with the authorization or reason
  recorded
- cross-repo contract or interface notes
- integration gates by name or link and validation proof needed before closure
- repo-local PR links or implementation child issue links when they exist;
  expected repo PR slots or pre-implementation placeholders are allowed before
  implementation when the issue is otherwise ready, but `$codex-orchestrator`
  must record real PR links or equivalent proof before completion
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
