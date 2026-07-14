# Codex Review And Parent Closeout

Load this reference only when `delivery_mode=pull-request` and
`pr_closeout=merge-ready`. `gates.md` owns this route and all gate selection;
this file owns the resulting current-head review, wait, feedback disposition,
parent-PRD closeout, watch, and post-merge algorithm.

## Codex PR Review Gate

For `pull-request` delivery with `pr_closeout=merge-ready`, resolve
`codex_review_policy` per workstream before declaring the PR merge-ready or the
workstream complete. The default `required` value requires a verified terminal
Codex result for the current head. An exact scoped owner instruction may select
`skip`; that bypasses only the Codex request and wait, not local `$autoreview`,
CI, validation, PRD acceptance, integration, domain closeout, or parent-closeout
head checks. For `pr_closeout=draft-only`, record the policy and this gate as
`not-applicable` with the explicit user instruction or structured PRD field. If
that restriction is removed, resume this sequence at ready-for-review with the
newly resolved review policy.

When `codex_review_policy=skip`:

1. Record the exact owner instruction and its `owner-ref`, workstream
   `scope-ref`, and workstream `target-ref` in `## Option Resolution`, with both
   scoped refs equal to the current workstream. Record `pr-ref=not-applicable`
   for a workstream-scoped instruction. For a PR-scoped instruction, preserve
   its immutable canonical `<owner>/<repo>#<number>` as `pr-ref`, resolve it to
   every current workstream mapped to that PR, and require it to equal each
   refreshed `current_pr_ref` before every skip-path action. If the live PR
   changes, invalidate the skip row and reset the policy to `required` unless
   the owner provides a new exact instruction.
2. Mark the PR ready after local gates pass, but do not post `@codex review`, run
   a wait, poll an active request, or treat review unavailability as a blocker.
3. Fix or explicitly disposition any actionable Codex feedback already known
   when the skip is resolved. Do not wait for pending or later feedback.
4. Record `codex_review=skipped`, request/result evidence as absent unless an
   already-known result is being dispositioned, and the fully validated current
   PR head as the closeout-qualified SHA.

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
state source. Run
`<plugin-root>/scripts/gitstack --json reviews check --provider codex --repo <owner/repo> --pr <number> --head <current-sha>`
before any review request, promotion, resumed wait, or extended-deadline
decision, and use its bounded `reviews wait` command after a request. The
checker owns provider bot identities, review objects, acknowledgements,
reactions, head matching, and stable state/exit-code mapping. Use an
authenticated GitHub connector read only as supplemental evidence when Codex
posted a terminal current-head comment that the checker does not represent;
never trust display text alone.

Human comments, unverified authors, acknowledgements, pending or status
messages, cloud task replies without a terminal review result, and provider
errors are not completion evidence. Record request head, result head, checker
status, evidence kind, provider identity, object id or URL, terminal status, and
disposition.

### Codex Review Request Matrix

When `codex_review_policy=required`, run this preflight before every
`@codex review` mutation:

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

### Codex Review Wait Budget

For `codex_review_policy=required`, use only a 15-minute standard or 30-minute
extended total active-wait budget per PR head. These budgets are timeout
deadlines for bounded `reviews wait`, not polling intervals, and are derived
runtime state rather than selectable options. The ledger's
`## Codex Review Wait Registry` is the sole timing authority: atomically find
or create exactly one row keyed by `<owner>/<repo>#<number>@<current-sha>`.
Every workstream mapped to that PR and head must reuse that row's earliest
`wait_started_at`, single `wait_deadline`, and `wait_record`; workstream fields
are projections and must never initialize or extend an independent window.

1. A PR starts with `wait_profile=standard` and a 15-minute total active-wait
   budget. Persist the exact `wait_profile_pr` as `<owner/repo>#<number>` or the
   canonical PR URL. The first workstream to wait creates the registry row,
   persists `wait_started_at`, and sets `wait_deadline` to 15 minutes after that
   start. Any concurrent or later mapped workstream must reuse the existing
   row and run only for its deadline-derived remaining time. Only the row
   creator with the full initial budget runs GitStack with
   `<plugin-root>/scripts/gitstack --json reviews wait --provider codex --repo <owner/repo> --pr <number> --head <current-sha> --timeout 15m --interval 10s --max-interval 30s`.
   This polls after about 10, 15, 22.5, and then 30 seconds, capped at 30
   seconds.
2. If that deadline expires, rerun `reviews check` before waiting again. Only
   when the same request object and current head remain `acknowledged` or
   `pending`, promote the PR to `wait_profile=extended` and move the deadline
   to 30 minutes after the original `wait_started_at`. Continue only for the
   remaining budget, normally 15 minutes; never start a fresh 30-minute wait
   after already consuming the standard window. Subtract the current time from
   `wait_deadline`, round down to positive integer seconds, and, when at least
   one second remains, run
   `<plugin-root>/scripts/gitstack --json reviews wait --provider codex --repo <owner/repo> --pr <number> --head <current-sha> --timeout <remaining-seconds>s --interval 10s --max-interval 30s`.
   When less than one second remains, do not invoke GitStack; continue to the
   extended-deadline handling below.
