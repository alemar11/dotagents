# PRD-Backed Delivery Reference

Use this reference when an implementation workstream is tied to a PRD issue,
generated implementation issues, or a user request such as "implement PRD #46".
It separates PRD delivery contracts from ad hoc implementation requests.

## When This Applies

Apply this reference when any of these are true:

- the user asks to implement a PRD issue or a set of generated implementation
  issues;
- an issue body contains `source_prd_ref: #<number>` or a linked PRD path;
- a workspace PRD or generated issue links sibling repo-scoped partial PRDs for
  the same feature;
- an issue body contains `## Orchestrator Handoff`;
- the source item was produced by `$plan-feature`;
- the source item has a `## Delivery`, `Delivery Mode`, `Completion`, or
  closeout section that defines branch, PR, or issue-closing behavior.

If none of those are true, treat the source as ad hoc or legacy work. Default
implementation to local code/docs edits plus validation, without requiring a
delivery mode, branch, PR, parallelization, handoff, or source-closeout field.
Project that default into the ledger as runtime delivery `local-only`,
publication `none`, issue mutation `none`, and closeout through local acceptance
criteria plus validation. Use `worker.md` for worker authorization, and require
explicit owner authorization before any publication or external mutation.

If `source_prd_ref` is a draft ref such as `draft-prd:<...>`, treat it as a dry-run
planning reference, not durable implementation authority. The root may inspect
the graph, but real worker dispatch, commit, push, PR creation, issue closeout,
or tracker mutation requires a hosted PRD number, a local PRD path, or the
scoped canonical row `temporary_source_execution=owner-approved`. That row
does not replace separate publication and issue-mutation authority.

For generated implementation issues, `## Orchestrator Handoff` is the
canonical issue-level dispatch contract. It must restate the source PRD,
feature slug, `delivery_mode`, `delivery_source`,
`delivery_source_evidence`, `issue_mutation_authority`,
`issue_mutation_authority_evidence`, `branch_name`, `pr_shape`, `pr_closeout` when applicable,
affected repos or product scope, scope, start rule, dependencies, validation,
domain closeout, `closeout_mode`, and `integration_mode`. `domain_closeout` is
`not-applicable` unless the issue has a
`## Domain Knowledge Closeout` section; when it does, preserve the exact
`implementation-closeout` operation, decisions, target surfaces, and evidence.
The handoff is not an
authorization grant: worker authorization, publication authority, and issue
mutation authority are still resolved by the root orchestrator from the owner
request, linked PRD, issue body, gate state, and current session authority.
For an inherited `direct-commit` handoff, require
`owner-ref`, `scope-ref=issue:<NN>`, the PRD's preserved `target-ref`,
`target-branch=<branch_name>`, and `scope-transfer-ref=run` in both delivery
and explicit issue-mutation evidence. Preserve and fingerprint both evidence
records independently: their scope, target, branch, and transfer tokens must
match, while each `owner-ref` remains unchanged and the mutation ref must
independently authorize final-commit issue closure. Delivery authority alone is
insufficient. When registering
the exact generated issue as `workstream:<id>`, create the scoped evidence by
changing only `scope-ref` to that workstream and `scope-transfer-ref` to the
issue scope. Preserve owner, target, and branch tokens verbatim; any mismatch
is `needs-owner` and cannot grant publication.
For a legacy handoff that predates `pr_closeout`, resolve `delivery_mode`
first. Normalize a missing value to `merge-ready` for `pull-request` and
`not-applicable` for `direct-commit`, then rewrite the projection when touched.
For a legacy handoff that predates `pr_shape`, inherit the linked PRD's
canonical value when present. Otherwise derive `single-pr` for one-repo
`pull-request`, `per-repo-pr` for multi-repo `pull-request`, or `none` for
`direct-commit`. If repo scope is ambiguous, stop as `needs-owner`; never infer
the value from loose prose.
For a legacy handoff that predates `integration_mode`, inherit a canonical
value from the linked PRD when present. Otherwise normalize the omitted
ordinary inherited case to `not-applicable`. An explicit legacy
`Integration mode` field is normalized through the migration table below. If legacy
structured integration data contradicts the inherited or default value, stop
as `needs-owner` instead of choosing from prose.
For a legacy handoff that predates `closeout_mode`, derive the canonical value
from tracker backend, `delivery_mode`, and `pr_shape` using `options.md`. Stop
as `needs-owner` when any required input is missing or contradictory.
For a legacy handoff that predates `issue_mutation_authority`, derive
`pr-body-closeout-only` for hosted pull-request delivery and `none` for local
trackers. Do not derive `explicit-direct-mutation` from direct-commit delivery;
a hosted direct-commit closeout remains `needs-owner` until separately scoped
final-commit closure evidence is recorded.

