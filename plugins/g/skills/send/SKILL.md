---
name: send
description: Send local work to GitHub. Use when the user explicitly requests the complete flow to confirm scope, commit, push the branch, link every confirmed resolved issue for automatic closure, open a draft or update an existing pull request without changing its draft state, and link the new PR to an existing target PR when applicable.
---

# Send

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../references/network-execution.md).
Connector calls and local-only commands do not use shell escalation.

## Role

Publish local work from a checkout. This skill composes bundled G
skills, direct `git`, the shared CLI, and connector-backed PR operations:

- Use `$g:git-commit` for staging and commit authoring.
- Use `<plugin-root>/scripts/g publish preflight` for structured local
  readiness and `publish open --title-file --body-file` for new PRs. Use the
  connector for supported existing-PR lifecycle operations. Do not put PR
  title or body text in argv or a shell string.
- When the publish path is selected, load
  [`../../references/gh-dependency-preflight.md`](../../references/gh-dependency-preflight.md)
  before the first `gh`-dependent command. The shared reference owns the
  `gh` availability, authentication, and conditional `gh-stack` checks.
- Use `<plugin-root>/scripts/g stack ensure` and `stack link` only when
  the selected PR base branch is the head of exactly one existing PR in the
  same repository. Pass PR numbers in bottom-to-top order so this operation
  links the two published PRs without taking ownership of another branch's
  push. Do not use `stack submit` for this path.
- Use `$g:github-issues`, `$g:github-repository-triage`, `$g:github-investigation`, `$g:github-actions`,
  or `$g:github-review-threads` only for focused follow-up GitHub work.

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md`. The CLI cannot invoke connector tools; it uses direct `git` and
authenticated `gh` for its preflight and fallback commands.

If there is no local work to publish, or the request is only GitHub issue
hygiene such as creating, commenting on, labeling, or closing issues, do not run
the full publish flow. Route that work to `$g:github-issues`, perform the
authorized GitHub issue operation with resolved `mutation_mode=apply|dry-run`,
the exact repository and issue target, and one canonical `issue_operation`, and
state that full `send` was not applicable.

Prefer the shortest publish path that matches the state in front of you:

- If a good local commit already exists, reuse it instead of reopening commit
  authoring.
- If the branch already has a PR, update that PR instead of treating the run as
  a fresh publish. Preserve its current draft or ready state and return the
  exact publication read-back.
- If the selected PR base branch is itself the head of exactly one open PR in
  this repository, publish or update the current PR against that branch and
  link the target and current PR as one stacked pair after the child PR is
  read back. This is one explicit link, not automatic management of a local
  stack.
- If there is no publishable local change, stop early and route issue-only
  follow-up to `$g:github-issues`.

## Target PR And Stacked Link

Resolve the PR base branch before committing or pushing. Use the explicit base
branch supplied by the caller; otherwise use the repository default branch.
Never treat the worker or feature head branch as the PR base merely because it
is named `target_branch_name`.

When the selected base is not the default branch, look for the target PR by its
head branch, not by its base branch:

```bash
gh pr list --repo <owner/repo> --state open \
  --head <owner>:<pr-base-branch> --limit 2 \
  --json number,url,state,headRefName,headRepositoryOwner,headRepository,baseRefName,isDraft
```

Treat the result as follows:

- Zero PRs: continue the normal single-PR flow, using `--base
  <pr-base-branch>` for a new PR when that base was explicitly selected.
- Exactly one PR: record it as `target_pr` and use the stacked path after the
  current PR exists. The target PR is the bottom item and the current PR is the
  top item.
- More than one PR, a fork head, a different head branch, or a repository
  mismatch: stop before mutation. Do not choose a parent heuristically.

After the current PR is created or updated and its exact base, head, title,
body, and draft state are read back, run:

```bash
<plugin-root>/scripts/g --json stack ensure
<plugin-root>/scripts/g --json stack link <target-pr-number> <current-pr-number>
```

Use PR numbers, never branch arguments, so `Send` remains the sole owner of the
current branch push. Omit `--open`: linking must not convert either PR from
draft to ready. `stack ensure --install` requires separate explicit authority
and is never implicit. Read back both PRs after the link and record the command
output or stack identity as the `stack_link_receipt`.

Do not call `stack submit`, `stack push`, `stack sync`, `stack rebase`, or
`stack merge` from this skill. Those commands can publish, rewrite, or operate
on more than the current branch. If linking fails or its result is ambiguous,
report the current PR as published and the stack link as unverified; do not
repeat publication or the link blindly.

Stack detection does not relax the issue-linkage contract. A non-default child
PR with nonempty `closing_issue_refs` remains blocked by the default-branch
requirement; never move those references to `target_pr` automatically, because
that would mutate another PR's body and ownership.

## Issue Linkage Contract

Resolve `closing_issue_refs` as factual input: the exact GitHub issues whose
accepted scope is fully satisfied by this PR. Collect them from explicit user
or caller input and unambiguous execution or tracker evidence. Validate every
candidate against its exact GitHub repository and issue before PR mutation.
Never infer an issue from a bare number, branch name, commit subject, nearby
issue, parent Feature Spec, dependency, or partial implementation.

When `closing_issue_refs` is nonempty:

- require the PR base to equal the repository's current default branch;
- include one canonical `Closes` line per deduplicated issue under `## Issues`
  in the PR description, using `Closes #<number>` for the PR repository and
  `Closes <owner>/<repository>#<number>` for another repository;
