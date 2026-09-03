# Send Workflows

## Publish New Work

Complete this read-only preflight before staging, committing, or pushing:

```bash
<plugin-root>/scripts/g --json publish preflight --repo <owner/repo>
```

The shared command owns the branch, status, origin, upstream, authenticated
GitHub API, default-branch, and matching open-PR checks. Run the complete
command with scoped network permission from the outset. Do not replace it with
an ad hoc group of raw `git` and `gh` commands or run only its authentication
check in the restricted sandbox.

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
- Require successful `gh auth status` from the network-capable shared preflight
  before any push. A result from a restricted sandbox is inconclusive and must
  not be used to diagnose or change credentials.
- Record whether the PR lookup returns zero or one open PR. Stop if it returns
  more than one or if its head branch/repository does not match the verified
  push target.
- When one PR exists, record its `isDraft` value. Updating its branch, title, or
  body must preserve that exact value; Send never changes an existing PR
  between draft and ready.

### Base Selection And Existing PR Reuse

Resolve the intended PR base branch before commit or push. Use the explicit base
branch supplied by the composing caller for a new PR; otherwise use
`defaultBranchRef.name`. A non-default explicit base is valid and is not evidence
of a stack. The current implementation or feature head branch is not a PR base
merely because another contract calls it `target_branch_name`.

When the preflight finds exactly one matching open PR for the current branch,
that PR is the publication target. If no base was explicitly supplied, preserve
its exact `baseRefName`; if a base was supplied, require it to equal that
read-back base. A missing or ambiguous base, an explicit-base mismatch, a fork
head, or a repository mismatch blocks mutation. Never retarget an existing PR or
silently fall back to the default branch. Preserve its `isDraft` value.

Send does not infer, verify, link, or manage a stack. A composing workflow that
has already established a parent/child relationship invokes the separate
`$g:github-stack` flow after Send's publication readback. Do not make
`gh stack submit` the fallback: it publishes every local stack branch and
bypasses Send's one-branch push, body, and draft-state contracts.

### Closing Issue References

Before committing or mutating a PR, receive the exact caller-owned
`closing_issue_refs` set for issues fully resolved by this PR. A composing
workflow owns the implementation and acceptance evidence; Send validates the
issue identities and transports the set. Preserve valid closing references
already present in an existing PR description.

Do not derive a closing ref from a bare number, branch name, commit subject,
parent Feature Spec, related issue, dependency, or issue whose accepted scope
is only partially satisfied. A parent issue is closable only when this PR
itself satisfies that parent's complete accepted scope. Plain mentions and
phrases such as `Related to #12` are tracking context, not
`closing_issue_refs`.

Normalize each candidate to `<owner>/<repository>#<number>`, deduplicate the
set, and verify every exact issue:

```bash
gh issue view <number> --repo <owner/repository> \
  --json number,state,title,url
```

Stop if a candidate is missing, resolves to another repository or number, is a
pull request rather than an issue, or has conflicting ownership or completion
evidence. Preserve a valid existing closing reference even when its issue is
already closed; it remains part of the PR's tracking history. Do not add a new
closing reference for an already-closed issue unless the explicit or accepted
execution evidence still identifies it as resolved by this PR.

The selected PR base does not change this validation. Send carries the exact
caller-provided set to the PR body and verifies the canonical lines and provider
references; it does not decide whether the current delivery topology will make
GitHub close those issues or mutate an issue directly. A composing workflow such
as Implement owns the standalone/stacked interpretation and any separate
post-publication delivery verification.

Render one line per issue under this exact PR-description section:

```markdown
## Issues

Closes #10
Closes #123
Closes octo-org/octo-repo#100
```

Use repository-local shorthand only when the issue and PR share the same
repository. Use `Closes <owner>/<repository>#<number>` for every cross-repository
issue. Each issue gets its own complete `Closes` line; do not render one keyword
followed by a comma-separated list.

For a new PR, preserve the repository PR template and append `## Issues` when
it has no issue-link section. If a template already owns an issue-link section,
place the canonical lines there without duplicating the heading. For an
existing PR, read its complete body, preserve unrelated template and author
content byte-for-byte where possible, union its valid closing refs with the
new verified set, and update only the issue-link section. Stop instead of
silently deleting, changing, or duplicating a conflicting closing reference.

When the verified set is empty, omit `## Issues`; do not emit `Closes none`, a
blank placeholder, or a guessed ref. Record `closing_issue_refs=[]` in the
closeout.

