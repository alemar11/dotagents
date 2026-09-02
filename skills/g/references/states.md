# G State Registry

This is the canonical owner of every behavior-affecting state derived or
persisted by the standalone G skill. Selectable invocation values live in
`options.md`, not here.

Most values below are transient derived results for one invocation. GitHub
lifecycle, checks, reviews, rules, queues, Projects, releases, issue
`blockedBy` and `blocking` relationships, and stars are external provider
state. Git branches, commits, tags, the index, and the worktree are external
Git state. Preserve those authoritative values as observed instead of
translating them into new G states.

Only review reservation markers and operation journals are skill-persisted,
under `~/.cache/dotagents/skills/g/`. Typed receipts and result files are
caller-persisted artifacts. The audit registry exists only in the current task.

## Audit

| Namespace | Values | Meaning |
| --- | --- | --- |
| `coverage` | `complete`, `partial` | Whether every qualifying active task and evidence frontier was authoritatively visible. |
| `finding_kind` | `feedback`, `bug`, `improvement` | Observed feedback, a proven contract violation, or an actionable proposal. |
| `bug_status` | `provisional`, `confirmed`, `resolved`, `withdrawn` | Incomplete evidence; proven violation; later recovery; or later disproof. |
| `priority` | `p0`, `p1`, `p2`, `p3` | Security/data-loss/total failure; workflow blocker; meaningful degradation; or clarity/polish. |

`provisional` may become `confirmed` or `withdrawn`; `confirmed` may become
`resolved` or `withdrawn`. Terminal audit states do not transition further.

## Actions inspection

These are transient summaries derived from the authoritative check rollup.

| Value | Meaning |
| --- | --- |
| `no-checks` | The authoritative rollup is empty; this is not evidence that CI passed. |
| `no-failing-checks` | At least one check exists and none is classified as failing. |
| `failing-checks` | One or more failing checks were analyzed. |

## Delivery status

Delivery values are transient classifications. Provider mergeability,
merge-state, policy, automation, checks, reviews, rules, queue, and exact HEAD
remain external state.

| Namespace | Value | Meaning |
| --- | --- | --- |
| `delivery_disposition` | `ready` | The pull request is open, exact-head evidence matches, construction is clean, and observed required gates pass. |
| `delivery_disposition` | `ready-with-manual-action` | The ready evidence holds, but an active restricted-update rule leaves the action to an eligible actor. |
| `delivery_disposition` | `pending` | Mergeability or a required check/review is still pending. |
| `delivery_disposition` | `blocked` | A verified gate is unsatisfied, the pull request is draft/not open, the head is stale, or an update is required. |
| `delivery_disposition` | `conflicting` | GitHub reports a conflict or cannot construct a clean merge commit. |
| `delivery_disposition` | `unknown` | Evidence is unfamiliar, contradictory, incomplete, or cannot explain a provider block. |
| `attribution` | `verified`, `partial` | Evidence fully explains a terminal classification, or attribution remains limited. |

Collect the current pull-request identity and lifecycle, technical
mergeability, detailed merge state, review decision, check/status rollup,
review threads, closing references, merge queue, auto-merge request,
repository merge settings, active rules, visible bypass actors, and classic
branch protection. Keep provider technical mergeability distinct from policy
readiness.

A provider `BLOCKED` value becomes `ready-with-manual-action` only when the
pull request is technically mergeable, no observed required check or review is
pending or failing, and active rules attribute the remaining boundary to
restricted updates. Otherwise an unexplained block is `unknown`. `UNSTABLE`
may remain `ready` when all required checks pass. `BEHIND` is `blocked` only
when active strict status-check policy requires the head to be current. Every
same-name required check must pass, and a rule tied to a GitHub App requires
that exact app identity.

Repository auto-merge capability, an existing auto-merge request, and a merge
queue entry are external automation observations. They neither authorize a
mutation nor block an otherwise ready pull request. Record unavailable
provider surfaces explicitly; unfamiliar values produce `unknown` rather than
a guessed compatibility mapping.

## Investigation

| Namespace | Values | Meaning |
| --- | --- | --- |
| `provenance_confidence` | `clear`, `likely`, `unknown` | Evidence directly identifies provenance, supports one explanation with ambiguity, or cannot attribute it safely. |
| `refactor_disposition` | `required`, `optional`, `not-required` | A broader change is necessary, merely beneficial, or outside the sound fix boundary. |

## Issue dependency operations

Each native dependency operation returns exactly one transient result.

