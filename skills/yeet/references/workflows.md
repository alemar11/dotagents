# Yeet Workflows

## Publish New Work

Before staging, committing, or pushing, inspect the checkout with Git and `gh`:

```bash
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --porcelain=v1
git remote get-url origin
git config --get branch.<branch>.remote
git config --get branch.<branch>.merge
gh repo view --json nameWithOwner,defaultBranchRef
gh pr list --repo <owner/repo> --head <owner>:<branch> --state open --limit 2 \
 --json number,url,isDraft,headRefName,headRepositoryOwner,headRepository,baseRefName
```

Resolve placeholders from observed values and check authentication as required
by `SKILL.md`. An absent upstream configuration is allowed only as described
below. Record the full HEAD SHA and worktree state; do not stash or discard
unrelated changes to make publication pass.

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
- Require successful `gh auth status` in a network-enabled context
 before any push. A result from a restricted sandbox is inconclusive and must
 not be used to diagnose or change credentials.
- Record whether the PR lookup returns zero or one open PR. Stop if it returns
 more than one or if its head branch/repository does not match the verified
 push target.
- When one PR exists, record its `isDraft` value. Updating its branch, title, or
 body must preserve that exact value; Yeet never changes an existing PR
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

Yeet does not infer, verify, link, or manage a stack. A composing workflow that
has already established a parent/child relationship invokes the separate
`$github-stacked-pr` flow after Yeet's publication readback. Do not make
`gh stack submit` the fallback: it publishes every local stack branch and
bypasses Yeet's one-branch push, body, and draft-state contracts.

### Closing Issue References

Before committing or mutating a PR, receive the exact caller-owned
`closing_issue_refs` set for issues fully resolved by this PR. The caller owns
the acceptance evidence for that set; Yeet validates the issue identities and
transports them. Preserve valid closing references already present in an
existing PR description.

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

The selected PR base does not change this validation. Yeet carries the exact
caller-provided set to the PR body and verifies the canonical lines and provider
references; it does not decide whether the current delivery topology will make
GitHub close those issues or mutate an issue directly. A composing caller owns
the standalone/stacked interpretation and any separate post-publication
delivery verification.

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
the complete `$git-commit` workflow with
`commit_operation=commit-only`, even when the
overall user request includes publishing. Do not stage or commit directly in
Yeet: `$git-commit` owns the pre-existing-index guard, explicit staging,
staged-diff verification, and commit authoring. Do not let the
delegated `$git-commit` call push; Yeet retains sole ownership of push after its
second preflight. Do not force `commit_kind=regular`: let Git Commit
apply its canonical default and honor an explicit or target-repository fixup
requirement only with an exact target.

After commit creation, rerun the complete preflight above immediately
before any push. Branch, remote, upstream, authentication, and PR state may
have changed while the commit was prepared. Only then publish:

Record the full intended commit SHA. Fetch the verified origin branch when it
exists and compare it with local HEAD; stop if local HEAD is behind or diverged.
Recheck HEAD and the worktree after fetching. Push only the verified branch,
without force, using an explicit destination:

```bash
git push origin HEAD:refs/heads/<branch>
# For the first push only:
git push -u origin HEAD:refs/heads/<branch>
```

Run only the applicable command. Verify the remote branch SHA equals the
recorded commit, then repeat the exact-head open-PR lookup. If HEAD, branch,
remote, upstream, or worktree changed unexpectedly, reconcile before continuing.
A newly appeared matching PR must be read and reused with its base and draft
state preserved; stop on ambiguity or an explicit-base mismatch.

When no PR exists, write a complete JSON request file with `title`, `body`,
`head`, `base`, and `draft: true`. Use a JSON serializer to preserve literal
text; the title must be one nonempty line without a trailing line terminator.
Inspect the final text, repository template, and verified closing references.
Immediately before creating, recheck local HEAD, remote branch SHA, worktree
state, and the absence of a matching PR. Then create once:

```bash
gh api --method POST repos/<owner>/<repo>/pulls --input <absolute-request-json>
```

For an existing PR, use the Existing PR procedure below. Never change its base
or draft state. After either operation, independently read the exact PR back:

```bash
gh pr view <number> --repo <owner/repo> \
 --json number,url,title,body,headRefName,headRefOid,headRepository,headRepositoryOwner,baseRefName,isDraft
```

