# Issue Tracker: Local Markdown

PRDs and implementation issues for this repo live as markdown files under
`.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The PRD is `.scratch/<feature-slug>/PRD.md`
- Implementation issues are `.scratch/<feature-slug>/issues/<NN>-<slug>.md`,
  numbered from `01`
- Issue type is recorded as a `Type:` line near the top of each issue file,
  using the type strings from `project-memory/agents/triage-labels.md`
- Triage state is recorded as a `Status:` line near the top of each issue file,
  using the state strings from `project-memory/agents/triage-labels.md`
- Comments and conversation history append under a `## Comments` heading

Implementation issues created from a PRD usually use `Type: task`. PRD files
do not need a `Type:` line unless the repo chooses to treat PRDs as local
feature issues.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/`, creating the directory if
needed.

## When a skill says "fetch the relevant issue"

Read the referenced markdown file. The user will normally pass the path or
feature/issue number directly.
