# Mandatory Codex Review And Closeout

## Ownership

The visible Feature Spec task owns every delivery's review request, wait,
feedback fixes, CI, tracker-closeout preparation, ready-for-review transition,
and terminal proof. The root issues immutable timing assignments, reconciles
typed evidence, and independently verifies closeout; it never takes worker work
back as a fallback.

## Delivery-Revision Review

Request exactly one Codex review for each delivery's current exact repository,
PR number and URL, head SHA, base ref, and merge-base SHA tuple. Establish the
tuple through `revision-observed`, bind its lifecycle through
`delivery-observed`, and apply the result through delivery-keyed
`review-observed`. Reuse a result only when the entire tuple matches and every
finding is dispositioned. The review request is mandatory and has no skip
value. Only an exact request that remains pending through its fixed deadline may
use the explicit timeout-accepted outcome below.

The revision observation must bind canonical GitHub `owner/repository`, the PR
number, and the exact URL
`https://github.com/<owner/repository>/pull/<number>`. The lifecycle observation
must repeat that identity. A malformed, non-GitHub, or mismatched URL blocks
before review timing begins.

Actionable findings return the task to fix, focused validation, `$autoreview`,
push, and a new current-revision review. A head, base, merge base, PR identity,
material diff, repository-rule, tracker delivery, evidence-target, or relevant
documentation change invalidates affected delivery-revision gates and the
complete task-revision-set gates. Resolve review threads only after fix proof.

Before terminal sealing, require every delivery PR lifecycle `OPEN`, exact
non-draft identity, conflict-free GitHub mergeability, required base freshness,
approvals, and merge-queue eligibility. Unknown or pending state blocks. Never
enqueue or merge.

When a nonempty accepted knowledge delta exists, a later material code,
evidence, target, or documentation change invalidates captured domain-closeout
evidence whenever it can affect support or destinations. Rerun Project Memory
closeout and persist fresh delta, destination, documentation-diff, and complete
implementation revision-set evidence.

## Typed Review State And Idempotency

The run state is the sole request and timing owner. Keep one review entity keyed
by `task_key`, `delivery_key`, and the exact delivery `revision_key`. Store
the exact PR URL, request, provider/result/disposition, bounded observation fingerprints,
`wait_started_at`, `wait_deadline`, `wait_invoked_at`, `provider_timeout`,
and the optional durable timeout-warning reference.

Before request, resume, or terminal acceptance, recompute the exact tuple and
run the canonical GitStack review check. Reuse a current result, wait on a
current acknowledged request, and create a request only for proven
not-requested or stale revision. Apply `review-wait-started` before polling so
recovery cannot duplicate mutation. API, authentication, or configuration
uncertainty never authorizes another request.

At the GitStack boundary, pass only the exact PR and canonical
`review_operation`; add GitStack-owned `mutation_mode=apply` only for an
authorized mutation. Do not pass App permission, Feature Spec, phase, or fixed
actions, and never expose the translation as a user option.

## One Fixed Wait Deadline

Each delivery revision owns one 45-minute total active-wait deadline. The worker
reports tuple/request evidence; the root atomically records
`review-wait-started` with `wait_started_at` and the helper derives
`wait_deadline=wait_started_at+45m`, then returns the immutable assignment.

Before launch, set `wait_invoked_at=now`, require it to be at or after the
recorded start and not later than the current clock, and compute
`provider_timeout=max(0,floor(wait_deadline-wait_invoked_at))`. The root must persist
`review-wait-invoked` before the worker calls GitStack. That event is the single
launch authority; once recorded, recovery never starts another waiter. For a
positive timeout use:

```text
--timeout <provider_timeout>s --interval 10s --max-interval 30s
```

The canonical invocation is
`--timeout <provider_timeout>s --interval 10s --max-interval 30s`.

At zero, perform one immediate no-wait check. Never use a provider default,
hardcode `15m`, start before `wait_started_at`, segment, restart, wrap, or extend
the unchanged deadline.

The one provider call ends as `clean`, `findings`, `failed`, or `waiting`.
Persist exactly one `review-observed` event for the exact request and revision:

- `clean` pairs with `accepted` and no warning.
- `findings` pairs with `fix-required` and returns to the fix loop.
- `failed` pairs with `blocked`; request, access, authentication, configuration,
  or provider failure is never a timeout acceptance.
- `waiting` may pair with `timeout-accepted` only when observed at or after the
  immutable deadline and only after a persistent PR warning has been posted. The
  event must carry that exact PR's canonical GitHub issue-comment URL as
  `warning_ref`; unrelated URLs and free text are invalid. It must also carry
  the observed comment creation time as `warning_posted_at` and the SHA-256 of
  this exact UTF-8 body as `warning_fingerprint`:

```text
Implement Feature continued because Codex review remained pending for the full 45-minute wait.

Pull request: <exact pr_url>
Review request: <exact request_ref>
Revision: <exact revision_key>

This is not a clean review verdict. A later merge workflow must re-check this pull request for late Codex findings before merge.
```

The helper derives the expected body from stored review identity. The comment
timestamp must be at or after the immutable deadline and no later than the
observation. The warning reference may not reuse the review request reference.

The timeout result means only that the current revision proceeds without a returned
Codex verdict. It is not `clean`, does not waive `$autoreview`, CI, mergeability,
branch rules, approvals, base freshness, tracker closeout, or any other gate,
and cannot override a rule that still blocks the pull request. Surface the same
warning in the user-facing final report. Superseded revision warnings remain
history but are excluded from current status and terminal projections. A later merge workflow must re-check
the exact PR for late Codex findings before merge.

Never schedule another check, pause a Goal, arm an App heartbeat, start another
waiter, or change the original timing fields. Root and worker Goals remain
active through the remaining gates and complete only through their normal
terminal transitions. Recovery observes the already-launched waiter or records
its single final outcome; it never relaunches it.

## Tracker Closeout

Put each generated implementation issue's hosted closing keyword in its owning
delivery PR. After an implementation-eligible Feature Spec's whole-Spec gates
pass, put that Spec's closing keyword in its designated default-branch closeout
PR. The final integration partial may additionally arm an accepted hosted
parent/global Feature Spec after every partial gate passes. Use fully qualified
refs across repositories. Non-default-base PRs cannot be closeout vehicles
because their closing keywords cannot take effect.

For local Markdown, first finish substantive acceptance, integration proof,
and any knowledge closeout. Then perform only the predeclared local move in its
owning delivery. The typed move dirties tracker delivery state and invalidates
the old revision set. Commit and push it, observe the new head containing the
move, rerun final validation and `$autoreview`, convert drafts to
ready-for-review, then obtain current-revision review and CI before terminal
merge-ready state. Report closeout as prepared because the default branch sees
it only after later merge.

## Terminal Handoff Only

An in-flight fixed review wait retains the active claim and creates no handoff
or release. A timeout-accepted result continues normal closeout with its warning
evidence; it does not create a nonterminal handoff.

`terminal-handoff-recorded` is terminal-only and allowed only after
`task-terminal-sealed` and
`task-goal-completed`. It binds the unchanged terminal seal, next action, and
typed `external-merge-required` authority; the seal binds the exact delivery
revisions. After all task handoffs, the root independently verifies the
portfolio, completes its Goal, then releases and archives. A later GitHub
workflow owns merge and post-merge closure.