After preflight and scope verification, reuse a suitable existing commit or run
the complete `$g:git-commit` workflow with
`commit_operation=commit-only`, even when the
overall user request includes publishing. Do not stage or commit directly in
Send: `$g:git-commit` owns the pre-existing-index guard, explicit staging,
staged-diff verification, and commit authoring. Do not let the
delegated `$g:git-commit` call push; Send retains sole ownership of push after its
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
<plugin-root>/scripts/g --json repo snapshot
<plugin-root>/scripts/g --json publish open --repo <owner/repo> --title-file <absolute-title-file> --body-file <absolute-body-file> --base <pr-base-branch> --draft --expected-worktree-fingerprint <sha256>
```

Use explicit pathspecs for staging. Run only one of the two push commands. Run
`publish open` only when the post-push lookup still returns no PR. It sends
title and body through JSON stdin, verifies exact UTF-8 byte fingerprints and
the returned PR target, and performs one exact-head read-back after an
ambiguous response. Do not retry it blindly.

Before `publish open`, require the body file to contain the complete canonical
`## Issues` section whenever `closing_issue_refs` is nonempty. After creation,
read back the PR description and require every expected `Closes` line exactly
once. The base read-back must equal the selected `<pr-base-branch>` regardless
of whether that branch is the repository default.

When the post-push lookup returns an existing PR, do not run `publish open
--draft` and do not invoke any draft-state lifecycle mutation. Require its
post-update `isDraft` value to equal the pre-push value. An existing ready PR
therefore remains ready while its branch and optional title/body are updated.
Require its base to equal the pre-push base or the explicitly requested base;
Send never silently retargets an existing PR.

After the post-push lookup returns the exact existing PR or `publish open`
returns the exact newly created PR, require the PR head to equal the full
published commit SHA. Verify the exact repository, PR, base, full published head
SHA, draft state, and issue linkage. Send stops after this publication evidence.
It must not
request or wait for an automated Codex review. A composing workflow may invoke
`$g:github-review-threads` separately using this exact publication evidence;
the ready transition and any automatic provider review remain outside Send.

## No Publishable Local Work

Use this branch when the user invokes `send` but the task is issue-only hygiene
or the checkout has no intended code/docs changes to publish.

```bash
git status --short --branch
gh auth status
gh issue list --state open --limit 50 --json number,title,state,url
```

If there are no relevant local changes to stage, do not create an empty commit,
branch, push, or PR. Route issue creation, comments, labels, type changes,
relationships, or closure to `$g:github-issues` with
`mutation_mode=apply`, the exact repository and issue target, and one matching
`issue_operation` per write. Then verify the result with
`$g:github-issues` or direct read-only `gh issue view` / `gh issue list`.

Close out by saying explicitly:

- full `send` was not applicable because there was no publishable local change;
- which GitHub issue mutations were performed;
- current branch/worktree state;
- any untracked files intentionally left alone.

## Existing PR

Read the existing PR including its body and base. For title or body edits,
write the complete reviewed request object to an absolute JSON file and send
it through `gh api --input`; do not use `gh pr edit` with free-form text in
argv.

```bash
gh pr view <number> --repo <owner/repo> \
  --json number,title,body,url,isDraft,headRefName,headRepositoryOwner,baseRefName
gh api --method PATCH repos/<owner>/<repo>/pulls/<number> \
  --input <absolute-request-json>
```

Verify `headRefName` and the head repository still match the preflight before
editing. Never silently retarget a PR or change its `isDraft` value. Preserve
the existing `baseRefName`, merge the canonical issue lines into the existing
body, and read back every expected line exactly once. Preserve every previously
valid closing reference. If `isDraft=false`, keep the PR ready; if `isDraft=true`,
keep it draft. After the normal push updates this PR, verify its full head SHA,
unchanged draft state, unchanged base, and complete issue linkage. If the caller
also needs a stack relationship, invoke `$g:github-stack` separately after this
publication readback.

## Safe Retry

- A normal `git push` is safe to retry after re-running the remote/upstream and
  branch gates. Do not add `--force` or `--force-with-lease` unless the owner
  explicitly authorizes history rewriting for the named branch.
- If a push reports a network or transport error, compare the local commit with
  the remote branch before retrying; the remote may already have accepted it.
- If `publish open` reports an ambiguous write, preserve its read-back evidence
  and stop. It already performed the only automatic exact-head read-back; do
  not issue another create attempt.
- On any changed branch, remote, upstream, authentication, or PR state, stop and
  rerun the full preflight rather than continuing from stale assumptions.

## Closeout

Return:

- branch name
- commit hash
- PR URL
- whether the PR is draft or ready
- PR base and current default branch
- canonical `closing_issue_refs` and exact PR-body read-back
- exact published head SHA and draft-state read-back
- validation performed before publishing

If CI fails or review comments need follow-up, route to
`$g:github-actions` or `$g:github-review-threads` after the
publish step. Supply the exact repository and PR
plus one `review_operation`; add `mutation_mode=apply` only for an authorized
reply, request, review submission, or resolution.
