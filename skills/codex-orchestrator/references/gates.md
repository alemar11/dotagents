# Shared Orchestration Gates

## Universal Gates

Before owner-ready or terminal status require:

- scope and acceptance evidence;
- exact mutation authority;
- preserved owner changes and safe checkout ownership;
- current diff and focused validation;
- non-trivial `$autoreview` with actionable findings resolved;
- dependency and integration proof;
- delivery-target proof;
- issue/source closeout proof;
- no active execution, due check, or ready-next action.

## Authorization

Commit, push, PR creation/readiness, issue mutation, review skip, merge, release,
deployment, and target-repo instruction changes each require their canonical
permission and exact scope evidence. Permissions are independent. Read access
and one mutation never imply another.

## Adapter Checkout Gate

The selected adapter owns checkout proof:

- `codex-app-task` requires App-managed isolated checkout evidence for every
  repository in the Feature Spec;
- `codex-cli-session` requires the CLI manifest, unique worktree/branch map,
  terminal worker artifacts, and root-owned integration evidence.

Missing adapter checkout proof blocks. The gate never falls back to another
adapter's checkout machinery.

## Delivery Gates

For `codex-app-task`, only the merge-ready PR gate applies. Other delivery gates
below exist solely for the CLI adapter's broader source contracts and must not
be selected, offered, or used as App fallback conclusions.

- Validated-uncommitted requires focused validation and an inspectable diff.
- Local commit requires the intended commit and clean relevant checkout.
- Push-without-PR requires remote branch proof and no implied issue closure.
- Draft PR requires current diff, validation, published draft URL, and declared
  remaining gates.
- Merge-ready PR requires current-revision review disposition, passing required
  CI, resolved review threads, safe PR metadata, parent-closeout preparation,
  and ready state.

An App run succeeds only when every affected repository has a real non-draft
PR URL at its current head, all required checks pass, current-revision review is
dispositioned, actionable feedback is resolved, and the PR is ready to merge.
Draft publication is intermediate evidence, never App completion.

## Review And CI

Current-revision Codex review is required for merge-ready delivery unless the
authorized user explicitly selects
`codex_review_requirement=explicitly-skipped-by-authorized-user`. That skip
does not bypass autoreview, CI, issue, integration, or publication gates.

Material diff changes, base-ref changes, or merge-base changes invalidate older
review evidence. Failed CI or actionable review feedback returns the execution
to fixing and revalidation.

## Merge And Source Closeout

Merge is root-owned and unavailable by default. It requires permission for the
named PR and the configured confirmation behavior. Parent Feature Spec closure
is prepared before merge but verified only after merge and actual tracker
closure. `armed` is not closed.

Multi-repo completion requires every child delivery plus cross-repo integration
proof. Release/deployment gates require their separate authority, artifacts,
credentials, and live proof.
