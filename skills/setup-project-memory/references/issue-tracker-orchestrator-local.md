# Issue Tracker: Local Orchestrator Workspace

Cross-repo PRDs and vertical feature issues live as markdown files in this
orchestrator workspace. The workspace coordinates external repos; it does not
replace their repo-local project memory or code ownership.

Tracker mode: `orchestrator-local`
Local PRD path pattern:
`projects/<project-slug>/features/<feature-slug>/PRD.md`
Local issue path pattern:
`projects/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md`
Done issue path pattern:
`projects/<project-slug>/features/<feature-slug>/issues/done/<NN>-<slug>.md`

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

- `$to-prd` owns the feature PRD and, when writing an orchestrator-local PRD,
  may create or update `projects/<project-slug>/PROJECT.md`,
  `projects/<project-slug>/repos/<repo-slug>.md`, and
  `projects/<project-slug>/features/<feature-slug>/integration-gates.md` only
  from accepted project, repo, or PRD source material.
- `$to-issues` owns files under
  `projects/<project-slug>/features/<feature-slug>/issues/` and records
  issue-specific integration proof requirements inside those issue files.
- `$to-issues` reads `PROJECT.md`, `repos/*.md`, and `integration-gates.md`,
  but does not create or refresh those supporting files unless the user
  explicitly asks for that broader orchestrator artifact update.

## Orchestrator Issue Content

Generated feature issues should include:

- `Type:` and `Status:` lines from `project-memory/agents/triage-labels.md`
- `Source PRD:` pointing to the feature PRD
- affected repo list
- cross-repo contract or interface notes
- integration gates and validation proof needed before completion
- repo-local PR links or implementation child issue links when they exist

Vertical issues are cross-repo outcomes by default. Repo-specific chores should
stay inside the vertical issue unless a separate repo-local issue is needed for
ownership, review, or CI.

## Completion

A local orchestrator issue is complete only after the feature slice is
implemented and validated across the required repos. Move the issue to
`issues/done/` only after cross-repo integration proof is recorded.

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
