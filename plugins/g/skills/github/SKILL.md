---
name: github
description: Handle general or mixed GitHub work. Use when a request crosses issues, pull requests, Actions, releases, or local publishing, or when the user is unsure which focused G skill fits.
---

# GitHub

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../references/network-execution.md).
Connector calls and local-only commands do not use shell escalation.

Before the first provider-facing direct `gh` or `<plugin-root>/scripts/g`
operation, load
[`../../references/gh-dependency-preflight.md`](../../references/gh-dependency-preflight.md).
Connector-only paths skip the gate; stack operations additionally require the
exact `github/gh-stack` readiness check owned by that reference.

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
- The shared CLI at `<plugin-root>/scripts/g` uses `gh`; it cannot invoke
  connector tools or access the GitHub App token.
- Use `<plugin-root>/scripts/g stack ...` for the GitHub stacked-PR CLI
  boundary. It wraps the official `github/gh-stack` extension, checks the
  extension before invoking it, and never installs the agent skill. Run
  `stack ensure --install` only when extension installation is explicitly
  authorized; it is network-bearing and can change the local GitHub CLI setup.
- Read [`../../references/stack-cli.md`](../../references/stack-cli.md) for the
  typed command surface, JSON envelope, raw escape hatch, and extension
  readiness states.
- Read
  [`../../references/gh-dependency-preflight.md`](../../references/gh-dependency-preflight.md)
  for the shared `gh`, authentication, and conditional `gh-stack` gate.

Resolve `<plugin-root>` as two directories above this `SKILL.md`.

## Routing

| Request | Bundled skill |
| --- | --- |
| Local staging or commit, optionally push without PR | `$g:git-commit` |
| Send local work as a branch and draft PR, linking it to an existing target PR when applicable | `$g:send` |
| Stacked PR branch/stack lifecycle | `$g:github-stack` |
| Issue and PR queue triage for one or more repositories | `$g:github-repository-triage` |
| GitHub issue lifecycle and relationships | `$g:github-issues` |
| Evidence-backed technical review of an issue, PR, or proposed fix | `$g:github-investigation` |
| Actions inspection or explicit CI repair | `$g:github-actions` |
| Exact-head PR delivery readiness, merge policy, rulesets, checks, queue, and automation state | `$g:github-delivery-status` |
| Automated review check/wait, review feedback, implementation, replies, resolution | `$g:github-review-threads` |
| Tags, releases, notes, assets, packages | `$g:github-releases` |
| Stars and star lists | `$g:github-stars` |

Do not load every specialist. Select the smallest owner, then return here only
if the work crosses domains.

## References

- [`../../references/stack-cli.md`](../../references/stack-cli.md): stacked-PR
  wrapper contract and maintenance commands.
- [`../github-stack/SKILL.md`](../github-stack/SKILL.md): stack-level routing,
  lifecycle, and recovery guidance.
- [`../../references/network-execution.md`](../../references/network-execution.md):
  shell network and authentication boundaries.
