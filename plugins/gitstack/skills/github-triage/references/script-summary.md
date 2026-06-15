# GitHub triage command summary

Use this as the authoritative triage-domain command map referenced by the
bundled `github-triage` skill.

## Direct `gh` first

- Repository orientation: `gh repo view`
- Maintainer triage report: `references/project-triage.md`
- Issue queue scan: `gh issue list`
- PR queue scan: `gh pr list`
- Issue reads and writes: `gh issue view`, `gh issue create`, `gh issue edit`
- PR reads and metadata edits: `gh pr view`, `gh pr edit`

Route broad, multi-repo, or portfolio queue scans to
`../../github-portfolio-triage/references/script-summary.md` instead of
expanding this current-repo triage surface.

## Shared `ghflow` helpers kept in triage

- Resolve the artifact with `../../github/references/core/ghflow-resolution.md`
  before running helper commands.
- `<resolved-ghflow> stars list`
- `<resolved-ghflow> stars add`
- `<resolved-ghflow> stars remove`
- `<resolved-ghflow> stars lists list`
- `<resolved-ghflow> stars lists items`
- `<resolved-ghflow> stars lists delete`
- `<resolved-ghflow> stars lists assign`
- `<resolved-ghflow> stars lists unassign`

## Raw `gh` workflows

- `gh issue comment` + `gh issue close` for close-with-evidence
- `gh issue view` + `gh issue create` for cross-repo copy
- `gh issue create` + `gh issue comment` + `gh issue close` for cross-repo move
- `gh api graphql` with `createUserList` for star-list creation
