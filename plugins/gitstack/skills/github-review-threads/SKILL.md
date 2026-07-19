---
name: github-review-threads
description: Check or wait for automated PR reviews, inspect feedback, implement selected fixes, validate them, and manage replies or resolution.
---

# GitHub Review Threads

## Role

Own the feedback-to-code workflow for pull-request reviews: preserve thread
context, identify actionable feedback, implement only selected fixes, validate
them, and draft or publish dispositions with explicit authority.

## Transport and CLI

Prefer the GitHub connector for thread-aware listing and resolution state. For
provider text, use only a structured connector mutation whose exact target can
be read back, or the typed file-backed GitStack commands below. Never place a
title, body, description, reply, or review text in argv or a shell string.

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md`:

```bash
<plugin-root>/scripts/gitstack --help
<plugin-root>/scripts/gitstack --version
<plugin-root>/scripts/gitstack --json doctor
<plugin-root>/scripts/gitstack --json repo snapshot
<plugin-root>/scripts/gitstack --json reviews address --repo <owner/repo> --pr <number>
<plugin-root>/scripts/gitstack --json reviews request --provider codex --repo <owner/repo> --pr <number> --head <full-40-sha> --request-key <request-key>
<plugin-root>/scripts/gitstack --json reviews check --provider codex --repo <owner/repo> --pr <number> --head <sha>
<plugin-root>/scripts/gitstack --json reviews wait --provider codex --repo <owner/repo> --pr <number> --head <full-40-sha> --request-receipt-file <absolute-receipt-file> --timeout <caller-owned-duration>
<plugin-root>/scripts/gitstack reviews comment --repo <owner/repo> --pr <number> --body-file <absolute-message-file> --expected-worktree-fingerprint <sha256> --dry-run
```

The CLI validates absolute regular non-symlink UTF-8 files, sends JSON to `gh
api --input -`, emits byte counts and SHA-256 fingerprints instead of text, and
verifies provider identity, target, response text, and an optional Git
worktree fingerprint. It writes no implicit config.
It cannot invoke connector tools. Its Codex adapter normalizes formal reviews,
inline findings, authenticated top-level terminal result comments, and clean
reactions into one current-head state and one stable observation fingerprint.

## Workflow

1. Resolve the base repository and PR, then list review threads with resolution
   state and enough surrounding diff context to understand each comment.
   For an automated-review request, capture the intended full head SHA and a
   caller-owned request key, invoke `reviews request`, and persist its complete
   request receipt. Pass that receipt unchanged to `reviews wait`; the waiter
   fetches the exact provider comment id and never substitutes a newer comment.
   Never accept review evidence from an older head. Reuse the returned
   `observation_fingerprint`; unchanged observations are not state transitions
   and must not cause caller-side ledger writes or progress messages.
2. Group duplicates and classify feedback as actionable, already addressed,
   informational, obsolete, or requiring a user decision.
3. Present or honor the selected actionable set. Do not silently implement
   every comment when the request selects only some.
4. Inspect adjacent code and tests, implement the selected changes locally, and
   validate the affected behavior.
5. Draft a disposition per selected thread that names the change and proof.
   Keep provider text in UTF-8 regular files outside the repository. Capture a
   `repo snapshot` immediately before each mutation and pass its fingerprint
   when the caller requires worktree protection.
6. Post replies, edit comments, submit reviews, or resolve threads only when the
   user explicitly authorizes publication or a calling workflow supplies exact
   PR/action authority. Never infer it from an inspect or review request.
   A failed or unreadable mutation gets one exact-target read-back and no blind
   retry. Preserve returned partial-success evidence if the provider write is
   confirmed but the worktree guard fails.
7. Resolve a thread only after its requested change is implemented and
   validated, or when an authorized disposition clearly explains why no change
   is appropriate. Never substitute a top-level PR comment for a thread reply
   silently.
8. After pushing a review fix, request a fresh automated review with a new
   request key when required and check or wait against the new full head SHA.
   If a bounded wait times out and
   continued monitoring is authorized, return the pending state to the caller;
   scheduling or heartbeat ownership remains with that caller. Callers must use
   the bounded waiter instead of wrapping one-shot checks in manual sleep loops.
   A composing caller owns and passes its duration; GitStack never selects,
   extends, or segments that caller's deadline.

For a composed workflow, require the exact PR target and one canonical
`review_operation`. Mutating operations additionally require
`mutation_mode=apply`. Caller-specific authorization and phase policy must be
normalized before invocation; reject those caller-owned fields instead of
interpreting them here.

## References

- `references/workflows.md`: feedback, reply, resolution, and fallback flows.
- `references/script-summary.md`: shared `gitstack reviews` contract.
- `../../references/options.md`: shared canonical GitStack options and caller handoffs.
