# Feature Spec-Backed Delivery

Use this reference when a registered workstream comes from a Feature Spec,
generated implementation issue, linked partial Feature Spec, or
`## Orchestrator Handoff`. Load `options.md` first.

## Applicability And Hard Cut

Feature Spec-backed work uses the source contract for scope, dependencies,
acceptance, delivery target, and issue lifecycle. The root still resolves every
permission and worker action for the exact workstream.

Ad hoc sources without a Feature Spec default to:

```text
change_delivery_target=validated-changes-left-uncommitted
change_delivery_permission=not-required-for-uncommitted-changes
issue_update_permission=no-issue-changes
codex_review_requirement=not-needed-for-selected-delivery-target
pull_request_count_strategy=no-pull-request
issue_completion_method=no-issue-completion
```

Retired delivery, PR-closeout, authority, topology, and integration fields are
invalid. Do not normalize them at runtime. Reject stale Feature Specs or issues
before registration.

If `source_spec_ref` is `draft-spec:<...>`, allow real dispatch only with
`temporary_source_execution_permission=granted-by-authorized-user`. That
permission never grants commit, push, PR, issue, or merge actions.

## Required Handoff

A generated issue's `## Orchestrator Handoff` must contain:

- `source_spec_ref`, `feature_slug`, affected repositories or product scope;
- `repository_layout`, `issue_repository_layout`, `workspace_context`, and
  workspace parent/child refs when applicable;
- `delivery_decision_origin`, `change_delivery_target`,
  `change_delivery_permission`, `delivery_decision_origin_evidence`, and
  `change_delivery_permission_evidence`;
- `target_branch_name`, `pull_request_count_strategy`, and
  `codex_review_requirement`;
- `issue_update_permission` and `issue_update_permission_evidence` as an
  independently scoped evidence chain;
- scope, start rule, parallelization, dependencies, validation, and proof;
- `issue_completion_method`; and
- `domain_closeout` plus exact decision/evidence data when implementation
  closeout is required, including `domain_operation=implementation-closeout`
  when Project Memory capture owns the final integrated decision update.

`repository_integration_method` and `pr_closeout` are not handoff fields.
Derive their former behavior from `change_delivery_target`,
`pull_request_count_strategy`, repository refs, and the selected issue
completion method.

The handoff never grants worker actions. It transfers only current source
contract evidence. The root validates that evidence, resolves the matching
workstream rows, and selects an exact `worker_allowed_actions` list.

## Permission Transfer

For a Feature Spec or implementation-issue delivery grant, preserve these
evidence tokens:

```text
permission-source-ref=<feature-spec-default:feature_slug|authorized-user:instruction-ref>
scope-ref=<run or issue scope>
target-ref=<feature or source ref>
target-branch=<target_branch_name>
```

Feature-level inherited issue rows use
`delivery_decision_origin=inherited-from-feature-spec`, preserve the Feature
Spec permission source, target, and branch, change only `scope-ref` to the
issue, and record the run as `permission-transfer-ref=run`. The canonical
default PR target uses
`permission-source-ref=feature-spec-default:<feature_slug>`; an authorized
issue override uses `overridden-by-implementation-issue` plus
`permission-source-ref=authorized-user:<instruction-ref>` and its own exact
evidence.

When registering the issue as a workstream, the root may change only the scope
projection to `workstream:<id>` and record the exact issue in
`delivery_permission_source_issue_ref`. Preserve permission source, target,
branch, and original evidence unchanged.

Issue-update permission has a separate evidence chain and transfer row:
`issue_update_permission_source_issue_ref`. A delivery grant never creates or
widens issue-update permission. The canonical PR-closing-keyword permission may
preserve the same Feature Spec default ref; direct issue updates always require
an independent `authorized-user:<instruction-ref>` permission source.

Any missing, stale, or contradictory transfer evidence stops as `needs-owner`.

## Authority Model

Resolve these concerns separately:

