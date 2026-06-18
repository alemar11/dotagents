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

Run `gh` commands with `--repo <owner>/<repo>` unless the current checkout is
the coordination repository.

## Non-Mutating Runs

If this setup is being used for a temp exercise, validation pass, rehearsal,
dry run, or any workflow where external GitHub mutation is not authorized, do
not run `gh issue create`, `gh issue edit`, `gh issue comment`,
`gh label create`, or other GitHub mutation commands. Use local orchestrator
markdown for that run, or return draft issue bodies and exact `gh` commands
without executing them. Record the non-mutating choice in
`project-memory/agents/issue-tracker.md`.

## Conventions

- PRD issue title: `PRD: <Feature Name>`
- Vertical feature issue title:
  `<feature-slug>: <NN> <vertical outcome>`
- PRD issues use the mapped `feature` issue type when GitHub issue types are
  available.
- Vertical feature issues use the mapped `task` issue type when available.
- Vertical feature issues are GitHub sub-issues of the PRD parent issue.
- Each vertical feature issue body includes `Source PRD: #<prd-number>`.
- Each PRD parent issue and vertical feature issue gets a GitHub label named
  exactly `<project-slug>`. This is a project grouping/search label, not a
  workflow state label.

Before creating the first issue for a project, ensure the project label exists:

```bash
gh label list --repo <owner>/<repo> --search "<project-slug>"
gh label create "<project-slug>" --repo <owner>/<repo> --description "Project: <project-slug>"
```

If the label already exists, keep using it.

Create the PRD parent issue with:

```bash
gh issue create --repo <owner>/<repo> --label "<project-slug>" --title "PRD: <Feature Name>" --body-file <file>
```

Create a vertical issue under a PRD with:

```bash
gh issue create --repo <owner>/<repo> --parent <prd-number> --label "<project-slug>" --title "..." --body-file <file>
```

Attach an existing issue to a PRD with:

```bash
gh issue edit <prd-number> --repo <owner>/<repo> --add-sub-issue <issue-number-or-url>
```

## Orchestrator Issue Content

Generated vertical feature issues should include:

- affected repo list
- cross-repo contract or interface notes
- integration gates and validation proof needed before closure
- repo-local PR links or implementation child issue links when they exist
- completion rule for the coordination issue
- project label applied: `<project-slug>`

Repo-local child issues are optional in v1. Create them only when a repo needs
its own implementation queue item for ownership, review, or CI. When child
issues live in other repos, attach them to the coordination issue using issue
URLs.

## Completion

Close a vertical feature issue only after implementation and validation across
the affected repos is complete. Repo-local implementation PRs should link back
to the coordination issue, but do not close the PRD parent issue from a single
repo PR unless the maintainer explicitly says the whole PRD is complete.

Use closing keywords only for issues actually satisfied by the change.
