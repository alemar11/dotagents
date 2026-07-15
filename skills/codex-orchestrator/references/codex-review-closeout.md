# Codex Review And Parent Closeout

Load this reference only when
`change_delivery_target=pull-request-ready-for-merge-but-not-merged`.
`gates.md` owns this route and all gate selection;
this file owns the resulting current-revision review, wait, feedback disposition,
parent Feature Spec closeout, watch, and post-merge algorithm.

## Execution Owner

When `visible_app_task_permission=granted-by-authorized-user`, the single
visible task assigned to the Feature Spec executes this entire algorithm
through `merge-ready-report`, including every GitStack `reviews check` and
`reviews wait`, review request, feedback disposition and fix, validation and CI
cycle, PR-body closeout mutation, and ready transition. The root only reads the
task through `read_thread`, compares its reported state with the ledger and expected state order,
sends corrective messages on drift, and reconciles final evidence. It must not
invoke the review check/wait workflow, poll the PR review, fix findings, mutate
the PR, or mark it ready for that Spec.

If the assigned task fails or loses required capability, the root may steer,
resume-equivalent, or replace it with one visible task for the same Feature
Spec. It must not fall back to root-owned or background-only review closeout.
Outside mandatory visible Feature Spec task mode, the root may execute this
algorithm directly or assign its explicit actions to a capable worker.

## Codex PR Review Gate

For `pull-request-ready-for-merge-but-not-merged`, resolve
`codex_review_requirement` per workstream before declaring the PR merge-ready or the
workstream complete. The default
`required-on-current-pull-request-head` value requires a verified terminal
Codex result for the current pull-request revision: the exact head SHA, base
ref, and merge-base SHA. An exact scoped authorized-user instruction
may select `explicitly-skipped-by-authorized-user`; that bypasses only the Codex request and wait, not local `$autoreview`,
CI, validation, Feature Spec acceptance, integration, domain closeout, or parent-closeout
head checks. Other delivery targets never load this reference.

When `codex_review_requirement=explicitly-skipped-by-authorized-user`:

1. Record the exact authorized-user instruction as
   `permission-source-ref=authorized-user:<instruction-ref>`, plus workstream
   `scope-ref` and workstream `target-ref` in `## Option Resolution`, with both
   scoped refs equal to the current workstream. Record `pr-ref=not-applicable`
   for a workstream-scoped instruction. For a PR-scoped instruction, preserve
   its immutable canonical `<owner>/<repo>#<number>` as `pr-ref`, resolve it to
   every current workstream mapped to that PR, and require it to equal each
   refreshed `target_pull_request_ref` before every skip-path action. If the live PR
   changes, invalidate the skip row and reset the policy to
   `required-on-current-pull-request-head` unless
   the owner provides a new exact instruction.
2. Keep a draft PR draft while the skip evidence and non-review gates are being
   resolved. Do not post `@codex review`, run a wait, poll an active request, or
   treat review unavailability as a blocker.
3. Fix or explicitly disposition any actionable Codex feedback already known
   when the skip is resolved, then rerun the affected validation and CI. Do not
   wait for pending or later feedback.
4. Record `codex_review=skipped`, request/result evidence as absent unless an
   already-known result is being dispositioned, and the fully validated current
   PR head, base ref, and merge-base SHA as the closeout-qualified revision.
   Mark the PR ready only through the
   common post-policy promotion step below.

Review completion is evidence-based, not GitHub-object-type-based. A verified
terminal Codex result may be either:

- a formal GitHub review whose reviewed commit matches the current PR head and
  whose recorded request base ref and merge-base SHA still match the live PR; or
- a Codex-provider-authored PR comment posted after the request that names an
  unambiguous matching current-head SHA or prefix, was requested for the same
  base ref and merge-base SHA, and gives a terminal result such as clean/no
  findings or concrete findings; or
- an authenticated Codex clean reaction that GitStack binds to a review request
  naming the current PR revision and reports as `clean` with
  `head_is_current=true`, provided the locally verified base ref and merge-base
  SHA still match the request revision.

