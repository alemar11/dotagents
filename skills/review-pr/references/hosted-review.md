# Hosted Codex Review

Read for inspection, requests, waits, and resume through authenticated `gh`.
[states.md](states.md) owns result meanings and the caller-retained review
record. This skill ships no custom CLI or persistent ledger.

## Inspect the PR and provider evidence

Read the PR identity and HEAD, then paginate the relevant collections:

```bash
gh pr view <number> --repo <owner/repo> \
  --json number,url,state,isDraft,headRefOid,headRefName,headRepository,headRepositoryOwner
gh api --paginate repos/<owner>/<repo>/pulls/<number>/reviews
gh api --paginate repos/<owner>/<repo>/pulls/<number>/comments
gh api --paginate repos/<owner>/<repo>/issues/<number>/comments
```

When thread context is needed, use `gh api graphql --input <request-json>` for
the exact PR's `reviewThreads` connection. Retain returned thread/comment IDs,
URLs, author, body, commit identity, and resolved/outdated state. Follow
`pageInfo` on both threads and nested comments. Do not derive IDs or treat one
page, GraphQL errors, or partial data as proof that no review exists.

## Select the exact request

Resolve the repository/PR, expected full HEAD (the current HEAD when the caller
has not bound it), current ready state, and available explicit request lineage.

- Reuse a verified terminal explicit review for this target, whether clean or
  findings, and return it without another request or wait.
- Resume a matching pending explicit request with its original record and
  deadline. Do not repost merely because Codex has
  not answered yet.
- When no applicable explicit lineage exists, reconcile prior uncertain effects,
  then request review and wait. Automatic/ready-triggered reviews or results for
  an older HEAD do not satisfy this skill's explicit current-target contract.

Inspect-only scope overrides request-and-wait and reports missing evidence as a
gap. Missing local record output alone never proves no request exists. Recover
an existing request from its exact GitHub object and the caller's record; if its
identity/correlation cannot be established, report blocked rather than
duplicating the request.

Before a new request or wait, verify ready state and unchanged expected full HEAD.
A draft returns deferred to the caller; this skill never marks it ready.
No local candidate review is required by this skill. The caller supplies any
local gate before invoking it.

Use one request identity per intended cycle and preserve the complete review
record.
Reconcile uncertain request effects before any retry. Only an explicitly requested
fresh cycle may replace a verified existing same-target lineage. If the expected
HEAD changes during the run, return the drift to the caller; never silently
follow a moving branch or consume old evidence for the new HEAD. A subsequent
invocation bound to a newly published HEAD may request that new target.

## Post or reconcile the request

For an authorized new cycle, place `@codex review` in a UTF-8 body file and
inspect its final text. Record the expected full HEAD and creation time locally;
the mention requests a PR review, not an API guarantee of execution pinned to
that commit. Recheck HEAD immediately before posting:

```bash
gh pr comment <number> --repo <owner/repo> --body-file <request-body-file>
```

Capture and independently read back the exact returned comment, author, body,
and creation time, then recheck PR HEAD. Preserve those facts and the original
deadline in the review record. Overlapping requests that cannot be distinguished
are ambiguous; do not choose whichever result is convenient.

If a request may have applied, paginate PR comments and reconcile exact body,
author, target, and attempt time. Recover only a unique matching artifact. If
success or nonapplication cannot be established, return blocked without
reposting. Reconcile old receipts against their referenced GitHub objects;
never replay historical operations or depend on a retired helper.

For an authorized correction of the same request, serialize the complete `body`
into a JSON file and use `gh api --method PATCH
repos/<owner>/<repo>/issues/comments/<comment-id> --input <request-json>`.
Never interpolate provider text into shell commands. Verify object membership
and HEAD before writing; read back that same object's body, author, and target
and recheck HEAD afterward. Report an applied write separately from subsequent
HEAD drift. Reconcile uncertain effects instead of making a replacement comment.

## Bounded observation and return

Poll through `gh` until terminal review evidence, caller stop,
a blocking failure, or the original deadline. Keep the existing total 30-minute
limit per explicit lineage. Resume preserves that deadline; never segment or
extend it. If the deadline is exhausted, read-only reconciliation may recover a
result that has since arrived, but it cannot start a fresh wait window or
replacement request. Return pending when the review remains unanswered at timeout
or caller stop. Do not schedule an automation or spawn a monitoring task/subagent.
Use bounded backoff, respect rate limits, keep each wait at most 60 seconds, and
report meaningful changes rather than unchanged polls.

Return completed only when verified evidence establishes a terminal
provider verdict for the exact selected request and expected HEAD. Clean and
findings both end monitoring. Return the findings and links without proposing or
performing repair batches, rebuttals, replies, or resolutions. Zero unresolved
threads, absence of comments, generic not-requested, automatic review, stale
results, and ambiguous correlation cannot stand in for terminal evidence.

Verify provider author identity from GitHub account/app metadata rather than
display names or text claiming to be Codex. Correlate formal reviews by
`commit_id`, provider author, submission after the selected request, and
associated comments. Read the complete review before classifying its verdict;
`COMMENTED` alone does not mean clean, and findings may have no inline comments.

Provider-authored terminal comments must identify the reviewed commit and match
the selected cycle. Reactions require the exact provider actor and timestamp:
eyes are acknowledgment only. A provider thumbs-up may establish clean only
when its target and timing uniquely identify this cycle, the expected HEAD
remained stable, and no conflicting evidence exists. A bare PR reaction with
no provable cycle/commit association is insufficient. Silence is never clean
evidence; preserve uncertainty when GitHub cannot prove correlation.

Infrastructure failures or unreconciled effects return blocked with the exact
available record and evidence. Preserve provider verdict separately from the
monitoring result. No CI check, local code review, or delivery acceptance gate
is part of this monitor, and no workflow position is stored in a new ledger.
