# Execution-Ready Feature Spec Delivery

## Applicability

Load only for a durable Feature Spec with its complete generated implementation
issue graph and Orchestrator Handoffs. This is the adapter-neutral
execution-ready bundle. Reject rough intent, a standalone Feature Spec, ad-hoc
implementation requests, retired planning or authority vocabulary, and missing
or contradictory handoff evidence.

The Feature Spec and generated issues are acceptance and execution authority;
the ledger is their runtime projection. This contract never creates, repairs,
regenerates, or publishes planning artifacts. Planning happens outside an active
orchestrator run.

## Required Handoff

Require a stable durable source Spec ref; the complete issue/workstream ids;
repository and issue layouts; every affected repository; scope and allowed
paths; acceptance criteria; validation commands; dependencies and
parallelization; delivery target, permission, branch, and evidence; issue
update permission; review requirement; parent closeout vehicle; and
durable-knowledge handoff. Merge authority is not an execution-ready handoff
field; the root may resolve it separately only after the fixed PR-ready
conclusion is complete by loading `core/merge-authorization.md`.

Missing implementation detail makes the bundle non-executable. Missing
mutation authority blocks only the affected mutation; it never expands from
prose or another permission. A `draft-spec:<...>` ref is inspection-only and
non-executable for every adapter; no permission promotes it to an executable
source. Replace it with a durable hosted or local Feature Spec ref before
intake. The App adapter reports the missing durable source as
`planning-required`.

A generated issue's `## Orchestrator Handoff` must contain its source Spec, repository and
workstream scope, dependency graph, validation commands, delivery tuple, issue
completion method, and `delivery_decision_origin_evidence` for the exact workstream.
The execution-ready bundle owns target selection, delivery permission, and
issue mutation authority. The root validates and preserves that tuple; it never
selects, rewrites, or widens it. The selected adapter executes the resolved
contract. The root owns only a separately requested post-conclusion merge
authorization.

## Delivery Targets

The App adapter accepts only
`pull-request-ready-for-merge-but-not-merged`. If a Feature Spec or generated
issue resolves another target, App intake stops as
`unsupported-app-delivery-target` before CLAIM; it does not rewrite the source
contract, ask for another target, or downgrade delivery.
The remaining target variants are available only to adapters whose public
contract explicitly supports them.

- `validated-changes-left-uncommitted`: validate and leave an inspectable diff.
- `local-commit-created-without-pushing`: validate and create the authorized
  local commit.
- `changes-pushed-to-target-branch-without-pull-request`: validate and push the
  named branch; do not imply issue closure. Named remote branch contains the validated commit before this target is complete.
- `validated-draft-pull-request-published`: validate and publish a draft with
  remaining gates explicit.
- `pull-request-ready-for-merge-but-not-merged`: validate, publish, obtain the
  required current-head review, resolve feedback, pass CI, prepare parent
  closeout, and mark ready without merging.

The selected adapter decides who executes an accepted target:

- App: the visible Feature Spec task owns delivery through the selected target;
- CLI: the root CLI session owns integration and delivery after worker exit.

Workers and adapters never reinterpret the target or permissions.

## Repository Layout

Single-repository and monorepo delivery normally produces one PR. A
multi-repository Feature Spec produces one PR per affected repository using the
same feature branch name unless the Spec records an explicit repository-level
exception. Every child outcome and cross-repo integration gate must pass before
parent closeout. Real PR refs replace placeholders before completion.

## Issue Completion

GitHub issues close through the authorized PR closing keyword by default.
Direct final-commit closure requires independent direct-issue-update authority.
Local Markdown issues move to the configured done folder only after delivery
and integration proof. Parent Feature Specs remain open until every child and
post-merge closeout condition is actually satisfied.

Local Markdown issues use `move-local-issue-to-done-after-proof`; a generated
issue's handoff must name that completion method when it applies.

## Closeout

Record target proof, repository commits/PRs, current reviewed SHA, CI,
integration, issue/parent closeout state, adapter evidence, and remaining owner
actions. Merge remains a separate root-owned permission.