1. `change_delivery_target`: observable stopping point.
2. `change_delivery_permission`: whether the target's Git or GitHub mutations
   are allowed.
3. `delivery_allowed_actions`: derived actions needed to reach that target.
4. `worker_allowed_actions`: exact subset a worker may execute.
5. `issue_update_permission`: independently allowed issue lifecycle mutation.
6. `codex_review_requirement`: current-head review behavior for the merge-ready
   PR target.
7. `pull_request_merge_permission`: whether the named PR may be merged.
8. `pull_request_merge_confirmation`: whether another checkpoint remains after
   all merge gates pass.

Do not collapse these into a boolean or infer one from another. In particular,
`pull-request-ready-for-merge-but-not-merged` never grants merge.

## Canonical Target Resolution

| `change_delivery_target` | `change_delivery_permission` | PR count | Review requirement | Required terminal state |
| --- | --- | --- | --- | --- |
| `validated-changes-left-uncommitted` | `not-required-for-uncommitted-changes` | `no-pull-request` | `not-needed-for-selected-delivery-target` | Local acceptance and validation pass; no commit, push, or PR. |
| `local-commit-created-without-pushing` | `granted-for-selected-target` | `no-pull-request` | `not-needed-for-selected-delivery-target` | Validated commit exists locally on the named branch; no push. |
| `changes-pushed-to-target-branch-without-pull-request` | `granted-for-selected-target` | `no-pull-request` | `not-needed-for-selected-delivery-target` | Named remote branch contains the validated commit; no PR exists. |
| `validated-draft-pull-request-published` | `granted-for-selected-target` | One total or one per repository | `not-needed-for-selected-delivery-target` | Validated draft PR exists; do not mark ready or request review. |
| `pull-request-ready-for-merge-but-not-merged` | `granted-for-selected-target` | One total or one per repository | Required on current head or explicitly skipped | PR is non-draft and all selected gates pass; do not merge without separate permission. |

For every target except uncommitted changes, a missing delivery grant yields
`delivery_gate_status=blocked`; it is not another permission value.

## Target-Specific Rules

### Validated Changes Left Uncommitted

- Use only for ad hoc work or an exact explicit source contract.
- The target branch and PR ref are `not-applicable`.
- Workers may receive `edit-files` and `run-validation`, never commit, push, or
  PR actions.

### Local Commit Created Without Pushing

- Require exact branch and permission evidence.
- Workers require `create-local-commit`; do not grant `push-target-branch`.
- For local Markdown trackers, record commit proof and then use
  `move-local-issue-to-done-after-proof`.
- A local-only commit cannot close a hosted issue; use
  `issue_completion_method=no-issue-completion` there.

### Changes Pushed Without A Pull Request

- Require exact branch and permission evidence.
- Workers need the exact subset of `edit-files`, `run-validation`,
  `create-local-commit`, and `push-target-branch` required by the assignment.
- For hosted final-commit closure, require
  `issue_update_permission=direct-issue-updates-explicitly-authorized` and
  `issue_completion_method=final-commit-closing-keyword` with independently
  scoped evidence. Branch publication alone is insufficient.
- For local Markdown trackers, use the local done move after remote-branch
  proof instead of a hosted closing keyword.

### Validated Draft Pull Request Published

- Open or update the draft PR only after local validation and publication
  safety pass.
- Do not mark it ready, request Codex review, claim merge readiness, or arm
  parent Feature Spec closeout.
- Record review and parent-closeout gates as `not-applicable` with this target
  as evidence.

### Pull Request Ready For Merge But Not Merged

- Open as draft initially, complete validation and publication safety, then
  mark ready.
- Apply `codex_review_requirement` to the current PR head.
- Load `gates.md`; it alone routes current-head Codex review and parent Feature
  Spec closeout through `codex-review-closeout.md`.
- The Feature Spec source contract may grant commit, push, PR publication,
  mark-ready, review request/poll, required discussion disposition, and parent
  closing-keyword update after gates. It never grants merge.
