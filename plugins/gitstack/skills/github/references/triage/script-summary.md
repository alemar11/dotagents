# GitHub triage command summary

Use this as the authoritative triage-domain command map referenced by the
bundled `github` skill.

## Direct `gh` first

- Repository orientation: `gh repo view`
- Issue reads and writes: `gh issue view`, `gh issue create`, `gh issue edit`
- PR reads and metadata edits: `gh pr view`, `gh pr edit`

## Shared `ghflow` helpers kept in triage

- `ghflow stars list`
- `ghflow stars add`
- `ghflow stars remove`
- `ghflow stars lists list`
- `ghflow stars lists items`
- `ghflow stars lists delete`
- `ghflow stars lists assign`
- `ghflow stars lists unassign`

## Raw `gh` workflows

- `gh issue comment` + `gh issue close` for close-with-evidence
- `gh issue view` + `gh issue create` for cross-repo copy
- `gh issue create` + `gh issue comment` + `gh issue close` for cross-repo move
- `gh api graphql` with `createUserList` for star-list creation
