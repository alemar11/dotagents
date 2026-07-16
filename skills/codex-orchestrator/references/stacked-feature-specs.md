# Two-Level Stacked Feature Specs

## Eligibility

Load only when a same-repository downstream Feature Spec has an explicit
`upstream-merge-ready-head` dependency on exactly one upstream Spec. Do not
infer this flow from generic dependency prose. Reject multi-repository edges,
more than one live upstream, and stacks deeper than two.

## State

The root records upstream Spec/PR/branch/reviewed SHA, downstream
Spec/PR/branch/base, dependency classification, visible task refs, and promotion
state. The upstream must be validated, reviewed at its current head, CI-clean,
and merge-ready before downstream dispatch.

Create a distinct downstream visible App task and managed checkout from the
exact upstream reviewed SHA. Never reuse the upstream task or checkout. Each
Spec keeps its own branch, PR, review evidence, gates, Goal evidence, and
closeout.

## Promotion

After upstream merge, verify the actual merged default-branch result. The
downstream task rebases or retargets its branch, re-runs affected validation,
requests a new current-head review, resolves feedback, and passes CI. History
rewrite requires explicit force-push authority for the named branch; otherwise
use a non-rewriting integration path or block.

Any upstream head drift, review invalidation, merge-result mismatch, task
evidence loss, or deeper dependency invalidates downstream readiness and
returns it to blocked/resyncing.
