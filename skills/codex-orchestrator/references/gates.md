# Gates Reference

Use gates before declaring work owner-ready, issue-closed, merge-ready,
release-ready, or complete. Portfolio ledgers may add stricter gates, but they
should not weaken these defaults without explicit owner approval.

## Universal Gates

Gate selection is per workstream. Always evaluate `authorization` and
`closure`. Add `live-proof` for user-facing behavior, `autoreview` for
non-trivial code edits, `ci` for merge or release readiness,
`codex-pr-review` before declaring pull-request delivery merge-ready,
`merge-authorization` only before an actual merge,
`owner-decision` when progress depends on approval or risk acceptance,
`follow-up` before closing partially satisfied work, `risk-follow-up` when a
worker or validation reports residual risk, `credential-and-access` when proof
or execution depends on credentials, service access, hardware, or protected
environments,
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

For PRD-backed `pull-request` workflows,
`publication_authority=prd-backed-pull-request` satisfies authorization for
commit, push, initial draft PR creation, ready-for-review transition, Codex
review, required discussion disposition, and the root-owned gated final PR-body
parent-PRD closeout update after tests, integration checks, and `$autoreview`
pass. Owner restrictions must first normalize to the scoped
`publication_authority`, `delivery_mode`, `pr_closeout`, and worker capability
rows; gates never reinterpret the restriction prose. Default
`pr_closeout=merge-ready`. Set `pr_closeout=draft-only` only from its canonical
option-resolution row. PR-shape prose and
`no_mutation_override=draft-output` cannot select it.
Draft-only makes downstream ready/review/merge-ready
gates `not-applicable` until the user removes the restriction. Record both
publication authority and pr_closeout in the ledger.
This does not authorize merge, release, direct issue mutation, production
deploy, or unrelated GitHub cleanup.

### Merge Authorization Gate

Before an actual merge, require `merge_authority=explicit-owner-authorization`
for the named PR or PR set. `merge_policy=owner-approval` requires a current
owner checkpoint after every other merge gate passes;
`merge_policy=automatic-after-gates` permits the root to merge without another
checkpoint only when that canonical scoped row and the matching merge-authority
row are valid for the named PR or PR set. Evidence text is recorded for audit
but is never reparsed inside this gate. Finish, complete, deliver, ship, close
out, and make merge-ready do not select either row.

Merge is root-owned. Workers cannot receive merge authority. Record the owner
instruction and timestamp, exact PR/head, mergeability, current CI, latest-head
review proof, unresolved-thread count, and merge result. When authority is
missing or ambiguous, stop at merge-ready under `needs-owner`; do not infer it
from publication or issue-mutation authority.

### Publication Safety Gate

Before push, draft PR publication, or ready-for-review transition, evaluate
`publication-safety`. Record:

- `push_policy`: `no-push`, `explicit-refspec-only`, or `block-plain-push`.
- `branch_target_guard`: `default-branch-blocked`,
  `protected-branch-blocked`, or `verified-feature-branch`.
- `publication_checkout_guard`: `worker-worktree`, `integration-worktree`,
  `caller-checkout-approved`, or `blocked`.
- `caller_checkout_guard`: `preserved`, `policy-approved-switch`, or
  `not-applicable`.
- `pr_diff_status`: `non-empty`, `empty`, or `not-checked`.
- `ready_for_review_state`: `draft`, `ready`, `not-checked`, or `not-applicable`.
- `post_push_verification`: `verified`, `failed`, or `not-applicable`.

Publication should use an explicit refspec, target the expected feature branch,
run from the recorded publication checkout, and verify the pushed branch or
draft PR state after push. When worker or integration worktrees are available,
the caller checkout should remain on its original branch; if the caller checkout
was switched, the gate must reference the scoped
`caller_checkout_policy=caller-checkout-approved` row. If the PR diff is empty,
the publication checkout is not on the expected branch, or the target is the
default/protected branch without a direct-commit row whose scoped evidence
names that exact target, stop and record `blocked`.

In a Codex App session, `worker-worktree` or `integration-worktree` passes this
gate for a newly created checkout only when the ledger records its owning App
thread id. A newly created or allocated raw Git worktree requires recorded
App-surface failure or unsuitability plus explicit owner fallback authority;
otherwise set `publication_checkout_guard=blocked`. This additional guard does
not apply in CLI-only sessions or to an existing owner-supplied checkout.

### Live Proof Gate

For user-facing behavior, require proof from the real app, CLI, API, service,
or rendered artifact before declaring the source item complete. Synthetic proof
is acceptable only when live proof is impossible, unsafe, or blocked by missing
credentials, setup, hardware, paid access, external service state, or explicit
owner deferral.

