# Plan Feature Publication Contract

Use this reference when Plan Feature publishes planning artifacts or returns a
non-mutating proposal. Plan Feature resolves each target from the current Git
remote; GitHub is the authoritative artifact store and `$gitstack:github-issues`
owns transport, mutation safety, and hosted-state verification.

Feature workflows own artifact metadata, label and issue-type semantics,
delivery, branch/PR strategy, and executor permissions. Do not persist those
values as project context or create a repository-local planning mirror.

## GitHub Boundary

Feature Specs, implementation issues, and consumed Ideas are GitHub issues. Use
the exact repository/issue target derived from the affected Git repository and
the feature's explicit repository data. Temporary body files are transport
only, must live outside the repository, and must be removed after use.

Use `$gitstack:github-issues` for issue reads, comments, relationships, types,
labels, and lifecycle transitions. A read or proposal supplies no mutation
authority and must not be upgraded at this boundary. Keep globally durable
hosted refs in the form `owner/repository#<number>` or a canonical hosted URL;
never use a bare issue number as a cross-repository identity.

## Write Mode

| `write_mode` | GitHub behavior |
| --- | --- |
| `apply` | Publish or update hosted issues, verify resulting state, and remove temporary transport files. |
| `propose` | Return proposed titles, bodies, metadata, relationships, and publication order without mutating GitHub or returning executable commands. |

`write_mode` is run-scoped planning authority, not durable project context.
Resolve inspect-only, review-only, dry-run, rehearsal, validation, and proposal
requests to `propose`. Resolve `apply` for an explicit request to create or
update durable planning artifacts.

For `apply`, use non-interpolating temporary writes outside the repository,
verify hosted state after every mutation, remove transport files after use, and
inspect GitHub before retrying a partially completed publication. Never persist
a repository-local planning mirror.

## Recoverable Multi-Repository Publication

For any new multi-repository bundle, Plan Feature owns one recoverable
publication transaction across all roles: predeclare every role, the
parameterized final-body template, and each allowed ref slot. Create uniquely
marked non-executable staging issues for hosted roles whose refs are unknown;
materialize final bodies after every hosted ref is resolved; then use only the
predeclared `edit` substitutions to finalize hosted cross-links. Apply
contract-owned metadata only after each final hosted body verifies.

A retry may resume only an exact transaction identity, role map, complete
reconstructable parameterized templates, allowed ref slots, materialized final
bodies, selected Idea refs plus prior outcomes, and current hosted state.
Foreign or changed targets block. This transaction is run data, not Project
Memory configuration. Never persist an issue that points to a staging identity.

## Stable Feature Spec References

Every handoff from a Feature Spec to generated issues carries `source_spec_ref`:

- applied Feature Spec in one repository or a multi-repository feature:
  `source_spec_ref=owner/repository#<spec-number>` or its canonical hosted URL;
- proposed output before publication:
  `source_spec_ref=proposed-spec:<feature-slug>` for one Feature Spec, or
  `source_spec_ref=proposed-spec:<feature-id>/<repository-key>` for a linked
  multi-repository member.

Proposed multi-repository output carries one canonical lowercase UUID
`feature_id`, the Feature Spec title, `feature_slug`, and one stable lower-kebab
`repository_key` per member. Each key is at most 48 characters, unique inside
the set, persisted in that member's Planning Identity, and frozen with set
membership. Create every member, update every `Feature Spec Set` and Feature
Dependency with globally unambiguous refs, verify exact normalized set
equality, then create issues under their owning Specs. Bare issue numbers are
never executable source identities.

A `proposed-spec:<...>` ref is non-executable. It cannot dispatch an
implementation worker or become durable through permission metadata; publish
the complete linked set first.

## Phase Ownership

- The Feature Spec phase owns new Feature Spec body creation and publication.
  When intake supplies any canonical durable member of a multi-repository
  feature, it traverses its `Feature Spec Set` and validates the complete
  connected implementation set unchanged. For a single Spec, it validates and
  preserves that source body and ref unchanged.
- The issue phase owns desired issue bodies, complete durable state enumeration
  before synthesis, fixed-ID reuse of matching issues, uncovered-scope
  synthesis, missing-issue publication, metadata and parent/sub-issue
  reconciliation, and replacement of proposed refs during applied publication.
  It revalidates the source, the applicable metadata contract, and complete
  hosted state before proposal or mutation and never renumbers a retained issue.
- Both phases carry the same `write_mode`, derived source route, planning
  identity, and `source_spec_ref`.
- `$implement-feature` consumes only a durable hosted Feature Spec ref,
  globally qualified for multi-repository work, never proposed output.

## Durable Targets And Completion

| Feature Spec | Implementation issues |
| --- | --- |
| GitHub Feature Spec issue; multi-repository refs use `owner/repository#<number>` or canonical URLs | GitHub sub-issues under their owning Feature Spec |

Use a GitHub closing keyword or explicit lifecycle transition only when the
consuming workflow has proved its artifact contract. Do not close a parent
artifact from an individual child unless the owning workflow's completion
contract explicitly permits it.

Immediately before a proposal, no-op, or first mutation, re-read the owning
Feature Spec, the current metadata contract, and the complete relevant hosted
state with the same pagination proof used during convergence. If any source,
contract, body, relationship, or candidate absence changed, discard the stale
projection and restart or block. Verify every successful mutation before
moving to the next operation.

Lower-kebab-case values are canonical. Reject noncanonical option values
instead of rewriting them.
