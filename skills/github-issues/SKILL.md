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
- When verifying native GitHub Issue Types with `gh issue view --json`, request
  `issueType`; do not request `type`, which is not a valid issue JSON field.
- Do not create labels, close issues, or mutate issue relationships unless the
  user or calling workflow has explicit mutation authority.
- Treat `tracker_writes: auto` as mutation authority for issue-ready content
  after repository context and duplicate checks are complete. Treat an accepted
  `tracker_writes: prompt` confirmation the same way.
- Resolve tracker write policy from `tracker_writes` when it is present:
  - `disabled`: do not write tracker artifacts; return exact draft commands and
    issue bodies instead.
  - `prompt`: when issue-ready PRD/task content exists, ask the user
    immediately whether to write it to the configured tracker target.
  - `auto`: write issue-ready content to the configured tracker target as soon
    as repository context, duplicate checks, labels, types, and relationships
    are resolved.
- Use `tracker_mode` to identify the tracker target:
  - `github`: create or edit GitHub issues through this skill.
  - `local`: do not create GitHub issues unless the user explicitly supplies a
    GitHub target; local artifact writes belong to the caller's local tracker
    workflow.
- For legacy tracker configs without `tracker_writes`, treat
  `external_tracker_mutation: allowed` as `tracker_writes: prompt` for GitHub
  targets. Do not infer `auto` from legacy `allowed` fields; `auto` must be
  explicit.
- Do not create new label taxonomy unless the repo's tracker configuration or
  user explicitly asks for it.

## Workflow

1. Resolve the target repository and authorization:
   - current checkout repo,
   - explicit `--repo <owner>/<repo>`,
   - or a target repository supplied by the user or calling workflow.
2. Resolve tracker policy from `tracker_mode` and `tracker_writes`.
3. If `tracker_writes: disabled`, return draft issue bodies and exact `gh`
   commands without mutating GitHub.
4. If `tracker_mode: github` and `tracker_writes: prompt`, but the user or
   calling workflow has not explicitly chosen mutation or non-mutation for
   issue-ready content, ask whether to create the GitHub issues immediately.
5. Read the relevant issue or label state before mutation.
6. Apply the smallest GitHub issue operation needed:
   - create issues with the requested title, body, type, labels, or parent,
   - set issue type,
   - add or remove labels,
   - add comments,
   - attach parent/sub-issue relationships,
   - close only after the requested disposition is explicit.
7. Verify the changed issue or queue state after mutation.
8. Report the issue URL/number, commands run or drafted, and any skipped
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
