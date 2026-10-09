---
name: gh
description: "Use the authenticated gh CLI for GitHub tasks, including stacked pull requests through the gh-stack extension."
---

# GitHub CLI

Use the authenticated `gh` CLI for GitHub reads and writes unless the user
explicitly requests another method. Prefer native subcommands; use `gh api`
for REST or GraphQL operations without a suitable subcommand. This includes
reading repository files, issues, pull requests, reviews, Actions, and releases.

For a single repository file without cloning, prefer `gh repo read-file`:

```sh
gh repo read-file path/to/file --repo OWNER/REPO --ref REF
```

This command is currently in preview; check the installed command's help. If
the CLI lacks it, request raw content through `gh api`:

```sh
gh api 'repos/OWNER/REPO/contents/path/to/file?ref=REF' \
  -H 'Accept: application/vnd.github.raw+json'
```

When piping a fetch into a decoder or filter, preserve gh's failure status;
use `set -o pipefail` in Bash or zsh so a later command cannot mask a failed read.

Quote `gh api` endpoints containing query strings or shell metacharacters:

```sh
gh api 'repos/OWNER/REPO/git/trees/REF?recursive=1'
```

A zsh `no matches found` error occurs before gh runs; fix endpoint quoting
before investigating GitHub access.

Do not substitute GitHub connectors, browser automation, or direct HTTP
requests. If `gh` cannot complete an operation, explain the concrete limitation
instead of silently changing access methods. Public installation documentation
and package downloads may be accessed without `gh` when needed for setup.

Use `git` for repository operations such as clone, fetch, pull, and push. Apply
this access policy alongside existing workflow skills; it does not replace
their publication, review, or authorization rules.

For local image or video uploads to issues, pull requests, or comments, read
[attachment guidance](references/attachments.md).

For Actions job logs, including completed jobs in an active workflow, read
[Actions log guidance](references/actions-logs.md).

## Extensions

For stacked branches, dependent PRs, or `github/gh-stack` installation, read
[stacked PR guidance](references/stacked-pr.md) for installation and direct
use of `gh stack`.
Use `$yeet` for single-PR publication; stack-wide operations and explicit
parent/child linking belong to this extension workflow.

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
