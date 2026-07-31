# Tracker Publishing Contract

Use this reference when `$plan-feature` needs to publish planning artifacts or
return a non-mutating proposal. `project-memory/config/issue-tracker.md` owns
durable tracker routing; this file owns the shared `write_mode` behavior.

## Tracker Provider

Feature Specs and implementation issues are GitHub issues managed through
`$gitstack:github-issues`. Do not store current-run mutation intent,
delivery policy, branch strategy, or executor authorization in Project Memory.

## Write Mode

| `write_mode` | GitHub behavior |
| --- | --- |
| `apply` | Publish or update hosted issues, verify resulting tracker state, and remove temporary transport files. |
| `propose` | Return proposed titles, bodies, metadata, relationships, and publication order without mutating GitHub or returning executable commands. |

`write_mode` is run-scoped authority, not durable configuration. Resolve
inspect-only, review-only, dry-run, rehearsal, validation, and proposal
requests to `propose`. Resolve `apply` only from explicit write authority for
the selected planning scope.

For `apply`, temporary body files are transport only. Keep them outside the
repository, use non-interpolating writes, verify hosted state after each
mutation, remove them after use, and inspect GitHub before retrying a partially
completed publication. Never persist a repository-local planning mirror.

For any multi-repository new-source bundle, Plan Feature owns one recoverable
publication transaction across all roles: predeclare every role, parameterized
final-body template, allowed ref slot, and optional exact final-only
body-metadata insertion. Create uniquely marked non-executable staging issues
for hosted roles whose refs are unknown; materialize and hash final bodies after
every hosted ref is resolved; then use only the predeclared `edit` substitutions
and body-metadata insertion to finalize hosted cross-links. Native Issue Type or
label metadata applies only after each final hosted body verifies; a configured
body-convention is absent from staging and verified inside the final body. A
retry may resume only an exact transaction identity, role map, complete
reconstructable parameterized templates and hashes, allowed ref slots, the
optional body-metadata slot and value, any materialized final hashes, selected
Idea refs plus prior outcomes, and current tracker state; a hash alone is
insufficient. Foreign or changed targets block. This transaction is run data,
not Project Memory configuration.

When a consumed GitHub mapping uses `label`, Plan Feature verifies the exact
configured label before the dependent artifact or metadata mutation. An
applied run may create and verify only that missing mapped label through
`issue_operation=create-label`; a proposal reports the intended operation
without mutation. Project Memory setup records mappings but does not create
repository labels.

## Stable Feature Spec References

Every handoff from a Feature Spec to generated issues carries
`source_spec_ref`:

- applied Feature Spec in one repository or a multi-repository feature:
  `source_spec_ref=owner/repository#<spec-number>` or its canonical hosted URL;
- proposed output before publication:
  `source_spec_ref=proposed-spec:<feature-slug>` for one Feature Spec, or
  `source_spec_ref=proposed-spec:<feature-id>/<repository-key>` for a linked
  multi-repository member.

Proposed multi-repository output carries one canonical lowercase UUID
`feature_id`, the Feature Spec title, `feature_slug`, and one stable
lower-kebab `repository_key` per member. Each key is at most 48 characters,
unique inside the set, persisted in that member's Planning Identity, and frozen
with set membership. Create every member, update every `Feature Spec Set` and
Feature Dependency with globally unambiguous refs, verify exact normalized set
equality, then create issues under their owning Specs. Bare issue numbers are
never executable source identities.

A `proposed-spec:<...>` ref is non-executable. It cannot dispatch an
implementation worker or become durable through permission metadata; publish
the complete linked set first.

## Phase Ownership

- The `$plan-feature` Feature Spec phase owns new Feature Spec body creation and
  publication. When intake supplies any canonical durable member of a
  multi-repository feature, it traverses its `Feature Spec Set` and validates
  the complete connected implementation set unchanged. For a single Spec, it
  validates and preserves that source body and ref unchanged.
- The `$plan-feature` issue phase owns desired issue bodies, complete durable
  state enumeration before synthesis, fixed-ID reuse of matching issues,
  uncovered-scope synthesis, missing-issue publication, metadata and
  parent/sub-issue reconciliation, and replacement of proposed refs during
  applied publication. It revalidates source, mappings, and complete tracker
  state before proposal or mutation and never renumbers a retained issue.
- `$plan-feature` carries the same `write_mode`, derived source route, planning
  identity, and `source_spec_ref` through both phases.
- `$implement-feature` consumes only a durable hosted Feature Spec ref,
  globally qualified for multi-repository work, never proposed output.

## Durable Targets

| Feature Spec | Implementation issues |
| --- | --- |
| GitHub Feature Spec issue; multi-repository refs use `owner/repository#<number>` or canonical URLs | GitHub sub-issues under their owning Feature Spec |

Lower-kebab-case values are canonical. Reject noncanonical option values
instead of rewriting them.
