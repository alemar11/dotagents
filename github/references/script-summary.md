# GitHub script summary

Use this as the top-level helper index referenced by `github/SKILL.md`.
Each domain keeps its own authoritative script catalog and documented flags.

## Domain catalogs

- Core setup, auth, and retry helpers:
  `references/core/installation.md`
- Triage helpers for repos, issues, PR metadata, patches, reactions, and
  issue-link wording:
  `references/triage/script-summary.md`
- Review helpers for actionable review threads, replies, and review
  submission:
  `references/reviews/script-summary.md`
- CI helpers for PR checks and generic GitHub Actions investigation:
  `references/ci/script-summary.md`
- Release helpers for planning, notes generation, and release publication:
  `references/releases/script-summary.md`
- Publish helpers for current-branch PR open or reuse and PR lifecycle
  mutations:
  `references/publish/script-summary.md`

## Fast picks

- Routine triage: `scripts/triage/repos_view.sh`,
  `scripts/triage/issues_view.sh --summary`,
  `scripts/triage/prs_view.sh --summary`
- Actionable review feedback: `scripts/reviews/prs_address_comments.sh`
- PR checks and Actions: `scripts/ci/prs_checks.sh`,
  `scripts/ci/actions_run_inspect.sh`
- Release planning: `scripts/releases/release_plan.sh`
- Already-pushed branch to PR: `scripts/publish/publish_context.sh`,
  `scripts/publish/prs_open_current_branch.sh`