Use `$gitstack:github-review-threads` automated-review status as the primary
state source. Before every check, derive the live review revision by reading the
PR head SHA and base ref and computing the merge-base SHA between that head and
the current base head. Run
`<plugin-root>/scripts/gitstack --json reviews check --provider codex --repo <owner/repo> --pr <number> --head <current-sha>`
before any review request, promotion, resumed wait, or extended-deadline
decision, and use its bounded `reviews wait` command after a request. The
checker owns provider bot identities, review objects, acknowledgements,
provider-authored terminal comments, reactions, head matching, stable
observation fingerprints, and state/exit-code mapping. Use an authenticated
GitHub connector only as the documented read-only fallback after an actual
checker API/authentication/configuration error or an evidenced tool-capability
gap. A normal `acknowledged` or `pending` result never activates the fallback;
never trust display text alone.

For controller state, derive the stored review observation fingerprint from
GitStack's stable observation plus the verified base ref and merge-base SHA.
This preserves GitStack's provider classification while ensuring that a
head-only match cannot make a changed effective diff look current.

This flow uses the manual top-level PR-comment trigger `@codex review`.
Automatic reviews are a separate repository setting and are neither required
nor request evidence here. Do not infer that a manual request is unavailable
only because the PR is draft. If live provider evidence proves that the manual
trigger cannot run on the draft PR, record a capability blocker and stop; do
not move the PR to ready early to bypass the selected draft-review-first flow.

Human comments, unverified authors, acknowledgements, pending or status
messages, cloud task replies without a terminal review result, and provider
errors are not completion evidence. Record request and result head SHAs, base
refs, merge-base SHAs, checker status, evidence kind, provider identity, object
id or URL, terminal status, and disposition.

### Codex Review Request Matrix

When `codex_review_requirement=required-on-current-pull-request-head`, run this preflight before every
`@codex review` mutation:

| Status or evidence | Required freshness | Required action | May post another request? | Ledger consequence |
| --- | --- | --- | --- | --- |
| GitStack `clean` | `head_is_current=true` and the request base ref plus merge-base SHA equal the live revision | Reuse the result and pass the review-result portion of the gate. | No. | Record the terminal result and object for this revision. |
| GitStack `findings` | `head_is_current=true` and the request base ref plus merge-base SHA equal the live revision | Evaluate and disposition findings; fix accepted findings before closeout. | No for this revision. | Record findings and disposition; a fix or effective-base change creates a new revision with a new preflight. |
| GitStack `acknowledged` or `pending` | `head_is_current=true` and the request base ref plus merge-base SHA equal the live revision | Run bounded `reviews wait` for the same revision and preserve the existing request. | No. | Keep the existing request object and next poll. |
| GitStack `stale` | Refresh the full revision, rerun `reviews check`, require `head_is_current=true`, re-read the head/base/merge-base immediately before mutation, and require no request object for that revision. | Post one request naming the proven current head and base. | Yes, exactly once for that revision. | Record the request revision before polling. |
| Locally stale base ref or merge-base SHA | Ignore any head-only clean/pending classification, recompute the full revision, and require no request object for that revision. | Post one request naming the unchanged head and new base revision. | Yes, exactly once for that revision. | Preserve the old result as history and record a new request revision before polling. |
| GitStack `not-requested` | Require `head_is_current=true`, re-read the head/base/merge-base immediately before mutation, and require no request object for that revision. | Post one request naming the proven current head and base. | Yes, exactly once for that revision. | Record the request revision before polling. |
| GitStack API, authentication, or configuration error | Current revision or request state is unproven. | Record the error and use the documented read-only fallback. An evidenced tool-capability gap uses this same error path; the fallback may classify an authenticated terminal comment only when its head/base/merge-base revision is proven. | No. | Preserve any known request evidence; do not mutate from uncertainty. |
| Terminal provider error for the current-revision request | Existing request object and current revision are recorded. | Record the error and follow recovery without another request for the unchanged revision. | No. | Block or wait until a new revision or external recovery exists. |
| Unverified or human-authored comment claiming success | No verified result; use the GitStack status plus local base evidence for the proven current revision. | Ignore the comment and follow the matching GitStack row. | Only through a proven stale-revision or `not-requested` row. | Record that the comment was rejected as evidence. |