When live proof is blocked, record the exact blocker, the synthetic proof that
was collected, and the owner decision or follow-up needed. Do not land,
release, close, or mark complete on synthetic proof alone unless
`completion_proof_policy=synthetic-accepted` for that workstream or the source
item is moved to `deferred` with an owner-visible follow-up.

### Closure Gate

Before closing any source item or moving work to `completed`, verify that the
source acceptance criteria are satisfied by root-verifiable proof. If live proof
is feasible but blocked by credentials, setup, service access, or missing
hardware, do not treat the source item as fully complete unless the scoped row
is `completion_proof_policy=synthetic-accepted`.

For implementation issues that include `## Delivery`, verify that closeout
matches the recorded delivery mode and closeout path, and verify that direct
dependencies or blocking relationships recorded in the issue are satisfied
before declaring closure. Close through the relevant PR body by default. Use
final-commit closure only for `closeout_mode=direct-commit-closes-issue` with
the exact scoped authorization evidence. For local markdown sources, completion is
the configured move to `issues/done/` after validation and proof; do not treat a
commit alone as local issue closure.

For PRD-backed workflows with authorized pull-request delivery, do not
declare the workstream `completed` while the expected PR remains uncreated.
When `pr_closeout=merge-ready`, also do not declare completion while
the PR is still draft after local gates pass or missing a satisfied
`codex-pr-review` gate. Either record the PR URL, ready-for-review state, Codex
review evidence when required, and PR-body closeout path, or record the blocker
and move the publication or review action to `needs-owner`, `blocked`, or
`deferred`. For a default-branch GitHub PR that is the whole-PRD closeout
vehicle, do not declare completion or merge-ready until the current-head
`codex-pr-review` gate passes, all PRD closeout proof is satisfied, and the PR
body has been updated with the parent PRD closing keyword. A non-default-base PR
may report merge-ready only through the linked deferred-vehicle path below.
When `pr_closeout=draft-only`, require validation
and the expected draft PR, record the explicit restriction, and mark
ready/review/merge-ready gates `not-applicable`; the requested terminal state
is not itself a blocker. Record parent PRD closeout as `not-applicable` with
reason `draft-only`; if the restriction is later removed, return it to
`pending-review` and resume the merge-ready flow. Direct issue comments, labels,
manual issue or parent PRD closure, merge, and release are separate mutations requiring explicit
authority; the gated parent closing keyword in the final PR body is part of
`prd-backed-pull-request` publication authority and closes the parent only on
merge.

For local markdown sources using `pull-request` delivery with
`pr_closeout=merge-ready`, do not move the issue to
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

For `pull-request` delivery with `pr_closeout=merge-ready`, require a verified
terminal Codex result before declaring the PR merge-ready or the workstream
complete. This is distinct from local `$autoreview` and from Codex sandbox
auto-review. For `pr_closeout=draft-only`, record this gate as `not-applicable`
with the explicit user instruction or structured PRD field. If that restriction
is removed, resume this sequence at ready-for-review.

Review completion is evidence-based, not GitHub-object-type-based. A verified
terminal Codex result may be either:

- a formal GitHub review whose reviewed commit matches the current PR head; or
- a Codex-provider-authored PR comment posted after the request that names an
  unambiguous matching current-head SHA or prefix and gives a terminal result
  such as clean/no findings or concrete findings; or
- an authenticated Codex clean reaction that GitStack binds to a review request
  naming the current PR head and reports as `clean` with
  `head_is_current=true`.

Use `$gitstack:github-review-threads` automated-review status as the primary
state source. Run its JSON `reviews check --provider codex --repo <owner/repo>
--pr <number> --head <current-sha>` command before any review request and its
bounded `reviews wait` command after a request. The checker owns provider bot
identities, review objects, acknowledgements, reactions, head matching, and
stable state/exit-code mapping. Use an authenticated GitHub connector read only
as supplemental evidence when Codex posted a terminal current-head comment that
the checker does not represent; never trust display text alone.

Human comments, unverified authors, acknowledgements, pending or status
messages, cloud task replies without a terminal review result, and provider
errors are not completion evidence. Record request head, result head, checker
status, evidence kind, provider identity, object id or URL, terminal status, and
disposition.

#### Codex Review Request Matrix

Run this preflight before every `@codex review` mutation:

