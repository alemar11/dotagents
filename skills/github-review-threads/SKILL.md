---
name: github-review-threads
description: Use when listing, understanding, drafting, or posting replies to GitHub pull request review threads and conversation comments.
---

# GitHub Review Threads

## Role

Handle PR review threads, PR discussion comments, and comment replies. Use the
shipped `scripts/reviews` helper first for normal PR discussion comments,
thread-aware comment listing, and selected reply routing. Use direct `gh` only
as a fallback when the helper is unavailable or lacks the needed GitHub
operation, and state that fallback reason.

## Public Script

```bash
skills/github-review-threads/scripts/reviews --help
skills/github-review-threads/scripts/reviews --version
skills/github-review-threads/scripts/reviews --json doctor
skills/github-review-threads/scripts/reviews comment --repo <owner/repo> --pr <number> --body-file <message-file> --dry-run
```

The script emits stable JSON success/error envelopes for JSON mode and writes
no implicit config.

## Workflow

1. Resolve the target PR and repository.
2. List review context before replying.
3. Draft comments or replies that reference the implemented change and
   verification.
4. Use `scripts/reviews comment` for top-level PR discussion comments.
5. Use dry-run mode for multi-comment replies unless the user explicitly asks
   to post.
6. Post only to selected comments or threads.

## References

- `references/workflows.md`: review-thread and reply workflows.
- `references/script-summary.md`: `reviews` command contract.
