# GitHub Stars Workflows

## Star Inventory

```bash
<plugin-root>/scripts/g stars list
<plugin-root>/scripts/g --json stars list --limit 100
```

## Add Or Remove Stars

```bash
<plugin-root>/scripts/g stars add <owner/repo>
<plugin-root>/scripts/g stars remove <owner/repo>
```

Confirm removals unless the user explicitly asked to unstar.

## Lists

```bash
<plugin-root>/scripts/g stars lists list
<plugin-root>/scripts/g stars lists items <list-id>
<plugin-root>/scripts/g stars lists assign <list-id> <owner/repo>
<plugin-root>/scripts/g stars lists unassign <list-id> <owner/repo>
<plugin-root>/scripts/g stars lists delete <list-id>
```

Use JSON mode for parsing:

```bash
<plugin-root>/scripts/g --json stars lists list
```
