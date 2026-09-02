# GitHub Stars Workflows

## Star Inventory

```bash
<skill-root>/scripts/g stars list
<skill-root>/scripts/g --json stars list --limit 100
```

## Add Or Remove Stars

```bash
<skill-root>/scripts/g stars add <owner/repo>
<skill-root>/scripts/g stars remove <owner/repo>
```

Confirm removals unless the user explicitly asked to unstar.

## Lists

```bash
<skill-root>/scripts/g stars lists list
<skill-root>/scripts/g stars lists items <list-id>
<skill-root>/scripts/g stars lists assign <list-id> <owner/repo>
<skill-root>/scripts/g stars lists unassign <list-id> <owner/repo>
<skill-root>/scripts/g stars lists delete <list-id>
```

Use JSON mode for parsing:

```bash
<skill-root>/scripts/g --json stars lists list
```
