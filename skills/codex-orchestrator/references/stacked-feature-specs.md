# Stacked Feature Spec Flow

Load this reference only after `spec-backed-delivery.md` when the registered
dependency graph contains an explicit `upstream-merge-ready-head` edge. This is
a narrow same-repository acceleration path. It does not replace ordinary
dependency completion, create a user-selectable stacking option, or authorize
merge, force-push, PR closeout, or source mutation.

## Eligibility

Call the upstream Spec and PR `A` and the downstream Spec and PR `B`. The root
may dispatch B from A's unmerged head only when every condition is proven:

- A and B each affect the same exact single Git repository and neither Spec
  spans another repository. `multi-repository-workspace` work is ineligible.
- The source graph explicitly classifies B's edge to A as
  `upstream-merge-ready-head`. Generic `depends-on`, issue order, shared paths,
  or owner intent to continue autonomously is insufficient.
- A is B's only unmerged upstream. The active stack contains exactly A and B;
  depth is at most two. While A remains unmerged, B cannot become the unmerged
  base for a third Spec.
- Both Specs resolve
  `change_delivery_target=pull-request-ready-for-merge-but-not-merged` with
  current publication authority for their own distinct branches and PRs.
- A has its own non-draft PR targeting the repository's current default branch.
  Its branch and worktree are clean, local validation and current CI pass, all
  actionable feedback is dispositioned, and a terminal Codex review is verified
  for A's exact current head SHA, base ref, and merge-base SHA. A review skip is
  not sufficient for this flow.
- A is independently merge-ready and its parent closeout is valid for its own
  Spec. It does not depend on B for acceptance, integration, or closure.
- Managed-worktree execution is available. The serial caller-checkout strategy
  cannot use this flow.
- `visible_app_task_permission=granted-by-authorized-user` selected mandatory
  one-task-per-Spec execution, so B can retain one visible task through draft,
  upstream merge, reconciliation, final review, and ready transition.
- Dispatching B stays within the run-wide ceiling of three nonterminal Feature
  Spec executions.

Record the cross-Spec edge and its runtime evidence in the ledger's Feature
Spec Dependency Rows. Keep generated-issue `dependency_ids` and
`blocked_issue_ids` limited to intra-Spec issue IDs; never project A's Feature
Spec ref into those fields. The edge evidence names A's PR, default base,
reviewed head SHA, merge-base SHA, review result, CI, and merge-ready proof.
These are source-graph and runtime evidence, not new options.

If any condition is absent or contradictory, keep B dependency-blocked. Do not
silently fall back to a cumulative default-branch PR or a deeper stack.

## Ownership

A and B remain separate Feature Spec executions:

- A's task keeps its branch, PR, review evidence, and parent closing-keyword
  preparation through merge-ready. The root retains the merge decision, any
  authorized merge/watch, and post-merge source proof.
- B gets its own visible task, Goal, managed worktree, branch, commits, draft PR,
  validation, CI, final review, fixes, and ready transition.
- The root chooses the stack, creates and monitors B's task, reconciles evidence,
  and may merge a named PR only through its existing exact
  `pull_request_merge_permission` and confirmation rows, including A during
  this flow. It never implements, rebases, retargets, validates, reviews, fixes,
  pushes, or marks B ready.
- B's task never merges, closes, replaces, or supersedes A. B's PR may reference
  A non-closingly, but it must not carry A's closing keywords or claim that
  merging B completes A.

No PR, task, branch, worktree, review result, or closeout vehicle is shared
between the two Specs.

## Dispatch B From A

After the eligibility proof is current:

1. Freeze the stack start at A's exact reviewed head SHA and current default-base
   identity. Re-read A immediately before creating B; a changed head, base,
   review state, CI state, or merge-readiness state invalidates the start.
2. Create B's visible task with its own managed worktree and distinct target
   branch starting from that exact A reviewed SHA. Do not reuse A's worktree or
   let B commit on A's branch.
3. Require B's task-owned Goal before work. Assign only B's scope and its already
   resolved delivery actions.
