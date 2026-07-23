# Tracker Publishing Contract

Use this reference when `$plan-feature` needs to publish planning artifacts or
return a non-mutating proposal. `project-memory/config/issue-tracker.md` owns
durable tracker routing; this file owns the shared `write_mode` behavior.

## Tracker Backend

Use `tracker_backend` to choose the durable artifact target:

- `github`: Feature Specs and implementation issues are GitHub issues managed
  through `$gitstack:github-issues`;
- `local`: Feature Specs and implementation issues are Markdown files under
  `planning/features/<feature-slug>/` inside each owning repository.

Reject tracker configuration without a canonical `tracker_backend`. Do not
store current-run mutation intent, implementation delivery policy, branch
strategy, or executor authorization in Project Memory.

## Write Mode

| `write_mode` | GitHub backend | Local backend |
| --- | --- | --- |
| `apply` | Publish or update hosted issues, verify resulting tracker state, and remove temporary transport files. | Write or update durable Feature Spec and issue files at their canonical paths. |
| `propose` | Return proposed titles, bodies, metadata, relationships, and publication order without mutating GitHub or returning executable commands. | Return proposed bodies and canonical target paths without writing tracker files. |

`write_mode` is run-scoped authority, not durable configuration. Resolve
inspect-only, review-only, dry-run, rehearsal, validation, and proposal
requests to `propose`. Resolve `apply` only from explicit write authority for
the selected planning scope.

For GitHub `apply`, temporary body files are transport only. Keep them outside
the repository, use non-interpolating writes, verify tracker state after each
mutation, remove them after use, and inspect GitHub before retrying a partially
completed publication. Never persist a repo-local mirror solely for transport.

For any multi-repository new-source bundle, Plan Feature owns one recoverable
publication transaction across all roles: predeclare every role, parameterized
final-body template, allowed ref slot, and optional exact final-only
body-metadata insertion. Create uniquely marked
non-executable staging issues only for hosted roles whose refs are unknown;
materialize and hash final bodies after every hosted or deterministic local ref
is resolved; then use only the predeclared `edit` substitutions and body-
metadata insertion to finalize hosted cross-links. Native Issue Type or label
metadata applies only after each final hosted body verifies; a configured body
convention is absent from staging and verified inside the final body. In a
mixed-backend bundle, keep local bodies unwritten
until the hosted subset is final, then create only missing predeclared local
files with qualified final refs and verify one connected hosted/local set. The
same identity makes an all-local partial write recoverable through exact missing
file creates. A retry may resume only an exact transaction identity, role map,
complete reconstructable parameterized templates and hashes, allowed ref slots,
the optional body-metadata slot and value, any materialized final hashes,
selected Idea refs plus prior outcomes, and current tracker state; a hash alone
is insufficient. Foreign or changed targets block. This transaction is run
data, not Project Memory configuration.

When a consumed GitHub mapping uses `label`, Plan Feature verifies the exact
configured label before the dependent artifact or metadata mutation. An applied
run may create and verify only that missing mapped label through
`issue_operation=create-label`; a proposal reports the intended operation
without mutation. Project Memory setup records the mapping but does not create
repository labels.

## Stable Feature Spec References

Every handoff from a Feature Spec to generated issues carries
`source_spec_ref`:

- applied hosted Feature Spec in one repository:
  `source_spec_ref=#<spec-number>`;
- applied hosted partial in a multi-repository bundle:
  `source_spec_ref=owner/repository#<spec-number>` or its canonical hosted URL;
- applied local Feature Spec in one repository:
  `source_spec_ref=planning/features/<feature-slug>/SPEC.md`;
- applied local partial in a multi-repository bundle:
  `source_spec_ref=<repository-slug>/planning/features/<feature-slug>/SPEC.md`;
- proposed output before publication:
  `source_spec_ref=proposed-spec:<feature-slug>` for one Feature Spec,
  `source_spec_ref=proposed-spec:<project-slug>/<feature-slug>` for a
  multi-repository parent, or
  `source_spec_ref=proposed-spec:<project-slug>/<feature-slug>/<repository-slug>`
  for a repo-scoped implementation partial.

Proposed output also carries the Feature Spec title, `feature_slug`,
`project_slug` when applicable, and enough proposal identity to keep child
issue bodies attached to the same proposed parent. For one Feature Spec, create
that Spec, replace its proposed ref with the resulting durable ref, then create
and attach its issues. For multi-repository work, create the accepted parent
when present, create every implementation partial, update repo-to-child mappings,
sibling links, and Feature Dependencies with the same globally unambiguous
`owner/repository#<number>`, hosted URL, or
`<repository-slug>/planning/features/<feature-slug>/SPEC.md`
identities, then create issues under their owning Specs. Bare issue numbers and
bare repo-relative paths are repository-local and invalid across siblings.

A `proposed-spec:<...>` ref is non-executable. It cannot dispatch an
implementation worker or become durable through permission metadata; publish
the parent or write the canonical local file first.

## Phase Ownership

- The `$plan-feature` Feature Spec phase owns new Feature Spec body creation and
  publication. When intake supplies any canonical durable member of a
  multi-repository bundle, the phase traverses the canonical mapping and
  validates the complete connected parent and implementation set
  unchanged. For a single Spec, it validates and preserves that source body and
  ref unchanged.
- The `$plan-feature` issue phase owns desired issue bodies,
  complete durable-state enumeration before synthesis, fixed-ID reuse of
  matching durable issues, uncovered-scope synthesis, missing-issue publication,
  metadata and parent/sub-issue reconciliation, and replacement of proposed
  refs when applying hosted publication. It revalidates the source, mapping,
  and complete tracker state before proposal or mutation and never renumbers a
  retained issue.
- `$plan-feature` carries the same `tracker_backend`, `write_mode`, derived
  source route, planning identity, and `source_spec_ref` through both phases.
- `$implement-feature` consumes only a durable hosted or local Feature Spec
  ref, globally qualified for multi-repository work, never proposed output.

## Durable Targets

| Tracker backend | Feature Spec | Implementation issues |
| --- | --- | --- |
| `github` | GitHub Feature Spec issue; multi-repository refs use `owner/repository#<number>` or canonical URLs | GitHub sub-issues under their owning Feature Spec |
| `local` | `planning/features/<feature-slug>/SPEC.md` inside each owning repository; multi-repository refs prefix that repo-relative path with the owning repository slug | `planning/features/<feature-slug>/issues/<NN>-<slug>.md` inside the owning repository |

Lower-kebab-case values are canonical. Reject noncanonical option values
instead of rewriting them.
