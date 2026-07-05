---
name: github-review-threads
description: Inspect PR review threads, draft or post replies, and manage conversation comments.
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
3. Draft comments or replies by default. Reference the implemented change and
   verification.
4. Post only when the user explicitly asks to post and the target comments or
   threads are selected.
5. Use `scripts/reviews comment --dry-run` for draft or multi-comment replies
   until posting authority is explicit.
6. Use `scripts/reviews comment` for authorized top-level PR discussion
   comments; use direct `gh` fallback only when the helper cannot perform the
   selected operation.

## References

- `references/workflows.md`: review-thread and reply workflows.
- `references/script-summary.md`: `reviews` command contract.
