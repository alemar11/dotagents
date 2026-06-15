# GitHub Stars Workflows

## Star Inventory

```bash
skills/github-stars/scripts/stars list
skills/github-stars/scripts/stars --json list --limit 100
```

## Add Or Remove Stars

```bash
skills/github-stars/scripts/stars add <owner/repo>
skills/github-stars/scripts/stars remove <owner/repo>
```

Confirm removals unless the user explicitly asked to unstar.

## Lists

```bash
skills/github-stars/scripts/stars lists list
skills/github-stars/scripts/stars lists items <list-id>
skills/github-stars/scripts/stars lists assign <list-id> <owner/repo>
skills/github-stars/scripts/stars lists unassign <list-id> <owner/repo>
skills/github-stars/scripts/stars lists delete <list-id>
```

Use JSON mode for parsing:

```bash
skills/github-stars/scripts/stars --json lists list
```