### Legacy Handoff Migration

Legacy issue and handoff fields are read aliases only. Before routing,
registration, or validation, normalize the complete projection and rewrite it
when touched:

| Legacy field or value | Canonical projection |
| --- | --- |
| `Source PRD` | `source_prd_ref` |
| `Feature slug` | `feature_slug` |
| `Delivery mode` | `delivery_mode`; move inheritance/override prose to `delivery_source` and `delivery_source_evidence` |
| `Issue mutation authority` | `issue_mutation_authority`; preserve its separately scoped evidence in `issue_mutation_authority_evidence` |
| `PR shape` | `pr_shape` |
| `PR closeout` | `pr_closeout` |
| `Affected repos or product scope` | `affected_repos_or_product_scope` |
| `Scope` | `scope` |
| `Start rule: independent` | `parallelization=independent`; empty dependency data |
| `Start rule: depends-on <ids>` | `parallelization=depends-on`; move ids to `dependency_ids` |
| `Start rule: blocks <ids>` | `parallelization=blocks`; move ids to `blocked_issue_ids` |
| `Start rule: root-integrated` | `parallelization=root-integrated`; keep dependency data separate |
| `Dependencies` | `dependency_ids`, `blocked_issue_ids`, and `dependency_reason` |
| `Validation` | `validation` |
| `Domain closeout` | `domain_closeout`; move decisions, targets, evidence, and operation to `domain_closeout_data` |
| `Closeout` | `closeout_mode` |
| `Integration mode` | `integration_mode` |
| `Integration mode: omitted` | `integration_mode=not-applicable` |
| `Issue integration shape: none` | `integration_mode=not-applicable` |
| `Issue integration shape: feature-pr` | `integration_mode=single-repo-pr` |
| `Issue integration shape: repo-pr` | `integration_mode=repo-pr` |
| `Issue integration shape: direct-commit` | `integration_mode=direct-commit` |

Parse only the recognized enum token and stable ids from a combined legacy
value. Preserve the remaining text as evidence or reason data. If a legacy
value cannot be mapped unambiguously, stop as `needs-owner`; never retain the
combined value as a current enum and never infer a new option from its prose.

For workspace features split across multiple repositories, a repo-scoped
partial PRD may be the entry point. Before scheduling, expand its linked sibling
partial PRDs and register the connected graph in the ledger. Treat each partial
PRD and generated issue as its own source item, use their cross-links to
understand which repo work can run together, and require cross-repo integration
proof before marking the feature graph complete.

## Authority Model

Record these five authority and lifecycle concerns separately in the ledger:

- **Delivery authority**: where the branch, canonical `pr_shape`, dependency
  graph, and closeout path come from. For generated issues this is usually the linked
  `source_prd_ref` plus the generated issue's copied delivery label, issue-level
  dependency fields, and `## Orchestrator Handoff`.
- **Publication authority**: whether the root may commit, push, open or update
  the PR, mark it ready for review, request Codex review, and perform PR
  discussion updates or no-update-needed dispositions after gates pass.
- **pr_closeout**: whether pull-request delivery ends `merge-ready` or
  intentionally ends `draft-only`. This is lifecycle intent, not publication
  authority or merge authority.
