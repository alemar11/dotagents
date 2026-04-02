# GitHub workflows

Use this as the top-level runbook index referenced by `github/SKILL.md`.
Choose the domain first, then open the matching detailed workflow document.

## Domain runbooks

- Triage-owned repository, authenticated-user star/list, issue, PR metadata,
  reaction, and issue-link flows:
  `references/triage/workflows.md`
- Review-thread inspection, reply, and review submission:
  `references/reviews/workflows.md`
- PR checks and generic GitHub Actions investigation:
  `references/ci/workflows.md`
- Release-backed tags, tag-only flows, and release publication:
  `references/releases/workflows.md`
- Current-branch PR open or reuse and PR lifecycle mutations:
  `references/publish/workflows.md`

## Routing rules

- Stay in `github` for triage, reviews, CI, releases, and publish or
  lifecycle work.
- Route only full local-worktree publish to `yeet`.
- Use `references/core/failure-retries.md` when the chosen helper fails and
  you need the next retry path quickly.
