# Tracker Publishing Contract

Use this reference when `$plan-feature` needs to publish planning artifacts or
return a non-mutating proposal. `project-memory/config/issue-tracker.md` owns
durable tracker routing; this file owns the shared `write_mode` behavior.

## Tracker Backend

Use `tracker_backend` to choose the durable artifact target:

- `github`: Feature Specs and implementation issues are GitHub issues managed
  through `$gitstack:github-issues`;
- `local`: Feature Specs and implementation issues are Markdown files in the
  configured local conventions.

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

## Stable Feature Spec References

Every handoff from a Feature Spec to generated issues carries
`source_spec_ref`:

- applied hosted Feature Spec in one repository:
  `source_spec_ref=#<spec-number>`;
- applied hosted partial in a multi-repository bundle:
  `source_spec_ref=owner/repository#<spec-number>` or its canonical hosted URL;
- applied local Feature Spec in one repository:
  `source_spec_ref=<repo-relative-spec-path>`;
- applied local partial in a multi-repository bundle:
  `source_spec_ref=<repository-slug>/<repo-relative-spec-path>`;
- applied hosted integration partial: its own
  `source_spec_ref=owner/repository#<integration-spec-number>` or canonical URL
  in a multi-repository bundle, produced by the distinct title `Feature Spec:
  <Feature Name> - Integration` and body marker `Partial role: integration`;
- applied local integration partial:
  `source_spec_ref=<repository-slug>/planning/features/<feature-slug>/integration/SPEC.md`
  in a multi-repository bundle, or the unqualified configured path only in one
  repository; never the implementation partial's `SPEC.md`;
- proposed output before publication:
  `source_spec_ref=proposed-spec:<feature-slug>` for one Feature Spec,
  `source_spec_ref=proposed-spec:<project-slug>/<feature-slug>` for a
  multi-repository parent, or
  `source_spec_ref=proposed-spec:<project-slug>/<feature-slug>/<repository-slug>`
  for a repo-scoped implementation partial. A dedicated integration partial
  uses
  `source_spec_ref=proposed-spec:<project-slug>/<feature-slug>/<repository-slug>/integration`.

Proposed output also carries the Feature Spec title, `feature_slug`,
`project_slug` when applicable, and enough proposal identity to keep child
issue bodies attached to the same proposed parent. For one Feature Spec, create
that Spec, replace its proposed ref with the resulting durable ref, then create
and attach its issues. For multi-repository work, create the accepted parent
when present, create every implementation partial, create the integration
partial after its upstream refs are durable, update repo-to-child mappings,
sibling links, and Feature Dependencies with the same globally unambiguous
`owner/repository#<number>`, hosted URL, or
`<repository-slug>/<repo-relative-spec-path>` identities, then create issues
under their owning Specs. Bare issue numbers and bare repo-relative paths are
repository-local and invalid across siblings.

A `proposed-spec:<...>` ref is non-executable. It cannot dispatch an
implementation worker or become durable through permission metadata; publish
the parent or write the canonical local file first.

## Phase Ownership

- The `$plan-feature` Feature Spec phase owns Feature Spec body creation,
  Feature Spec publication, and the `source_spec_ref` it returns.
- The `$plan-feature` issue phase owns generated issue bodies, issue
  publication, parent/child relationships, and replacement of proposed refs when
  applying hosted publication.
- `$plan-feature` carries the same `tracker_backend`, `write_mode`, planning
  identity, and `source_spec_ref` through both phases.
- `$implement-feature` consumes only a durable hosted or local Feature Spec
  ref, globally qualified for multi-repository work, never proposed output.

## Durable Targets

| Tracker backend | Feature Spec | Implementation issues |
| --- | --- | --- |
| `github` | GitHub Feature Spec issue; multi-repository refs use `owner/repository#<number>` or canonical URLs, and a dedicated integration partial uses a separate `Feature Spec: <Feature Name> - Integration` issue in its owner repository | GitHub sub-issues under their owning Feature Spec; integration issues use the integration partial's distinct globally qualified hosted ref |
| `local` | `planning/features/<feature-slug>/SPEC.md` or `orchestration/<project-slug>/features/<feature-slug>/SPEC.md`; multi-repository refs prefix the owning repository slug, and an integration partial appends `/integration/SPEC.md` beneath the feature directory | `planning/features/<feature-slug>/issues/<NN>-<slug>.md` or its configured equivalent; integration issues append `/integration/issues/<NN>-<slug>.md` and complete under `/integration/issues/done/` beneath the feature directory |

Lower-kebab-case values are canonical. Reject noncanonical option values
instead of rewriting them.