- preserve and union valid closing references already present when updating a
  PR, without replacing unrelated template or author content;
- stop on conflicting, ambiguous, missing, or only partially satisfied issue
  evidence rather than adding a closing keyword that could close the wrong
  issue.

When no issue is confirmed, omit `## Issues` rather than inventing a placeholder
or asking merely to fill the section. Report the empty linkage result in the
closeout. See `references/workflows.md` for body construction and verification.

## Workflow

1. Run the complete publish preflight before any push: require a named branch,
   reject the repository default branch, verify `gh` authentication, verify the
   `origin` repository and any configured upstream match the current branch,
   and look up an existing open PR for that branch. The shared network execution
   contract applies to the complete GitHub-dependent preflight from the outset.
2. Resolve `<pr-base-branch>` and perform the read-only target-PR lookup above.
   Capture zero or one exact `target_pr`; stop on ambiguity and repeat this
   lookup after the commit/preflight boundary.
3. Inspect worktree state and confirm the intended scope when it is mixed.
4. Resolve and validate `closing_issue_refs`. Read an existing PR body when
   present, preserve its valid closing references, and prepare the complete
   template-aware PR body. If the resulting set is nonempty, require the PR
   base to equal the current default branch before any PR mutation.
5. Reuse the current commit when it already represents the intended scope.
   Otherwise create one through `$g:git-commit` with
   `commit_operation=commit-only`; Send retains ownership of push. Do not
   override Git Commit's `commit_kind` selection: it defaults to `regular` and
   may select a targeted fixup only from the explicit request or
   target-repository instructions with an exact target.
6. Rerun the complete publish preflight immediately before pushing and repeat
   the target-PR lookup. The selected base and exact `target_pr` identity must
   still agree; otherwise stop and reconcile the changed remote state. Use a
   normal push to the verified upstream, or `git push -u origin HEAD` only when
   no upstream exists. Never infer permission to force-push.
7. Re-check for an existing PR after push. Open a draft PR only when none
   exists; otherwise update the existing PR without changing its `isDraft`
   value. In particular, a ready PR must remain ready; never call a draft
   conversion or the draft-only creation path for an existing PR. After an
   ambiguous create failure, look up the PR again before retrying so a
   successful first request cannot create a duplicate. Read back the PR body
   and require the exact canonical `Closes` line for every resolved
   `closing_issue_ref`. If `target_pr` exists, require an existing child PR's
   base to equal the selected target branch; never retarget it implicitly. Read
   back the target identity and child base before linking, then run the typed
   `stack link` flow above and verify both PRs after the link.
8. Stop after publication and its read-backs. Send must not request or wait for
   an automated Codex review. If a composing workflow needs one, it must invoke
   `$g:github-review-threads` as a separate operation using the exact repository,
   PR, and full published head SHA from Send's publication evidence. The ready
   transition and any automatic provider review remain outside Send.
9. Return branch, PR URL, commit hash, PR base, canonical
   `closing_issue_refs`, issue-linkage verification, exact published head and
   draft-state read-back, stacked target PR identity and `stack_link_receipt`
   when applicable, and verification performed. If the
   post-publication verification or stack link fails after the push or PR
   mutation succeeded, preserve and report the successful publish evidence
   separately; do not repeat the push, PR creation, or link blindly.

## References

- `references/workflows.md`: publish, existing-PR, and retry workflows.
- `../../references/options.md`: shared canonical G options.