4. B's task implements and validates B, runs required local `$autoreview`,
   commits and publishes only B's branch, and opens B as a draft PR whose base is
   A's branch. Verify that the draft diff contains B's intended delta relative
   to A and no unrelated work.
5. Run the applicable draft-stage CI and integration checks against A's reviewed
   head. Keep B draft. Do not request the canonical final Codex PR review, add a
   parent closing keyword, mark B ready, or report B merge-ready while its base
   is A's branch. An automatic or unsolicited review at this stage is
   informational and cannot satisfy B's final current-revision review gate.

B may remain draft and monitored while A awaits independent merge. This is an
actionable dependency wait, not completion and not permission to merge B first.

## Upstream Merge And Downstream Promotion

The next transition begins only after live proof shows that A's own PR merged
independently into the expected default branch. A's root-owned post-merge source
closeout continues independently and never transfers to B, but it does not
delay B's branch reconciliation once the merge itself is proven. If the root
lacks exact merge authority, it preserves the owner handoff and waits; B's task
does not merge A on the root's behalf.

After A merges, the same B task performs all downstream work:

1. Fetch the current default branch and B's remote branch. Record A's reviewed
   pre-merge head, A's merge result, the current default head, B's local head,
   B's live remote head, and B's live PR base. Keep B draft; if GitHub already
   retargeted it because A's branch disappeared, record that state but do not
   enter final review yet.
2. Reconcile B's branch locally onto the current default head before changing
   the PR base yourself. Use A's recorded reviewed
   SHA as the old stack boundary when replaying only B commits. Prefer a
   non-rewriting reconciliation when ancestry and the resulting diff are
   already correct; otherwise use the guarded lease flow below.
3. Publish the reconciled B branch under its existing authority, then retarget
   the still-draft PR from A's branch to the current default branch when that
   did not already happen. Re-read the live head, base, and diff and prove the
   PR contains only B's intended downstream delta.
4. Rerun B's affected validation, integration proof, `$autoreview`, and current
   CI on the reconciled head and default base.
5. Only now enter the canonical Codex PR review flow for B. Request or reuse the
   review for B's final head SHA, base ref, and merge-base SHA; disposition
   findings, apply fixes in B's task, reconcile again when a fix changes the
   revision, and require current CI.
6. Add only B's authorized issue and parent closing keywords, verify B's head,
   default base, diff, body, and checks, then mark B ready and report its own
   merge-ready target.

If the default head advances during reconciliation or review, re-read the base
and live diff. Repeat affected validation, CI, and review whenever that movement
changes B's effective diff, ancestry, or integration proof. A head-only review
record never excuses a materially changed base diff.

## Guarded History Rewrite

History rewriting is exceptional and task-owned. B's task may use
`--force-with-lease` only when all of these conditions hold:

- the branch is B's exact task-owned target branch and no other Spec or task
  owns it;
- B already has the publication authority required to push that branch;
  that authority was resolved before stacking and is not created by this flow;
- the task fetched the remote immediately before publishing the rewritten
  history, proved it had not changed since reconciliation began, and recorded
  the exact live remote branch object id as the lease expectation;
- the push uses an explicit B refspec and explicit
  `--force-with-lease=<remote-branch>:<expected-object-id>`; and
- B's draft PR still names that branch as its head.

Never use plain `--force`, an implicit lease, a stale observation, or a lease on
A's branch. The root never performs the rewrite. A lease rejection, remote-head
mismatch, ambiguous ownership, missing publication authority, reconciliation
conflict outside B's scope, or failed post-push verification blocks B. Preserve
the draft PR and current evidence; do not retry by weakening the lease.

## Invalidation And Exit

Before A merges, any A head change invalidates B's recorded stack start. Pause B
until A again reaches a clean default-base merge-ready state with a terminal
review on its new head, then let B's task reconcile from the old reviewed
boundary to the new one under the same guarded rules. If A closes unmerged,
retargets away from default, loses required proof, or gains another unmerged
dependency, block B and return to ordinary dependency routing.

The stack path exits only when A is independently merged and closed through its
own evidence and B is independently merge-ready against the current default
branch through its own final review and gates. Merging B never serves as A's
merge, PR closure, issue closure, or supersession proof.
