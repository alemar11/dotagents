# GitHub Issues

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../network-execution.md).

## Transport

Use authenticated `gh` for every provider read and write. Use high-level `gh`
commands when their free-form fields are file-backed; otherwise use a reviewed
JSON request file with `gh api --input`. Use the shipped attachment uploader as
the only attachment transport. Before the first provider operation, load
[`../../gh-dependency-preflight.md`](../../gh-dependency-preflight.md) and
require its host and authentication checks.

Use the `<skill-root>` resolved by the active G entrypoint. For every attachment upload, use only:

```bash
<skill-root>/scripts/g --json attachment upload \
  --repo <owner/repo> \
  --file <absolute-file>
```

## Role

Own GitHub issue lifecycle mechanics. Use this workflow when another workflow has
already decided what issue content, label, type, state, or relationship is
needed and needs the GitHub operation performed or drafted.

Keep product planning, issue splitting, metadata classification and taxonomy
proposals, queue triage, CI, review threads, releases, stars, commits, and PR
publishing in their focused workflows. The `github-tagger` workflow owns evidence-backed
label and type selection and read-only taxonomy proposals; this workflow only
handles GitHub Issues lifecycle mechanics.

## Core Rules

- Use direct `gh` or file-backed `gh api --input` operations. Use the shipped
  `attachment upload` command as the only attachment transport; never
  reproduce its token or HTTP logic.
- Confirm repository context before mutation, using the current checkout or an
  explicit `--repo <owner>/<repo>`.
- Keep issue titles, bodies, label descriptions, comments, and other free-form
  provider fields out of argv. Use a body-file-capable high-level command or a
  reviewed JSON request file with `gh api --input`.
- Create temporary `--body-file` inputs outside checkout-owned artifact paths
  and remove them after mutation unless the user or calling workflow explicitly
  provides a persistent body-file or local mirror path.
- Own safe body-file transport for composing workflows. When a caller supplies
  generated Markdown body text, this workflow creates the transient body files,
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
- Return exactly one canonical native dependency result from
  [../../states.md](../../states.md) per invocation. The caller owns
  whether a non-success result is a workflow gate.
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
   files using the patterns in `workflows.md`.
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

- Use the `github-tagger` workflow when the issue must be read to choose among available
  labels or native issue types, or when an explicit request asks for
  repository-backed proposals for missing labels or organization issue types.
- Use the `github-repository-triage` workflow for current-repository queue snapshots, stale/blocker
  grouping, and PR triage.
- Use the `github-investigation` workflow when the question needs root cause, provenance, or
  fix-quality judgment before deciding issue disposition.
- Use the `github-review-threads` workflow for PR review-thread context or replies.
- Use the `github-actions` workflow for Actions, checks, and failing PR logs.
- Use the `github-releases` workflow for tags, GitHub Releases, notes, and assets.
- Use the `send` workflow for publishing local work as a branch and draft PR.

## References

- `workflows.md`: direct `gh` issue lifecycle commands, attachment
  uploads, and dry-run conventions. Read its attachment section before
  publishing a file in an issue body or comment.
- `../../states.md`: canonical native dependency result states.
- `../../options.md`: shared canonical G options.