| Value | Meaning |
| --- | --- |
| `verified` | Reciprocal reads prove the authorized edge state. |
| `no-op` | Pre-reads already proved the requested edge. |
| `failed` | The provider definitively rejected the mutation. |
| `unavailable` | Capability, access, authentication, or target resolution prevented an attempt. |
| `unknown` | The mutation may have happened or readback remained inconclusive. |

## GitHub Projects operations

Project lifecycle, visibility, template state, fields, values, linked
repositories or teams, item content, and archival state remain external
GitHub state. Each Projects mutation returns exactly one transient
`project_operation_result`:

| Value | Meaning |
| --- | --- |
| `previewed` | Exact target and input were resolved without a provider mutation. |
| `no-op` | The pre-read already proved the requested state. |
| `verified` | Exact readback proved the requested state after mutation. |
| `failed` | The provider definitively rejected the attempted mutation. |
| `unavailable` | Capability, scope, access, or exact target resolution prevented an attempt. |
| `unknown` | The mutation may have applied or exact readback remained inconclusive. |

Projects operations persist no G-owned state. A multi-item request returns one
result per authorized operation rather than one aggregate state.

## Releases

Provider lifecycle values are `missing`, `draft`, and `published`. External
attributes `prerelease`, `latest`, and `immutable` may coexist with them.

| Transient value | Meaning |
| --- | --- |
| `target-unresolved` | Repository, tag, or comparison range is ambiguous or missing. |
| `notes-preview-ready` | An exact title/body proposal awaits approval. |
| `draft-creation-authorized` | The exact ordinary-create preview was approved. |
| `direct-publish-authorized` | Direct publication was explicitly requested for one resolved release. |
| `notes-update-authorized` | The exact replacement title/body was approved. |
| `verified` | Readback matches the authorized tag, lifecycle, and requested fields. |

## Review threads

Review observations and dispositions are transient; reservation and journal
evidence is persisted only for recovery.

| Namespace | Values | Meaning |
| --- | --- | --- |
| `feedback_disposition` | `actionable`, `already-addressed`, `informational`, `obsolete`, `needs-user-decision` | Whether current-head work is required, already satisfied, non-actionable, stale, or caller direction is needed. |
| `request_binding` | `absent`, `recognized`, `unbound`, `invalid`, `unknown`, `ambiguous` | Correlation between typed request identity and provider evidence. |
| `automated_review_state` | `not-requested`, `acknowledged`, `pending`, `clean`, `findings`, `stale`, `ambiguous`, `error` | Review request and terminal-result state for one exact head and lineage. |
| `recovery` | `needs-owner` | Exact reconciliation could not prove one unique prior provider artifact. |
| `operation_status` | `completed`, `failed`, `ambiguous`, `blocked` | Admitted terminal operation result. |
| `marker_state` | `absent`, `exact`, `conflicting` | Persisted one-use marker is missing, uniquely matches, or conflicts. |
| `provider_artifact_state` | `missing`, `unique`, `conflicting`, `ambiguous`, `unreadable` | Result of one bounded exact provider readback. |

For `automated_review_state`, `clean`, `findings`, `stale`, `ambiguous`, and
`error` are terminal. `not-requested`, `acknowledged`, and `pending` are not.
The normal result exits are respectively `0` for `clean`, `1` for `findings`,
`2` for non-terminal states, `3` for `stale`, and `4` for `ambiguous` or
provider-authored terminal `error`. Invalid arguments and bounded wait timeout
remain command failures outside this state namespace.

Managed operation outcomes are closed by operation:

| Operation | Allowed outcomes |
| --- | --- |
| `request` | `created`, `recognized-existing` |
| `wait` | `clean`, `findings`, `pending-at-deadline`, `request-correlation-failure`, `provider-failure` |
| `ready-check` | `clean`, `findings`, `pending`, `stale`, `ambiguous`, `provider-failure` |
| `ready-wait` | `clean`, `findings`, `pending-at-deadline`, `stale`, `ambiguous`, `provider-failure` |
| `warning` | `posted`, `recognized-existing` |
| `reply` | `posted`, `recognized-existing` |
| `resolve` | `resolved`, `already-resolved` |
| `reconcile-mutation` | `completed-from-readback`, `missing`, `conflicting`, `ambiguous` |
| `reconcile-terminal` | `clean-verified`, `findings-verified` |