- **Issue mutation authority**: whether the root may directly comment, label,
  close, or otherwise mutate GitHub issues outside the PR body closeout path.
- **Merge authority**: whether the root may merge the named PR or PR set after
  every required gate passes, and whether another owner checkpoint is required.

Do not collapse these into one boolean. Pull-request publication defaults to a
merge-ready closeout, while merge remains separately unauthorized by default.
Only a canonical option-resolution row containing
`pr_closeout=draft-only` may stop the lifecycle at draft.

`$plan-feature` may publish the PRD and generated implementation issues before
implementation starts. After the root registers those generated issues as
workstreams, source lifecycle and closeout mutations are orchestrator-owned:
issue comments, label changes, direct closure when authorized, real PR link
recording, and integration proof all require the root's resolved issue mutation
authority.

## Structured Authority Values

Use these PRD-backed authority values in the ledger and worker prompts:

- `publication_authority`: `none` means no publication,
  `explicit-owner-authorization` means the owner authorized the recorded
  publication actions in the current run, `prd-backed-pull-request` means the
  PRD delivery contract authorizes commit, push, initial draft PR publication,
  ready-for-review transition, `@codex review`, polling, and required
  discussion disposition after gates, plus the root-owned final PR-body
  parent-PRD closing-keyword update after the current-head Codex review gate
  passes.
  Review-request authority remains subject to the current-head GitStack
  preflight and cannot justify a duplicate request. `blocked` means publication
  is expected but blocked by a gate or access issue.
- `pr_closeout`: `merge-ready` is the default for `pull-request` and requires
  the full review lifecycle; `draft-only` intentionally stops after validated
  draft publication and requires owner-instruction or source-contract evidence
  in `## Option Resolution`. Use `not-applicable` for `local-only` and
  `direct-commit`.
- `publication_owner`: `root` means the root orchestrator owns the publication
  decision. A worker may execute assigned `commit`, `push`, or `pr` steps only
  inside an exact root-assigned scope. `none` means no publication owner exists.
- `issue_mutation_authority`: `none` means no direct issue mutation,
  `pr-body-closeout-only` means closure only through the relevant PR body,
  including the parent PRD after its final closeout gates pass, and
  `explicit-direct-mutation` means direct issue comments, labels, or closure are
  authorized.
- `merge_authority`: `none` is the default and means stop at merge-ready;
  `explicit-owner-authorization` requires the matching scoped option row to
  name the PR or PR set in owner evidence.
- `merge_policy`: `owner-approval` is the default and requires a final owner
  checkpoint; `automatic-after-gates` is allowed only when the same explicit
  instruction authorizes merging after gates without another checkpoint.

`merge_authority=explicit-owner-authorization` requires an option-resolution
row whose owner evidence unambiguously names the PR or PR set. Other lifecycle
or completion evidence cannot select it. When authority is ambiguous, keep
`merge_authority=none` and move the decision to `needs-owner`.

### Legacy Authority Migration

Treat legacy authority values as read aliases, not current output values:

| Legacy value | Normalized publication authority | Normalized pr_closeout |
| --- | --- | --- |
| `prd-backed-merge-ready-pr` | `prd-backed-pull-request` | `merge-ready` |
| `prd-backed-branch-plus-draft-pr` | `prd-backed-pull-request` | Canonical `pr_closeout` from option resolution; otherwise `merge-ready`. |

Rewrite either legacy value when its ledger or prompt projection is touched.
Natural-language PR shape, mutation restrictions, and merge restrictions are
option-resolution evidence only. They cannot become values or override a
canonical field from `options.md`.

## Canonical PR Closeout Resolution

Resolve these fields before publication and branch only on their canonical
values:

| `delivery_mode` | `publication_authority` | `pr_closeout` | `merge_authority` | Required next state |
| --- | --- | --- | --- | --- |
| `pull-request` | `prd-backed-pull-request` | `merge-ready` | `none` | Open draft initially, validate, continue through current-head Codex review, and stop merge-ready. |
| `pull-request` | `prd-backed-pull-request` | `draft-only` | `none` | Validate and publish the draft; do not mark ready or request Codex review. |
| `local-only` | `none` | `not-applicable` | `none` | Complete local acceptance and validation only. |
| `direct-commit` | `explicit-owner-authorization` | `not-applicable` | `none` | Follow the authorized direct-commit closeout path. |

An existing draft PR with `pr_closeout=merge-ready` resumes at
ready-for-review after required local gates. A canonical change from
`draft-only` to `merge-ready` resumes the same path. A legacy handoff with
missing delivery fields is normalized only after `delivery_mode` is known.
Missing `pr_closeout` becomes `merge-ready` for `pull-request` or
`not-applicable` for `direct-commit`. Missing `pr_shape` inherits the linked
PRD's canonical value or uses the deterministic repo-scope rule under
`Legacy Handoff Migration`. Rewrite the projection when touched.

An initial draft state is never terminal evidence by itself. Merge authority is
orthogonal: reaching merge-ready does not authorize merge.

delivery_mode values are owned by the PRD and generated issue body. Worker
authorization modes are owned by `worker.md` and resolved per workstream by the
root orchestrator. Ignore legacy project-memory worker-authorization setup
values; they are not delivery, publication, or issue mutation authority.
Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases when reading existing artifacts. When updating an artifact
that contains legacy aliases, rewrite touched structured values to
lower-kebab-case.

## Scheduling Values

Use generated issue scheduling fields as the wave graph. Read dependency refs
from their data fields; never append them to the enum value.

| `parallelization` | Dependency data | Start rule |
| --- | --- | --- |
| `independent` | `dependency_ids=none`; `blocked_issue_ids=none` | May start when authorization, ownership boundaries, and gates allow it. |
| `depends-on` | One or more `dependency_ids` | Queue-ready is not start-ready; wait for root-verifiable dependency proof. |
| `blocks` | One or more `blocked_issue_ids` | May start when otherwise eligible; dependent work remains unassigned. |
| `root-integrated` | Dependency ids as applicable | Keep implementation in root; workers may inspect or prove only if integration stays root-owned. |

Reject a workstream before dispatch when its scheduling enum and dependency
data violate these rows. Preserve `dependency_reason` separately for every
non-empty dependency or blocked-ID set.

## PRD-Backed Publication

When the owner asks to implement a PRD or generated PRD issue, and the PRD or
generated issue defines `pull-request` delivery, treat commit, push, initial
draft PR creation, ready-for-review transition, Codex review, feedback
disposition, and merge-ready reporting as the default delivery contract after
required tests, integration checks, and `$autoreview` pass, unless canonical
authority or delivery fields restrict those actions.

Set `pr_closeout=draft-only` only from a valid option-resolution row with
owner-instruction or source-contract evidence. Plan Feature's planning-only
`no_mutation_override` is not an Orchestrator input; `pr_shape` and merge
authority are separate fields and cannot select `pr_closeout`. Draft-only
blocks ready-for-review transition,
Codex review, and merge-ready reporting until the current user changes the
decision; validation and draft publication still complete normally.

This PRD-backed publication authority is sufficient for the root orchestrator
to use `$gitstack:git-commit` for commit/push-only delivery, or `$gitstack:yeet` when the resolved
delivery path requires draft PR creation or updating an existing PR.
Merge-ready publication authority is additionally sufficient to use
`$gitstack:github-review-threads` for the `@codex review` request and the required PR
discussion update or no-update-needed disposition after the Codex review
completes, then to update the default-branch whole-PRD closeout PR body with the
parent PRD closing keyword once every whole-PRD closeout gate passes. Neither
authority is sufficient for merge, release, production deploy, final issue
closure by direct mutation, broad GitHub cleanup, or switching the caller
checkout away from its current branch. When worker or integration worktrees are
available, the root should publish from one of those checkouts and preserve the
caller checkout unless
`caller_checkout_policy=caller-checkout-approved` for that workstream.

