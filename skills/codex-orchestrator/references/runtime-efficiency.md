# Runtime Efficiency

Load this reference when resuming from a recovery packet, entering a second
controller wave, or recording exact phase-token counters. It refines evidence
transport only; the ledger, source items, authority model, and gates remain
authoritative.

## Recovery Validation

On resume:

1. Read only the ledger `## Recovery Packet`.
2. Recompute the packet Content fingerprint from every derived packet field,
   excluding `Status`, `Updated`, `Projection fingerprint`, and `Content
   fingerprint`. Require it to match both the packet value and the
   `Recovery packet content fingerprint` stored under authoritative
   `## Active Root`. Use this canonical extraction:

   ```bash
   awk '
     /^## Recovery Packet$/ { inside=1; next }
     /^## Worker And Delivery References$/ { exit }
     inside && $0 !~ /^(Status|Updated|Projection fingerprint|Content fingerprint):/ { print }
   ' "$ledger" | shasum -a 256
   ```

3. Recompute the packet's Projection fingerprint from the authoritative ledger
   and require an exact match. Hash all ledger content before `## Notes`,
   excluding the complete `## Recovery Packet` section, with this canonical
   extraction:

   ```bash
   awk '
     /^## Recovery Packet$/ { skip=1; next }
     /^## Worker And Delivery References$/ { skip=0 }
     /^## Notes$/ { exit }
     !skip { print }
   ' "$ledger" | shasum -a 256
   ```

4. Require the packet Source checkpoint IDs to equal the complete current set
   of in-scope registered source item IDs represented across every current
   `## Workstreams` status bucket, not the discovery feed IDs. Recompute each
   underlying issue, PR, checklist, file, commit, CI, or other source-item
   fingerprint; reject missing or extra checkpoints.
5. Require packet repo checkpoint realpaths to equal the complete canonical
   in-scope/claimed repo set from `## Scope` and `## Active Root`; reject
   missing or extra repos. Then recompute every HEAD, branch, and
   `git status --short` fingerprint and verify the root claim plus active-worker
   state still match.
6. If every check matches, mark the packet `fresh` and load only its named
   workstream rows, gate rows, sources, proofs, and references.
7. If any check differs, mark it `stale` or `invalid`; do not mutate or dispatch
   from it. Read the authoritative ledger sections, reconcile all in-scope
   sources, and replace the packet.

Refresh the packet after each wave, source mutation, and planned pause using
this order: derive every packet field from authoritative state; compute and
write the packet Content fingerprint to both the packet and Active Root;
compute the Projection fingerprint, which now binds that content fingerprint;
then write it to the packet. Packet freshness never bypasses claims,
capabilities, authority, dependencies, gates, or final reconciliation.

## Delta Evidence

Take one full snapshot per stable fingerprint. Later passes should carry:

- artifact path/ref and fingerprint;
- changed files and ledger sections/rows;
- focused hunks needed for the current decision;
- validation command and compact result;
- failed-gate excerpt and next action.

Prefer `git status --short`, `git diff --stat`, `git diff --name-only`,
`git diff --check`, and path-scoped hunks. Read the complete relevant diff
before `$autoreview`, commit/publication, or when focused evidence cannot
explain a gate failure. Report ledger section changes plus the new projection
fingerprint instead of printing the complete ledger after every patch.

Require a full-ledger read for initial claim, stale/invalid recovery, ownership
ambiguity, or final reconciliation when compact freshness proof is insufficient.

## Phase Metrics

Use exact phase attribution only when counters are scoped to this root and the
checkpoint interval contains no concurrent worker, tool, or other-phase
activity. Then checkpoint and subtract adjacent values for:

- `claim-register-route`;
- `dispatch-integrate:<wave>`;
- `gate-reconcile:<wave>`;
- `recovery:<packet-version>`.

Record exact input, cached-input, output, and total deltas in the ledger. If a
cumulative-counter interval is interleaved, label it `exact-interval` and do
not attribute it to a phase; use `unavailable` for that phase. Never infer usage
from file size, text length, rate-limit percentages, or a whole-run total. If
counters are absent, write one `unavailable` row with `n/a` numeric fields and
continue; metrics are diagnostic, not gate or closeout proof.