`request-codex-review` is idempotent per PR revision. Do not post when a valid
terminal result or an active request already exists for the current head SHA,
base ref, and merge-base SHA. A new commit, base-ref change, or merge-base
change invalidates the old result and permits exactly one new request for the
new revision. Advancing the base branch without changing the merge base does
not create a new revision. GitHub storing a valid Codex result as a comment
rather than a formal review never permits a duplicate request by itself. Owner
wording and retry instructions cannot override unchanged-revision idempotency.

### Codex Review Wait Budget

For `codex_review_requirement=required-on-current-pull-request-head`, use only a 15-minute standard or 30-minute
extended total active-wait budget per PR revision. These budgets are timeout
deadlines for bounded `reviews wait`, not polling intervals, and are derived
runtime state rather than selectable options. The ledger's
`## Codex Review Wait Registry` is the sole timing authority: atomically find
or create exactly one row keyed by
`<owner>/<repo>#<number>@<head-sha>@<base-ref>@<merge-base-sha>`.
Every workstream mapped to that PR revision must reuse that row's earliest
`wait_started_at`, single `wait_deadline`, and `wait_record`; workstream fields
are projections and must never initialize or extend an independent window.
The row also stores GitStack's stable `observation_fingerprint` and
`last_transition_at`. Persist the initial observation, then change those fields
and the mapped workstream projections only for a new fingerprint, checker/wait
state, request object/revision, terminal result, or deadline tier. Repeated polls
with the same fingerprint inside one bounded waiter perform no ledger write,
timestamp refresh, note, metric, or progress message. If the complete bounded
waiter times out unchanged in `monitoring-required`, write the next scheduled
`due_at` once without refreshing review transition state or reporting progress.
Compute elapsed time from timestamps only for a report; never persist it as
controller state.

1. A PR starts with `wait_profile=standard` and a 15-minute total active-wait
   budget. Persist the exact `wait_profile_pr` as `<owner/repo>#<number>` or the
   canonical PR URL. The first workstream to wait creates the registry row,
   persists `wait_started_at`, and sets `wait_deadline` to 15 minutes after that
   start. Any concurrent or later mapped workstream must reuse the existing
   row and run only for its deadline-derived remaining time. Only the row
   creator with the full initial budget runs GitStack with
   `<plugin-root>/scripts/gitstack --json reviews wait --provider codex --repo <owner/repo> --pr <number> --head <current-sha> --timeout 15m --interval 10s --max-interval 30s`.
   This single bounded waiter polls after about 10, 15, 22.5, and then 30
   seconds, capped at 30 seconds. Do not replace it with a caller loop of
   `reviews check` plus shell `sleep`, and do not run another waiter while it is
   active.
2. If that deadline expires, recompute the live head, base ref, and merge-base
   SHA, then rerun `reviews check` before waiting again. Only when the same
   request object and current revision remain `acknowledged` or
   `pending`, promote the PR to `wait_profile=extended` and move the deadline
   to 30 minutes after the original `wait_started_at`. Continue only for the
   remaining budget, normally 15 minutes; never start a fresh 30-minute wait
   after already consuming the standard window. Subtract the current time from
   `wait_deadline`, round down to positive integer seconds, and, when at least
   one second remains, run
   `<plugin-root>/scripts/gitstack --json reviews wait --provider codex --repo <owner/repo> --pr <number> --head <current-sha> --timeout <remaining-seconds>s --interval 10s --max-interval 30s`.
   When less than one second remains, do not invoke GitStack; continue to the
   extended-deadline handling below.
3. Once any revision on a PR requires promotion, every workstream mapped to that PR
   preserves its exact `wait_profile_pr` plus `wait_profile=extended`, and
   subsequent revisions of that same PR start with a 30-minute total active-wait
   budget. Reset `wait_started_at` and `wait_deadline` for the new revision and run
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
   The waiter owns the repeated checks and returns immediately on a clean,
   findings, stale, or error transition. Persist its final fingerprint once;
   do not replay its unchanged intermediate attempts into the ledger.
5. If the current request is still `acknowledged` or `pending` at the extended
   deadline, rerun the current-revision check, preserve the request, set
   `wait_state=monitoring-required`, and stop the continuous waiter. Keep the
   action `ready-next`. In mandatory visible Feature Spec task mode, the
   assigned task remains the polling owner and resumes bounded polling at the
   next check while the root monitors only that task's progress. Outside that
   mode, use root monitoring, owner handoff, or an explicitly authorized
   automation handoff. A still-pollable review is not a blocker and is never
   completion evidence; only an unpollable check, provider error, or missing
   required access may become blocked.

