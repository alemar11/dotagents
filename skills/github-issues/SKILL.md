---
name: github-issues
description: Use direct gh commands for GitHub issue lifecycle, labels, types, parent/sub-issues, explicit repo targeting, and dry-run commands.
---

# GitHub Issues

## Role

Own GitHub issue lifecycle mechanics. Use this skill when another workflow has
already decided what issue content, type, state, or relationship is needed and
needs the GitHub operation performed or drafted.

Keep product planning, issue splitting, triage classification, CI, review
threads, releases, stars, commits, and PR publishing in their focused skills.
This skill only handles GitHub Issues.

## Core Rules

- Use direct `gh` commands. This skill is scriptless by design.
- Confirm repository context before mutation, using the current checkout or an
  explicit `--repo <owner>/<repo>`.
- Prefer `--body-file` for non-trivial issue bodies or comments.
- Create temporary `--body-file` inputs outside checkout-owned artifact paths
  and remove them after mutation unless the user or calling workflow explicitly
  provides a persistent body-file or local mirror path.
- Inspect current labels, issue type, state, and relationships before changing
  them.
- Do not create labels, close issues, or mutate issue relationships unless the
  user or calling workflow has explicit mutation authority.
- If external mutation is not authorized, return exact draft commands and issue
  bodies instead of running mutating commands.
- Do not create new label taxonomy unless the repo's tracker configuration or
  user explicitly asks for it.

## Workflow

1. Resolve the target repository and authorization:
   - current checkout repo,
   - explicit `--repo <owner>/<repo>`,
   - or a target repository supplied by the user or calling workflow.
2. Read the relevant issue or label state before mutation.
3. Apply the smallest GitHub issue operation needed:
   - create issues with the requested title, body, type, labels, or parent,
   - set issue type,
   - add or remove labels,
   - add comments,
   - attach parent/sub-issue relationships,
   - close only after the requested disposition is explicit.
4. Verify the changed issue or queue state after mutation.
5. Report the issue URL/number, commands run or drafted, and any skipped
   mutation because authorization was missing.

## Routing

- Use `$github-triage` for current-repository queue snapshots, stale/blocker
  grouping, and PR triage.
- Use `$github-deep-review` when the question needs root cause, provenance, or
  fix-quality judgment before deciding issue disposition.
- Use `$github-review-threads` for PR review-thread context or replies.
- Use `$github-ci` for Actions, checks, and failing PR logs.
- Use `$github-releases` for tags, GitHub Releases, notes, and assets.
- Use `$yeet` for publishing local work as a branch and draft PR.

## References

- `references/workflows.md`: direct `gh` issue lifecycle commands and dry-run
  conventions.
