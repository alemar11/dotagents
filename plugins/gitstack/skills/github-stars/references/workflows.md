# GitHub Stars Workflows

## Star Inventory

```bash
<plugin-root>/scripts/gitstack stars list
<plugin-root>/scripts/gitstack --json stars list --limit 100
```

## Add Or Remove Stars

```bash
<plugin-root>/scripts/gitstack stars add <owner/repo>
<plugin-root>/scripts/gitstack stars remove <owner/repo>
```

Confirm removals unless the user explicitly asked to unstar.

## Lists

```bash
<plugin-root>/scripts/gitstack stars lists list
<plugin-root>/scripts/gitstack stars lists items <list-id>
<plugin-root>/scripts/gitstack stars lists assign <list-id> <owner/repo>
<plugin-root>/scripts/gitstack stars lists unassign <list-id> <owner/repo>
<plugin-root>/scripts/gitstack stars lists delete <list-id>
```

Use JSON mode for parsing:

```bash
<plugin-root>/scripts/gitstack --json stars lists list
```