For `codex_review_requirement=explicitly-skipped-by-authorized-user` or an otherwise inapplicable review gate, record
the wait-profile PR identity, profile, budget, timestamps, observation
fingerprint, transition time, and state as
`not-applicable`; do not start or resume a waiter.

An `upstream-merge-ready-head` downstream PR is not eligible to enter the
review algorithm while it still targets the upstream branch. Its assigned task
may implement, validate, push, publish the draft PR, and run CI, then must keep
the PR draft with `dependency_state=awaiting-upstream-merge`. After the upstream
PR merges independently, the same task must reconcile the downstream branch
onto the current default branch, retarget the PR, and record
`dependency_state=satisfied` before requesting Codex review. Do not spend a
review request or wait budget on the intentionally temporary stacked base.

1. Verify the PR exists, targets the expected branch/base, contains the latest
   intended commit, and has passed required local gates plus current CI or a
   recorded CI blocker.
2. Reconcile the PR body before the policy-specific closeout gate. If it already
   contains the parent Feature Spec closing keyword while parent closeout is not `armed`
   with the same closeout-qualified revision and recorded PR-body evidence, the
   closeout executor must remove it or replace it with a non-closing reference and record
   `pending-review` for `required-on-current-pull-request-head` or
   `pending-closeout` for `explicitly-skipped-by-authorized-user`. If the
   authorized closeout executor cannot disarm it, record `blocked` and stop
   before merge-ready. A pre-existing keyword is never proof that the
   post-gate mutation occurred.
3. If the PR is draft, keep it draft through the policy-specific review,
   feedback disposition, and fix-validation path. If it is already non-draft,
   record that live state, but do not treat it as review or merge-ready evidence
   and do not convert it to draft without separate authority.
4. When `codex_review_requirement=required-on-current-pull-request-head`, derive
   and record the current head SHA, base ref, and merge-base SHA, then run GitStack
   using the exact `reviews check` command above with that head. Apply
   the returned status and the matrix before posting anything. Use an
   authenticated connector only for the documented read-only fallback after a
   checker error or evidenced capability gap; do not add a connector read to a
   normal pending poll. For an explicit skip, record this step as
   `not-applicable` and continue to feedback disposition without checking or
   polling review status.
5. Only when `codex_review_requirement=required-on-current-pull-request-head` and the matrix permits it,
   immediately re-read the PR head and base, recompute the merge base, and
   verify all three values still equal the checked revision and the ledger has
   no request object for that revision. Then post exactly one top-level PR
   comment. The official trigger is exactly `@codex review`; name the current
   head, base ref, and merge-base SHA and add a short focus only when useful. Record the request
   object, head, base ref, and merge-base SHA before any other action.
6. When `codex_review_requirement=required-on-current-pull-request-head`, run bounded GitStack
   `reviews wait` against the same revision using the Codex Review
   Wait Budget contract above. Reuse the request across `acknowledged`,
   `pending`, and timeouts; never post another request merely because the wait
   returned without a terminal result. At a final extended timeout, preserve
   the request and record troubleshooting evidence: Code review enabled for the
   repository, Codex cloud configured for the repository, exact trigger used,
   request object, current head, base ref, and merge-base SHA. Classify it as
   `monitoring-required` while
   it remains pollable, not as blocked. For `skip`, record this step as
   `not-applicable` and do not wait.
7. Evaluate the feedback required by the resolved policy: all current-revision Codex
   feedback for the required path, or only already-known actionable Codex
   feedback for the explicit-skip path. Fix accepted actionable findings, rerun the relevant tests,
   `$autoreview`, CI, and review-thread checks, then push the update. For
   the required path, run the request matrix for the new revision when the head,
   base ref, or merge base materially changed; for the explicit-skip path,
   revalidate the new revision without requesting review.
8. For findings judged non-actionable, not applicable, or intentionally
   deferred, post a PR discussion update with the disposition, evidence, and
   validation so the discussion is not left silent. Merge-ready Feature Spec-backed
   delivery permission covers this disposition mutation for both review paths;
   otherwise require separate comment permission or record the
   disposition only in the ledger and keep external comment mutation pending.
   If Codex reports no
   findings, or every finding is fully addressed by commits plus validation,
   record `no-update-needed` in the ledger instead of posting a redundant
   comment.
