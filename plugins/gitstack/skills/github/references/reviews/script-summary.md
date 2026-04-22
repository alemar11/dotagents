# GitHub review command summary

Use this as the authoritative reviews-domain command map referenced by the
bundled `github` skill.

## Direct `gh` first

- `gh pr comment <n> --repo <owner/repo> --body <text>`
- `gh pr review <n> --repo <owner/repo> --approve`
- `gh pr review <n> --repo <owner/repo> --request-changes --body <text>`

## Shared `ghflow` helper kept in reviews

- `ghflow reviews address`
