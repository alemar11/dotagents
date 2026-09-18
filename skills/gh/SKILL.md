---
name: gh
description: "Route GitHub reads and writes through the authenticated gh CLI. Use whenever a task accesses GitHub; suggest macOS or Linux installation when gh is missing."
---

# GitHub CLI

Use the authenticated `gh` CLI for GitHub reads and writes unless the user
explicitly requests another method. Prefer native subcommands; use `gh api`
for REST or GraphQL operations without a suitable subcommand. This includes
reading repository files, issues, pull requests, reviews, Actions, and releases.

Do not substitute GitHub connectors, browser automation, or direct HTTP
requests. If `gh` cannot complete an operation, explain the concrete limitation
instead of silently changing access methods. Public installation documentation
and package downloads may be accessed without `gh` when needed for setup.

Use `git` for repository operations such as clone, fetch, pull, and push. Apply
this access policy alongside existing workflow skills; it does not replace
their publication, review, or authorization rules.

## Availability

Check `command -v gh` and `gh --version` in the environment that will perform
the GitHub operation. If `gh` is missing, read
[installation guidance](references/installation.md) and suggest the commands
appropriate to that environment. Installation is a suggestion unless the user
has authorized it; do not install the CLI or a package manager automatically.
Continue any independent local work while GitHub access is unavailable.

Use existing authentication. If authentication is missing or invalid, suggest
`gh auth login --hostname <host>` for the target GitHub host. Do not start login
or change accounts without authorization. A permission failure for one operation
does not establish that the CLI is missing or unauthenticated.