3. Once any head on a PR requires promotion, every workstream mapped to that PR
   preserves its exact `wait_profile_pr` plus `wait_profile=extended`, and
   subsequent heads of that same PR start with a 30-minute total active-wait
   budget. Reset `wait_started_at` and `wait_deadline` for the new head and run
   GitStack with
   `<plugin-root>/scripts/gitstack --json reviews wait --provider codex --repo <owner/repo> --pr <number> --head <current-sha> --timeout 30m --interval 10s --max-interval 30s`.
   If the live PR identity differs from `wait_profile_pr`, reset to `standard`,
   persist the new PR identity, and use 15 minutes; never carry an extended
   profile to a deferred closeout vehicle or any other PR.
   Promotion updates the one registry row first and then every mapped
   workstream projection; no workstream may calculate a later replacement
   deadline.
4. On recovery or resume, calculate the remaining timeout from the persisted
   deadline using the same round-down rule and remaining-budget command from
   step 2. Invoke it only when the substituted `<remaining-seconds>` is a
   positive integer. When no time remains, rerun `reviews check`, promote an
   expired `standard` profile only through step 2, or apply the extended
   deadline handling below. The substituted timeout is deadline-derived data,
   not another selectable budget. A partial prior wait never creates a third
   budget tier or extends the deadline.
5. If the current request is still `acknowledged` or `pending` at the extended
   deadline, rerun the current-head check, preserve the request, set
   `wait_state=monitoring-required`, and stop the continuous waiter. Keep the
   action `ready-next` under root monitoring, owner handoff, or an explicitly
   authorized automation handoff. A still-pollable review is not a blocker and
   is never completion evidence; only an unpollable check, provider error, or
   missing required access may become blocked.

For `codex_review_policy=skip` or an otherwise inapplicable review gate, record
the wait-profile PR identity, profile, budget, timestamps, elapsed time, and state as
`not-applicable`; do not start or resume a waiter.

1. Verify the PR exists, targets the expected branch/base, contains the latest
   intended commit, and has passed required local gates plus current CI or a
   recorded CI blocker.
2. Reconcile the PR body before the policy-specific closeout gate. If it already
   contains the parent PRD closing keyword while parent closeout is not `armed`
   with the same closeout-qualified SHA and recorded PR-body evidence, the root
   must remove it or replace it with a non-closing reference and record
   `pending-review` for `required` or `pending-closeout` for `skip`. If the
   authorized root cannot disarm it, record `blocked` and stop before
   merge-ready. A pre-existing keyword is never proof that the root's post-gate
   mutation occurred.
3. If the PR is still draft, mark it ready for review with `gh pr ready <pr>`
   or an equivalent authorized GitHub action, then record the non-draft state.
4. When `codex_review_policy=required`, run GitStack
   using the exact `reviews check` command above with the current head. Apply
   the returned status and the matrix before posting anything. Use an
   authenticated connector read only for supplemental terminal-comment
   evidence or the documented checker fallback. For `skip`, record this step as
   `not-applicable` and continue to feedback disposition without checking or
   polling review status.
5. Only when `codex_review_policy=required` and the matrix permits it,
   immediately re-read the PR head and verify
   it still equals the checked SHA and the ledger has no request object for that
   SHA. Then post exactly one top-level PR comment. The official trigger is
   exactly `@codex review`; name the current head and add a short focus only when
   useful. Record the request object and head before any other action.
6. When `codex_review_policy=required`, run bounded GitStack
   `reviews wait` against the same head using the Codex Review
   Wait Budget contract above. Reuse the request across `acknowledged`,
   `pending`, and timeouts; never post another request merely because the wait
   returned without a terminal result. At a final extended timeout, preserve
   the request and record troubleshooting evidence: Code review enabled for the
   repository, Codex cloud configured for the repository, exact trigger used,
   request object, and current head. Classify it as `monitoring-required` while
   it remains pollable, not as blocked. For `skip`, record this step as
   `not-applicable` and do not wait.
7. Evaluate the feedback required by the resolved policy: all current-head Codex
   feedback for `required`, or only already-known actionable Codex feedback for
   `skip`. Fix accepted actionable findings, rerun the relevant tests,
   `$autoreview`, CI, and review-thread checks, then push the update. For
   `required`, run the request matrix for the new head when the diff materially
   changed; for `skip`, revalidate the new head without requesting review.
8. For findings judged non-actionable, not applicable, or intentionally
   deferred, post a PR discussion update with the disposition, evidence, and
   validation so the discussion is not left silent. Merge-ready PRD-backed
   publication authority covers this disposition mutation for both `required`
   and `skip`; otherwise require separate comment authority or record the
   disposition only in the ledger and keep external comment mutation pending.
   If Codex reports no
   findings, or every finding is fully addressed by commits plus validation,
   record `no-update-needed` in the ledger instead of posting a redundant
   comment.

Use this closeout state order for merge-ready PR work:

1. `draft-pr-published`
2. `ready-for-review`
3. `codex-review-policy-resolved` (`required` or owner-scoped `skip`)
4. `current-head-review-preflight` (`required`) or `not-applicable` (`skip`)
5. `codex-review-requested-or-reused` (`required`) or `not-applicable` (`skip`)
6. `current-head-terminal-result-received` (`required`) or `not-applicable` (`skip`)
7. `known-review-feedback-dispositioned` (required feedback, already-known skipped feedback, or `not-applicable`)
8. `fixes-validated-and-pushed`
9. `post-fix-ci-current`
10. `closeout-head-current` (reviewed SHA for `required`; fully validated current SHA for `skip`)
11. `parent-prd-closeout-resolved` (`armed`, `deferred-to-default-branch`, or `not-applicable`)
12. `post-closeout-head-current` (`pass` for `armed`; otherwise `not-applicable` with reason)
13. `parent-closeout-watch-established` (`root-monitoring`, `owner-handoff`, `automation-handoff`, or `not-applicable`)
14. `merge-ready-report`

Do not final-answer from an intermediate state as complete, released, or
merge-ready. Keep the ledger active, `ready-next`, or blocked while review is
only requested, accepted findings are unresolved, a review fix is dirty in any
publication checkout, a fix is committed but unpushed, checks are pending for
the pushed fix, a policy-required fresh current-head Codex result is pending
after a material diff change, or known PR review threads remain unresolved
without an explicit disposition. Poll an existing current-head request instead
of posting again only when `codex_review_policy=required`.

For `codex_review_policy=required`, this gate passes only when the PR is
non-draft, a verified terminal Codex result exists for the current PR head,
actionable feedback is fixed or explicitly dispositioned, and the PR discussion
was updated or explicitly marked `no-update-needed`. For
`codex_review_policy=skip`, it passes when the PR is non-draft, scoped owner
evidence is recorded, no request/wait remains actionable, and any already-known
actionable feedback is fixed or explicitly dispositioned. In both paths, no
required check may block human merge. Neither path authorizes merging the PR.

After this gate passes, resolve parent PRD closeout before the merge-ready
report. Arm it only after all PRD closeout proof is satisfied. A final feature
or integration PR that completes the whole PRD and
targets the repository's current default branch must add the parent PRD closing
keyword. Verify the PR body now closes every satisfied generated issue plus the
parent PRD, record the updated body URL or fingerprint, and leave the PRD open
until GitHub processes the closing keyword on merge. Use
`Closes #<PRD-number>` in the same repository. Across repositories, use
`Closes owner/repo#<PRD-number>` only when that closeout path is intended and
supported; otherwise record `blocked` or `needs-owner`. If the PR targets a
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
it to equal the closeout-qualified SHA: the reviewed SHA for `required`, or the
fully validated current SHA for `skip`; also re-read the current default branch and
require the PR base to match it. Re-read the head, current default branch, PR
base, and current PR body after the body update and immediately before the
merge-ready report. Require the live body or its fingerprint to match the
recorded closeout evidence and contain exactly the intended parent closer. If
the head differs, do not add the parent keyword, or remove/replace an
already-added parent closing keyword with a non-closing reference, set
`parent_prd_closeout=pending-review` and return to current-head review preflight
for `required`; for `skip`, set `parent_prd_closeout=pending-closeout`, rerun the
affected validation and current CI for the new head, and do not request review.
If the default branch or PR base no longer matches, disarm the keyword
and record `deferred-to-default-branch` until a linked default-branch closeout
vehicle passes the gates. If only the body differs, set
`parent_prd_closeout=pending-closeout`, reconcile the live body without
overwriting concurrent edits, and repeat the post-update checks. Any relevant
change after `armed` invalidates that state and requires the matching
disarm-and-review or disarm-and-revalidate cycle, body reconciliation, or
closeout-vehicle cycle.

`armed` is not terminal parent closure while the PR remains open. Before
releasing the active root, establish exactly one parent closeout watch:

- `root-monitoring`: use only when
  `merge_authority=explicit-owner-authorization` and the root is the designated
  merger. Keep the root claim active through the root-controlled merge and
  actual PRD closure check. Immediately before merge, re-read the PR head, base,
  current default branch, and live body fingerprint; on any mismatch disarm the
  parent closer and stop the merge for the matching review/revalidation or
  closeout cycle;
- `owner-handoff`: required when `merge_authority=none` or another actor will
  merge. Move the unmerged parent closeout to `needs-owner`, keep the ledger
  `paused`, and record an owner-visible handoff that requires rechecking the PR
  head, base, current default branch, and body fingerprint immediately before
  merge; on any mismatch the owner must not merge and must return the work to
  the orchestrator for policy-specific disarm and review/revalidation;
- `automation-handoff`: use only when the matching scoped row is
  `automation_authority=explicit-owner-authorization` for a real event-driven
  monitor that can observe head, base/default-branch, and PR-body
  mutations before merge, block the merge or disarm the closer on mismatch, and
  verify post-merge issue state. Record its id, event triggers, last successful
  check, and identical mismatch/disarm behavior; or
- `not-applicable`: only when parent closeout itself is not applicable.

The durable watch packet must name the PR, parent PRD, resolved review policy,
closeout-qualified SHA,
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
