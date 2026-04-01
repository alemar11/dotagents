# GitHub review script summary

Use this as the authoritative reviews-domain script catalog referenced by
`github/SKILL.md`.

## Fast helper picks

- Use `scripts/reviews/prs_address_comments.sh` for review-thread inspection and reply
  preview/write flows.
- Use `scripts/reviews/prs_review.sh` for review submission.
- Use `scripts/reviews/prs_comment_add.sh` for top-level PR comment follow-up tied to
  review work.

## Repository setup and preflight

- `scripts/core/check_gh_installed.sh [--min-version <version>]`: Validate that `gh` is installed and meets a minimum version.
- `scripts/core/check_gh_authenticated.sh [--host github.com]`: Verify active GitHub CLI authentication.
- `scripts/core/preflight_gh.sh [--host github.com] [--min-version <version>] [--expect-repo <owner/repo>] [--allow-non-project]`: Run prerequisite checks before other `gh` operations.
- `scripts/core/check_docs_script_refs.sh [--skill-dir <path>]`: Verify docs reference existing scripts and documented flags are present in `--help` output.
- `scripts/core/issue_resolve_repo.sh [--repo <owner/repo>] [--allow-non-project]`: Resolve the target repository, defaulting to current git project.

## Review scripts

- `scripts/reviews/prs_address_comments.sh --pr <number> [--repo <owner/repo>] [--include-resolved] [--json] [--selection <rows>] [--comment-ids <ids>] [--reply-body <text>] [--dry-run] [--allow-non-project]`: Fetch normalized PR conversation, review-comment, and review-thread context; optionally reply to selected comments.
- `scripts/reviews/prs_comment_add.sh --pr <number> --body <text> [--repo <owner/repo>] [--allow-non-project]`
- `scripts/reviews/prs_comments_list.sh --pr <number> [--repo <owner/repo>] [--allow-non-project]`
- `scripts/reviews/prs_review_comments_list.sh --pr <number> [--repo <owner/repo>] [--allow-non-project]`
- `scripts/reviews/prs_review.sh --pr <number> [--approve|--request-changes|--comment] [--body <text>] [--repo <owner/repo>] [--allow-non-project]`
