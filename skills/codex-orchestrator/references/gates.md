# Gates Reference

Use gates before declaring work owner-ready, issue-closed, merge-ready,
release-ready, or complete. Portfolio ledgers may add stricter gates, but they
should not weaken these defaults without explicit owner approval.

## Universal Gates

Gate selection is per workstream. Always evaluate `authorization` and
`closure`. Add `live-proof` for user-facing behavior, `autoreview` for
non-trivial code edits, `ci` for merge or release readiness,
`codex-pr-review` before declaring pull-request delivery merge-ready,
`owner-decision` when progress depends on approval or risk acceptance,
`release` only for tag, package, deploy, or promotion work,
`public-model-identifier` only when public names or API fields are changed or
exposed, `cross-repo-integration` only when multiple repositories or packages
must remain compatible, and `publication-safety` before push, draft PR
publication, or a ready-for-review transition. Record
`not-applicable` only with a short reason in the ledger gate matrix.

Proof means root-verifiable evidence, not only a worker assertion. Acceptable
proof includes command output, test names and outcomes, CI URLs, commit SHAs,
PR or issue links, resolved review-thread links, Markdown checkbox diffs,
TODO-removal diffs, screenshots, rendered artifacts, API responses, release
URLs, timestamps, and owner decisions.

## Gate Lenses And Stable Review Items

Use the narrowest review lens that matches the current phase:

- `source-readiness`: source scope, PRD or issue readiness, dependencies, and
  blockers.
- `implementation`: code behavior, regressions, tests, and live proof.
- `documentation`: durable wording, portable evidence, rationale, and handoff
  clarity.
- `publication`: branch, checkout, PR, source mutation, and closeout safety.
- `integration`: cross-repo or cross-package compatibility and proof.

When a gate or review pass finds actionable items, keep those items stable until
they are resolved or consciously rejected. A stable item needs an id, lens,
scope, check or finding, evidence, status, and disposition. On reruns, verify
the existing accepted items first; add new items only when new evidence or a
changed scope exposes a distinct issue. Do not create a separate review
artifact only to hold these items when the ledger, issue comment, or final
report already records them clearly.

## Structured Gate Values

Use the gate names listed in `## Universal Gates` and the sections below. Use
these `gate_status` values in the ledger gate matrix:

- `pass`: gate is satisfied with root-verifiable evidence.
- `fail`: gate was evaluated and failed.
- `blocked`: gate cannot be evaluated or satisfied without external action.
- `not-applicable`: gate does not apply, with a short recorded reason.

`publication-safety` owns `push_policy`, `branch_target_guard`,
`publication_checkout_guard`, `caller_checkout_guard`, `pr_diff_status`,
`ready_for_review_state`, and `post_push_verification` values.
Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases when reading existing artifacts. When updating an artifact
that contains legacy aliases, rewrite touched structured values to
lower-kebab-case.

### Authorization Gate

Confirm the worker's requested action is covered by the current authorization
modes. Stop for owner approval before push, PR, merge, close, release, external
service mutation, destructive local changes, or broad scope changes.
For worker assignments, `commit`, `push`, and `pr` are separate capability
flags. Do not allow PR creation to imply commit or push, and do not allow push
to imply local commit creation.

For PRD-backed workflows, branch plus draft PR delivery in the PRD or generated
issue can satisfy authorization for commit, push, and draft PR creation after
tests, integration checks, and `$autoreview` pass, unless the owner restricted
the request to local-only, inspect-only, no-push, no-PR, or equivalent work.
Ready-for-review transition and a Codex PR review request require separate
merge-ready closeout authority from the source or current owner request, such
as `publication_authority=prd-backed-merge-ready-pr` or
`publication_authority=explicit-owner-authorization` with those actions named.
`stay-draft` or equivalent wording blocks the transition until the owner
changes that decision. Record the resolved publication authority in the ledger.
This does not authorize merge, release, direct issue mutation, production
deploy, or unrelated GitHub cleanup.

### Publication Safety Gate

Before push, draft PR publication, or ready-for-review transition, evaluate
`publication-safety`. Record:

