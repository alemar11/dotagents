---
name: github-issues
description: Manage individual GitHub issues and their lifecycle. Use when the exact content, attachment, label, type, comment, state, native dependency, or relationship change is already decided; use $g:github-tagger when labels or type must be inferred or missing taxonomy must be proposed, and $g:github-repository-triage for repository-wide queues.
---

# GitHub Issues

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../references/network-execution.md).
Connector calls and local-only commands do not use shell escalation.

## Transport

Prefer the required GitHub connector for supported remote reads and writes.
Use `gh` or the shipped attachment uploader for connector gaps. An authorized
connector write may fall back automatically only when the operation and
repository are identical, `gh` authentication and access succeed, and the
transport switch is reported. A
connector gap is safe for direct `gh` when the operation contains only exact
provider identities, as with native issue dependencies, or when every
free-form provider field is genuinely file-backed. Otherwise fail closed.
When a connector gap requires direct `gh`, load
[`../../references/gh-dependency-preflight.md`](../../references/gh-dependency-preflight.md)
immediately before that fallback. Connector-only operations do not require the
CLI gate.

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md`. For every attachment upload, use only:

```bash
<plugin-root>/scripts/g --json attachment upload \
  --repo <owner/repo> \
  --file <absolute-file>
```

## Role

Own GitHub issue lifecycle mechanics. Use this skill when another workflow has
already decided what issue content, label, type, state, or relationship is
needed and needs the GitHub operation performed or drafted.

Keep product planning, issue splitting, metadata classification and taxonomy
proposals, queue triage, CI, review threads, releases, stars, commits, and PR
publishing in their focused skills. `$g:github-tagger` owns evidence-backed
label and type selection and read-only taxonomy proposals; this skill only
handles GitHub Issues lifecycle mechanics.

## Core Rules

- Prefer connector issue tools for supported operations. Use direct `gh` only
  for a connector gap whose free-form provider text is genuinely file-backed;
  otherwise fail closed. Use the shipped `attachment upload` command as the
  only attachment transport; never reproduce its token or HTTP logic.
- Confirm repository context before mutation, using the current checkout or an
  explicit `--repo <owner>/<repo>`.
- Send issue titles and other free-form fields through the structured GitHub
  connector. Use `gh --body-file` only for operations whose every free-form
  field is genuinely file-backed.
- Create temporary `--body-file` inputs outside checkout-owned artifact paths
  and remove them after mutation unless the user or calling workflow explicitly
  provides a persistent body-file or local mirror path.
- Own safe body-file transport for composing workflows. When a caller supplies
  generated Markdown body text, this skill creates the transient body files,
  writes them with a non-interpolating method, runs `gh --body-file`, verifies
  state, and cleans up.
- Treat issue attachments as part of one authorized create, edit, or comment
  operation. Upload only the exact caller-selected files to the exact target
  repository, place each returned stable attachment URL in that operation's
  Markdown, and verify the raw body contains the same URL. Never infer or
  upload additional local files.
- Do not upload attachments during a dry run. Return the planned upload and
  Markdown placement without creating a remote asset.
- Keep attachment credentials and private delivery URLs secret. Never print
  `gh auth token`, enable shell tracing around an upload, or report the
  expiring signed URL that GitHub may use to render a private attachment.
- Never embed generated Markdown bodies in shell command strings, `echo`,
  unquoted heredocs, command substitutions, or other interpolating shell input.
  Markdown bodies commonly contain backticks, `$...`, and fenced code.
- Inspect current labels, issue type, state, and relationships before changing
  them.
- Treat a native issue dependency as one directed edge: the exact target issue
  is blocked by one exact blocker issue. Accept a repository-qualified number
  or URL for the blocker; require an exact URL for a cross-repository edge.
  Read `blockedBy` and `blocking` before mutation, skip an already-correct edge,
  mutate one edge per operation, and require exact readback afterward.
- Native dependency state is provider projection, not planning authority. Add
  or remove only the exact caller-authorized edge. Never infer an edge from
  issue order, titles, labels, types, parent/sub-issue hierarchy, or prose.
- Return exactly one native dependency result per invocation: `verified` after
  a successful mutation and reciprocal readback, `no-op` when pre-read already
  proves the requested state, `failed` for a definite rejected mutation,
  `unavailable` when the operation cannot be attempted, or `unknown` when an
  attempted mutation or readback is inconclusive. The caller owns whether a
  non-success result is a workflow gate.
- When verifying native GitHub Issue Types with `gh issue view --json`, request
  `issueType`; do not request `type`, which is not a valid issue JSON field.
- Do not create labels, close issues, or mutate issue relationships unless the
  user or calling workflow has explicit mutation authority.
- Treat a composed-workflow handoff with `mutation_mode=apply`, an exact target,
  and one canonical `issue_operation` as authority for that operation after
  repository context, duplicate checks, labels, issue types, and relationships
  are resolved. Caller-specific policy must be normalized before invocation.
- Treat direct user instructions such as create, publish, or open the issue as
  mutation authority for the requested GitHub issue operation unless the same
  request explicitly says dry run, draft only, local only, or do not mutate.
- Resolve those phrases to `mutation_mode=apply|dry-run` and one canonical
  `issue_operation` from the shared option registry. Reject noncanonical
  structured tracker policy.
- Do not create new label taxonomy unless the repo's tracker configuration or
  user explicitly asks for it.

## Workflow

1. Resolve the target repository and `issue_operation`:
   - current checkout repo,
   - explicit `--repo <owner>/<repo>`,
   - or a target repository supplied by the user or calling workflow.
2. Resolve `mutation_mode` from the user request or canonical calling workflow
   handoff. Default to `dry-run` when mutation authority is absent. Reject
   unnormalized caller-owned policy fields.
3. If `mutation_mode=dry-run`, return draft issue bodies and exact `gh`
   commands without mutating GitHub.
4. If the evidence requires a user decision before publishing, ask, then store
   the answer as `mutation_mode=apply|dry-run` rather than branching on prose.
5. Read the relevant issue or label state before mutation.
6. For create, edit, or comment operations with generated Markdown or
   attachments, prepare safe body files and upload only authorized attachment
   files using the patterns in `references/workflows.md`.
7. Apply the smallest GitHub issue operation needed:
   - create issues with the requested title, body, type, labels, or parent,
   - set issue type,
   - add or remove labels,
   - add comments,
   - attach parent/sub-issue relationships,
   - add or remove one native `blocked by` issue dependency,
   - close only after the requested disposition is explicit,
   - reopen only when the requested transition is explicit.
8. If any multi-issue publication step fails after a partial mutation, stop,
   verify the current tracker state, clean up temp files, and retry only the
   missing or incorrect issue operations. A native dependency invocation owns
   one edge only: make one bounded readback after failure or ambiguity, return
   its terminal result, and never replay the mutation blindly.
9. Verify the changed issue or queue state after mutation. For attachments,
   require the exact stable upload URL in raw Markdown and, when the rendered
   interface is available, confirm that the media loads.
10. Report the issue URL/number, stable attachment URLs, commands run or
    drafted, any skipped mutation, and, for a dependency operation, its
    terminal result plus every available exact `blockedBy`/`blocking`
    readback. Never report a token or expiring private delivery URL.

## Routing

- Use `$g:github-tagger` when the issue must be read to choose among available
  labels or native issue types, or when an explicit request asks for
  repository-backed proposals for missing labels or organization issue types.
- Use `$g:github-repository-triage` for current-repository queue snapshots, stale/blocker
  grouping, and PR triage.
- Use `$g:github-investigation` when the question needs root cause, provenance, or
  fix-quality judgment before deciding issue disposition.
- Use `$g:github-review-threads` for PR review-thread context or replies.
- Use `$g:github-actions` for Actions, checks, and failing PR logs.
- Use `$g:github-releases` for tags, GitHub Releases, notes, and assets.
- Use `$g:send` for publishing local work as a branch and draft PR.

## References

- `references/workflows.md`: direct `gh` issue lifecycle commands, attachment
  uploads, and dry-run conventions. Read its attachment section before
  publishing a file in an issue body or comment.
- `../../references/options.md`: shared canonical G options.
