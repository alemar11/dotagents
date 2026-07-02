---
name: github-ci
description: Inspect GitHub Actions checks and failing PR logs with direct gh reads or the focused ci-inspect CLI.
---

# GitHub CI

## Role

Inspect GitHub Actions and PR checks. Prefer direct `gh` reads for simple
status questions, and run `scripts/ci-inspect` when you need a focused failure
snippet from a PR's failing checks.

## Public Script

```bash
skills/github-ci/scripts/ci-inspect --help
skills/github-ci/scripts/ci-inspect --version
skills/github-ci/scripts/ci-inspect --json doctor
```

The script emits stable JSON success/error envelopes for JSON mode and writes
no implicit config.

## Workflow

1. Check `gh auth status` and repository context.
2. Use direct `gh pr checks`, `gh run list`, or `gh run view --log` for simple
   inspection.
3. Run `scripts/ci-inspect --repo <owner/repo> --pr <n>` when a PR has failing
   checks and the useful log lines need extraction.
4. Report failing workflow/job names, URLs, and the smallest actionable log
   snippet.

## References

- `references/workflows.md`: direct `gh` CI workflows.
- `references/script-summary.md`: `ci-inspect` command contract.