- `push_policy`: `no-push`, `explicit-refspec-only`, or `block-plain-push`.
- `branch_target_guard`: `default-branch-blocked`,
  `protected-branch-blocked`, or `verified-feature-branch`.
- `publication_checkout_guard`: `worker-worktree`, `integration-worktree`,
  `caller-checkout-approved`, or `blocked`.
- `caller_checkout_guard`: `preserved`, `explicitly-approved-switch`, or
  `not-applicable`.
- `pr_diff_status`: `non-empty`, `empty`, or `not-checked`.
- `ready_for_review_state`: `draft`, `ready`, `not-checked`, or `not-applicable`.
- `post_push_verification`: `verified`, `failed`, or `not-applicable`.

Publication should use an explicit refspec, target the expected feature branch,
run from the recorded publication checkout, and verify the pushed branch or
draft PR state after push. When worker or integration worktrees are available,
the caller checkout should remain on its original branch; if the caller checkout
was switched, the gate must record the explicit approval that allowed it. If the
PR diff is empty, the publication checkout is not on the expected branch, or
the target is the default/protected branch without explicit authorization, stop
and record `blocked`.

### Live Proof Gate

For user-facing behavior, require proof from the real app, CLI, API, service,
or rendered artifact before declaring the source item complete. Synthetic proof
is acceptable only when live proof is impossible, unsafe, or blocked by missing
credentials, setup, hardware, paid access, external service state, or explicit
owner deferral.

When live proof is blocked, record the exact blocker, the synthetic proof that
was collected, and the owner decision or follow-up needed. Do not land,
release, close, or mark complete on synthetic proof alone unless the owner
explicitly accepts that gap or the source item is moved to `deferred` with an
owner-visible follow-up.

### Closure Gate

Before closing any source item or moving work to `completed`, verify that the
source acceptance criteria are satisfied by root-verifiable proof. If live proof
is feasible but blocked by credentials, setup, service access, or missing
hardware, do not treat the source item as fully complete unless the owner
explicitly accepts that gap.

For implementation issues that include `## Delivery`, verify that closeout
matches the recorded delivery mode and closeout path, and verify that direct
dependencies or blocking relationships recorded in the issue are satisfied
before declaring closure. Close through the relevant PR body by default. Use
final-commit closure only when the issue records `direct-commit` or another
explicit final-commit closeout path. For local markdown sources, completion is
the configured move to `issues/done/` after validation and proof; do not treat a
commit alone as local issue closure.

For PRD-backed workflows with authorized branch plus draft PR delivery, do not
declare the workstream `completed` while the expected PR remains uncreated.
When merge-ready closeout authority exists, also do not declare completion while
the PR is still draft after local gates pass or missing a satisfied
`codex-pr-review` gate. Either record the PR URL, ready-for-review state, Codex
review evidence when required, and PR-body closeout path, or record the blocker
and move the publication or review action to `needs-owner`, `blocked`, or
`deferred`. Treat direct issue comments, labels, manual issue closure, parent
PRD closure, merge, and release as separate mutations that require explicit
authority.

For local markdown sources using `pull-request` delivery with merge-ready
closeout authority or a merge-ready closeout target, do not move the issue to
`issues/done/` until local validation, real PR proof, required CI or integration
proof, and Codex review evidence plus disposition are recorded. If any proof is
missing, keep the local issue open and record the remaining action as
`needs-owner`, `blocked`, or `deferred`.

If the implementation intentionally satisfies only part of the source item,
keep the source item open or move it to `needs-owner` until the deferred scope
has an owner-visible follow-up and the closeout links it.

### Follow-Up Gate

Before closing a partially satisfied source item, create or link a follow-up for
deferred work when mutation is authorized. The follow-up must include the
missing setup or behavior, the blocker or decision needed, the proof already
collected, and the acceptance criteria that remain.

If mutation is not authorized, do not close the source item. Record the proposed
follow-up title/body, file patch, reply, or owner-visible update in the ledger
under `needs-owner` or `deferred`.

### Source-Type Exit Criteria

- GitHub issue: acceptance criteria satisfied, proof recorded, and issue closed
  only when mutation is authorized; otherwise record the proposed closeout body.
- GitHub PR review thread: thread resolved or reply drafted with proof and
  owner-visible next action.