9. Promote the PR only after the policy-specific path is resolved on the exact
   current revision. For the required path, require a verified terminal current-revision
   Codex result, fully dispositioned feedback, and no unresolved actionable
   findings. For the skip path, require the current scoped skip evidence and
   disposition of already-known feedback. In both paths, require the
   closeout-qualified head, affected validation, and current CI to pass before
   running `gh pr ready <pr>` or an equivalent authorized action. Record the
   non-draft state, re-read the head, base, merge base, body, and any checks
   triggered by the ready transition, and return to the matching review or CI cycle if any
   evidence becomes stale or fails. Never mark a draft PR ready while required
   review is pending, findings remain unresolved, fixes are unpushed, or required
   checks are not current.

Use this closeout state order for merge-ready PR work:

1. `draft-pr-published`
2. `codex-review-policy-resolved` (required or explicitly skipped)
3. `current-revision-review-preflight` (required path) or `not-applicable` (skip path)
4. `codex-review-requested-or-reused` (required path) or `not-applicable` (skip path)
5. `current-revision-terminal-result-received` (required path) or `not-applicable` (skip path)
6. `known-review-feedback-dispositioned` (required feedback, already-known skipped feedback, or `not-applicable`)
7. `fixes-validated-and-pushed`
8. `post-fix-ci-current`
9. `closeout-revision-current` (reviewed head/base/merge-base for the required path; fully validated current revision for the skip path)
10. `ready-for-review`
11. `post-ready-revision-and-ci-current`
12. `parent-spec-closeout-resolved` (`armed`, `deferred-to-default-branch`, or `not-applicable`)
13. `post-closeout-revision-current` (`pass` for `armed`; otherwise `not-applicable` with reason)
14. `parent-closeout-watch-established` (`root-monitoring`, `owner-handoff`, `automation-handoff`, or `not-applicable`)
15. `merge-ready-report`

Do not final-answer from an intermediate state as complete, released, or
merge-ready. Keep the ledger active, `ready-next`, or blocked while review is
only requested, accepted findings are unresolved, a review fix is dirty in any
publication checkout, a fix is committed but unpushed, checks are pending for
the pushed fix, a policy-required fresh current-revision Codex result is pending
after a material diff change, or known PR review threads remain unresolved
without an explicit disposition. Poll an existing current-revision request instead
of posting again only when `codex_review_requirement=required-on-current-pull-request-head`.

For `codex_review_requirement=required-on-current-pull-request-head`, this gate passes only when the PR is
non-draft, a verified terminal Codex result exists for the current PR head,
base ref, and merge-base SHA,
actionable feedback is fixed or explicitly dispositioned, and the PR discussion
was updated or explicitly marked `no-update-needed`. For
`codex_review_requirement=explicitly-skipped-by-authorized-user`, it passes when the PR is non-draft, scoped owner
evidence is recorded, no request/wait remains actionable, and any already-known
actionable feedback is fixed or explicitly dispositioned. In both paths, no
required check may block human merge. Neither path authorizes merging the PR.

After this gate passes, resolve parent Feature Spec closeout before the merge-ready
report. Arm it only after all Feature Spec closeout proof is satisfied. A final feature
or integration PR that completes the whole Feature Spec and
targets the repository's current default branch must add the parent Feature Spec closing
keyword. Verify the PR body now closes every satisfied generated issue plus the
parent Feature Spec, record the updated body URL or fingerprint, and leave the Feature Spec open
until GitHub processes the closing keyword on merge. Use
`Closes #<spec-number>` in the same repository. Across repositories, use
`Closes owner/repo#<spec-number>` only when that closeout path is intended and
supported; otherwise record `blocked` or `needs-owner`. If the PR targets a
non-default branch, leave the keyword absent, record
`deferred-to-default-branch`, and select or create a linked later default-branch
PR as the parent closeout vehicle; do not record `armed` for the
non-default-branch PR. The current PR may report merge-ready after its own gates
pass, but keep the later closeout vehicle in `ready-next` or `active` and do not
mark the whole Feature Spec or ledger complete until that vehicle reaches `armed`. If any Feature Spec scope,
dependency, integration proof, or required domain closeout remains, also leave
the parent keyword absent and record `pending-closeout`; use `blocked` only when
an external condition prevents the next safe action. For partial PRs, ad hoc
PRs, local-tracker PRs, and workstreams without a parent GitHub Feature Spec, record
parent closeout as `not-applicable` and continue.

