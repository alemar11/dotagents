# Two-Level Stacked Feature Specs

## Eligibility

Load only when a same-repository downstream Feature Spec has an explicit
`upstream-merge-ready-head` dependency on exactly one upstream Spec. Do not
infer this flow from generic dependency prose. Reject multi-repository edges,
more than one live upstream, and stacks deeper than two.

## Shared State

The root records upstream Spec/PR/branch/reviewed SHA, downstream
Spec/PR/branch/base, dependency classification, adapter execution refs, and
promotion state. The upstream must be validated, reviewed at its current head,
CI-clean, and merge-ready before downstream dispatch.

## Adapter Checkout

The root asks the selected adapter to create a distinct downstream execution
and isolated checkout from the exact upstream reviewed SHA:

- App creates a separate managed visible task and managed checkout;
- CLI prepares a separate isolated execution through its own adapter contract.

Never reuse the upstream execution or checkout. Each Spec keeps its own branch,
PR, review evidence, gates, Goal/objective evidence, and closeout.

## Promotion

After upstream merge, verify the actual merged default-branch result. Rebase or
retarget the downstream branch only through its owning adapter, re-run affected
validation, request a new current-head review, resolve feedback, and pass CI.
History rewrite requires explicit force-push authority for the named branch;
otherwise use a non-rewriting integration path or block.

Any upstream head drift, review invalidation, merge-result mismatch, adapter
evidence loss, or deeper dependency invalidates downstream readiness and
returns it to blocked/resyncing.
