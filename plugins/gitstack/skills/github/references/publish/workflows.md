# GitHub publish workflows

Use this reference for the current-branch publish helpers that still justify
`ghflow`.

## Publish Context

```bash
<resolved-ghflow> --json publish context [--repo <owner/repo>]
```

Run this from the target repo root before branch, push, or PR decisions when
upstream state or open-PR state is uncertain.
Resolve `<resolved-ghflow>` by preferring bare `ghflow` when it is already on
`PATH`, otherwise by using the installed GitStack artifact path directly. If
neither can be resolved, stop and treat it as broken install or runtime drift.

## Open Or Reuse Current Branch PR

```bash
<resolved-ghflow> publish open [--title <text>] [--body <text>] [--body-from-head] [--base <branch>] [--draft] [--repo <owner/repo>] [--dry-run]
```

Use this only for the already-pushed current branch. Keep explicit PR lifecycle
mutations on plain `gh pr ...` commands.
When the caller already has a locked PR base, always pass `--base <branch>`.
After create or reuse, verify the final base with
`gh pr view <number> --json baseRefName,url,isDraft`.