The generic non-default-base completion rule does not make an
`upstream-merge-ready-head` downstream PR merge-ready while its upstream is
unmerged. That PR remains draft and nonterminal until the upstream merges and
the downstream task reconciles it onto the default branch. Never add a closing
keyword for the upstream Feature Spec or PR to the downstream PR, never treat
the downstream merge as an indirect substitute for merging the upstream PR,
and never transfer upstream PR ownership to the downstream task.

Immediately before the closeout executor updates the PR body, re-read the PR
head and base, recompute the merge base, and require all three to equal the
closeout-qualified revision: the reviewed revision for the required path or the
fully validated current revision for the skip path. Also re-read the current
default branch and require the PR base to match it. Re-read the head, current
default branch, PR base, merge base, and current PR body after the body update
and immediately before the merge-ready report. Require the live body or its
fingerprint to match the recorded closeout evidence and contain exactly the
intended parent closer. If the default branch or PR base no longer matches,
disarm the keyword and record `deferred-to-default-branch` until a linked
default-branch closeout vehicle passes the gates. Otherwise, if the head or
merge base differs, do not add the parent keyword, or remove/replace an
already-added parent closing keyword with a non-closing reference, set
`parent_spec_closeout=pending-review` and return to current-revision review preflight
for the required path; for the skip path, set
`parent_spec_closeout=pending-closeout`, rerun the
affected validation and current CI for the new revision, and do not request
review. If only the body differs, set
`parent_spec_closeout=pending-closeout`, reconcile the live body without
overwriting concurrent edits, and repeat the post-update checks. Any relevant
change after `armed` invalidates that state and requires the matching
disarm-and-review or disarm-and-revalidate cycle, body reconciliation, or
closeout-vehicle cycle.

`armed` is not terminal parent closure while the PR remains open. Before
releasing the active root, establish exactly one parent closeout watch:

- `root-monitoring`: use only when
  `pull_request_merge_permission=granted-for-named-pull-request` and the root is the designated
  merger. Keep the root claim active through the root-controlled merge and
  actual Feature Spec closure check. Immediately before merge, re-read the PR
  head, base, merge base, current default branch, and live body fingerprint; on
  any mismatch disarm the
  parent closer and stop the merge for the matching review/revalidation or
  closeout cycle;
- `owner-handoff`: required when `pull_request_merge_permission=not-granted` or another actor will
  merge. Move the unmerged parent closeout to `needs-owner`, keep the ledger
  `paused`, and record an owner-visible handoff that requires rechecking the PR
  head, base, merge base, current default branch, and body fingerprint immediately before
  merge; on any mismatch the owner must not merge and must return the work to
  the orchestrator for policy-specific disarm and review/revalidation;
- `automation-handoff`: use only when the matching scoped row is
  `scheduled_automation_change_permission=granted-by-authorized-user` for a real event-driven
  monitor that can observe head, base/merge-base/default-branch, and PR-body
  mutations before merge, block the merge or disarm the closer on mismatch, and
  verify post-merge issue state. Record its id, event triggers, last successful
  check, and identical mismatch/disarm behavior; or
- `not-applicable`: only when parent closeout itself is not applicable.

The durable watch packet must name the PR, parent Feature Spec, resolved review
policy, closeout-qualified head and merge-base SHAs, base/default branch,
PR-body evidence, mutation triggers, and post-merge
issue-state check. A final report alone is owner-visible but is not durable
handoff evidence unless the same packet is persisted in the ledger. Do not set
the ledger `complete` while the parent is merely `armed` or
`deferred-to-default-branch`; a released root with owner or automation handoff
leaves the ledger `paused`, not complete.

After merge, verify that the merged head/base and closing keyword still match
the armed evidence and that GitHub actually closed the parent Feature Spec. Only then set
the watch to `complete` and parent closeout to `closed`. If the PR merged but the issue
remains open, record `needs-owner`; direct closure still requires
`direct-issue-updates-explicitly-authorized`.
