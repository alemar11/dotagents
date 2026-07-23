---
name: github-actions
description: Inspect failing GitHub Actions checks and logs, diagnose the root cause, or implement an explicitly requested fix with local validation and a remote recheck.
---

# GitHub Actions

## Role

Inspect GitHub Actions and PR checks. Keep status, diagnosis, and review
requests read-only. When the user explicitly asks to fix CI, carry the workflow
through the smallest implementation, local validation, and remote recheck.

## Transport and CLI

Prefer the GitHub connector for supported workflow, job, log, artifact, status,
and rerun operations. Use `gh` for unsupported or external checks. An authorized
write may fall back automatically only for the same operation and repository
after `gh` authentication and access verification; report the fallback.

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md`. Use the shared CLI when stable aggregation or focused snippets add
value:

```bash
<plugin-root>/scripts/gitstack --help
<plugin-root>/scripts/gitstack --version
<plugin-root>/scripts/gitstack --json doctor
<plugin-root>/scripts/gitstack --json ci inspect --repo <owner/repo> --pr <n>
```

The CLI uses `gh`, emits stable JSON envelopes, and writes no implicit config.
It cannot invoke connector tools.

## Workflow

1. Resolve the repository and PR or commit; gather the current check rollup.
2. Retrieve only the failed or incomplete jobs and the smallest useful log
   excerpts. Distinguish GitHub Actions from external checks.
3. Explain the failing command, root cause, and supporting evidence before any
   code change.
4. Stop after diagnosis unless the user explicitly requested a fix.
5. For an explicit fix, inspect the local checkout, implement the narrowest
   correction, and run the relevant local tests or checks.
6. Re-read the remote checks when a new run exists. Report local proof,
   remaining failures, pending checks, external checks, and residual risk.
7. Rerun jobs only when the user authorized that mutation or the enclosing
   workflow explicitly owns it.

Do not treat third-party check URLs as GitHub Actions logs, claim success from a
local test alone, or edit code during an inspection-only request.

## References

- `references/workflows.md`: connector and `gh` CI workflows.
- `references/script-summary.md`: shared `gitstack ci inspect` contract.
