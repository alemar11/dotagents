# Issue Tracker: Local Orchestrator Workspace

Cross-repo PRDs and vertical feature issues live as markdown files in this
orchestrator workspace. The workspace coordinates external repos; it does not
replace their repo-local project memory or code ownership.

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `tracker_mode` | enum | `orchestrator-local` | `orchestrator-local` | Local orchestrator workspace files are the authoritative cross-repo planning store. |
| `tracker_writes` | enum | `auto` | `disabled`, `prompt`, `auto` | Whether local orchestrator tracker writes are disabled, confirmation-gated, or automatic. |
| `local_prd_path_pattern` | path-pattern | `projects/<project-slug>/features/<feature-slug>/PRD.md` | repo-relative path pattern | Local cross-repo PRD location. |
| `local_issue_path_pattern` | path-pattern | `projects/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md` | repo-relative path pattern | Active local vertical issue location. |
| `done_issue_path_pattern` | path-pattern | `projects/<project-slug>/features/<feature-slug>/issues/done/<NN>-<slug>.md` | repo-relative path pattern | Completed local vertical issue location. |
| `delivery_mode` | enum | `one-pr-per-repo` | `one-pr-per-repo`, `one-feature-branch`, `one-pr-per-issue`, `direct-commit` | Default delivery shape for true multi-repo work. |

Current-run override: record any temp, dry-run, rehearsal, or disabled-write
constraint as `tracker_writes: disabled`. Do not treat a current-run override
as a durable coordination backend change unless the user explicitly says to make
it persistent.

## Conventions

- One durable initiative per project directory:
  `projects/<project-slug>/`
- Project overview and shared constraints:
  `projects/<project-slug>/PROJECT.md`
- Repo pointer sheets:
  `projects/<project-slug>/repos/<repo-slug>.md`
- One PRD per feature:
  `projects/<project-slug>/features/<feature-slug>/PRD.md`
- Feature integration gates:
  `projects/<project-slug>/features/<feature-slug>/integration-gates.md`
- Vertical feature issues:
  `projects/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md`
- Vertical feature issue headings use:
  `<feature-slug>: <NN> <vertical outcome>`
- Completed vertical issues move to:
  `projects/<project-slug>/features/<feature-slug>/issues/done/<NN>-<slug>.md`
- Create `issues/done/` only when moving the first completed issue into it.

Setup is config-only: it may create root setup files such as `AGENTS.md`,
`project-memory/agents/*`, and accepted root coordination context, but it must
not create project or feature folders. Create those only when a feature is
actually planned or written.

## Artifact Ownership

- The `$plan-feature` PRD phase owns the feature PRD and, when writing an
  orchestrator-local PRD, may create or update
  `projects/<project-slug>/PROJECT.md`,
  `projects/<project-slug>/repos/<repo-slug>.md`, and
  `projects/<project-slug>/features/<feature-slug>/integration-gates.md` only
  from accepted project, repo, or PRD source material. It must record the
  accepted source in each support doc or in its completion report so the source
  boundary is auditable.
- The `$plan-feature` issue phase owns files under
  `projects/<project-slug>/features/<feature-slug>/issues/` and records
  issue-specific integration proof requirements inside those issue files.
- The `$plan-feature` issue phase reads `PROJECT.md`, `repos/*.md`, and
  `integration-gates.md`, but does not create or refresh those supporting files
  unless the user explicitly asks for that broader orchestrator artifact update.

## Delivery Defaults

- Default `delivery_mode`: `one-pr-per-repo` for true multi-repo orchestrator work.
- Branch naming: default to `feature/<feature-slug>` in each affected repo
  unless that repo has a stricter branch policy.
- PR shape: one draft PR per affected repo, linked from the local PRD or
  vertical feature issue.
- Integration proof: cross-repo validation is required before local
  orchestrator issues move to `issues/done/`. Planning artifacts may contain
  expected repo PR slots or pre-implementation placeholders, but completion
  requires `$codex-orchestrator` to record real PR links or equivalent proof.
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

Generated feature issues should include:

- `Type:` and `Status:` lines from `project-memory/agents/triage-labels.md`
- `Source PRD:` pointing to the feature PRD
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
- integration gates by name or link and validation proof needed before
  completion
- repo-local PR links or implementation child issue links when they exist;
  expected repo PR slots or pre-implementation placeholders are allowed before
  implementation when the issue is otherwise ready, but `$codex-orchestrator`
  must record real PR links or equivalent proof before completion

Vertical issues are cross-repo outcomes by default. Repo-specific chores should
stay inside the vertical issue unless a separate repo-local issue is needed for
ownership, review, or CI.

## Completion

A local orchestrator issue is complete only after all acceptance criteria pass,
validation is complete across the required repos, and cross-repo integration
proof is recorded. Move the issue to `issues/done/` only after that proof is
recorded.

Do not delete completed issue files. Do not add a `done` status; the
`issues/done/` folder is the completion signal. If `issues/done/` does not
exist yet, create it when completing the first issue.

## When a skill says "publish to the issue tracker"

Create or update files under
`projects/<project-slug>/features/<feature-slug>/`, creating directories only
for the feature being written.

## When a skill says "fetch the relevant issue"

Read the referenced markdown file. The user will normally pass the project,
feature, and issue path directly.
