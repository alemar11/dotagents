---
name: github-stars
description: Manage the authenticated GitHub user's stars and star lists. Use to list, add, remove, or organize starred repositories.
---

# GitHub Stars

## Transport

Prefer the required GitHub connector for supported remote reads and writes. Use
`gh` for connector gaps. An authorized connector write may fall back
automatically only when the operation and repository are identical, `gh`
authentication and access succeed, and the transport switch is reported.


## Role

Manage authenticated-user stars and star lists with `<plugin-root>/scripts/gitstack stars`. This skill
owns star and list workflows that should not live in repository triage.

## Public Script

```bash
<plugin-root>/scripts/gitstack stars --help
<plugin-root>/scripts/gitstack --version
<plugin-root>/scripts/gitstack --json doctor
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
