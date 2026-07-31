---
name: github
description: Handle general or mixed GitHub work. Use when a request crosses issues, pull requests, Actions, releases, or local publishing, or when the user is unsure which focused GitStack skill fits.
---

# GitHub

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../references/network-execution.md).
Connector calls and local-only commands do not use shell escalation.

## Role

Use this plugin-only umbrella when a GitHub request is mixed, ambiguous, or
spans multiple lifecycle stages. Route focused work to the smallest bundled
skill and keep that skill's authority and safety rules intact.

## Transport

- Prefer the required GitHub connector for supported remote reads and writes.
- Use `gh` for connector gaps or when a connector call fails. A write may fall
  back automatically only when the original write was authorized, the target
  repository and operation are identical, and provider authentication plus
  repository access succeed. Report the transport switch.
- Use direct `git` for local status, diffs, staging, commits, branches, hooks,
  tests, and pushes.
- The shared CLI at `<plugin-root>/scripts/gitstack` uses `gh`; it cannot invoke
  connector tools or access the GitHub App token.

Resolve `<plugin-root>` as two directories above this `SKILL.md`.

## Routing

| Request | Bundled skill |
| --- | --- |
| Local staging or commit, optionally push without PR | `$gitstack:git-commit` |
| Publish local work as a branch and draft PR | `$gitstack:submit` |
| Issue and PR queue triage for one or more repositories | `$gitstack:github-repository-triage` |
| GitHub issue lifecycle and relationships | `$gitstack:github-issues` |
| Evidence-backed technical review of an issue, PR, or proposed fix | `$gitstack:github-investigation` |
| Actions inspection or explicit CI repair | `$gitstack:github-actions` |
| Automated review check/wait, review feedback, implementation, replies, resolution | `$gitstack:github-review-threads` |
| Tags, releases, notes, assets, packages | `$gitstack:github-releases` |
| Stars and star lists | `$gitstack:github-stars` |

Do not load every specialist. Select the smallest owner, then return here only
if the work crosses domains.
