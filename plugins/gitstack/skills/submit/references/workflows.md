# Submit Workflows

## Publish New Work

Complete this read-only preflight before staging, committing, or pushing:

```bash
git status --short --branch
git diff --stat
git diff --staged --name-status
git symbolic-ref --quiet --short HEAD
git remote get-url origin
gh auth status
gh repo view --json nameWithOwner,defaultBranchRef,url
git config --get "branch.<branch>.remote"
git config --get "branch.<branch>.merge"
gh pr list --repo <owner/repo> --head <branch> --state open --limit 2 \
  --json number,title,url,isDraft,headRefName,headRepositoryOwner
```

Apply all of these gates before continuing:

- Stop on detached `HEAD`; do not invent or switch branches without owner
  authorization.
- Stop when `<branch>` equals `defaultBranchRef.name`; this workflow publishes
  a feature branch and never pushes the repository default branch.
- Resolve `<owner/repo>` from the checkout with `gh repo view`, then verify the
  `origin` URL identifies that same repository. Stop on a fork/base mismatch or
  an ambiguous remote instead of choosing a push target.
- If `branch.<branch>.remote` and `branch.<branch>.merge` are both absent, the
  first push may establish `origin/<branch>`. If either is present, require both
  and require exactly `origin` plus `refs/heads/<branch>`; stop on a different
  remote or branch.
- Require successful `gh auth status` before any push.
- Record whether the PR lookup returns zero or one open PR. Stop if it returns
  more than one or if its head branch/repository does not match the verified
  push target.
- When one PR exists, record its `isDraft` value. Updating its branch, title, or
  body must preserve that exact value; Submit never changes an existing PR
  between draft and ready.

After preflight and scope verification, reuse a suitable existing commit or run
the complete `$gitstack:git-commit` workflow with
`commit_operation=commit-only`, even when the
overall user request includes publishing. Do not stage or commit directly in
Submit: `$gitstack:git-commit` owns the pre-existing-index guard, explicit staging,
staged-diff verification, and commit authoring. Do not let the
delegated `$gitstack:git-commit` call push; Submit retains sole ownership of push after its
second publish preflight. Do not force `commit_kind=regular`: let Git Commit
apply its canonical default and honor an explicit or target-repository fixup
requirement only with an exact target.

After commit creation, rerun the complete publish preflight above immediately
before any push. Branch, remote, upstream, authentication, and PR state may
have changed while the commit was prepared. Only then publish:

```bash
git push                         # verified existing origin/<branch> upstream
git push -u origin HEAD          # only when the preflight found no upstream
gh pr list --repo <owner/repo> --head <branch> --state open --limit 2 \
  --json number,title,url,isDraft,headRefName,headRepositoryOwner
<plugin-root>/scripts/gitstack --json repo snapshot
<plugin-root>/scripts/gitstack --json publish open --repo <owner/repo> --title-file <absolute-title-file> --body-file <absolute-body-file> --draft --expected-worktree-fingerprint <sha256>
```

Use explicit pathspecs for staging. Run only one of the two push commands. Run
Run `publish open` only when the post-push lookup still returns no PR. It sends
title and body through JSON stdin, verifies exact UTF-8 byte fingerprints and
the returned PR target, and performs one exact-head read-back after an
ambiguous response. Do not retry it blindly.

When the post-push lookup returns an existing PR, do not run `publish open
--draft` and do not invoke any draft-state lifecycle mutation. Require its
post-update `isDraft` value to equal the pre-push value. An existing ready PR
therefore remains ready while its branch and optional title/body are updated.

After the post-push lookup returns the exact existing PR or `publish open`
returns the exact newly created PR, require the PR head to equal the full
published commit SHA. Then invoke `$gitstack:github-review-threads` for the
exact repository and PR with `review_operation=request`,
`mutation_mode=apply`, `provider=codex`, that full head SHA, and a fresh
Submit-owned request key for this logical publish invocation. Preserve the key
for reconciliation and persist the complete typed request receipt. This step
is required for both new and existing PR paths. It must use the typed request
operation, not a plain discussion comment.

Do not wait by default. If the user or a composing caller also requested
monitoring, invoke `$gitstack:github-review-threads` again with
`review_operation=wait`, the persisted complete receipt, and the caller-owned
bounded duration. Keep the request and wait as separate operations.

## No Publishable Local Work

Use this branch when the user invokes `submit` but the task is issue-only hygiene
or the checkout has no intended code/docs changes to publish.

```bash
git status --short --branch
gh auth status
gh issue list --state open --limit 50 --json number,title,state,url
```

If there are no relevant local changes to stage, do not create an empty commit,
branch, push, or PR. Route issue creation, comments, labels, type changes,
relationships, or closure to `$gitstack:github-issues` with
`mutation_mode=apply`, the exact repository and issue target, and one matching
`issue_operation` per write. Then verify the result with
`$gitstack:github-issues` or direct read-only `gh issue view` / `gh issue list`.

Close out by saying explicitly:

- full `submit` was not applicable because there was no publishable local change;
- which GitHub issue mutations were performed;
- current branch/worktree state;
- any untracked files intentionally left alone.

## Existing PR

Read the existing PR, then use the structured GitHub connector for title/body
edits. GitStack does not expose `publish edit`, and `gh pr edit` requires the
free-form title in argv.

```bash
gh pr view <number> --repo <owner/repo> \
  --json number,title,body,url,isDraft,headRefName,headRepositoryOwner,baseRefName
```

Verify `headRefName` and the head repository still match the preflight before
editing. Never silently retarget a PR or change its `isDraft` value. If
`isDraft=false`, keep the PR ready; if `isDraft=true`, keep it draft. After the
normal push updates this PR, verify its full head SHA and unchanged draft state,
then perform the same required typed current-head Codex review request
described in `Publish New Work`.

## Safe Retry

- A normal `git push` is safe to retry after re-running the remote/upstream and
  branch gates. Do not add `--force` or `--force-with-lease` unless the owner
  explicitly authorizes history rewriting for the named branch.
- If a push reports a network or transport error, compare the local commit with
  the remote branch before retrying; the remote may already have accepted it.
- If `publish open` reports an ambiguous write, preserve its read-back evidence
  and stop. It already performed the only automatic exact-head read-back; do
  not issue another create attempt.
- If the typed Codex review request fails after a confirmed push or PR
  creation, preserve and report the successful publish evidence and the exact
  review-request failure separately. Do not repeat the push, PR creation, or
  review request blindly.
- On any changed branch, remote, upstream, authentication, or PR state, stop and
  rerun the full preflight rather than continuing from stale assumptions.

## Closeout

Return:

- branch name
- commit hash
- PR URL
- whether the PR is draft or ready
- current-head Codex review request status and typed receipt identity
- validation performed before publishing

If CI fails or review comments need follow-up, route to
`$gitstack:github-actions` or `$gitstack:github-review-threads` after the
publish and required review-request steps. Supply the exact repository and PR
plus one `review_operation`; add `mutation_mode=apply` only for an authorized
reply, request, review submission, or resolution.
