---
name: github-actions
description: "Inspect GitHub Actions failures, logs, or permissions and implement requested CI fixes."
---

# GitHub Actions

Use authenticated `gh` directly. Before remote `gh` commands, use the runtime's
narrowest network-enabled context. Verify `gh` is runnable (`command -v gh`,
`gh --version`) and authentication with:

```sh
gh auth status --active --hostname github.com --json hosts \
  --jq '.hosts["github.com"] | map(select(.active == true) | {state, scopes})'
```

Require exactly one active account with `state=success`. Treat
restricted-environment network failures as inconclusive. Do not install or
refresh `gh` without explicit authorization. Network permission is not
mutation authority.

Keep status, diagnosis, and review requests read-only. An explicit CI fix
request authorizes the smallest implementation and relevant local validation;
remote reruns and publication require their own established authority.

For checks, jobs, and logs, read [workflows.md](references/workflows.md).
Interpret provider lifecycle and conclusions using
[states.md](references/states.md). For workflows that create or approve PRs,
branches, or tags, read [configuration.md](references/configuration.md) before
authoring them. Its repository-settings check is advisory: unavailable settings
do not prevent an explicitly requested workflow edit.

Report the exact repository and PR or commit, failing command and supporting
evidence, actionable diagnosis, pending or unavailable evidence, and relevant
check/run links. An authoritative empty check inventory means no checks were
reported for that target; it proves neither successful CI nor absent workflow
configuration. After a fix, distinguish local validation from remote evidence;
recheck when a new run exists before claiming remote success.
