---
name: git-commit
description: "Create local Git commits or push them when requested. Use $yeet for pull-request publication."
---

# Git Commit

Use direct Git commands. A commit request is local-only; push only when
requested. A push-only request never stages files or creates commits. Use
`$yeet` for PR publication. Reuse established scope and authorization.

## Preserve the intended change

Inspect the branch, worktree, and pre-existing staged paths before staging.
Review the intended diff; stage explicit paths or selected hunks, then verify
that the staged content matches the requested commit. Split independent
responsibilities into separate commits. Do not sweep unrelated edits into a
commit or reset the user's index to make it convenient.

For unrelated staged work, use the full-file isolation path in
[workflows.md](references/workflows.md#unrelated-staged-work) only when the
intended complete files are authorized. Partial-hunk or ambiguous ownership
needs a scoped decision; leave unrelated staged content intact.

Use a concise imperative subject, with a body only when rationale or validation
needs explanation. Complete applicable repository checks before committing.
Verify the resulting commit and remaining worktree/index. For a requested push,
verify the intended branch, upstream, and commit range, then the remote result.
Report local commits and pushed state separately.

## Targeted commits

Default to a regular commit. Select `fixup` or `amend-fixup` only when explicitly
requested or required by repository instructions; review feedback alone does
not select one. Before either, read
[workflows.md](references/workflows.md#targeted-fixup-and-amend-fixup) for target
validation and the noninteractive editor adapter. These operations create a new
commit; never amend the target in place, autosquash, rebase, or force-push as an
incidental part of this skill.

For explicitly authorized issue closure through a regular commit, include
closing references only for satisfied issues. Do not add them to generated
fixup messages. Hosted issue edits belong to `$github-issues`.

## Composed invocation

These fields let existing callers express the same operations; ordinary user
requests do not need a structured invocation.

| Field | Values | Meaning |
| --- | --- | --- |
| `commit_operation` | `commit-only`, `commit-and-push`, `push-only` | Requested action; a plain commit request selects `commit-only`. |
| `commit_kind` | `regular`, `fixup`, `amend-fixup` | Defaults to `regular` for commit creation; omitted for push-only. |
| `target_commit` | Exact commit reference | Required only for targeted kinds; resolve and validate to one full ancestor SHA. |
