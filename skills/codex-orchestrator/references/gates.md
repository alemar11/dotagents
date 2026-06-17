# Gates Reference

Use gates before declaring work owner-ready, issue-closed, merge-ready,
release-ready, or complete. Portfolio ledgers may add stricter gates, but they
should not weaken these defaults without explicit owner approval.

## Universal Gates

### Authorization Gate

Confirm the worker's requested action is covered by the current authorization
mode. Stop for owner approval before push, PR, merge, close, release, external
service mutation, destructive local changes, or broad scope changes.

### Live Proof Gate

For user-facing behavior, require proof from the real app, CLI, API, service,
or rendered artifact before declaring the source item complete. Synthetic proof
is acceptable only when live proof is impossible, unsafe, or blocked by missing
credentials, setup, hardware, paid access, external service state, or explicit
owner deferral.

When live proof is blocked, record the exact blocker, the synthetic proof that
was collected, and the owner decision or follow-up needed. Do not land,
release, close, or mark complete on synthetic proof alone unless the owner
explicitly accepts that gap or the source item is moved to `Deferred` with an
owner-visible follow-up.

### Closure Gate

Before closing a GitHub issue, marking a PR thread resolved, or moving work to
`Completed`, verify that the source acceptance criteria are satisfied by
recorded proof. If live proof is feasible but blocked by credentials, setup,
service access, or missing hardware, do not treat the source item as fully
complete unless the owner explicitly accepts that gap.

If the implementation intentionally satisfies only part of the source item,
keep the source item open or move it to `Needs Owner` until the deferred scope
has an owner-visible follow-up and the closeout links it.

### Follow-Up Issue Gate

Before closing a partially satisfied GitHub issue or PR thread, create or link
a follow-up issue for deferred work when GitHub mutation is authorized. The
follow-up must include the missing setup or behavior, the blocker or decision
needed, the proof already collected, and the acceptance criteria that remain.

If GitHub mutation is not authorized, do not close the source item. Record the
proposed follow-up title/body in the ledger under `Needs Owner` or `Deferred`.

### Autoreview Gate

After non-trivial code edits, run focused tests and `$autoreview`. Treat
findings as advisory, verify each accepted finding in real code, fix actionable
issues, then rerun focused tests and `$autoreview`.

### CI Gate

Before merge-ready or release-ready status, require current CI state or a clear
reason CI is unavailable. Failing checks need a short failure summary, link, and
owner-ready next action.

### Owner Decision Gate

When progress depends on product direction, risk acceptance, credentials,
budget, merge timing, release timing, or external coordination, produce a
decision brief with options and recommended next action.

### Risk Follow-Up Gate

When a worker reports a residual risk, dependency audit warning, security
finding, untested adapter, schema/data-loss concern, credential gap, or
production-readiness caveat, resolve it before closure by doing one of:

- fix it and rerun the relevant validation;
- prove it is not applicable;
- create or link a follow-up issue when mutation is authorized;
- record a `Needs Owner`, `Blocked`, or `Deferred` ledger item with the proposed
  follow-up when mutation is not authorized.

Do not leave unresolved worker-reported risks only in chronological notes when
declaring a workstream complete.

### Release Gate

Before release-ready status, verify version, changelog or release notes, tags,
package artifacts, migration notes, rollback path, and CI. Use the standalone
GitHub Releases skill for GitHub-backed releases.

### Public Model Identifier Gate

When work exposes model identifiers, tool names, public API fields, or user-
visible integration names, verify the exact spelling against source docs or
runtime metadata before shipping.

### Cross-Repo Integration Gate

For portfolios involving multiple repositories, require compatibility evidence
across repo boundaries before owner-ready status: shared API shape, version
pinning, migration order, deploy order, fixtures, or an explicit integration
test.

### Credential And Access Gate

If work requires credentials, paid service access, private repo permission, or
local secrets, stop and report the minimum missing access. Do not ask workers to
work around protected systems with unsafe local substitutes.
