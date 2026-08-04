# Delivery Status Model

This reference owns the normalized pull-request delivery-status vocabulary.
GitHub remains the source of truth; preserve provider-native fields alongside
every derived value.

## Provider surfaces

Collect current pull-request identity and lifecycle, `MergeableState`,
`MergeStateStatus`, review decision, check/status rollup, review threads,
closing issue references, merge queue, auto-merge request, repository merge
settings, active branch rules, ruleset details, bypass actors when visible, and
classic branch protection when available.

Official references:

- https://docs.github.com/en/graphql/reference/pulls
- https://docs.github.com/en/rest/repos/rules
- https://docs.github.com/en/rest/repos/rule-suites
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets

GitHub currently exposes `CONFLICTING`, `MERGEABLE`, and `UNKNOWN` technical
mergeability plus detailed merge states including `BEHIND`, `BLOCKED`, `CLEAN`,
`DIRTY`, `DRAFT`, `HAS_HOOKS`, `UNKNOWN`, and `UNSTABLE`. Do not collapse the
two provider enums: conflict-free construction and policy readiness are
different facts.

## Canonical dispositions

| Disposition | Meaning |
| --- | --- |
| `ready` | The PR is open, exact-head evidence matches, GitHub can construct the merge, and observed required gates are satisfied. |
| `ready-with-manual-action` | The same evidence is satisfied, while an active restricted-update rule leaves the actual branch update to an eligible human or provider actor. |
| `pending` | GitHub is calculating mergeability or a required check/review is still pending. |
| `blocked` | A verified required gate is unsatisfied, the PR is draft/not open, the head is stale, or the branch must be updated. |
| `conflicting` | GitHub reports a merge conflict or cannot construct a clean merge commit. |
| `unknown` | The provider state is unfamiliar, contradictory, incomplete, or a `BLOCKED` cause cannot be attributed safely. |

`BLOCKED` becomes `ready-with-manual-action` only when the PR is technically
mergeable, no observed required check or review is pending/failing, and the
active rule set attributes the remaining boundary to restricted updates.
Unrecognized rules or an unattributed block remain `unknown`.

`UNSTABLE` remains `ready` when every required check is satisfied because
GitHub defines it as mergeable with a non-passing, non-required commit status.
`BEHIND` is `blocked` only when an active strict status-check policy requires
the head to be current; otherwise the provider still permits the merge. For a
required check name shared by a check run and commit status, require every
matching context to pass. When a rule names a GitHub App integration, require
the matching app identity rather than accepting a same-name check from another
source.

## Automation

Keep these facts outside the disposition:

- whether the repository allows auto-merge;
- whether this PR already has an auto-merge request;
- whether this PR has a merge-queue entry.

They describe provider configuration or externally established state. They do
not authorize this skill or a composing workflow to mutate or merge the PR and
do not make an otherwise ready PR blocked.

## Completeness

Record unavailable surfaces explicitly. A missing active-rules read prevents
verified attribution of a `BLOCKED` state. An inaccessible optional ruleset
detail may reduce attribution confidence while preserving the active rules
already returned by GitHub. Preserve new provider values and return `unknown`
instead of rejecting or inventing a compatibility mapping.