- CI failure: latest relevant run is green, or the failure is summarized with a
  blocker, owner action, and link.
- Markdown checklist or plan item: checkbox or text updated, or a proposed patch
  is recorded when file mutation is not authorized.
- Local TODO: TODO removed, updated, or linked to a follow-up with proof.
- Ledger-only item: moved to `completed`, `deferred`, `blocked`,
  `needs-owner`, or `ignored-or-suppressed` with proof and reason.
- Release checklist: release gate satisfied, or residual release scope moved to
  `deferred`, `blocked`, or `needs-owner`.

### Autoreview Gate

After non-trivial code edits, run focused tests and `$autoreview`. Treat
findings as advisory, verify each accepted finding in real code, fix actionable
issues, then rerun focused tests and `$autoreview`.

### CI Gate

Before merge-ready or release-ready status, require current CI state or a clear
reason CI is unavailable. Failing checks need a short failure summary, link, and
owner-ready next action.

### Codex PR Review Gate

For `pull-request` delivery with merge-ready closeout authority or a merge-ready
closeout target, require a Codex GitHub review before declaring the PR
merge-ready or the workstream complete. This is distinct from local
`$autoreview` and from Codex sandbox auto-review. If merge-ready closeout is
expected but not authorized, stop as `needs-owner` or `blocked` before marking
the PR ready for review.

1. Verify the PR exists, targets the expected branch/base, contains the latest
   intended commit, and has passed required local gates plus current CI or a
   recorded CI blocker.
2. If the PR is still draft, mark it ready for review with `gh pr ready <pr>`
   or an equivalent authorized GitHub action, then record the non-draft state.
3. Use `$github-review-threads` to post a top-level PR comment requesting Codex
   review. The current official Codex GitHub trigger is exactly
   `@codex review`; add a short focus after that phrase only when useful.
4. Wait or poll until Codex reacts and posts a completed GitHub review for the
   latest PR state. Do not treat a non-review PR comment, status update, cloud
   task reply, or error response as review completion. If Codex does not post a
   review, record the blocker and troubleshooting evidence: Code review enabled
   for the repository, Codex cloud configured for the repository, and exact
   `@codex review` trigger used.
5. Evaluate Codex feedback. Fix accepted actionable findings, rerun the relevant
   tests, `$autoreview`, CI, and review-thread checks, then push the update and
   request or verify a fresh completed Codex review when the diff materially
   changed.
6. For findings judged non-actionable, not applicable, or intentionally
   deferred, post a PR discussion update with the disposition, evidence, and
   validation so the discussion is not left silent. If Codex reports no
   findings, or every finding is fully addressed by commits plus validation,
   record `no-update-needed` in the ledger instead of posting a redundant
   comment.

Use this closeout state order for merge-ready PR work:

1. `draft-pr-published`
2. `ready-for-review`
3. `codex-review-requested`
4. `latest-head-review-received`
5. `feedback-dispositioned`
6. `fixes-validated-and-pushed`
7. `post-fix-ci-current`
8. `fresh-latest-head-review-current`
9. `merge-ready-report`

Do not final-answer from an intermediate state as complete, released, or
merge-ready. In particular, keep the ledger active, `ready-next`, or blocked
while review is only requested, accepted findings are unresolved, a review fix is
dirty in any publication checkout, a fix is committed but unpushed, checks are
pending for the pushed fix, a fresh latest-head Codex review is pending after a
material diff change, or PR review threads remain unresolved without an explicit
disposition.

This gate passes only when the PR is non-draft, a completed Codex GitHub review
exists for the current PR state, actionable feedback is fixed or explicitly
dispositioned, the PR discussion was updated or explicitly marked
`no-update-needed`, and no required check blocks human merge. It does not
authorize merging the PR.

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
- record a `needs-owner`, `blocked`, or `deferred` ledger item with the proposed
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

For multi-repo `pull-request` delivery, also require the real repo PR links or
equivalent integration proof promised by the PRD or issue before declaring the
cross-repo issue closed, merge-ready, or complete.

### Credential And Access Gate

If work requires credentials, paid service access, private repo permission, or
local secrets, stop and report the minimum missing access. Do not ask workers to
work around protected systems with unsafe local substitutes.
