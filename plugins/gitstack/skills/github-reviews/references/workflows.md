# GitHub review workflows

Use this reference for review-domain GitHub flows.

## Direct `gh` first

- Top-level PR comments:
  `gh pr comment <n> --repo <owner/repo> --body <text>`
- Review submission:
  `gh pr review <n> --repo <owner/repo> --approve`
  `gh pr review <n> --repo <owner/repo> --request-changes --body <text>`

## Shared helper

- Review-thread triage and reply routing:
  `<resolved-ghflow> --json reviews address --pr <n> --repo <owner/repo>`
  `<resolved-ghflow> reviews address --pr <n> --repo <owner/repo> --selection <rows> --reply-body <text>`

Resolve `<resolved-ghflow>` with
`../../github/references/core/ghflow-resolution.md` first; bare `ghflow` is not
assumed to be on `PATH`.
