# GitHub review command summary

Use this as the authoritative reviews-domain command map referenced by the
bundled `github-reviews` skill.

## Direct `gh` first

- `gh pr comment <n> --repo <owner/repo> --body <text>`
- `gh pr review <n> --repo <owner/repo> --approve`
- `gh pr review <n> --repo <owner/repo> --request-changes --body <text>`

## Shared `ghflow` helper kept in reviews

- Resolve the artifact with `../../github/references/core/ghflow-resolution.md`
  before running helper commands.
- `<resolved-ghflow> reviews address`
