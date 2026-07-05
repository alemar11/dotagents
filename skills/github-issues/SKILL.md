---
name: github-issues
description: Manage GitHub issues with gh for creation, edits, labels, types, comments, closure, relationships, and dry-runs.
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
- Own safe body-file transport for composing workflows. When a caller supplies
  generated Markdown body text, this skill creates the transient body files,
  writes them with a non-interpolating method, runs `gh --body-file`, verifies
  state, and cleans up.
- Never embed generated Markdown bodies in shell command strings, `echo`,
  unquoted heredocs, command substitutions, or other interpolating shell input.
  Markdown bodies commonly contain backticks, `$...`, and fenced code.
- Inspect current labels, issue type, state, and relationships before changing
  them.
- When verifying native GitHub Issue Types with `gh issue view --json`, request
  `issueType`; do not request `type`, which is not a valid issue JSON field.
- Do not create labels, close issues, or mutate issue relationships unless the
  user or calling workflow has explicit mutation authority.
- Treat a calling workflow handoff with `tracker_backend=github` and
  `effective_target=configured-tracker` as mutation authority for issue-ready
  planning artifacts after repository context, duplicate checks, labels, issue
  types, and relationships are resolved.
- Treat direct user instructions such as create, publish, or open the issue as
  mutation authority for the requested GitHub issue operation unless the same
  request explicitly says dry run, draft only, local only, or do not mutate.
- Resolve compact and legacy tracker write policy through
  `references/workflows.md`; keep the top-level contract focused on the final
  write mode and requested GitHub operation.
- Do not create new label taxonomy unless the repo's tracker configuration or
  user explicitly asks for it.

## Workflow

1. Resolve the target repository and write mode:
   - current checkout repo,
   - explicit `--repo <owner>/<repo>`,
   - or a target repository supplied by the user or calling workflow.
2. Resolve the effective target and write mode from the user request or calling
   workflow handoff, using `references/workflows.md` for legacy tracker fields.
3. If the resolved write mode says dry run, draft only, local only, or do not
   mutate, return draft issue bodies and exact `gh` commands without mutating
   GitHub.
4. If the resolved write mode requires a user decision before publishing, ask
   whether to create or update the GitHub issues immediately.
5. Read the relevant issue or label state before mutation.
6. For create, edit, or comment operations with generated Markdown, prepare
   safe body files using the pattern in `references/workflows.md`.
7. Apply the smallest GitHub issue operation needed:
   - create issues with the requested title, body, type, labels, or parent,
   - set issue type,
   - add or remove labels,
   - add comments,
   - attach parent/sub-issue relationships,
   - close only after the requested disposition is explicit.
8. If any multi-issue publication step fails after a partial mutation, stop,
   verify the current tracker state, clean up temp files, and retry only the
   missing or incorrect operations. Do not create duplicates from stale local
   assumptions.
9. Verify the changed issue or queue state after mutation.
10. Report the issue URL/number, commands run or drafted, and any skipped
   mutation because a no-mutation override was active.

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
