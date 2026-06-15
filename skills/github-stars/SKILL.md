---
name: github-stars
description: Use when listing, adding, removing, or organizing the authenticated GitHub user's stars and star lists.
---

# GitHub Stars

## Role

Manage authenticated-user stars and star lists with `scripts/stars`. This skill
owns star and list workflows that should not live in repository triage.

## Public Script

```bash
skills/github-stars/scripts/stars --help
skills/github-stars/scripts/stars --version
skills/github-stars/scripts/stars --json doctor
```

The script emits stable JSON success/error envelopes for JSON mode and writes
no implicit config.

## Workflow

1. Confirm `gh auth status` before private or authenticated-user operations.
2. Use list operations for inventory and search.
3. Confirm destructive actions such as unstar or list delete unless the user
   explicitly asked for them.
4. Return repository URLs and list names/ids in results.

## References

- `references/workflows.md`: star and star-list workflows.
- `references/script-summary.md`: `stars` command contract.