Verify repository and PR identity, head branch and full published SHA, selected
base, expected draft state, exact intended title/body, and every expected closing
line exactly once. Recheck local HEAD and worktree state after publication;
report an unexpected change separately from the observed remote result. A
successful create response alone is not verified publication. Follow Safe Retry
below for errors or uncertain effects.

Yeet stops after publication and requested attachments. A composing caller may
invoke `$review-pr` or `$github-stacked-pr` separately with the exact
repository, PR, and published SHA; Yeet does not request or wait for review.

## No Publishable Local Work

Use this branch when the user invokes `yeet` but the task is issue-only hygiene
or the checkout has no intended code/docs changes to publish.

```bash
git status --short --branch
gh auth status
gh issue list --state open --limit 50 --json number,title,state,url
```

If there are no relevant local changes to stage, do not create an empty commit,
branch, push, or PR. Perform explicitly requested issue operations with `gh`
against the exact repository and issue target. Use file-backed bodies or
structured JSON input for text. Read back the affected issue to verify the
result; reconcile ambiguous writes before retrying.

Close out by saying explicitly:

- full `yeet` was not applicable because there was no publishable local change;
- which GitHub issue mutations were performed;
- current branch/worktree state;
- any untracked files intentionally left alone.

## Existing PR

Read the existing PR including its body and base. For title edits, or body edits
without new attachments, write the complete reviewed request object to an
absolute JSON file and send it through `gh api --input`; do not use
`gh pr edit` with free-form text in argv.

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
also needs a stack relationship, invoke `$github-stacked-pr` separately after this
publication readback.

## PR Attachments

For caller-selected images or videos, verify `gh pr edit --help` exposes
`--attach` before publication. Use native `gh` uploads; do not install an
extension or use a custom upload endpoint. Missing support blocks the attachment
step and does not authorize upgrading `gh`. Check repository push access and
current media type and size limits in
[GitHub's attachment guide](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli).

For new PRs, use the file-backed creation procedure above. Create with
prose that omits unpublished local media references, then attach to the verified
PR. For existing PRs, retain the same head, base, and draft-state checks.

```bash
gh pr edit <number> --repo <owner/repo> --attach <absolute-image-file>
gh pr edit <number> --repo <owner/repo> \
 --body-file <absolute-complete-body-file> --attach <absolute-image-file>
```

Choose append-only or complete-body replacement as requested. In a replacement
file, use `![Alt text](<absolute-image-file>)`, or a standalone
`![](<absolute-video-file>)` paragraph for a video, with the same path supplied
to `--attach`. `gh` rewrites local references and appends unreferenced files.
Repeat the flag for distinct files, up to 50. Keep alt text in the body file.

Upload only authorized files in apply mode. A dry run prepares the final body
and command without executing it. After the edit, including a nonzero exit,
read the exact PR back and verify media URLs, preserved text and closing refs,
full head SHA, base, and draft state. Check rendering when available and retain
stable Markdown URLs rather than private signed delivery URLs. Report partial
uploads separately from PR publication; reconcile before retrying only proven
missing work, never recreate the PR. Attachment work finishes before closeout.

## Safe Retry

- A normal `git push` is safe to retry after re-running the remote/upstream and
 branch gates. Do not add `--force` or `--force-with-lease` unless the owner
 explicitly authorizes history rewriting for the named branch.
- If a push reports a network or transport error, compare the local commit with
 the remote branch before retrying; the remote may already have accepted it.
- After an uncertain PR creation, perform one lookup by exact head repository
 and branch, then read the unique candidate. Verify its target, text, draft
 state, published SHA, and available author/creation-time evidence against the
 attempted write. If absent, ambiguous, or mismatched, report the unresolved
 result and stop; do not issue another create attempt.
- After an uncertain update, read the same PR and compare its current text with
 the intended request before retrying. Never create a replacement PR.
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

For CI failures after publication, inspect the failing run and logs with `gh`,
binding the evidence to the published SHA and run attempt. Distinguish local
fix validation from a successful remote run; publication alone does not authorize
reruns or additional pushes. The caller can use `$review-pr` for a hosted Codex
review of the exact repository, PR, and published SHA. Other explicitly
requested review actions use authenticated `gh` directly; publication does not
authorize replies, formal review submissions, or thread resolution.