Direct commit remains a special case. Use `delivery_mode=direct-commit` only
when its scoped option row records the target branch, closeout behavior, and
exact owner authorization evidence. A source contract may preserve that
evidence; unproven source prose cannot grant direct-commit publication.

For local markdown trackers, `direct-commit` proves delivery but does not close
the local issue by itself. After validation and commit proof are recorded, move
the issue file to `issues/done/`. Use final-commit closure only for hosted or
custom sources whose canonical `closeout_mode` is
`direct-commit-closes-issue` and whose scoped authorization evidence is
preserved.

For local markdown trackers using `pull-request` delivery with
`pr_closeout=merge-ready`, do not move the issue file
to `issues/done/` until local validation, real PR proof, required CI or
integration proof, and Codex review evidence plus disposition are recorded. If
any of those are missing, keep the local issue open and record the remaining
action as `needs-owner`, `blocked`, or `deferred`.

## Required Resolution Steps

Before scheduling or publishing PRD-backed work:

1. Read the generated issue body and the linked `source_prd_ref`. Accept legacy
   `Source PRD` only as the migration alias above and normalize it before
   continuing. If the ref is `draft-prd:<...>`, stop before implementation
   scheduling unless the matching scoped row is
   `temporary_source_execution=owner-approved`; separately resolve the
   publication and issue-mutation authority that execution may use.
2. For generated issues, read `## Orchestrator Handoff` and verify it contains
   source PRD, feature slug, `delivery_mode`, `delivery_source`,
   `delivery_source_evidence`, `branch_name`, `pr_shape`, `pr_closeout` when applicable,
   affected repos or product scope, scope, start rule,
   dependencies, validation, domain closeout, `closeout_mode`, and
   `integration_mode`. Require `domain_closeout:
   implementation-closeout` with exact decisions, targets, and evidence when
   the issue contains `## Domain Knowledge Closeout`; otherwise require
   `not-applicable`. For a legacy handoff missing `pr_closeout`, `pr_shape`, or
   `integration_mode`, apply the deterministic delivery-mode, repo-scope, and
   linked-PRD/default migrations above and rewrite the touched projection. If
   another required field is missing, repo scope is ambiguous, or the handoff contradicts the issue body, stop as
   `needs-owner` or route back through `$plan-feature` issue generation instead
   of dispatching implementation.
3. If the linked PRD is a workspace partial PRD, expand the connected sibling
   partial-PRD graph and record each partial PRD/source item plus cross-link in
   the ledger before building waves.
4. Resolve the effective delivery mode from the PRD first, then resolve
   `pr_shape` and `pr_closeout`, defaulting `pull-request` closeout to
   `merge-ready`; apply only issue-level overrides that are explicit and
   authorized.
5. Record delivery authority, publication authority, `pr_shape`, pr_closeout, issue
   mutation authority, parent-PRD closeout applicability/reason/state, merge
   authority, merge policy, authorizing owner instruction when any, closeout
   vehicle, branch expectation, publication checkout, caller
   checkout policy, integration proof target, and handoff projection in the
   ledger.
6. Build the wave graph from the generated issues' handoff start rules,
   dependency fields, and parallelization fields. Queue-ready does not mean
   start-ready when an issue depends on another incomplete issue.
7. Stop as `needs-owner` or `blocked` if the PRD, issue body, handoff,
   dependency graph, branch expectation, or closeout path is missing,
   contradictory, or unsafe.

## Closeout Rules

For PRD-backed implementation, local code completion is not enough for
`completed` when publication authority exists. A workstream reaches
`completed` only after:

- acceptance criteria are satisfied with root-verifiable proof;
- required gates pass, including focused tests and `$autoreview` for
  non-trivial code edits;
- dependency and integration proof targets are satisfied;
- the expected branch and PR exist when PRD-backed publication is authorized;
- if `pr_closeout=merge-ready`, the PR is marked ready for review when local
  gates pass;