| Status or evidence | Required freshness | Required action | May post another request? | Ledger consequence |
| --- | --- | --- | --- | --- |
| GitStack `clean` | `head_is_current=true` | Reuse the result and pass the review-result portion of the gate. | No. | Record the terminal result and object for this head. |
| GitStack `findings` | `head_is_current=true` | Evaluate and disposition findings; fix accepted findings before closeout. | No for this head. | Record findings and disposition; a fix may create a new head with a new preflight. |
| GitStack `acknowledged` or `pending` | `head_is_current=true` | Run bounded `reviews wait` for the same head and preserve the existing request. | No. | Keep the existing request object and next poll. |
| GitStack `stale` | Refresh the assigned SHA, rerun `reviews check`, require `head_is_current=true`, re-read the PR head immediately before mutation, and require no request object for that SHA. | Post one request naming the proven current head. | Yes, exactly once for that SHA. | Record the request before polling. |
| GitStack `not-requested` | Require `head_is_current=true`, re-read the PR head immediately before mutation, and require no request object for that SHA. | Post one request naming the proven current head. | Yes, exactly once for that SHA. | Record the request before polling. |
| GitStack API, authentication, or configuration error | Current head or request state is unproven. | Record the blocker and use the documented read-only fallback. | No. | Preserve any known request evidence; do not mutate from uncertainty. |
| Verified terminal clean provider-authored comment not represented by GitStack | Authenticated provider plus unambiguous current-head SHA or prefix. | Record supplemental evidence and pass the review-result portion of the gate. | No. | Record the result kind, object, provider, and head. |
| Verified terminal findings in a provider-authored comment not represented by GitStack | Authenticated provider plus unambiguous current-head SHA or prefix. | Record supplemental evidence and disposition findings. | No for this head. | Record findings and disposition. |
| Terminal provider error for the current-head request | Existing request object and current head are recorded. | Record the error and follow recovery without another request for the unchanged head. | No. | Block or wait until a new head or external recovery exists. |
| Unverified or human-authored comment claiming success | No verified result; use the GitStack status for the proven current head. | Ignore the comment and follow the matching GitStack row. | Only through a proven `stale` or `not-requested` row. | Record that the comment was rejected as evidence. |

`request-codex-review` is idempotent per PR head. Do not post when a valid
terminal result or an active request already exists for the current head. A new
commit that changes the PR head invalidates the old result and permits exactly
one new request. GitHub storing a valid Codex result as a comment rather than a
formal review never permits a duplicate request by itself. Owner wording and
retry instructions cannot override unchanged-head idempotency.

1. Verify the PR exists, targets the expected branch/base, contains the latest
   intended commit, and has passed required local gates plus current CI or a
   recorded CI blocker.
2. Reconcile the PR body before current-head review preflight. If it already
   contains the parent PRD closing keyword while parent closeout is not `armed`
   with the same current reviewed SHA and recorded PR-body evidence, the root
   must remove it or replace it with a non-closing reference and record
   `pending-review`. If the authorized root cannot disarm it, record `blocked`
   and stop before merge-ready.
3. If the PR is still draft, mark it ready for review with `gh pr ready <pr>`
   or an equivalent authorized GitHub action, then record the non-draft state.
4. Run GitStack `reviews check --provider codex` with the exact current head.
   Apply the returned status and the matrix before posting anything. Use an
   authenticated connector read only for supplemental terminal-comment evidence
   or the documented checker fallback.
5. Only when the matrix permits it, immediately re-read the PR head and verify
   it still equals the checked SHA and the ledger has no request object for that
   SHA. Then post exactly one top-level PR comment. The official trigger is
   exactly `@codex review`; name the current head and add a short focus only when
   useful. Record the request object and head before any other action.
6. Run bounded GitStack `reviews wait --provider codex` against the same head.
   Reuse the request across `acknowledged`, `pending`, and timeouts; never post
   another request merely because the wait returned without a terminal result.
   If no terminal result appears, record the blocker and troubleshooting
   evidence: Code review enabled for the repository, Codex cloud configured for
   the repository, exact trigger used, request object, and current head.
7. Evaluate Codex feedback. Fix accepted actionable findings, rerun the relevant
   tests, `$autoreview`, CI, and review-thread checks, then push the update and
   run the request matrix for the new head when the diff materially changed.
8. For findings judged non-actionable, not applicable, or intentionally
   deferred, post a PR discussion update with the disposition, evidence, and
   validation so the discussion is not left silent. If Codex reports no
   findings, or every finding is fully addressed by commits plus validation,
   record `no-update-needed` in the ledger instead of posting a redundant
   comment.

Use this closeout state order for merge-ready PR work:

1. `draft-pr-published`
2. `ready-for-review`
3. `current-head-review-preflight`
4. `codex-review-requested-or-reused`
5. `current-head-terminal-result-received`
6. `feedback-dispositioned`
7. `fixes-validated-and-pushed`
8. `post-fix-ci-current`
9. `fresh-current-head-result-current`
10. `parent-prd-closeout-resolved` (`armed`, `deferred-to-default-branch`, or `not-applicable`)
11. `post-closeout-head-current` (`pass` for `armed`; otherwise `not-applicable` with reason)
12. `parent-closeout-watch-established` (`root-monitoring`, `owner-handoff`, `automation-handoff`, or `not-applicable`)
13. `merge-ready-report`

