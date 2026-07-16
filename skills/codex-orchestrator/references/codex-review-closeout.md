# Codex Review And Parent Closeout

## Execution Owner

For App execution, the visible Feature Spec task owns review request, polling,
feedback fixes, CI, and ready transition. The root only monitors and reconciles.
For CLI execution, the root CLI session owns those steps after accepting the
terminal worker result. Ownership never changes mid-loop as a convenience
fallback.

## Current-Revision Review

For merge-ready delivery, request one Codex review for the current revision
tuple: PR, head SHA, base ref, and merge-base SHA. Record that tuple with
request evidence, state, findings, disposition, and completion time. Reuse an
existing review only when the entire tuple matches and its findings are fully
dispositioned. A base update or retarget invalidates review freshness even when
the head SHA is unchanged.

Poll within the documented total wait budget. Poll cadence does not extend that
budget. A pending pollable review is ongoing work, not a blocker. An
unavailable/unpollable review after the budget is a real gate blocker.

Actionable findings return to fix, focused validation, `$autoreview`, push, and
a new current-head review. Material diff changes invalidate earlier review and
CI evidence. Resolve review threads only after the corresponding fix and proof
exist.

An exact authorized-user selection of
`codex_review_requirement=explicitly-skipped-by-authorized-user` skips only this
Codex review loop. Record its scope and evidence.

## Request Registry And Idempotency

The ledger's Codex Review Wait Registry is the sole request and timing
authority. Keep exactly one row keyed by
`<owner>/<repo>#<number>@<head-sha>@<base-ref>@<merge-base-sha>`. The row stores
request object/evidence, provider state, observation fingerprint, result and
disposition, wait profile, `wait_started_at`, `wait_deadline`, `due_at`, and
poll owner. Every workstream mapped to the same PR revision reuses that row.

Before requesting, resuming a wait, or promoting a PR, recompute the full live
revision and run the canonical GitStack Codex review check. Reuse a current
clean/findings result; preserve and wait on a current acknowledged/pending
request; create a request only for a proven not-requested or stale revision.
API/auth/configuration uncertainty never authorizes a request.

The request operation is idempotent per full revision tuple. A terminal result
or active request forbids another request for that tuple. A head, base-ref, or
merge-base change creates a new tuple and permits exactly one request after
preflight. Persist the request row before polling so recovery cannot duplicate
the mutation.

## Wait Budget

Use a 15-minute standard or 30-minute extended total active-wait budget per PR
revision. These are fixed deadlines, not selectable options or polling
intervals. The first waiter atomically creates the registry row with
`wait_started_at` and a 15-minute `wait_deadline`; concurrent/resumed consumers
reuse the earliest row and wait only for the remaining time. Run one bounded
GitStack waiter with 10-second initial polling and a 30-second maximum interval;
never wrap repeated checks in a second caller loop.

At the standard deadline, recompute the full revision and check again. Promote
to the extended profile only when the same request and revision remain pending,
then move the deadline to 30 minutes after the original start and wait only the
remaining time. Once a PR needs the extended profile, later revisions of that
same PR start with 30 minutes; a different PR starts standard. No third tier or
deadline extension exists.

On resume, derive remaining seconds from the persisted deadline. When no time
remains, check once and either promote standard, record a terminal transition,
or set `monitoring-required` with one future `due_at`. Unchanged polls do not
rewrite timestamps or count as progress. A pending pollable review remains
ready-next work; only an unpollable provider/access failure is blocked.

## Parent Closeout

After all other whole-Spec gates pass, add the parent closing keyword only to
the default-branch whole-Spec PR selected as the closeout vehicle. Record
`armed` before merge. Non-default-base PRs link to a later closeout vehicle and
must not close the parent prematurely.

The root owns any separately authorized merge watch and post-merge verification.
The parent completes only after merge, actual issue closure, every child
outcome, and cross-repo integration proof. `armed`, merge-ready, or a merged
child PR is not final parent closure.
