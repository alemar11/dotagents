# Recovery Validation

Load this reference only when resuming from a Recovery Packet.

## Mandatory App Runtime Surface Revalidation

Re-run the App runtime surface gate before reading the Recovery Packet, its
ledger projection, or its recorded visible task. Require both visible Codex App
task creation and App-managed worktree binding capabilities; task readability,
generic subagents, filesystem access, and prior App evidence are insufficient.
If either required surface is absent or unverifiable, abort recovery as
unsupported in the current runtime without asking permission or touching
runtime artifacts. Only after this gate passes may recovery continue below.

## Freshness Validation

1. Recompute the current canonical option fingerprint and reject retired or
   unknown fields.
2. Verify every repository realpath, HEAD, branch, and tracked-status
   fingerprint named by the packet.
3. Verify source refs and acceptance/closeout fingerprints against their
   authoritative artifacts.
4. Verify the active-root claim still covers the same repositories and sources
   and no overlapping live claim appeared.
5. Verify every nonterminal Feature Spec task row has exactly one task ref and
   the total does not exceed three.
6. Read each current visible task and validate its Goal, managed checkout, and
   lifecycle evidence.
7. Re-evaluate dependencies, gates, review/CI waits, and next action. A stale
   dependency or due check invalidates dispatch eligibility.

Any mismatch invalidates the compact packet. Run full ledger and source
reconciliation before mutation or dispatch; do not repair the packet in place.

## Task Validation

- require the mandatory App runtime surface revalidation above to have passed;
- read the current visible task using the recorded id;
- require exact Feature Spec title and one active task per Spec;
- verify App-managed repository checkout paths and branches;
- verify task Goal objective hash, status, and tool/unavailable evidence;
- compare task-reported lifecycle, changes, PRs, review, CI, and blockers with
  the ledger;
- require the fixed App target and reject recovery into any non-PR or
  draft-only terminal state;
- reject root/background implementation or review evidence;
- resume or replace only after recording stale/failure evidence.

If a required managed checkout or visible task cannot be recovered, abort the
App run as blocked. Never create raw worktrees or rotate the caller branch
during recovery.

## Hard Cut

Ledgers containing removed worker-surface fields, checkout strategies,
unmanaged worktree permissions, raw-worktree guards, numeric worker options, or
task rows without current App evidence are incompatible. Do not migrate them
automatically. Release the old claim and create a fresh ledger.