- A review skip bypasses only request and wait. All other validation,
  discussion, CI, integration, and parent-closeout gates remain.

An existing draft PR may advance to the merge-ready target only after a new
canonical target and permission tuple is resolved. Never infer the transition
from the PR's existence.

## PR Count And Repository Layout

- One affected repository uses `one-pull-request-total`.
- Multiple affected repositories use `one-pull-request-per-repository`, the
  same exact branch name, and one PR per repository.
- `multi-repository-workspace` loads `multi-repo-workspace.md` before dispatch
  and preserves child repository layout in `issue_repository_layout`.
- Real PR refs replace placeholders before completion. Expected refs are not
  proof of publication.

## Issue Completion

- GitHub PR targets use `feature-pull-request-closing-keyword` for one final
  feature PR or `repository-pull-request-closing-keyword` for per-repository
  PRs.
- The parent Feature Spec closing keyword is root-owned and may be added only
  after the applicable whole-feature gates pass.
- GitHub push-without-PR delivery uses `final-commit-closing-keyword` only with
  its independent issue-update permission.
- Local Markdown issues use `move-local-issue-to-done-after-proof` after target,
  validation, and integration proof.
- Ad hoc work without a tracked issue uses `no-issue-completion`.

Direct comments, labels, immediate hosted closure, merge, release, and deploy
remain independently permissioned root actions.

## Merge Boundary

Default to:

```text
pull_request_merge_permission=not-granted
pull_request_merge_confirmation=ask-authorized-user-after-checks
```

Use `granted-for-named-pull-request` only when exact evidence names the PR or PR
set. Use `merge-automatically-after-checks` only when the same instruction
waives another checkpoint. Otherwise stop at the selected delivery target and
return `needs-owner` for merge.

## Required Resolution Steps

1. Read the Feature Spec or issue directly. Reject retired field names or
   values before registration.
2. Verify the required handoff fields and row fingerprint.
3. Verify repository layout and workspace child refs; load
   `multi-repo-workspace.md` when applicable.
4. Resolve the exact delivery target, permission, origin, branch, PR count,
   review requirement, issue-update permission, and completion method.
5. Verify transfer evidence and record source-issue refs.
6. Derive `delivery_allowed_actions` and `delivery_gate_status`.
7. Record worker location, exact worker actions, branch expectation,
   publication checkout, starting-checkout handling, parent-closeout state,
   merge fields, and proof targets in the ledger.
8. Build waves from dependencies, repository boundaries, and shared integration
   risk. Delivery targets do not decide parallelism.
9. Load `gates.md` before any owner-ready, issue-closed, release-ready, or final
   status.

## Closeout Rules

Feature Spec-backed implementation is incomplete whenever its selected target,
integration proof, source closeout, or domain closeout remains unfinished.

Before final status require:

- root-verifiable acceptance and validation proof;
- the exact delivery target's live proof;
- real branch and PR refs where applicable;
- required issue and parent Feature Spec closeout proof;
- required `$project-memory domain-memory` closeout; and
- no authorized `ready-next` delivery or closeout action.

`validated-draft-pull-request-published` is terminal only for that exact target.
It records ready-for-review, Codex review, merge-ready, merge, and parent
closeout as not applicable.

## Worker Boundary

The root owns target selection, delivery permission, branch and PR strategy,
review disposition, source and parent closeout, merge decisions, and final
status. Workers execute only the canonical actions explicitly listed in their
prompt.

Workers never infer permission from the handoff, choose another branch, create
independent feature PRs, add/remove the parent closing keyword, merge, close
issues directly, or mutate the ledger.

## Ad Hoc Sources

Do not block ad hoc implementation merely because Feature Spec fields are
absent. Use the safe uncommitted target tuple at the top of this reference.
Commit, push, PR, issue changes, merge, release, and deployment require a new
exact target plus their independently resolved permission rows.
