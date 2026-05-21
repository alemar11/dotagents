# GitHub publish workflows

Use this reference for the current-branch publish helpers that still justify
`ghflow`.

## Publish Context

```bash
<resolved-ghflow> --json publish context [--repo <owner/repo>]
```

Run this from the target repo root before branch, push, or PR decisions when
upstream state or open-PR state is uncertain.
Resolve `<resolved-ghflow>` with `../core/ghflow-resolution.md`. Do not assume
the bare `ghflow` command is on `PATH`; if the installed artifact cannot be
resolved, stop and treat it as broken install or runtime drift.

## Discover PR Template

```bash
<resolved-ghflow> --json publish template [--base <branch>] [--repo <owner/repo>]
```

Use this before composing a new PR body. Prefer the intended PR base when it is
already locked. If the result is `found`, adapt the returned template content
into final PR prose. If it is `ambiguous`, choose a template before creating the
PR. If it is `missing`, use the skill's fallback body shape.

## Open Or Reuse Current Branch PR

```bash
<resolved-ghflow> publish open [--title <text>] [--body <text>] [--body-file <path>] [--body-from-head] [--base <branch>] [--draft] [--repo <owner/repo>] [--dry-run]
```

Use this only for the already-pushed current branch. Keep explicit PR lifecycle
mutations on plain `gh pr ...` commands.
When the caller already has a locked PR base, always pass `--base <branch>`.
Prefer `--body-file <path>` for template-aware final PR bodies. Do not pass
`gh pr create --template`; compose the final Markdown first, then submit it.
After create or reuse, verify the final base with
`gh pr view <number> --json baseRefName,url,isDraft`.
