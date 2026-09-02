# GitHub

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../network-execution.md).

Before the first provider-facing direct `gh` or `<skill-root>/scripts/g`
operation, load
[`../../gh-dependency-preflight.md`](../../gh-dependency-preflight.md).
Stack operations additionally require the exact `github/gh-stack` readiness
check owned by that reference.

## Role

Use this workflow umbrella when a GitHub request is mixed, ambiguous, or
spans multiple lifecycle stages. Route focused work to the smallest focused
workflow and keep its authority and safety rules intact.

## Transport

- Use authenticated `gh` for every GitHub provider read and write, either
  directly or through `<skill-root>/scripts/g`.
- Use direct `git` for local status, diffs, staging, commits, branches, hooks,
  tests, and pushes.
- The shared CLI at `<skill-root>/scripts/g` uses the same authenticated `gh`
  session as direct GitHub CLI commands.
- Use `<skill-root>/scripts/g stack ...` for the GitHub stacked-PR CLI
  boundary. It wraps the official `github/gh-stack` extension, checks the
  extension before invoking it, and never installs the agent skill. Run
  `stack ensure --install` only when extension installation is explicitly
  authorized; it is network-bearing and can change the local GitHub CLI setup.
- Read [`../../stack-cli.md`](../../stack-cli.md) for the
  typed command surface, JSON envelope, raw escape hatch, and extension
  readiness states.
- Read
  [`../../gh-dependency-preflight.md`](../../gh-dependency-preflight.md)
  for the shared `gh`, authentication, and conditional `gh-stack` gate.

Use the `<skill-root>` resolved by the active G entrypoint.

## Routing

| Request | Workflow |
| --- | --- |
| Local staging or commit, optionally push without PR | the `git-commit` workflow |
| Send local work as a branch and draft PR | the `send` workflow |
| Stacked PR branch/stack lifecycle | the `github-stack` workflow |
| Issue and PR queue triage for one or more repositories | the `github-repository-triage` workflow |
| Content-based issue classification or explicit read-only taxonomy proposals | the `github-tagger` workflow |
| GitHub issue lifecycle and relationships | the `github-issues` workflow |
| GitHub Projects, fields, items, repository/team links, or templates | the `github-projects` workflow |
| Evidence-backed technical review of an issue, PR, or proposed fix | the `github-investigation` workflow |
| Actions inspection or explicit CI repair | the `github-actions` workflow |
| Exact-head PR delivery readiness, merge policy, rulesets, checks, queue, and automation state | the `github-delivery-status` workflow |
| Automated review check/wait, review feedback, implementation, replies, resolution | the `github-review-threads` workflow |
| Tags, releases, notes, assets, packages | the `github-releases` workflow |
| Stars and star lists | the `github-stars` workflow |

Do not load every specialist. Select the smallest owner, then return here only
if the work crosses domains.

## References

- [`../../stack-cli.md`](../../stack-cli.md): stacked-PR
  wrapper contract and maintenance commands.
- [`../github-stack/workflow.md`](../github-stack/workflow.md): stack-level routing,
  lifecycle, and recovery guidance.
- [`../github-projects/workflow.md`](../github-projects/workflow.md): GitHub
  Projects lifecycle, identity, authorization, and recovery guidance.
- [`../../network-execution.md`](../../network-execution.md):
  shell network and authentication boundaries.
