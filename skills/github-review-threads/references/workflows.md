# GitHub Review Workflows

## List Review Context

```bash
skills/github-review-threads/scripts/reviews address --repo <owner/repo> --pr <number>
skills/github-review-threads/scripts/reviews --json address --repo <owner/repo> --pr <number>
```

By default, resolved or outdated review threads are omitted. Add
`--include-resolved` only when the user asks for full history.

## Reply To Selected Comments

First list comments, then reply by displayed selection or comment id:

```bash
skills/github-review-threads/scripts/reviews address --repo <owner/repo> --pr <number> --selection "1 3" --reply-body "<body>" --dry-run
skills/github-review-threads/scripts/reviews address --repo <owner/repo> --pr <number> --comment-ids "123456" --reply-body "<body>"
```

Use `--dry-run` for batch replies unless the user already approved posting.

## Post Top-Level PR Discussion Comments

Use the helper for normal PR discussion comments, including simple review
requests:

```bash
skills/github-review-threads/scripts/reviews comment --repo <owner/repo> --pr <number> --body-file <message-file> --dry-run
skills/github-review-threads/scripts/reviews comment --repo <owner/repo> --pr <number> --body-file <message-file>
```

Use `--dry-run` unless the user explicitly asked to post the discussion comment.

## Fallback Direct Commands

Use direct `gh` only when `scripts/reviews` is unavailable, broken, or lacks the
needed operation. State the fallback reason in the response.

```bash
gh pr comment <number> --repo <owner/repo> --body-file <message-file>
gh pr view <number> --repo <owner/repo> --comments
```