- if `pr_closeout=merge-ready`, GitStack review-status preflight ran for the
  current head, an existing request/result was reused or exactly one request was
  posted when needed, a verified terminal Codex result exists for that head,
  and accepted actionable feedback was fixed or explicitly dispositioned;
- for a GitHub-backed `merge-ready` default-branch PR that is the whole-PRD
  closeout vehicle, the PR body closes every satisfied generated issue and
  includes the parent PRD closing keyword added by the root after the
  current-head Codex review gate passed, with the PR head revalidated against
  the reviewed SHA immediately before the body update and again before
  merge-ready reporting; and
- the ledger records the PR URL, publication checkout, caller checkout
  disposition, and, when `pr_closeout=merge-ready`, Codex result evidence
  including request/result head and object id plus discussion update or
  no-update-needed disposition plus parent-PRD PR-body closeout evidence when
  applicable; otherwise it
  records why publication/review is blocked and moves the remaining action to
  `needs-owner`, `blocked`, or `deferred`.

If PRD-backed publication is authorized and the only remaining action is
commit, push, or initial draft PR creation, keep that action in `ready-next` and
execute it before stopping when runtime access allows. If
`pr_closeout=merge-ready` and the only remaining action is ready-for-review transition,
Codex review preflight/request, waiting on the existing request, review-triggered fixes, or
PR discussion update, disposition, or the gated parent-PRD PR-body closeout
update, keep that action in `ready-next` and execute or poll it before stopping
when runtime access allows. For
`pr_closeout=draft-only`, record downstream ready/review/merge-ready gates as
`not-applicable` with the explicit restriction and allow validated draft
publication to satisfy the requested closeout without classifying it as a
blocker. If the current user later removes the restriction, change
`pr_closeout` to `merge-ready` and resume at ready-for-review.

Repo PR placeholders copied from PRDs or generated issues are not completion
proof. The root must replace or augment them during closeout with real PR links
or equivalent integration proof before marking a PRD-backed workstream
`completed`.

Close generated GitHub implementation issues through the relevant PR body by
default, using the closeout wording specified by the generated issue or PRD.
For a GitHub-backed PRD completed by one final feature or integration PR that
targets the current default branch, make that PR the parent closeout vehicle.
After the `codex-pr-review` gate passes for the current head, and only after
every generated implementation issue is satisfied and represented by its
required PR-body closeout, every PRD acceptance criterion, dependency,
integration gate, and required domain closeout is satisfied with no deferred
PRD scope, update the PR body with
`Closes #<PRD-number>`. When the PR and PRD live in different repositories, use
`Closes owner/repo#<PRD-number>` only when that cross-repo closeout path is
intended and supported; otherwise record the parent closeout as blocked or
`needs-owner`. This PR-body update arms GitHub closure when the PR reaches the
default branch; it does not close the PRD at review time. Do not add the parent
closing keyword to a partial PR, a `draft-only` PR, or a PR with unresolved or
deferred PRD scope. Direct comments, labels, manual issue or parent closure,
merge, and release remain separate mutations that require explicit authority.

The root must re-read the PR head immediately before the parent PRD PR-body
update and require it to equal the reviewed SHA. Re-read the head, base/current
default branch, and live PR body again after the update and immediately before
merge-ready reporting. Require the live body fingerprint to match the recorded
evidence and contain exactly the intended parent closer. A head change returns
parent closeout to `pending-review`; a body-only mismatch returns it to
`pending-closeout` for non-destructive reconciliation. Do not add the keyword,
or remove/replace an invalid already-added keyword, until the matching cycle
passes. For workstreams where parent closure does not apply, record
`not-applicable` instead of blocking merge-ready closeout.

At registration, recovery, and immediately before current-head Codex review
preflight, inspect the PR body for a parent PRD closing keyword. If one exists
while parent closeout is not already `armed` with a matching current reviewed
SHA and recorded PR-body evidence, the root must remove it or replace it with a
non-closing reference, then record `pending-review`. A pre-existing keyword is
never proof that the post-review root mutation occurred. If publication access
cannot disarm it, mark parent closeout `blocked` and do not proceed to
merge-ready.

