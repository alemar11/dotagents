---
name: github-issues
description: Use when GitHub issue lifecycle work needs direct gh commands: create/edit issues, labels, types, parent/sub-issues, comments, closure, or dry-run commands.
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
- Resolve legacy tracker write policy from `tracker_writes` when it is present:
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
  `tracker_backend=github` or `tracker_mode=github` as the target. If a
  no-mutation override is present, draft commands only; otherwise follow the
  user or calling workflow's create/publish/open instruction.
- Do not create new label taxonomy unless the repo's tracker configuration or
  user explicitly asks for it.

## Workflow

1. Resolve the target repository and write mode:
   - current checkout repo,
   - explicit `--repo <owner>/<repo>`,
   - or a target repository supplied by the user or calling workflow.
2. Resolve the effective target from the user request or calling workflow
   handoff. `tracker_backend=github` with `effective_target=configured-tracker`
   means create or update the requested GitHub issues.
3. If the request, handoff, or legacy `tracker_writes: disabled` policy says
   dry run, draft only, local only, or do not mutate, return draft issue bodies
   and exact `gh` commands without mutating GitHub.
4. If legacy `tracker_writes: prompt` is the only write policy and no
   create/publish/open instruction was provided, ask whether to create the
   GitHub issues immediately.
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
