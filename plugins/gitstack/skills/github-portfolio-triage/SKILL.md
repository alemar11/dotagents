---
name: github-portfolio-triage
description: Use when triaging broad, multi-repo, or portfolio GitHub issue/PR queues across explicit repositories; produce read-only URL-first queue, CI, release, blocker, and next-action summaries.
---

# GitHub Portfolio Triage

## Overview

Use this bundled skill for read-only maintainer triage across multiple GitHub
repositories. Keep current-repo triage in `github-triage`; use this skill only
when the request names a portfolio, asks for broad or multi-repo triage, or
provides several repositories.

## Runtime Surface

- Prefer direct `gh` for ad hoc single-repo reads.
- From the GitStack plugin root, run `scripts/ghflow portfolio scan ...` for
  normalized multi-repo queue scans.
- From a consuming repository, resolve the installed GitStack artifact with
  `../github/references/core/ghflow-resolution.md`, then run
  `<resolved-ghflow> portfolio scan ...`.
- The scan command is read-only. It does not parse maintainer-orchestrator
  ledgers; pass the repositories explicitly from the active portfolio scope.

## Workflow

1. Identify the repository set from the user, portfolio ledger, or explicit
   `owner/repo` list. Do not broaden to owners, orgs, forks, or archived repos
   unless the user explicitly asks.
2. Resolve the installed `ghflow` artifact before helper use.
3. Run one of:

```bash
<resolved-ghflow> portfolio scan --repo owner/repo --repo owner/other
<resolved-ghflow> portfolio scan --repo-file repos.txt --limit 20
<resolved-ghflow> --json portfolio scan --repo owner/repo
```

4. Expand details with direct `gh issue view`, `gh pr view`, `gh pr diff`, or
   `github-ci` only for surfaced items that need explanation.
5. Return a URL-first report with autonomous candidates, needs-owner items,
   blockers, and next actions. Do not implement, merge, close, rerun checks, or
   comment unless the user explicitly asks for that follow-up.

## References

- `references/script-summary.md`: command map and JSON shape.
- `references/workflows.md`: portfolio triage report workflow.

## Routing

- Use `github-triage` for one current repository.
- Use `github-ci` for failing GitHub Actions log inspection.
- Use `github-reviews` for PR review threads.
- Use `github-releases` for release planning and publication.
- Use `yeet` for local checkout publish flows.
