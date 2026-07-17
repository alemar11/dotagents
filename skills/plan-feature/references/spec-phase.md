# Feature Spec Phase

Use this internal phase to turn clarified feature, product, migration,
cross-repository, or workflow intent into a complete Feature Spec. Do not use
it as a public skill.

## Goal

Produce or publish a Feature Spec that can feed the issue phase. If the source
is too vague, return the smallest blocking question set through the caller.

## Boundaries

- Do not implement the feature or split it into issues.
- Do not edit `CONTEXT.md`, domain documents, or ADRs. Carry accepted durable
  knowledge only as optional phase data in `knowledge_delta`; never render it
  in a Feature Spec body.
- Do not invent users, requirements, constraints, or acceptance criteria.
- Use `references/options.md` for `mode` and `write_mode`; do not create another
  phase-level option.
- Treat tracker backend, repository layout, and tracker mappings as Project
  Memory facts.
- Publish only with `write_mode=apply`. With `write_mode=propose`, perform no
  local or hosted write and return proposed bodies, locations, metadata, and
  publication order rather than executable commands.
- Do not create hosted-artifact mirrors or temporary planning trees.
- Load `non-app-delivery.md` only when its current-request predicate is true or
  a canonical durable source Spec carries exactly one target and one resolvable
  `explicit_instruction_ref`.

## Phase Inputs

Receive:

- `mode` and `write_mode`;
- `tracker_backend`, `repository_layout`, and issue-type mappings from Project
  Memory;
- planning identity: `feature_slug` and any selected `product_slug`,
  `project_slug`, `workspace_path`, or `context_file`;
- affected repositories, allowed paths, per-Spec target branch, and any
  parent/child workspace links;
- existing or pending `source_spec_ref` state;
- authored Feature Spec dependency rows;
- optional `knowledge_delta` with `decisions`, `target_surfaces`, and
  `evidence` lists, plus a separate `planning_blockers` list;
- `non_app_delivery_target` and its non-option `explicit_instruction_ref` only
  when the conditional reference was loaded.

Absence of `knowledge_delta` means planning introduced no durable project
knowledge. Do not emit an empty object. Preserve unresolved planning blockers
independently and withhold output until they are resolved or proven
non-blocking.

## Workflow

### 1. Ground In Project Memory

Read the minimum evidence needed to establish the contract:

- `project-memory/config/issue-tracker.md`;
- `project-memory/config/project-layout.md`;
- `project-memory/config/triage-labels.md`;
- `project-memory/config/domain.md` and the selected `CONTEXT.md` when
  terminology or ownership requires them;
- relevant ADRs, product documentation, source, and tests when they constrain
  the feature;
- orchestrator workspace project, repository, and integration-gate documents
  when the selected scope is a multi-repository workspace.

Do not broadly scan unrelated domain or localization material. Widen evidence
only when the current sources are incomplete or contradictory.

When a context map describes multiple products or workspaces, resolve the
selected product, workspace path, context file, and feature slug before
drafting. Stop rather than guess when more than one owner remains plausible.

### 2. Resolve Artifact Targets

Use Project Memory facts to choose locations:

| Repository layout | Tracker backend | Feature Spec location |
| --- | --- | --- |
| `single-repository` | `github` | `Feature Spec: <Feature Name>` issue in the current repository. |
| `single-repository` | `local` | `planning/features/<feature-slug>/SPEC.md`. |
| `monorepo` | `github` or `local` | One Feature Spec scoped to the selected product/workspace and its configured tracker. |
| `multi-repository-workspace` | Per owning repository | Accepted parent/global Feature Spec when one exists, plus linked repo-scoped partial Feature Specs for affected child repositories. |

Do not invent a global workspace Feature Spec. Use one only when it is the
accepted planning source. Resolve every affected child repository's tracker
and topology facts independently. A GitHub child gets a repo-scoped hosted
Feature Spec; a local child gets its configured local path.

For multi-repository work:

1. Produce the accepted parent/global artifact first when one is required.
2. Produce every child partial to obtain stable durable or proposed refs. In
   proposal mode use
   `proposed-spec:<project_slug>/<feature_slug>/<repository_slug>` for each
   partial; never reuse the parent ref for a child.
   In apply mode, make every multi-repository ref globally unambiguous: use
   `owner/repository#<number>` or a canonical hosted URL for GitHub and
   `<repository_slug>/<repo-relative-spec-path>` for local Markdown. Use those
   same refs in the repo-to-child mapping, sibling links, and Feature
   Dependencies; bare `#<number>` and bare repo-relative paths are invalid in a
   multi-repository bundle.
3. Choose the one repository that owns post-merge cross-repository integration
   proof from accepted scope and evidence;
   stop if that owner is ambiguous. Create a dedicated integration partial with proposed ref
   `proposed-spec:<project_slug>/<feature_slug>/<repository_slug>/integration`.
   Its mandatory Feature Dependencies table contains one edge to every
   implementation partial, so it cannot execute until every upstream partial
   has merged. Its generated integration task owns the cross-repository proof.
   The integration owner is an affected child repository selected from evidence;
   this does not require or create a coordination repository. Create this
   partial independently of `knowledge_delta`, and never render the delta in its
   Feature Spec body. Require a bounded repo-owned integration vehicle that can
   produce a concrete path change and real PR in addition to validation proof;
   withhold the App-compatible bundle if no such vehicle exists. Derive its
   target branch as `<ordinary_target_branch_name>-integration` from the
   resolved ordinary branch in the same repository; the default result is
   `feature/<feature_slug>-integration`.
4. Give the integration partial a durable identity distinct from the ordinary
   implementation partial in the same repository. On GitHub, title it
   `Feature Spec: <Feature Name> - Integration`, include
   `Partial role: integration` in its Planning Identity, and use its own
   `owner/repository#<number>` ref or canonical hosted URL as the applied
   `source_spec_ref`. With the local backend, write it to
   `planning/features/<feature-slug>/integration/SPEC.md` or the configured
   equivalent, expose its applied source ref with the owning repository slug,
   and keep its issues under the matching `integration/issues/` subtree.
5. Validate every implementation-eligible partial as one bundle: each
   `(affected_repository, target_branch_name)` pair must have exactly one
   Feature Spec owner. The same branch string may appear in different
   repositories, but two partials in the same repository must not share it,
   even when paths are disjoint or dependencies serialize them. Resolve collisions
   before new publication; for an immutable existing source, stop rather than
   rename it.
6. Add the complete repo-to-child-ref mapping and sibling links to every child
   and integration partial.
7. Start issue generation only after the complete linked artifact set exists.

Mixed child tracker backends are valid because routing is an owning-repository
fact, not one run-wide choice. Preserve one publication plan ordered by parent,
implementation partials, the integration partial, cross-link
updates, then generated issues. Proposed refs are inspection-only and never
agent-executable.

### 3. Gate An Existing Source Or Draft

Use user conversation, clarification output, existing issues or documents,
project memory, and relevant repository behavior as sources. Ask only for
decisions that materially change scope, acceptance, dependencies, validation,
or repository ownership.

For `mode=issues-from-existing-spec`, do not draft or update the source. Carry
the original durable body and `source_spec_ref` unchanged through the dependency
and body gates below. After both gates pass, return that exact source to the
issue phase and skip Apply Or Propose. If a missing section, blocking question,
new decision, schema repair, or content correction would change the source,
stop and require a separate explicitly authorized Feature Spec update before
issue generation. Never switch this run to `full-flow`, rewrite the source, or
publish a repaired copy. Reject a source containing `knowledge_delta` or
`## Domain Knowledge Handoff` as incompatible structured input. The issue phase
may receive a delta only as explicit accepted invocation data kept separate from
this unchanged source. Normalize each of that delta's target surfaces to a
repository and repo-relative path, then require it to be contained by the
source's unchanged affected repositories and allowed paths. An out-of-scope or
ambiguously owned target blocks issue generation; never widen the immutable
source or a future issue to accommodate it.

