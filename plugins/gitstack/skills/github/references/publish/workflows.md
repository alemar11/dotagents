# GitHub publish workflows

Use this reference for the current-branch publish helpers that still justify
`ghflow`.

## Publish Context

```bash
ghflow --json publish context [--repo <owner/repo>]
```

Run this from the target repo root before branch, push, or PR decisions when
upstream state or open-PR state is uncertain.

## Open Or Reuse Current Branch PR

```bash
ghflow publish open [--title <text>] [--body <text>] [--body-from-head] [--base <branch>] [--draft] [--repo <owner/repo>] [--dry-run]
```

Use this only for the already-pushed current branch. Keep explicit PR lifecycle
mutations on plain `gh pr ...` commands.
