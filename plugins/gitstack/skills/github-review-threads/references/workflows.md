# GitHub Review Workflows

## Check Or Wait For Automated Review

Use the same provider-neutral state contract for a one-shot read or a bounded
wait. Always pass the intended PR head SHA when freshness matters:

```bash
<plugin-root>/scripts/gitstack --json reviews check --provider codex --repo <owner/repo> --pr <number> --head <sha>
<plugin-root>/scripts/gitstack --json reviews wait --provider codex --repo <owner/repo> --pr <number> --head <sha> --timeout <caller-owned-duration>
```

For composition, `<caller-owned-duration>` is the remaining time derived from
the caller's deadline. GitStack does not select, extend, or segment that bound.

`check` reads once. `wait` polls with bounded backoff until it sees `clean` or
`findings`, detects `not-requested` or `stale`, or reaches its timeout. The
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

After fixing and pushing findings, post a fresh review request and run the
check or wait against the new SHA. Include at least the first seven characters
of that SHA in the review-request comment so the CLI can bind acknowledgement
or clean-reaction evidence to the intended head; a plain request without a SHA
is reported as stale until a submitted review supplies commit evidence. A
timed-out wait returns exit code `124`, the last observed state, attempt count,
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

## Reply To Selected Comments

First list comments, then reply by displayed selection or comment id:

```bash
<plugin-root>/scripts/gitstack reviews address --repo <owner/repo> --pr <number> --selection "1 3" --reply-body-file <message-file> --dry-run
<plugin-root>/scripts/gitstack reviews address --repo <owner/repo> --pr <number> --comment-ids "123456" --reply-body-file <message-file>
```

Write reply text to a UTF-8 file outside the repository. Do not interpolate
arbitrary comment text into `--reply-body` in a shell command. Remove temporary
message files after the action is verified.

Use `--dry-run` for batch replies unless the user already approved posting or a
calling workflow supplies `mutation_mode=apply`, the exact PR, selected
comments, reply body, and `review_operation=reply`.

## Post Top-Level PR Discussion Comments

Use the helper for normal PR discussion comments, including simple review
requests:

```bash
<plugin-root>/scripts/gitstack reviews comment --repo <owner/repo> --pr <number> --body-file <message-file> --dry-run
<plugin-root>/scripts/gitstack reviews comment --repo <owner/repo> --pr <number> --body-file <message-file>
```

Use `--dry-run` unless the user explicitly asked to post the discussion comment
or a calling workflow supplies `mutation_mode=apply`, the exact PR, the comment
body, and `review_operation=request` for an automated-review request or
`review_operation=comment` for another discussion comment. Caller-specific
authorization and phase fields must be normalized before this boundary.

## Fallback Direct Commands

Use direct `gh` only when `<plugin-root>/scripts/gitstack reviews` is unavailable, broken, or lacks the
needed operation. State the fallback reason in the response.

```bash
gh pr comment <number> --repo <owner/repo> --body-file <message-file>
gh pr view <number> --repo <owner/repo> --comments
```
