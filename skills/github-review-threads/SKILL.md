---
name: github-review-threads
description: Use when listing, understanding, drafting, or posting replies to GitHub pull request review threads and conversation comments.
---

# GitHub Review Threads

## Role

Handle PR review threads and comment replies. Use direct `gh` where it is
enough, and run `scripts/reviews` when thread-aware comment listing or selected
reply routing is needed.

## Public Script

```bash
skills/github-review-threads/scripts/reviews --help
skills/github-review-threads/scripts/reviews --version
skills/github-review-threads/scripts/reviews --json doctor
```

The script emits stable JSON success/error envelopes for JSON mode and writes
no implicit config.

## Workflow

1. Resolve the target PR and repository.
2. List review context before replying.
3. Draft replies that reference the implemented change and verification.
4. Use dry-run mode for multi-comment replies unless the user explicitly asks
   to post.
5. Post only to selected comments or threads.

## References

- `references/workflows.md`: review-thread and reply workflows.
- `references/script-summary.md`: `reviews` command contract.
