---
name: github-status
description: "Inspect repository issue and pull-request queues, or one PR’s exact-head delivery readiness, read-only."
---

# GitHub Status

Read-only GitHub queue triage and exact-head delivery inspection through
authenticated `gh`. Before remote `git`, `gh`, or registry commands, use the
runtime's narrowest network-enabled context for that command family; keep
local-only git sandboxed. Verify `gh` is runnable (`command -v gh`,
`gh --version`) and authentication with:

```sh
gh auth status --active --hostname github.com --json hosts \
 --jq '.hosts["github.com"] | map(select(.active == true) | {state, scopes})'
```

Require exactly one active account with `state=success`. Treat
restricted-environment network failures as inconclusive. Do not install or
refresh `gh` without explicit authorization. Network permission is not
mutation authority.

## Select the work

- For repository issue and pull-request queues, blockers, and next actions,
 follow [triage-workflows.md](references/triage-workflows.md).
- For one pull request's exact-head checks, reviews, merge policy, and
 delivery readiness, follow [workflows.md](references/workflows.md) and
 interpret results with [states.md](references/states.md).

Require the caller's expected full HEAD SHA when inspecting a bound delivery
candidate; general inspection may use the current HEAD. Never reuse evidence
from another HEAD.

## Boundaries

This skill never performs GitHub writes. Route predetermined authorized issue
lifecycle mutations to `$github-issues` after normalizing `mutation_mode`, the
exact repository and issue, and one `issue_operation`. Route review-thread
provider operations to `$github-review-threads`. Ordinary code investigation
needs no skill.

Report URLs first, coverage limits, material blockers or pending gates, and
unavailable evidence. Delivery readiness does not authorize merging, bypassing
protections, updating branches, changing auto-merge or queue membership,
requesting reviews, resolving threads, rerunning CI, or editing hosted content.
Composing workflows own acceptance, implementation, review, and release policy.
