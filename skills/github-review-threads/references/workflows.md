# GitHub Review Workflows

## Inspect the PR and threads

Read the PR identity and HEAD, then paginate the relevant provider collections:

```bash
gh pr view <number> --repo <owner/repo> \
  --json number,url,state,isDraft,headRefOid,headRefName,headRepository,headRepositoryOwner
gh api --paginate repos/<owner>/<repo>/pulls/<number>/reviews
gh api --paginate repos/<owner>/<repo>/pulls/<number>/comments
gh api --paginate repos/<owner>/<repo>/issues/<number>/comments
```

Use `gh api graphql --input <request-json>` for review threads. Query the exact
repository and PR's `reviewThreads` connection, retaining thread `id`,
`isResolved`, `isOutdated`, and comments' `id`, `databaseId`, URL, body, author,
and commit identity. Follow `pageInfo` on both the thread collection and each
nested comments collection; one page is not proof of absence. GraphQL errors
or partial data are incomplete evidence even when the process exits zero.

Map REST review-comment IDs to their returned GraphQL node IDs and actual
thread membership. Never derive a node ID from a number. Default to unresolved,
current threads; include resolved/outdated history when needed to reconcile a
specific operation or when requested. Return actionable findings with links;
do not implement fixes as part of this skill.

## Request or resume Codex review

Read [states.md](states.md) for the record shared with callers. Verify the ready
PR and expected full HEAD. A draft is deferred to the caller; this skill does
not mark it ready. Inspect existing requests and reviews before posting.
Reuse a correlated current-target terminal result or resume a pending cycle;
missing local records do not prove that no request was sent.

For an authorized new explicit cycle, place `@codex review` in a UTF-8 body file.
Record the expected HEAD and creation time locally; the mention is a request to
review the PR, not an API guarantee that execution is pinned to a commit.
Recheck HEAD immediately before posting, then use:

```bash
gh pr comment <number> --repo <owner/repo> --body-file <request-body-file>
```

Capture and read back the exact returned comment, its author and creation time,
and recheck PR HEAD. Keep these facts and the original deadline in the review
record. Do not add private markers or require fingerprints. When explicitly
asked for a fresh same-HEAD review, record the new cycle separately; otherwise
reuse the existing one. Overlapping requests that cannot be distinguished are
ambiguous, not permission to select whichever result is convenient.

After an uncertain request, paginate PR comments and reconcile exact body,
author, target, and attempt time. Recover only a unique matching artifact.
If there is no unique proof, report unconfirmed and stop without reposting.
For old typed receipts or markers, reconcile their referenced GitHub objects;
do not replay their stored operations or require the retired CLI.

## Check, wait, and terminal evidence

`check` reads once; `wait` polls until terminal evidence, caller stop, an access
failure, HEAD drift, or the original deadline. Use the caller's remaining time;
when none is supplied, establish one 30-minute deadline. Poll with bounded
backoff, respecting rate limits and keeping individual waits at most 60 seconds.
Report meaningful changes rather than each unchanged observation. Resume keeps
the same deadline. At timeout return pending and the record, without requesting
again or launching background monitoring.

Verify provider author identity from GitHub's account/app metadata, not display
names or text claiming to be Codex. Correlate formal reviews by `commit_id`,
author, submission time after the selected request, and associated comments.
Read the complete review before classifying its verdict; a `COMMENTED` state
alone does not mean clean. Current-head findings may have no inline comments.

Provider-authored terminal comments must identify the reviewed commit and match
the selected cycle. Reactions require the exact provider actor and timestamp:
👀 is acknowledgment only. A provider 👍 can count as clean only when its target
and timing uniquely associate it with this cycle, the expected HEAD remained
stable, and no conflicting evidence exists. A bare PR reaction with no provable
cycle/commit association is insufficient. Missing comments, zero unresolved
threads, and silence are never clean evidence. Preserve uncertainty when GitHub
does not expose enough information to prove correlation.

For `ready-check` or `ready-wait`, observe an already-established automatic
review trigger and its HEAD/time instead of a posted request. Never change draft
state or post a request on that route. Missing trigger evidence is a correlation
gap. `terminal-evidence` rechecks the selected cycle's result without writing.
`review-pr` requires an explicit cycle; automatic evidence does not replace it.

## Replies, resolution, and other writes

Before writing, verify the exact object belongs to the selected PR, recheck HEAD,
and confirm the action and text are authorized. Put the complete payload in a
JSON file using a serializer, then use `gh api --input`; do not embed free-form
text in arguments. These endpoints are distinct:

| Action | Request |
| --- | --- |
| Reply to an inline review comment | POST `repos/<owner>/<repo>/pulls/<number>/comments/<root-comment-id>/replies` with `body` |
| Post PR discussion | POST `repos/<owner>/<repo>/issues/<number>/comments` with `body` |
| Edit a conversation comment | PATCH `repos/<owner>/<repo>/issues/comments/<comment-id>` with `body` |
| Edit a review comment | PATCH `repos/<owner>/<repo>/pulls/comments/<comment-id>` with `body` |
| Submit a formal review | POST `repos/<owner>/<repo>/pulls/<number>/reviews` with `commit_id`, `event`, and `body` |

For inline replies, find the thread's root comment; GitHub does not support
replying to an existing reply through that endpoint. Never substitute a PR-level
comment. Formal review events are GitHub-owned values `APPROVE`,
`REQUEST_CHANGES`, and `COMMENT`; select only the authorized event and exact HEAD.

Resolve a thread only when the caller authorizes resolution and supplies the
accepted disposition/evidence. For a claimed fix, verify the published commit
and validation evidence and post/read back an authorized evidence reply first.
For an explicitly accepted no-change disposition, state that rationale; do not
invent a fix. Locate the unique thread using returned node IDs and comment
membership, then use GitHub's `resolveReviewThread` GraphQL mutation with the
returned thread ID through a JSON request file. Never guess IDs. Read that same
thread afterward to verify `isResolved`; an already-resolved thread needs no
write. Check all GraphQL errors as well as returned data.

After any write, independently read the exact object, compare body, actor,
target, and review event where relevant, and recheck HEAD. Report successful
remote effects separately from subsequent HEAD drift. Before retrying a failed
reply or review submission, inspect exact-target history for an already-applied
write. Retry only proven missing work; if attribution or nonapplication remains
uncertain, stop with object links and the uncertainty. Do not undo uncertain
writes or create replacement comments.

## Attachments

For authorized standalone discussion attachments, check native `gh pr comment
--help` for `--attach` support. Keep body and alt text file-backed and pass only
caller-selected files. Missing support does not authorize an upgrade or custom
upload implementation. Use GitHub's current attachment documentation for limits
and local-file Markdown syntax. Read back the exact comment and media URLs after
the attempt, including a nonzero exit, and reconcile partial uploads before
retrying. A discussion attachment is not an inline reply or formal review.

## Provider references

Consult these when endpoint fields or provider behavior are uncertain:

- [Review comments and replies](https://docs.github.com/en/rest/pulls/comments)
- [Formal reviews](https://docs.github.com/en/rest/pulls/reviews)
- [GraphQL pull requests and thread resolution](https://docs.github.com/en/graphql/reference/pulls)
- [Codex GitHub review](https://learn.chatgpt.com/docs/third-party/github)
- [Native attachments](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli)
