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

Root-verifiable does not mean root-executed. When
`visible_app_task_permission=granted-by-authorized-user`, the assigned visible
Feature Spec task executes implementation, integration, validation,
publication, Codex-review request and polling, review/CI fixes, and every
pre-merge gate through ready. The root only monitors, steers drift, and
reconciles evidence; it never reruns those gates itself for that Spec.

## Gate Lenses And Stable Review Items

Use the narrowest review lens that matches the current phase:

- `source-readiness`: source scope, Feature Spec or issue readiness, dependencies, and
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
`result_checkout_path_guard`, `caller_checkout_guard`, `pr_diff_status`,
`ready_for_review_state`, and `post_push_verification` values.
Lower-kebab-case values are canonical. Retired structured values are invalid;
do not reinterpret them during gate evaluation.

### Authorization Gate

Confirm every requested worker action is present in `worker_allowed_actions`.
Stop for authorized-user approval before push, PR, merge, close, release, external
service mutation, destructive local changes, or broad scope changes.
`create-local-commit`, `push-target-branch`, and
`create-or-update-pull-request` are independent. No action implies another.

For Feature Spec-backed delivery,
`change_delivery_permission=granted-for-selected-target` satisfies
authorization only for `delivery_allowed_actions` derived from the exact
target. The worker still receives an explicit subset. Gates never reinterpret
restriction prose. `validated-draft-pull-request-published` makes downstream
ready/review/merge-ready gates `not-applicable`.
`pull-request-ready-for-merge-but-not-merged` defaults to
`codex_review_requirement=required-on-current-pull-request-head`; select an
explicit skip only from its scoped option row. Record the target, delivery
permission, allowed actions, gate status, and review requirement in the ledger.
This does not authorize merge, release, direct issue mutation, production
deploy, or unrelated GitHub cleanup.

### Merge Authorization Gate

Before an actual merge, require `pull_request_merge_permission=granted-for-named-pull-request`
for the named PR or PR set. `pull_request_merge_confirmation=ask-authorized-user-after-checks` requires a current
owner checkpoint after every other merge gate passes;
`pull_request_merge_confirmation=merge-automatically-after-checks` permits the root to merge without another
checkpoint only when that canonical scoped row and the matching merge-permission
row are valid for the named PR or PR set. Evidence text is recorded for audit
but is never reparsed inside this gate. Finish, complete, deliver, ship, close
out, and make merge-ready do not select either row.

Merge is root-owned. Workers cannot receive merge authority. Record the owner
instruction and timestamp, exact PR/head, mergeability, current CI, latest-head
review proof, unresolved-thread count, and merge result. When authority is
missing or ambiguous, stop at merge-ready under `needs-owner`; do not infer it
from delivery or issue-update permission.

### Publication Safety Gate

Before push, draft PR publication, or ready-for-review transition, evaluate
`publication-safety`. Record:

- `push_policy`: `no-push`, `explicit-refspec-only`, or `block-plain-push`.
- `branch_target_guard`: `default-branch-blocked`,
  `protected-branch-blocked`, or `verified-feature-branch`.
- `result_checkout_path_guard`: `worker-worktree`, `integration-worktree`,
  `serial-caller-checkout-branch`, or `blocked`.
- `caller_checkout_guard`: `preserved`, `policy-approved-switch`,
  `restored-after-terminal-task`, or `not-applicable`.
- `pr_diff_status`: `non-empty`, `empty`, or `not-checked`.
- `ready_for_review_state`: `draft`, `ready`, `not-checked`, or `not-applicable`.
- `post_push_verification`: `verified`, `failed`, or `not-applicable`.

Publication should use an explicit refspec, target the expected feature branch,
run from the recorded publication checkout, and verify the pushed branch or
draft PR state after push. When worker or integration worktrees are available,
the caller checkout should remain on its original branch; if the caller checkout
was switched, the gate must reference the scoped
`starting_checkout_branch_handling=branch-switch-authorized` row. If the PR diff is empty,
the publication checkout is not on the expected branch, or the target is the
default/protected branch without a
`changes-pushed-to-target-branch-without-pull-request` row whose scoped
evidence names that exact target, stop and record `blocked`.