For `full-flow` and `spec-only`, draft with `references/spec-template.md` unless
the repository has a stronger Feature Spec format. Keep it
implementation-facing:

- problem, users, goals, and non-goals;
- functional and integration requirements;
- product and repository scope;
- affected repositories, allowed paths, and the target branch shared inside
  this Feature Spec;
- acceptance criteria and validation expectations;
- cross-repository contracts and integration gates;
- risks, open questions, and issue-splitting notes.

The normal Feature Spec does not carry selectable delivery, review,
permission, pull-request-count, scheduling, or tracker-closeout fields. Its
generated issues are compatible with `$implement-feature`'s fixed flow.

When the explicit non-App exception applies, include exactly one selected
`non_app_delivery_target`, exactly one resolvable `explicit_instruction_ref`,
and a prominent App-incompatibility statement. The ref is evidence data, not an
option or issue field. Do not add authority fields.

### 4. Validate Feature Dependencies

For `full-flow` and `spec-only`, create the mandatory
`## Feature Dependencies` table with exactly `upstream_feature_spec_ref` and
`dependency_reason`. For `issues-from-existing-spec`, require and validate that
exact existing section without adding, removing, or rewriting anything.

For every edge:

- require a unique durable upstream ref, or a proposed ref only in
  `write_mode=propose`;
- in a multi-repository applied bundle, require every upstream ref to identify
  its owning repository through `owner/repository#<number>`, a canonical hosted
  URL, or `<repository_slug>/<repo-relative-spec-path>`;
- reject self, duplicate, missing, and ambiguous refs;
- require a concrete portable reason;
- normalize upstream-to-downstream edges and validate the reachable Feature
  Spec graph is acyclic;
- treat the edge as waiting for upstream merge and integration proof.

An empty table body means no authored cross-Spec dependencies. The section and
its two canonical columns are mandatory, including for
`mode=issues-from-existing-spec`. A Feature Spec without them is incompatible structured
input: stop and require an explicitly authorized canonical update
before issue generation. Never interpret absence as an empty edge set or infer
edges from prose, issue ordering, branch names, or similar titles.

Keep cross-Spec edges separate from generated issue dependencies. The issue
phase may validate and preserve the Feature Spec graph but never copies those
refs into issue `dependency_ids`.

### 5. Sanitize And Gate The Body

For `full-flow` and `spec-only`, replace local filesystem evidence with portable
references before return or publication. For `issues-from-existing-spec`,
validate without modifying the body; any nonportable evidence blocks issue
generation until a separate explicitly authorized source update lands.

Portable forms are:

- current repository: `path/to/file` or `path/to/file:line`;
- sibling repository: `<repo-slug>/<repo-relative-path>`;
- hosted evidence: URL, issue, PR, or `owner/repo:path`;
- local-only evidence without a stable identity: a descriptive source label.

Then verify:

- no machine-local absolute path remains;
- no runtime worker or App-session setting is present;
- the source, scope, acceptance, validation, and dependency contract are
  complete;
- open questions are empty or proven non-blocking;
- a present phase-level knowledge delta has explicit portable decisions,
  targets, and evidence, while no Feature Spec body contains `knowledge_delta`
  or a `## Domain Knowledge Handoff` section;
- every knowledge target has one unambiguous repository owner and lies inside
  the accepted Feature Spec repository/path scope, so the final issue can cover
  it without a later scope expansion;
- every multi-repository bundle has exactly one dedicated integration partial
  with Feature Dependencies covering every implementation
  partial, and its title or path plus `Partial role: integration` distinguish it
  from the implementation partial in the same repository;
- non-App data is absent unless the conditional reference was loaded; when
  present, exactly one target and one `explicit_instruction_ref` exist in the
  owning section, and the ref resolves to an authorized-user instruction that
  selects the same target and scope;