Before arming parent closeout, resolve the repository's current default branch
and require the closeout PR to target it; GitHub does not honor PR-description
closing keywords for a PR targeting another base. Revalidate both the current
default branch and PR base immediately before the PR-body update and again
before merge-ready reporting. If the reviewed PR targets an integration,
release, or other non-default branch, do not add the parent keyword or record
`armed`; record `deferred-to-default-branch`, select the later default-branch PR
as the parent closeout vehicle, and apply the same current-head Codex review and
closeout gates to that PR. The non-default-base PR may reach merge-ready after
its own gates pass, but the whole PRD, source graph, and ledger remain active
until the later vehicle is `armed`. If no authorized default-branch closeout
vehicle can be selected, record `blocked` or `needs-owner`.

Treat `armed` as a monitored pre-merge state, not completed parent closure.
Follow the parent closeout watch in `gates.md`: use `root-monitoring` only when
the root has explicit merge authority and is the designated merger; otherwise
require an owner pre-merge handoff or an explicitly authorized event-driven
automation handoff before reporting merge-ready. A handoff must preserve the
PR, parent PRD, reviewed head, default base, PR-body fingerprint, recheck
triggers, disarm procedure, and post-merge issue-closure check. A scheduled poll
alone is insufficient. The parent PRD source and portfolio ledger remain open
or paused until GitHub actually closes the issue; if the merged PR does not
close it, record `needs-owner` unless the scoped row is
`issue_mutation_authority=explicit-direct-mutation`.

## Worker Boundaries

The root orchestrator owns branch selection, shared PR shape, source closeout,
final parent-PRD PR-body closeout, final publication, Codex review disposition,
and merge-ready decision. Workers
may inspect, implement, test, and report within their assigned authorization
modes. The root normalizes owner/source input into scoped option rows, then
derives worker modes only from those rows, source data, dependency state,
dirty-worktree state, and gates. Workers may commit, push, open PRs, mark a PR ready for review, or
request Codex review only when the root lists the corresponding `commit`,
`push`, `pr`, or `review-ready` authorization mode for a specific repo,
branch/refspec, PR shape, and closeout target. These modes are capability flags,
not a cumulative ladder; list every allowed action explicitly. For
`review-ready`, also list the allowed sub-actions from `worker.md` so workers do
not infer Codex-review disposition authority.

For `pull-request`, workers do not create independent feature PRs unless the
source graph assigns them repo-scoped publication authority. In single-repo or
monorepo work, they provide patches, helper worktree diffs, or reviewed commits
for root integration into the feature branch. In multi-repo work, a repo-scoped
worker may prepare that repo's branch or draft PR only if the root assigned
repo-scoped `commit`, `push`, or `pr` authority matching each intended action.

## Ad Hoc And Legacy Sources

For ad hoc requests, PR reviews, CI diagnosis, local TODOs, or legacy issues
without a linked PRD delivery contract, `implement` means local code/docs
changes plus validation only. Commit, push, pull-request delivery, issue
mutation, merge, and release require explicit owner authorization. When the
owner authorizes `pull-request` delivery, set
`publication_authority=explicit-owner-authorization` and default
`pr_closeout=merge-ready`, including ready-for-review transition and Codex
review. Use `draft-only` only from the explicit evidence defined above. Worker
modes may grant `commit`, `push`, `pr`, `review-ready`, or `release` within
their scoped contracts, but merge remains a root-owned action governed by
`merge_authority` and `merge_policy`.

Do not block ad hoc or legacy implementation merely because PRD fields are
absent. In the ledger, use runtime delivery `local-only`, publication `none`,
issue mutation `none`, branch and publication checkout `not-applicable`, and a
closeout target of satisfied local acceptance criteria plus validation. If the
source contains contradictory or unsafe instructions, resolve that conflict as
`needs-owner` or `blocked`; missing PRD metadata by itself is not a conflict.
