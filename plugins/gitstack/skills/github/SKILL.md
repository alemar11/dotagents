---
name: github
description: Route mixed or general GitHub work to the smallest GitStack workflow.
---

# GitHub

## Role

Use this plugin-only umbrella when a GitHub request is mixed, ambiguous, or
spans multiple lifecycle stages. Route focused work to the smallest bundled
skill and keep that skill's authority and safety rules intact.

## Transport

- Prefer the required GitHub connector for supported remote reads and writes.
- Use `gh` for connector gaps or when a connector call fails. A write may fall
  back automatically only when the original write was authorized, the target
  repository and operation are identical, and `gh auth status` plus repository
  access succeed. Report the transport switch.
- Use direct `git` for local status, diffs, staging, commits, branches, hooks,
  tests, and pushes.
- The shared CLI at `<plugin-root>/scripts/gitstack` uses `gh`; it cannot invoke
  connector tools or access the GitHub App token.

Resolve `<plugin-root>` as two directories above this `SKILL.md`.

## Routing

| Request | Bundled skill |
| --- | --- |
| Local staging or commit, optionally push without PR | `$gitstack:git-commit` |
| Publish local work as a branch and draft PR | `$gitstack:yeet` |
| Current-repository issue and PR queue snapshot | `$gitstack:github-triage` |
| GitHub issue lifecycle and relationships | `$gitstack:github-issues` |
| Root-cause and fix-quality review | `$gitstack:github-deep-review` |
| Actions inspection or explicit CI repair | `$gitstack:github-ci` |
| Review feedback, implementation, replies, resolution | `$gitstack:github-review-threads` |
| Multi-repository queue scan | `$gitstack:github-portfolio-triage` |
| Tags, releases, notes, assets, packages | `$gitstack:github-releases` |
| Stars and star lists | `$gitstack:github-stars` |

Do not load every specialist. Select the smallest owner, then return here only
if the work crosses domains.
