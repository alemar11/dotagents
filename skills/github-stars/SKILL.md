---
name: github-stars
description: "List and manage the authenticated GitHub user’s stars and star lists."
---

# GitHub Stars

Before remote `gh` or skill helper commands, use the runtime's narrowest
network-enabled context. Verify `gh` is runnable (`command -v gh`,
`gh --version`) and authentication with:

```sh
gh auth status --active --hostname github.com --json hosts \
  --jq '.hosts["github.com"] | map(select(.active == true) | {state, scopes})'
```

Require exactly one active account with `state=success`. Treat
restricted-environment network failures as inconclusive. Do not install or
refresh `gh` without explicit authorization. Network permission is not
mutation authority.

Use authenticated `gh` directly for inventory, ordinary stars, and list
deletion; use `<skill-root>/scripts/stars` only for list membership updates.
Resolve `<skill-root>` as the absolute path of the directory containing this
`SKILL.md`.

Read [workflows](references/workflows.md) for the requested operation. Before
assigning or unassigning list members, also read the
[membership helper contract](references/script-summary.md) and
[result states](references/states.md).

Resolve the host, authenticated account, and exact repository or list identities
before writes. Inspection and dry runs never mutate. An explicit star, unstar,
assignment, removal, or list-deletion request authorizes only that operation;
ask only when its target or scope remains ambiguous.

Report repository URLs, list names and IDs, observed outcomes, and incomplete
coverage or per-target failures. Do not present a write receipt as verified state.
