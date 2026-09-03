---
name: github-stars
description: Manage the authenticated GitHub user's stars and star lists. Use to list, add, remove, or organize starred repositories.
---

# GitHub Stars

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../references/network-execution.md).

## Transport

Use `<plugin-root>/scripts/g stars`, backed by authenticated `gh`, for every
provider read and write in this skill.

Before the first provider-facing shared CLI operation, load
[`../../references/gh-dependency-preflight.md`](../../references/gh-dependency-preflight.md)
and require its host and authentication checks.


## Role

Manage authenticated-user stars and star lists with `<plugin-root>/scripts/g stars`. This skill
owns star and list workflows that should not live in repository triage.

## Public Script

```bash
<plugin-root>/scripts/g stars --help
<plugin-root>/scripts/g --version
<plugin-root>/scripts/g --json doctor
```

The script emits stable JSON success/error envelopes for JSON mode and writes
no implicit config.

## Workflow

1. Run the shared doctor with scoped network permission and require
   `authentication_status=verified` before private or authenticated-user
   operations.
2. Use list operations for inventory and search.
3. Confirm destructive actions such as unstar or list delete unless the user
   explicitly asked for them.
4. Return repository URLs and list names/ids in results.

## References

- `references/workflows.md`: star and star-list workflows.
- `references/script-summary.md`: `stars` command contract.
