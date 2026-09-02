---
name: g
description: Manage requested Git and GitHub work, including commits, pull requests, issues, Projects, Actions, reviews, releases, repository triage, stars, and stacked branches. Use for explicit Git or GitHub tasks or when a request crosses those domains; do not invoke merely because the current directory is a Git repository.
---

# G

Use one focused workflow for the requested Git or GitHub outcome. Load only the
selected workflow and any reference it directly routes to. For mixed work,
start with [the GitHub umbrella](references/workflows/github/workflow.md), then
load each focused workflow only when the request crosses that boundary.

Resolve `<skill-root>` as the directory containing this `SKILL.md`. Run the
shipped CLI only from `<skill-root>/scripts/g`; `projects/g/` is
maintenance-only source and never a runtime entrypoint.

## Routing

| Request | Read first |
| --- | --- |
| Local staging or commit, optionally a push preview | [Git commit](references/workflows/git-commit/workflow.md) |
| Publish local work as a branch and pull request | [Send](references/workflows/send/workflow.md) |
| Stacked branch or dependent pull-request lifecycle | [GitHub stack](references/workflows/github-stack/workflow.md) |
| General, ambiguous, or mixed GitHub work | [GitHub](references/workflows/github/workflow.md) |
| Repository issue and pull-request queues | [Repository triage](references/workflows/github-repository-triage/workflow.md) |
| Infer issue labels/types or propose taxonomy | [GitHub tagger](references/workflows/github-tagger/workflow.md) |
| Exact issue lifecycle or relationship work | [GitHub issues](references/workflows/github-issues/workflow.md) |
| GitHub Projects, fields, project items, links, or templates | [GitHub Projects](references/workflows/github-projects/workflow.md) |
| Investigate an issue, pull request, or proposed fix | [GitHub investigation](references/workflows/github-investigation/workflow.md) |
| Inspect Actions or diagnose/fix CI | [GitHub Actions](references/workflows/github-actions/workflow.md) |
| Inspect exact-head pull-request delivery readiness | [Delivery status](references/workflows/github-delivery-status/workflow.md) |
| Inspect or address pull-request review feedback | [Review threads](references/workflows/github-review-threads/workflow.md) |
| Work with versions, tags, or release-line policy | [Versioning](references/workflows/versioning/workflow.md) |
| Work with GitHub Releases, notes, assets, or packages | [GitHub releases](references/workflows/github-releases/workflow.md) |
| Inspect or organize stars and star lists | [GitHub stars](references/workflows/github-stars/workflow.md) |
| Explicitly monitor live tasks using this standalone skill | [Audit](references/workflows/audit/workflow.md) |

Read [the invocation registry](references/options.md) when normalizing a
write-shaped request or composing workflows. Read
[the state registry](references/states.md) before assigning a workflow state,
status, disposition, mode, or checkpoint. Before network-bearing shell work,
read [network execution](references/network-execution.md); before the first
direct GitHub CLI or shipped-CLI provider call, also read
[the GitHub CLI preflight](references/gh-dependency-preflight.md).

## Shared execution rules

- Use direct `git` for local repository work. Use authenticated `gh`, either
  directly or through `<skill-root>/scripts/g`, for every GitHub provider
  operation.
- Preserve exact repository, branch, commit, issue, pull-request, project,
  project-item, release, and review-thread identity across transport changes.
  Treat display text as supporting evidence rather than identity.
- Distinguish the requested operation, its immediate receipt, and independently
  observed state. After an ambiguous remote response, reconcile once through
  an exact read; never replay a mutation blindly.
- Keep free-form provider text file-backed and secret-safe. Never place tokens,
  credentials, or unreviewed generated text on a command line.
- Do not infer mutation authority from a broader goal. A write must have an
  exact target and explicit operation.

## Result

Report the selected workflow, exact target, operations performed, verification
evidence, and any unresolved or unavailable state.
