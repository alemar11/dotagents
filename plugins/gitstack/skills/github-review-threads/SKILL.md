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

Prefer the GitHub connector for thread-aware listing, replies, comment edits,
reviews, and resolution state. Use `gh` for gaps. An authorized write may fall
back automatically only for the same operation, repository, PR, and comment or
thread after `gh` authentication and access verification; report the fallback.

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md`:

```bash
<plugin-root>/scripts/gitstack --help
<plugin-root>/scripts/gitstack --version
<plugin-root>/scripts/gitstack --json doctor
<plugin-root>/scripts/gitstack --json reviews address --repo <owner/repo> --pr <number>
<plugin-root>/scripts/gitstack --json reviews check --provider codex --repo <owner/repo> --pr <number> --head <sha>
<plugin-root>/scripts/gitstack --json reviews wait --provider codex --repo <owner/repo> --pr <number> --head <sha> --timeout 15m
<plugin-root>/scripts/gitstack reviews comment --repo <owner/repo> --pr <number> --body-file <message-file> --dry-run
```

The CLI uses `gh`, emits stable JSON envelopes, and writes no implicit config.
It cannot invoke connector tools. Its Codex adapter normalizes formal reviews,
inline findings, authenticated top-level terminal result comments, and clean
reactions into one current-head state and one stable observation fingerprint.

## Workflow

1. Resolve the base repository and PR, then list review threads with resolution
   state and enough surrounding diff context to understand each comment.
   For an automated-review request, capture the intended head SHA and use
   `reviews check --provider <provider>` for a one-shot read or bounded
   `reviews wait --provider <provider>` when the caller should remain active.
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
   Keep replies in UTF-8 files outside the repository.
6. Post replies, edit comments, submit reviews, or resolve threads only when the
   user explicitly authorizes publication or a calling workflow supplies exact
   PR/action authority. Never infer it from an inspect or review request.
7. Resolve a thread only after its requested change is implemented and
   validated, or when an authorized disposition clearly explains why no change
   is appropriate. Never substitute a top-level PR comment for a thread reply
   silently.
8. After pushing a review fix, request a fresh automated review when required
   and check or wait against the new head SHA. If a bounded wait times out and
   continued monitoring is authorized, return the pending state to the caller;
   scheduling or heartbeat ownership remains with that caller. Callers must use
   the bounded waiter instead of wrapping one-shot checks in manual sleep loops.

For `$codex-orchestrator`, require
`change_delivery_permission=granted-for-selected-target`, the exact PR target,
and the requested review action in `delivery_allowed_actions` or
`worker_allowed_actions`.

## References

- `references/workflows.md`: feedback, reply, resolution, and fallback flows.
- `references/script-summary.md`: shared `gitstack reviews` contract.
- `../../references/options.md`: shared canonical GitStack options and caller handoffs.
