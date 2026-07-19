# GitHub Review Workflows

## Check Or Wait For Automated Review

Create the typed request first. GitStack owns the only accepted request grammar
and returns the complete provider identity receipt:

```bash
<plugin-root>/scripts/gitstack --json reviews request --provider codex --repo <owner/repo> --pr <number> --head <full-40-sha> --request-key <request-key>
```

The generated body is exactly `@codex review <full-40-sha>` followed by the
versioned GitStack marker and request fingerprint. Callers cannot provide or
assemble request text. The operation reuses only one exact matching comment;
plain, markerless, malformed, conflicting, or duplicate requests fail closed.

Use the returned receipt for the one-shot read or bounded wait:

```bash
<plugin-root>/scripts/gitstack --json reviews check --provider codex --repo <owner/repo> --pr <number> --head <full-40-sha> --request-receipt-file <absolute-receipt-file>
<plugin-root>/scripts/gitstack --json reviews wait --provider codex --repo <owner/repo> --pr <number> --head <full-40-sha> --request-receipt-file <absolute-receipt-file> --timeout <caller-owned-duration>
```

For composition, `<caller-owned-duration>` is the remaining time derived from
the caller's deadline. GitStack does not select, extend, or segment that bound.

`check` reads once. `wait` requires the complete persisted receipt and polls
with bounded backoff until it sees `clean` or `findings`, detects a typed
terminal state or binding failure, or reaches its timeout. The
current provider adapter is `codex`; provider-specific bot identities,
acknowledgements, formal reviews, inline findings, authenticated top-level
terminal comments, clean reactions, and current-head matching belong to the
CLI rather than this workflow. A terminal comment counts only when it follows
the matching request, names the expected reviewed commit, and comes from the
authenticated provider identity. Conflicting terminal outcomes or overlapping
requests for the same head that prevent safe result correlation return an API
error rather than an arbitrary result.

The returned `observation_fingerprint` covers normalized review and request
evidence but excludes attempts and elapsed time. A caller may persist the
first observation and later transitions, but must not rewrite control state or
emit progress for an unchanged fingerprint. Use one bounded `wait`; do not
build a manual `check` plus shell-sleep loop around it.

After fixing and pushing findings, post a fresh typed review request with a new
request key and run the check or wait against the new full SHA. A timed-out
wait returns exit code `124`, the last observed state, attempt count,
transition count, and unchanged-attempt count; a calling orchestrator decides
whether to schedule a later heartbeat.

## List Review Context

Resolve `<plugin-root>` as two directories above the directory containing the owning
`SKILL.md` before using these commands.

```bash
<plugin-root>/scripts/gitstack reviews address --repo <owner/repo> --pr <number>
<plugin-root>/scripts/gitstack --json reviews address --repo <owner/repo> --pr <number>
```

By default, resolved or outdated review threads are omitted. Add
`--include-resolved` only when the user asks for full history.

## Reply To One Review Comment

First list comments, then reply to exactly one provider review-comment id:

```bash
<plugin-root>/scripts/gitstack --json repo snapshot
<plugin-root>/scripts/gitstack reviews reply --repo <owner/repo> --pr <number> --comment-id <id> --body-file <absolute-message-file> --expected-worktree-fingerprint <sha256> --dry-run
<plugin-root>/scripts/gitstack reviews reply --repo <owner/repo> --pr <number> --comment-id <id> --body-file <absolute-message-file> --expected-worktree-fingerprint <sha256>
```

Write reply text to an absolute UTF-8 regular non-symlink file outside the
repository. The command rejects inline text. Remove temporary message files
after provider identity, target, body fingerprint, and worktree proof are
verified.

Use `--dry-run` unless the user already approved posting or a calling workflow
supplies `mutation_mode=apply`, the exact PR and comment id, reply body, and
`review_operation=reply`.

## Edit Comments Or Submit Reviews

```bash
<plugin-root>/scripts/gitstack reviews edit-comment --repo <owner/repo> --pr <number> --kind <conversation-or-review> --comment-id <id> --body-file <absolute-message-file> --expected-worktree-fingerprint <sha256>
<plugin-root>/scripts/gitstack reviews submit-review --repo <owner/repo> --pr <number> --event <approve-or-request-changes-or-comment> --body-file <absolute-message-file> --expected-worktree-fingerprint <sha256>
```

Each command verifies the existing target before writing and the returned
provider object afterward. On an ambiguous write it performs one exact-target
read-back and fails closed; do not retry it blindly.

## Post Top-Level PR Discussion Comments

Use the helper for normal PR discussion comments. The separate typed
review-request operation owns request composition, head binding, identity,
acknowledgment, and waiting.

```bash
<plugin-root>/scripts/gitstack reviews comment --repo <owner/repo> --pr <number> --body-file <absolute-message-file> --expected-worktree-fingerprint <sha256> --dry-run
<plugin-root>/scripts/gitstack reviews comment --repo <owner/repo> --pr <number> --body-file <absolute-message-file> --expected-worktree-fingerprint <sha256>
```

Use `--dry-run` unless the user explicitly asked to post the discussion comment
or a calling workflow supplies `mutation_mode=apply`, the exact PR, the comment
body, and `review_operation=comment` for another discussion comment. Use the
typed `reviews request` operation for automated-review requests. Caller-specific
authorization and phase fields must be normalized before this boundary.

## Fallback Direct Commands

Use direct `gh` only for a genuinely file-backed operation. If no file-backed
fallback exists, require the structured GitHub connector and fail closed.
State the fallback reason in the response.

```bash
gh pr comment <number> --repo <owner/repo> --body-file <message-file>
gh pr view <number> --repo <owner/repo> --comments
```

There is no direct legacy fallback for typed review requests; use GitStack's
typed operation so the request receipt and exact-head binding are preserved.
