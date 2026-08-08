---
name: github-actions
description: Inspect GitHub Actions checks and logs, read repository workflow permissions, diagnose failures, or implement an explicitly requested CI fix with local validation and a remote recheck.
---

# GitHub Actions

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../references/network-execution.md).
Connector calls and local-only commands do not use shell escalation.

## Role

Inspect GitHub Actions and PR checks. Keep status, diagnosis, and review
requests read-only. When the user explicitly asks to fix CI, carry the workflow
through the smallest implementation, local validation, and remote recheck.

## Transport and CLI

Prefer the GitHub connector for supported workflow, job, log, artifact, status,
and rerun operations. Use `gh` for unsupported or external checks. An authorized
write may fall back automatically only for the same operation and repository
after `gh` authentication and access verification; report the fallback.

Before the first provider-facing connector fallback or shared CLI command,
load
[`../../references/gh-dependency-preflight.md`](../../references/gh-dependency-preflight.md)
and require its host and authentication checks.

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md`. Use the shared CLI when stable aggregation or focused snippets add
value:

```bash
<plugin-root>/scripts/g --help
<plugin-root>/scripts/g --version
<plugin-root>/scripts/g --json doctor
<plugin-root>/scripts/g --json ci inspect --repo <owner/repo> --pr <n>
<plugin-root>/scripts/g --json ci permissions --repo <owner/repo> --allow-non-project
```

The CLI uses `gh`, emits stable JSON envelopes, and writes no implicit config.
It cannot invoke connector tools.

For release workflows that create pull requests, branches, or tags, run the
read-only permissions preflight before authoring the workflow. It checks the
repository Actions setting and workflow defaults but cannot prove the effective
token permission of a future workflow. A blocked or unavailable result is a
warning about runtime behavior, not a reason to omit a workflow the user has
explicitly asked the skill to write. See
[`references/configuration.md`](references/configuration.md).

## Workflow

1. Resolve the repository and PR or commit; gather the current check rollup.
2. For a new release workflow, run the Actions permissions preflight. If the
   repository-level PR automation setting is blocked or unavailable, warn that
   the Action will not complete its PR operation until the setting is enabled;
   continue writing the explicitly requested workflow and do not claim it is
   functional yet.
3. Retrieve only the failed or incomplete jobs and the smallest useful log
   excerpts. Distinguish GitHub Actions from external checks.
4. Explain the failing command, root cause, and supporting evidence before any
   code change.
5. Stop after diagnosis unless the user explicitly requested a fix.
6. For an explicit fix, inspect the local checkout, implement the narrowest
   correction, and run the relevant local tests or checks.
7. Re-read the remote checks when a new run exists. Report local proof,
   remaining failures, pending checks, external checks, and residual risk.
8. Rerun jobs only when the user authorized that mutation or the enclosing
   workflow explicitly owns it.

Do not treat third-party check URLs as GitHub Actions logs, claim success from a
local test alone, or edit code during an inspection-only request.

## References

- `references/workflows.md`: connector and `gh` CI workflows.
- `references/configuration.md`: repository Actions settings, workflow
  permissions, and the read-only permissions preflight.
- `references/script-summary.md`: shared `g ci inspect` contract.