- the body contains no workflow status field such as `Status: Draft`.

Withhold the artifact and return blockers when the gate fails.

### 6. Apply Or Propose

This step does not run for `mode=issues-from-existing-spec`; that branch returns
the unchanged durable source after the dependency and body gates pass.

It also performs no write for `mode=spec-only` with a nonempty
`knowledge_delta`, regardless of the resolved `write_mode`. Return a blocked,
non-durable preview with deterministic proposed refs and the exact delta as
report data, state that publication was withheld and no durable source exists,
and require a later explicit `full-flow` run. Do not silently downgrade
`write_mode`, persist a delta marker, or publish a source that a later
`issues-from-existing-spec` run could consume without the payload.

Read tracker and type mappings immediately before output.

- `write_mode=apply`, GitHub: publish the sanitized ordinary Feature Spec as
  `Feature Spec: <Feature Name>` and, for every multi-repository bundle, exactly
  one dedicated integration partial as
  `Feature Spec: <Feature Name> - Integration` through
  `$gitstack:github-issues`. Translate
  each write to GitStack-owned `mutation_mode=apply`, its exact target, and one
  canonical `issue_operation`; apply the mapped feature type when supported,
  verify every mutation, and retain the hosted issue number or URL as
  `source_spec_ref`. In multi-repository work, store `owner/repository#<number>`
  or the canonical URL, never a bare issue number.
- `write_mode=apply`, local: write the resolved Feature Spec path and use that
  durable path as `source_spec_ref`. Prefix it with `<repository_slug>/` in a
  multi-repository bundle. A dedicated integration partial and its issues use
  the distinct `integration/SPEC.md` and `integration/issues/` subtrees beneath
  the resolved feature directory.
- `write_mode=propose`: write nothing. Return the sanitized body, intended
  location, mapped metadata, and deterministic source identity:
  `proposed-spec:<feature_slug>` for a single Feature Spec,
  `proposed-spec:<project_slug>/<feature_slug>` for a multi-repository parent,
  or `proposed-spec:<project_slug>/<feature_slug>/<repository_slug>` for a
  repo-scoped implementation partial. A dedicated integration partial uses
  `proposed-spec:<project_slug>/<feature_slug>/<repository_slug>/integration`.
  Return publication order and state that every proposed source is
  non-executable until applied.

`write_mode=propose` never invokes GitStack. GitStack does not interpret Plan
Feature's tracker or write policy.

For hosted publication, use transient transport outside the repository and
remove it after verified mutation. Do not construct raw mutating commands with
generated Markdown.

### 7. Report

Return:

- title, feature slug, source ref, and intended or actual location;
- `mode`, `write_mode`, tracker backend, repository layout, and selected
  context identity;
- affected repositories, allowed paths, and each per-Spec target branch;
- validated Feature Spec dependencies and acyclicity result;
- workspace parent/child refs and publication order when applicable;
- issue type applied or proposed;
- open blockers and withheld output;
- derived domain capture outcome and future closeout owner;
- explicit App incompatibility when a non-App target is present.

When `knowledge_delta` is present, report `capture_outcome=deferred`. In
`mode=spec-only`, return the exact delta as non-persisted report data and report
`future_closeout_issue_source_spec_ref: <source_spec_ref>` for a single Spec or
`future_closeout_issue_source_spec_ref: <integration_source_spec_ref>` for a
multi-repository bundle. The latter must be the dedicated integration partial's
ref, never the parent or an ordinary partial ref. This is report data identifying
the future issue's owning Spec, not a task ref or selectable field. State that
publication was withheld, no durable source was created, and the standalone
preview is not App-executable until a later explicit `full-flow` run carries the
exact delta and persists it on its final issue. In `full-flow`, pass the delta
directly to the issue phase. Otherwise report
`capture_outcome=no-durable-change`. The result is report-only; this phase never
persists it in the Feature Spec or reports domain knowledge as captured.