The operation result admits only legal status/outcome pairs:
`pending-at-deadline` is `completed`; request-correlation and provider failures
are `failed`; reconciliation `missing` is `blocked`; reconciliation
`conflicting` or `ambiguous` is `ambiguous`; and both terminal reconciliation
outcomes are `completed`.

Mutation reconciliation is exact: `completed-from-readback` requires an
`exact` marker plus a `unique` provider artifact. `missing` permits an `absent`
or `exact` marker with a `missing` artifact. `conflicting` requires a
conflicting marker with a missing artifact or an exact marker with a
conflicting artifact. `ambiguous` requires an exact marker with ambiguous or
unreadable provider evidence. A marker alone never proves provider success.

Direct command status namespaces are distinct:

| Namespace | Values |
| --- | --- |
| `direct_request_status` | `dry-run`, `reused`, `posted`, `recovered` |
| `direct_warning_status` | `dry-run`, `posted`, `recovered` |
| `direct_reply_status` | `dry-run`, `replied`, `recovered` |
| `direct_edit_status` | `dry-run`, `reused`, `edited`, `recovered` |
| `direct_submit_status` | `dry-run`, `submitted`, `recovered` |
| `resolution_status` | `dry-run`, `resolved`, `recovered`, `already-resolved` |

`dry-run` proves the exact input/target without mutation. `reused` and
`already-resolved` prove existing matching state. `posted`, `replied`,
`edited`, `submitted`, and `resolved` require exact readback. `recovered`
means readback proved a possibly applied prior attempt without retry.

Only `reused`, `posted`, and `recovered` direct request results carry a
persistable request receipt. Only `replied` and `recovered` direct reply
results carry a reply receipt. Resolution `resolved` records that a mutation
was attempted and proven; `recovered` records a current or prior ambiguous
attempt proven by readback. `dry-run` and `already-resolved` record no mutation
attempt. Any uncertain post-attempt failure must report that the mutation may
have applied and forbid retry.

## Issue classification and taxonomy

| Namespace | Values | Meaning |
| --- | --- | --- |
| `tagger_mode` | `issue-classification`, `taxonomy-proposal` | Classify one issue or explicitly propose missing repository taxonomy. |
| `classification_disposition` | `complete-match`, `partial-match`, `no-confident-match`, `no-available-metadata`, `metadata-unavailable` | Completeness and confidence of a metadata match. |
| `application_status` | `not-applicable`, `previewed`, `unchanged`, `applied`, `partially-applied`, `failed` | Whether an issue-classification proposal could apply and what readback proved. |
| `taxonomy_disposition` | `proposal-ready`, `no-taxonomy-gap`, `insufficient-evidence`, `metadata-unavailable` | Whether evidence supports new taxonomy. |

`tagger_mode` is transient routing state, not durable configuration.
Taxonomy proposals never have an `application_status` and never mutate.
An uncertain classification write has no terminal `application_status` until
the exact issue is read back and reconciled.

## Versioning

All versioning values are derived or transient gates; Git tags remain external
Git/provider state.

| Value | Kind | Meaning |
| --- | --- | --- |
| `available` | Derived | The suggested canonical tag is unused. |
| `bootstrap-required` | Derived | No SemVer tags exist and an initial version is needed. |
| `release-in-progress` | Derived | The line already has release-candidate tags. |
| `finalized` | Derived | The stable tag already exists. |
| `blocked-finalized` | Derived | Candidate/final work is blocked because the line is final. |
| `migration-available` | Derived | A stable legacy tag can gain a missing canonical alias. |
| `already-present` | Derived | Canonical and legacy tags resolve to the same commit. |
| `target-conflict` | Derived | The canonical target resolves elsewhere. |
| `source-missing` | Derived | The legacy source commit cannot be resolved. |
| `nothing-to-migrate` | Derived | No stable legacy tags exist. |
| `canonical-format` | Derived | The exact tag matches `vX.Y.Z` or `vX.Y.Z-rc.N`. |
| `blocked-noncanonical` | Gate | The requested tag violates the canonical format. |
| `confirmation-required` | Gate | Exact tag, operation, and commit confirmation is still required. |
| `invalid-input` | Error | Mode, line, or tag input is invalid. |

Resolver comparison states are `resolver-absent`, `resolver-current`,
`resolver-upgrade-available`, `resolver-project-newer`, `resolver-unversioned`,
and `resolver-version-conflict`. They respectively mean no project resolver;
matching version/bytes; a lower project version; a higher project version; no
valid reported version; or equal versions with divergent bytes. Only the last
is a mutation gate.
