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
  `ghflow --json reviews address --pr <n> --repo <owner/repo>`
  `ghflow reviews address --pr <n> --repo <owner/repo> --selection <rows> --reply-body <text>`
