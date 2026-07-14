# Runtime Efficiency

Load this reference before entering a second controller wave or recording exact
phase-token counters. On resume, load `recovery-validation.md` first and load
this file afterward only if those multi-wave or metrics conditions apply. It
refines evidence transport only; the ledger, source items, authority model, and
gates remain authoritative.

## Recovery Routing

Recovery validation is not part of ordinary second-wave evidence transport.
On resume, load `recovery-validation.md` and run its complete freshness check
before mutation or dispatch. Load this file afterward only when the resumed
run enters another wave or records exact phase counters.

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
