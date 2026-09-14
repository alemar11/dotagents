# Exceptional Commit Workflows

Read only the branch needed by the request. Ordinary staging, committing, and
pushing use the [entrypoint](../SKILL.md) and direct Git commands.

## Unrelated staged work

Record the pre-existing index before staging. When the user authorizes a commit
of complete intended files while preserving unrelated staged entries, review
those files against `HEAD` and isolate the commit:

```bash
git diff HEAD -- <explicit-paths>
git commit --only -F <message-file> -- <explicit-paths>
git status --short --branch
git diff --staged --name-status
```

`--only` reads the complete current file contents, including unstaged changes.
Do not use it for selected hunks. Verify that unrelated staged contents are
unchanged afterward. If ownership or intended hunks are unclear, ask about that
scope without resetting or rewriting the index.

## Targeted fixup and amend-fixup

Resolve `<skill-root>` to the directory containing this skill's `SKILL.md`.
Before staging, run:

```bash
target_sha=$(<skill-root>/scripts/validate-fixup-target <target-commit>)
git show --stat --oneline --no-renames "$target_sha"
```

Continue only if validation succeeds. It resolves one ancestor of `HEAD` and
requires a nonempty subject unique across reachable history, because Git's
fixup matching uses that subject. Stop on a missing, non-ancestor, or ambiguous
target. Independently review the target diff and intended refinement: the
helper cannot prove they belong together. Split distinct target refinements.

After reviewing and staging the refinement, let Git generate the matcher:

```bash
git commit --fixup="$target_sha"
```

Use `amend-fixup` only when the target's message also needs replacement. Read
that message and prepare a UTF-8 file outside the repository containing the
complete replacement subject and body, without an `amend!` prefix. Then use:

```bash
G_AMEND_MESSAGE_FILE=<absolute-replacement-file> \
 GIT_EDITOR=<skill-root>/scripts/replace-amend-fixup-message \
 git commit --fixup="amend:$target_sha"
```

The editor adapter retains Git's generated `amend! <original subject>` matcher
and replaces the following message. It rejects a missing matcher, empty
replacement, or replacement that includes its own matcher. Do not substitute
an ordinary `git commit -F` for this command.

For either kind with unrelated staged work, the full-file isolation rule above
also applies. Require `git diff --quiet -- <explicit-paths>` to succeed before
using `git commit --only --fixup=... -- <explicit-paths>`; otherwise unstaged
hunks could enter the fixup. Review the staged refinement immediately before
committing. Partial-hunk isolation is unsupported on this path.

Verify the new commit's message, target, and contents and the preserved index.
The target remains unchanged; any later history rewrite is separately owned.

Any CI or review gate bound to the old HEAD needs evidence for the new published
commit; a fixup does not carry the target's passing evidence forward.