In a Codex App session, `worker-worktree` or `integration-worktree` passes this
gate for a newly created checkout only when the ledger records its owning App
task id. A newly created or allocated raw Git worktree requires recorded
App-surface failure or unsuitability plus
`unmanaged_git_worktree_fallback_permission=granted-by-authorized-user`;
otherwise set `result_checkout_path_guard=blocked`. This additional guard does
not apply in CLI-only sessions or to an existing owner-supplied checkout.

For `implementation_checkout_strategy=serial-caller-checkout-branches`, set
`result_checkout_path_guard=serial-caller-checkout-branch` only when all of the
following are proven:

- exact authorized-user evidence selected no-worktree execution and the
  workstream has `starting_checkout_branch_handling=branch-switch-authorized`;
- the caller checkout was clean before preparation and its original branch,
  HEAD, and status fingerprint are recorded;
- the active branch equals this Spec's exact `target_branch_name`, differs from
  the original branch, matches the retained run-wide serial branch-assignment
  row, and the same repository/branch pair has never been assigned to another
  Feature Spec;
- the ledger has no other active Feature Spec task; and
- the task owns implementation through its complete delivery target.

After the task reaches that target, do not dispatch the next Spec or close the
portfolio until the feature branch is clean, the root has restored the original
branch, and its branch, HEAD, and status match the recorded baseline. Record
`caller_checkout_guard=restored-after-terminal-task` with Git evidence. A
dirty baseline, branch reuse, early branch switch, restoration mismatch, or
missing proof blocks the serial lane.

### Live Proof Gate

For user-facing behavior, require proof from the real app, CLI, API, service,
or rendered artifact before declaring the source item complete. Synthetic proof
is acceptable only when live proof is impossible, unsafe, or blocked by missing
credentials, setup, hardware, paid access, external service state, or explicit
owner deferral.

When live proof is blocked, record the exact blocker, the synthetic proof that
was collected, and the owner decision or follow-up needed. Do not land,
release, close, or mark complete on synthetic proof alone unless
`completion_evidence_policy=allow-simulated-evidence-by-authorized-user-exception` for that workstream or the source
item is moved to `deferred` with an owner-visible follow-up.

### Closure Gate

Before closing any source item or moving work to `completed`, verify that the
source acceptance criteria are satisfied by root-verifiable proof. If live proof
is feasible but blocked by credentials, setup, service access, or missing
hardware, do not treat the source item as fully complete unless the scoped row
is `completion_evidence_policy=allow-simulated-evidence-by-authorized-user-exception`.

For implementation issues that include `## Delivery`, verify that
closeout matches the recorded target and completion method, and verify that direct
dependencies or blocking relationships recorded in the issue are satisfied
before declaring closure. Close through the relevant PR body by default. Use
final-commit closure only for `issue_completion_method=final-commit-closing-keyword` with
the exact scoped authorization evidence. For local markdown sources, completion is
the configured move to `issues/done/` after validation and proof; do not treat a
commit alone as local issue closure.

For either Feature Spec-backed PR target, do not declare the workstream
`completed` while the expected PR remains uncreated. The merge-ready target
requires the conditional Codex review and parent-closeout gate below. The draft
target requires validation and the expected draft PR, then records downstream
review, merge-ready, and parent closeout as `not-applicable`. Direct issue
updates, merge, and release remain separately permissioned actions.

For local Markdown sources using
`pull-request-ready-for-merge-but-not-merged`, do not move the issue to
`issues/done/` until local validation, real PR proof, required CI or integration
proof, the resolved review policy, and any required review disposition are
recorded. If any proof is
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

### Codex PR Review And Parent Closeout Gate

For
`change_delivery_target=pull-request-ready-for-merge-but-not-merged`, load
`codex-review-closeout.md` and apply its complete current-head review and
parent-closeout algorithm. In mandatory visible Feature Spec task mode, the
assigned task is the algorithm's execution and polling owner; the root must
not call the review check/wait workflow for it. For every other target, do not load that reference:
record this gate `not-applicable` with reason
`selected-delivery-target-does-not-require-merge-ready-review`. Missing or contradictory values
remain a routing error rather than an inapplicable gate. Do not reproduce or
reinterpret the conditional algorithm in another runtime document.

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

For multi-repository PR delivery, also require the real repository PR links or
equivalent integration proof promised by the Feature Spec or issue before declaring the
cross-repo issue closed, merge-ready, or complete.

### Credential And Access Gate

If work requires credentials, paid service access, private repo permission, or
local secrets, stop and report the minimum missing access. Do not ask workers to
work around protected systems with unsafe local substitutes.