Do not final-answer from an intermediate state as complete, released, or
merge-ready. Keep the ledger active, `ready-next`, or blocked while review is
only requested, accepted findings are unresolved, a review fix is dirty in any
publication checkout, a fix is committed but unpushed, checks are pending for
the pushed fix, a fresh current-head Codex result is pending after a material
diff change, or PR review threads remain unresolved without an explicit
disposition. Poll an existing current-head request instead of posting again.

This gate passes only when the PR is non-draft, a verified terminal Codex result
exists for the current PR head, actionable feedback is fixed or explicitly
dispositioned, the PR discussion was updated or explicitly marked
`no-update-needed`, and no required check blocks human merge. It does not
authorize merging the PR.

After this gate passes, resolve parent PRD closeout before the merge-ready
report. A final feature or integration PR that completes the whole PRD and
targets the repository's current default branch must add the parent PRD closing
keyword. Verify the PR body now closes every satisfied generated issue plus the
parent PRD, record the updated body URL or fingerprint, and leave the PRD open
until GitHub processes the closing keyword on merge. If the PR targets a
non-default branch, leave the keyword absent, record
`deferred-to-default-branch`, and select or create a linked later default-branch
PR as the parent closeout vehicle; do not record `armed` for the
non-default-branch PR. The current PR may report merge-ready after its own gates
pass, but keep the later closeout vehicle in `ready-next` or `active` and do not
mark the whole PRD or ledger complete until that vehicle reaches `armed`. If any PRD scope,
dependency, integration proof, or required domain closeout remains, also leave
the parent keyword absent and record `pending-closeout`; use `blocked` only when
an external condition prevents the next safe action. For partial PRs, ad hoc
PRs, local-tracker PRs, and workstreams without a parent GitHub PRD, record
parent closeout as `not-applicable` and continue.

Immediately before the root updates the PR body, re-read the PR head and require
it to equal the reviewed SHA; also re-read the current default branch and
require the PR base to match it. Re-read the head, current default branch, PR
base, and current PR body after the body update and immediately before the
merge-ready report. Require the live body or its fingerprint to match the
recorded closeout evidence and contain exactly the intended parent closer. If
the head differs, do not add the parent keyword, or remove/replace an
already-added parent closing keyword with a non-closing reference, set
`parent_prd_closeout=pending-review`, and return to current-head review
preflight. If the default branch or PR base no longer matches, disarm the keyword
and record `deferred-to-default-branch` until a linked default-branch closeout
vehicle passes the gates. If only the body differs, set
`parent_prd_closeout=pending-closeout`, reconcile the live body without
overwriting concurrent edits, and repeat the post-update checks. Any relevant
change after `armed` invalidates that state and requires the matching
disarm-and-review, body-reconciliation, or closeout-vehicle cycle.

`armed` is not terminal parent closure while the PR remains open. Before
releasing the active root, establish exactly one parent closeout watch:

- `root-monitoring`: use only when
  `merge_authority=explicit-owner-authorization` and the root is the designated
  merger. Keep the root claim active through the root-controlled merge and
  actual PRD closure check. Immediately before merge, re-read the PR head, base,
  current default branch, and live body fingerprint; on any mismatch disarm the
  parent closer and stop the merge for the matching review or closeout cycle;
- `owner-handoff`: required when `merge_authority=none` or another actor will
  merge. Move the unmerged parent closeout to `needs-owner`, keep the ledger
  `paused`, and record an owner-visible handoff that requires rechecking the PR
  head, base, current default branch, and body fingerprint immediately before
  merge; on any mismatch the owner must not merge and must return the work to
  the orchestrator for disarm/review;
- `automation-handoff`: use only when the matching scoped row is
  `automation_authority=explicit-owner-authorization` for a real event-driven
  monitor that can observe head, base/default-branch, and PR-body
  mutations before merge, block the merge or disarm the closer on mismatch, and
  verify post-merge issue state. Record its id, event triggers, last successful
  check, and identical mismatch/disarm behavior; or
- `not-applicable`: only when parent closeout itself is not applicable.

The durable watch packet must name the PR, parent PRD, reviewed SHA,
base/default branch, PR-body evidence, mutation triggers, and post-merge
issue-state check. A final report alone is owner-visible but is not durable
handoff evidence unless the same packet is persisted in the ledger. Do not set
the ledger `complete` while the parent is merely `armed` or
`deferred-to-default-branch`; a released root with owner or automation handoff
leaves the ledger `paused`, not complete.

After merge, verify that the merged head/base and closing keyword still match
the armed evidence and that GitHub actually closed the parent PRD. Only then set
the watch to `complete` and parent closeout to `closed`. If the PR merged but the issue
remains open, record `needs-owner`; direct closure still requires
`explicit-direct-mutation`.

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
package artifacts, migration notes, rollback path, and CI. Use
`$gitstack:github-releases` for GitHub-backed releases.

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
