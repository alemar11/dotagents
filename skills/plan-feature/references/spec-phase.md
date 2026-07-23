# Feature Spec Phase

Use this internal phase to turn clarified feature, product, migration,
cross-repository, or workflow intent into a complete Feature Spec. Do not use
it as a public skill.

## Goal

Produce, publish, or validate a Feature Spec that can feed the issue phase. An
existing source preserves stable fields while accepting current executor-owned
acceptance checkbox markers. If the source is too vague, return the smallest
blocking question set
through the caller.

## Boundaries

- Do not implement the feature or split it into issues.
- Do not edit `CONTEXT.md`, domain documents, or ADRs. Carry accepted durable
  knowledge only as optional phase data in `knowledge_delta`; never render it
  in a Feature Spec body.
- Do not invent users, requirements, constraints, or acceptance criteria.
- Use `references/options.md` for `write_mode`; consume the derived
  `source_route` and do not create another phase-level option.
- Treat tracker backend, repository layout, and tracker mappings as Project
  Memory facts. Resolve the canonical `feature` type mapping before rendering
  or validating a Feature Spec. Local trackers require `local-header`; GitHub
  requires one supported hosted transport.
- Publish only with `write_mode=apply`. With `write_mode=propose`, perform no
  local or hosted write and return proposed bodies, locations, metadata, and
  publication order rather than executable commands.
- Do not create hosted-artifact mirrors or temporary planning trees.
- Load `idea-source.md` when selected new-source `source_idea_refs` or derived
  existing-source `bound_source_idea_refs` are present. Explicit discovery must
  already have completed and produced a selection before new-source drafting.
  Bound refs are immutable continuation evidence only; never draft from them.

## Phase Inputs

Receive:

- `write_mode` and the frozen derived `source_route`;
- `tracker_backend`, `repository_layout`, and issue-type mappings with explicit
  transport plus exact tracker value from Project Memory;
- one stable `delivery_type` per implementation-eligible Spec: `github-pr` or
  `local-branch`; this is accepted execution data, not a Plan Feature option or
  Project Memory setting;
- planning identity: `feature_slug` and any selected `product_slug`,
  `project_slug`, `workspace_path`, or `context_files`, containing every
  applicable available root, child-root, and matched scoped context used for
  planning;
- affected repositories, allowed paths, per-Spec target branch, and any
  parent/child workspace links;
- intake, existing, or pending `source_spec_ref` state;
- optional explicitly selected `source_idea_refs`, their normalized canonical
  section evidence, verified prior partial-outcome refs, transient per-element
  durable coverage maps or report-only intended projections, and per-Spec
  relevance mapping, already constrained to one bounded feature;
- optional derived `bound_source_idea_refs` from exact `- Source Idea:` lines
  in the immutable existing-source Spec set, used only for continuation
  validation and later lifecycle reconciliation;
- optional exact multi-repository publication-continuation handoff containing
  transaction identity, role-to-target/ref map, reconstructable parameterized
  templates, ref and optional body-metadata slots, selected Idea and
  prior-outcome refs, any complete `knowledge_delta`, and verified completed
  plus exact missing operations;
- authored Feature Spec dependency rows;
- optional `knowledge_delta` with `decisions`, `target_surfaces`, and
  `evidence` lists, plus a separate `planning_blockers` list;

Absence of `knowledge_delta` means planning introduced no durable project
knowledge. Do not emit an empty object. Preserve unresolved planning blockers
independently and withhold output until they are resolved or proven
non-blocking.

When a publication-continuation handoff is present, validate its complete
identity, payload, and current tracker/file state before drafting or mutation.
Accept it only on the frozen new-source continuation route; omission, mismatch,
or an unreconstructable template blocks.

## Workflow

### 1. Ground In Project Memory

Read the minimum evidence needed to establish the contract:

- `project-memory/config/issue-tracker.md`;
- `project-memory/config/project-layout.md`;
- `project-memory/config/triage-labels.md`;
- root `CONTEXT.md` first when it exists, treating the current Git repository
  as a selected root; in a coordination workspace, also select affected child
  roots from its `Repository Registry` and read each available child root
  context; then
  select every available scoped `CONTEXT.md` matched by affected paths in each
  selected root's `Scoped Contexts` table and read every available matched
  context before drafting. For a root or matched route with no context, use
  repository evidence without inventing terminology or a dangling context
  pointer;
- relevant ADRs, product documentation, source, and tests when they constrain
  the feature;
- coordination-root context, an accepted parent Feature Spec when one exists,
  repo-owned partial Feature Specs, and named integration-gate evidence when
  the selected scope is a multi-repository workspace.

Do not broadly scan unrelated domain or localization material. Widen evidence
only when the current sources are incomplete or contradictory.

On the new-source route, when `source_idea_refs` are present, run ordinary
durable-artifact validation through `idea-source.md` before drafting. Read every
canonical Idea section and planning outcome, validate tracker ownership and
prior partial Feature Spec refs, and derive the cumulative covered and
remaining scope. Reject proposed refs, missing marker mappings, consumed or
typed GitHub Ideas, malformed local Ideas, and ambiguous repository ownership.

On the existing-source route, validate `bound_source_idea_refs` through
`idea-source.md` without drafting: require the exact complete set from the
immutable Spec bodies, validate each Idea and outcome history, and derive
coverage from the Idea content plus unchanged Specs rather than from links
alone. If explicit `source_idea_refs` were supplied, require exact set equality
with the bound refs. Any mismatch blocks. A missing Idea marker mapping does not
block planning runs whose Spec set contains no Idea refs.

Do not apply that ordinary consumed-source rejection to source-only recovery.
Plan Feature must route reconciliation-only recovery before this phase; a
recovery invocation never drafts or republishes a Feature Spec.

When root context routes multiple products or workspaces, resolve the selected
product, workspace path, applicable context files, and feature slug before
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
Feature Spec; a local child gets
`planning/features/<feature-slug>/SPEC.md` inside that repository.

For multi-repository work:

1. Produce the accepted parent/global artifact first when one is required.
2. Produce every child partial to obtain stable durable or proposed refs. In
   proposal mode use
   `proposed-spec:<project_slug>/<feature_slug>/<repository_slug>` for each
   partial; never reuse the parent ref for a child.
   In apply mode, make every multi-repository ref globally unambiguous: use
   `owner/repository#<number>` or a canonical hosted URL for GitHub and
   `<repository-slug>/planning/features/<feature-slug>/SPEC.md` for
   local Markdown. Use those same refs in the repo-to-child mapping, sibling
   links, and Feature Dependencies; bare `#<number>` and bare repo-relative
   paths are invalid in a multi-repository bundle.
3. Assign each cross-repository boundary to one existing implementation partial
   that can execute the combined proof within its accepted repository, paths,
   tools, and validation budget. Multiple boundaries may have different owners:
   for example, web owns web-to-backend proof and mobile owns mobile-to-backend
   proof against the same backend revision. Name the required peer Specs in the
   owner's Feature Dependencies and include the executable Integration Execution
   Contract in that existing partial. If no existing partial can own a required
   bundle-wide proof, withhold the bundle; never create a dedicated integration
   Spec or future worker as a fallback.
4. Validate every implementation-eligible partial as one bundle: each
   `(affected_repository, target_branch_name)` pair must have exactly one
   Feature Spec owner. The same branch string may appear in different
   repositories, but two partials in the same repository must not share it,
   even when paths are disjoint or dependencies serialize them. Resolve collisions
   before new publication; for an immutable existing source, stop rather than
   rename it.
5. Add the complete repo-to-child-ref mapping and sibling links to every child.
6. Start issue generation only after the complete linked artifact set exists.

Mixed child tracker backends are valid because routing is an owning-repository
fact, not one run-wide choice. Preserve one publication plan ordered by parent,
implementation partials, cross-link updates, then
generated issues. Proposed refs are inspection-only and never agent-executable.
In apply mode, place every role, including an all-local bundle, in one
recoverable publication transaction. Hosted roles use staging when their refs
are unknown. Keep deterministic local bodies unwritten until every hosted ref
is known and every hosted body is final; then write the local bodies with
qualified final refs and verify the hosted and local artifacts as one connected
set. Never persist a local body that points to a staging identity.

### 3. Gate An Existing Source Or Draft

Use user conversation, clarification output, existing issues or documents,
project memory, and relevant repository behavior as sources. Ask only for
decisions that materially change scope, acceptance, dependencies, validation,
or repository ownership.

On the existing-source route, do not draft or update the source. Carry the
current durable body and intake `source_spec_ref` through the dependency and
body gates below. Compare stable fields directly while treating acceptance
checkbox markers as executor-owned progress: preserve their current state, but
require criterion text, count, and order to remain unchanged. After both gates
pass, return that current source to the issue phase and skip Apply Or Propose.
If a missing section, blocking
question, new decision, schema repair, or content correction would change the
source, stop and require a separate explicitly authorized Feature Spec update
before issue generation. Never rewrite the source or publish a repaired copy.
Reject a source containing `knowledge_delta` or
`## Domain Knowledge Handoff` as incompatible structured input. The issue phase
may receive a delta only as explicit accepted invocation data or an exact
continuation handoff kept separate from this unchanged source. Normalize each of
that delta's target surfaces to a
repository and repo-relative path, then require it to be contained by the
source's unchanged affected repositories and allowed paths. An out-of-scope or
ambiguously owned target blocks issue generation; never widen the immutable
source or a future issue to accommodate it.

When the intake source is any member of a multi-repository bundle, traverse its
canonical parent, repo-to-child, sibling, and Feature Dependency links to load
the complete connected coordination and implementation Spec set. Validate every
body's stable fields and ref through the same gates,
preserving current acceptance checkbox markers. The
coordination parent owns no generated implementation issues; pass only
implementation-eligible partials to issue generation. A missing, ambiguous,
disconnected, or incompatible linked source blocks the run instead of being
drafted or repaired.

A missing sibling map, Feature Dependency, or other relationship represented
inside an immutable Feature Spec body is a source-contract failure. Do not hand
it to the issue phase as a repairable tracker relationship.

On the existing-source route, preserve every `- Source Idea:` line unchanged.
The Spec phase never adds, removes, or rewrites Idea evidence. Bound refs may
drive lifecycle reconciliation only after the issue phase verifies the complete
bundle; they never authorize Feature Spec mutation.

On the new-source route, draft with `references/spec-template.md` unless the
repository has a stronger Feature Spec format. Keep it
implementation-facing:

- problem, users, goals, and non-goals;
- functional and integration requirements;
- product and repository scope;
- affected repositories, allowed paths, and the target branch shared inside
  this Feature Spec;
- acceptance criteria and validation expectations;
- cross-repository contracts and integration gates;
- risks, open questions, and issue-splitting notes.

Acceptance criteria must be unique, individually provable checkboxes with
stable wording and order. Describe decisions and failure behavior as concise
behavioral or scenario prose; reserve tables for exact identity and scope facts.
For every paid, external, non-repeatable, or otherwise constrained validation,
state the attempt/retry budget, allowed fallback, evidence to retain, and
required terminal outcome before the Spec can become agent-ready. Treat
implementation and issue-splitting sections as planning-time recommendations,
not immutable technical scripts.

When durable Idea refs were supplied, transform their normalized evidence
through the mapping in `idea-source.md`. Before publication, trace every
material accepted element to a candidate Feature Spec section, explicit
non-goal, deferred remaining-scope item, or blocking question. Do not convert
tentative direction or expected value into accepted requirements without
evidence or clarification, and do not treat a candidate destination as durable
coverage.

Render each relevant ref exactly once as `- Source Idea: <durable-ref>` in
`## Source`. In a multi-repository bundle, include a ref in every parent or
partial whose scope derives from that Idea, and omit it from unrelated
partials. Preserve the Idea body and keep its refs and transient coverage maps
out of generated implementation issues.

Render `Delivery type: <delivery_type>` exactly once in `## Planning Identity`
for every implementation-eligible Feature Spec and copy it into every generated
issue. It is stable contract data, not a selectable Plan Feature option.
Support exactly these tracker/delivery combinations: GitHub plus `github-pr`,
local Markdown plus `local-branch`, and local Markdown plus `github-pr`.
Repository identity does not choose delivery: a `github:owner/repository`
identity may still use a local Spec and `local-branch`. On a new source, derive
delivery only from accepted intent and repository capability; GitHub tracking
has the sole compatible value `github-pr`, while an ambiguous local tracker in
a repository capable of either delivery requires clarification. On an existing
source, require the exact stable line unchanged. Do not persist delivery in
Project Memory configuration.

### 4. Validate Feature Dependencies

On the new-source route, create the mandatory `## Feature Dependencies` table
with exactly `upstream_feature_spec_ref` and `dependency_reason`. On the
existing-source route, require and validate that exact existing section without
adding, removing, or rewriting anything.

For every edge:

- require a unique durable upstream ref, or a proposed ref only in
  `write_mode=propose`;
- in a multi-repository applied bundle, require every upstream ref to identify
  its owning repository through `owner/repository#<number>`, a canonical hosted
  URL, or `<repository-slug>/planning/features/<feature-slug>/SPEC.md`;
- reject self, duplicate, missing, and ambiguous refs;
- require a concrete portable reason;
- normalize upstream-to-downstream edges and validate the reachable Feature
  Spec graph is acyclic;
- treat the edge as waiting for stable upstream branch/HEAD evidence and
  integration proof; require merge only when the durable dependency contract
  explicitly says the integration input must be merged.

An empty table body means no authored cross-Spec dependencies. The section and
its two canonical columns are mandatory on both source routes. A supplied
Feature Spec without them is incompatible structured input: stop and require an
explicitly authorized canonical update before issue generation. Never
interpret absence as an empty edge set or infer edges from prose, issue
ordering, branch names, or similar titles.

Keep cross-Spec edges separate from generated issue dependencies. The issue
phase may validate and preserve the Feature Spec graph but never copies those
refs into issue `dependency_ids`.

### 5. Sanitize And Gate The Body

On the new-source route, replace local filesystem evidence with portable
references before return or publication. On the existing-source route, validate
without modifying the body; any nonportable evidence blocks issue generation
until a separate explicitly authorized source update lands.

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
- acceptance criteria are unique, individually provable checkboxes with stable
  text and order;
- every materially constrained validation has an explicit prose failure policy
  with its attempt/retry budget, allowed fallback, retained evidence, and
  required terminal outcome;
- every implementation-eligible Spec carries exactly one supported
  `Delivery type:` line in Planning Identity;
- open questions are empty or proven non-blocking;
- a present phase-level knowledge delta has explicit portable decisions,
  targets, and evidence, while no Feature Spec body contains `knowledge_delta`
  or a `## Domain Knowledge Handoff` section;
- every knowledge target has one unambiguous repository owner and lies inside
  the accepted Feature Spec repository/path scope, so the final issue can cover
  it without a later scope expansion;
- every cross-repository acceptance boundary names one or more existing
  implementation partials as combined-proof owners and the exact peer Feature
  Dependencies required by each owner;
- every implementation partial that owns combined proof contains an executable
  `## Integration Execution Contract` covering component roles and start
  commands, endpoint/environment wiring, collision-safe ports, health checks,
  integration/E2E proof, timeout/retry/material budget, retained evidence,
  cleanup, exact input SHA vector, pre/post HEAD rereads by each owning worker,
  required terminal outcome, and an explicit assignment of each component to
  the proof-owner task or its peer task; each worker must stay inside its own
  worktree and the proof owner must use peer-exposed component boundaries;
- the body contains no workflow status field such as `Status: Draft`;
- an applied local body contains exactly one `issue_type: <configured feature
  value>` header after the H1 and before `## Source`; GitHub and proposed
  bodies contain no local header;
- every selected Idea ref appears only in the `## Source` section of each
  relevant Feature Spec and nowhere in generated issue contracts;
- every material selected-Idea element has exactly one candidate destination:
  a current Spec section, explicit non-goal, remaining-scope item, or blocking
  question; any blocking destination withholds the artifact.

Withhold the artifact and return blockers when the gate fails.

### 6. Apply Or Propose

On the existing-source route, skip body drafting and publication. Resolve the
configured transport for canonical `feature` metadata before comparing state.
For a local source, require the exact configured `local-header` value already
in the immutable body; a missing or conflicting header requires a separately
authorized source update. For GitHub, use `issue_operation=set-type` only for a
`native-type` mapping, `issue_operation=add-label` for a `label` fallback, or
the exact `body-field` convention when that convention is already satisfied by
the immutable source. Under `write_mode=apply`, repair only the missing hosted
native type or label; under `write_mode=propose`, report that exact intended
repair. A conflicting native type or mapped fallback blocks. Never invent or
attempt an unsupported native type operation when GitHub Issue Types are
disabled. Immediately before reporting or applying a repair, re-read the exact
source body/ref, current metadata, and mapping row; restart validation or block
on any drift rather than mutating against a stale immutable source. Local
Feature Specs have no separate source metadata mutation. Then return the
current durable source, including preserved executor-owned checkbox markers,
after the dependency and body gates pass.

Read tracker and type mappings immediately before output.

For a new-source apply, resolve the configured `feature` metadata transport
before publication. `native-type` and `label` transports are applied only after
the final hosted body verifies. A configured `body-field` is rendered
into the applied final body before final-body verification. In proposal mode, omit
applied metadata from the body and report the intended transport and value as
proposal metadata only.

Before the first Feature Spec staging create, direct create, edit, or metadata
mutation, revalidate every GitHub `feature` transport and exact value. A
`native-type` must still be enabled and expose the mapped value; otherwise block
for a Project Memory mapping update and never switch transport during recovery.
For `label`, verify the exact configured label exists. Under
`write_mode=apply`, create and verify only a missing exact mapped label through
`issue_operation=create-label`; under `write_mode=propose`, report that missing
label creation as an intended operation without mutation. Preserve verified
label creation in transaction recovery and retry only an operation still proven
missing. The same preflight applies before an existing-source metadata repair.

Re-read each canonical Feature Spec target immediately before the first
new-source write. If a durable source or partial-publication artifact outside
the recognized publication transaction appeared or changed after route
resolution, stop and restart from fresh intake comparison; do not switch routes
in place, overwrite it, or publish a duplicate. During one recognized
multi-repository transaction, artifacts created by its own verified hosted or
local operations are expected and do not trigger this foreign-race guard.
Immediately before each hosted staging or direct create and each local-file
create, re-read that exact target plus its source and mapping inputs and prove
the target remains absent. Use non-overwrite semantics, stop on a foreign or
ambiguous appearance, and verify each successful create before continuing.

For any multi-repository apply, use one recoverable publication transaction.
Hosted roles require staging because final issue numbers are unavailable before
creation; deterministic local refs are resolved before mutation:

1. Before any mutation, validate every role-keyed parameterized final-body
   template and predeclare the complete parent, implementation, sibling, and
   Feature Dependency ref slots plus the exact optional configured
   body-metadata slot and value. Generate one transaction identity and record
   each role, exact target, title, complete reconstructable template, allowed
   ref slots, and allowed body-metadata insertion. Materialize final bodies only
   after every ref used by that body is resolved and the optional final-only
   body metadata is inserted; all-local bodies may therefore be materialized
   before the first write. Do not compute whole-body tracker digests.
2. Re-read every target, then immediately re-read and prove exact-target absence
   before each missing predeclared hosted-role create with
   `issue_operation=create`. A hosted staged body contains all final content
   except the predeclared ref substitutions and optional final-only
   `body-field` metadata, plus a unique transaction/role marker and an explicit
   non-executable staging notice. Do not write local roles while a hosted role
   remains staged. Do not apply final feature metadata, generate issues, or
   present a staged issue as a Feature Spec.
3. After every hosted ref is known, combine those refs with deterministic local
   refs and materialize every final body. Invoke
   `issue_operation=edit` only to replace the predeclared ref slots, insert the
   exact predeclared final-only `body-field` metadata when configured, remove the
   staging marker and notice, and produce that predeclared final body. Reject every
   other body difference. Verify a body convention as part of that final body;
   apply any native Issue Type or label transport only after the body verifies.
4. Verify every hosted final body and globally qualified ref, then immediately
   re-read and prove exact-target absence before each missing predeclared local
   file create with its exact recorded final body. For
   an all-local bundle, this is the transaction's first mutation. Verify every
   local body, mapped metadata value, and cross-link as part of the same
   connected set before ending the transaction or starting issue generation.

After each transaction mutation, retain the verified role-to-ref map and return
it in any partial-failure continuation handoff together with every complete
parameterized body template, allowed ref slot, optional exact
body-metadata slot and value, selected `source_idea_refs`, all verified prior
outcome refs, the complete `knowledge_delta` when present, completed operations,
and exact missing operations. On retry, recognize a new-source continuation
only when the supplied or reconstructable transaction identity, role map,
reconstructable templates, allowed ref slots, optional body-metadata slot and
value, materialized final bodies when available, and current tracker state
match directly. A digest is insufficient recovery evidence.
Resume only missing `create`,
predeclared `edit`, exact local-file create, or metadata operations. This exact
continuation rule also covers an all-local partial write. A mixed partial/final
set without sufficient exact recovery evidence blocks; never adopt it as an
immutable existing-source bundle or create duplicates. Once every Spec is final
and verified, a later retry derives the ordinary existing-source route from any
member and traverses the whole connected set.

- `write_mode=apply`, GitHub: for a single Spec, publish the final sanitized
  body directly as `Feature Spec: <Feature Name>`. For a multi-repository
  bundle, publish each parent or implementation role through the transaction
  above, then finalize each hosted body through the authorized `edit`. Translate each write to
  GitStack-owned `mutation_mode=apply`, its exact target, and one canonical
  `issue_operation`; apply the configured feature metadata transport only after
  the final body verifies, and retain the hosted issue number or URL as
  `source_spec_ref`. In multi-repository work, store
  `owner/repository#<number>` or the canonical URL, never a bare issue number.
- `write_mode=apply`, local: write the ordinary Feature Spec to
  `planning/features/<feature-slug>/SPEC.md` inside its owning repository and
  use that path as `source_spec_ref`. Require the Project Memory `feature`
  mapping to use `local-header`, then insert exactly
  `issue_type: <configured tracker value>` after the H1 and before `## Source`.
  Do not add a workflow-state header to a Feature Spec. In a multi-repository bundle, use
  `<repository-slug>/planning/features/<feature-slug>/SPEC.md` as the qualified
  ref and create the file only as its predeclared transaction operation. On
  exact continuation, create only missing
  predeclared local files whose targets and final bodies still match; never
  overwrite or repair a conflicting file.
- `write_mode=propose`: write nothing. Return the sanitized body, intended
  location, mapped metadata, and deterministic source identity:
  `proposed-spec:<feature_slug>` for a single Feature Spec,
  `proposed-spec:<project_slug>/<feature_slug>` for a multi-repository parent,
  or `proposed-spec:<project_slug>/<feature_slug>/<repository_slug>` for a
  repo-scoped implementation partial.
  Return publication order and state that every proposed source and the
  complete proposed issue bundle are non-executable until applied.

After `write_mode=apply` publication succeeds, verify each selected-Idea
candidate section or non-goal through the final durable Feature Spec ref before
converting it to `covered` or `excluded`. If any destination cannot be resolved
durably, withhold the coverage result and source reconciliation as an
incomplete publication. With `write_mode=propose`, or any other non-durable
preview, keep durable coverage unchanged and return only the report-only
intended projection with `intended_coverage`, `intended_covered_scope`, and
`intended_remaining_scope`; do not render a canonical planning outcome block.

`write_mode=propose` never invokes GitStack for publication or mutation. Exact
GitHub Idea discovery and source validation may still use read-only GitStack
operations with mutation fields omitted. GitStack does not interpret Plan
Feature's tracker or write policy.

For hosted publication, use transient transport outside the repository and
remove it after verified mutation. Do not construct raw mutating commands with
generated Markdown.

### 7. Report

Return:

- title, feature slug, source ref, and intended or actual location;
- `write_mode`, derived `source_route`, tracker backend, repository layout, and
  selected context identity;
- affected repositories, allowed paths, and each per-Spec target branch;
- validated Feature Spec dependencies and acyclicity result;
- workspace parent/child refs and publication order when applicable;
- issue type applied or proposed;
- open blockers and withheld output;
- selected or bound durable Idea refs, verified prior outcome refs, and each per-Idea
  cumulative durable `coverage`, `covered_scope`, and `remaining_scope`, or the
  distinct report-only `intended_coverage`, `intended_covered_scope`, and
  `intended_remaining_scope`;
- derived domain capture outcome and future closeout owner;
- any applicable multi-repository publication-transaction identity,
  role-to-ref map, and exact reconstructable continuation handoff when Spec
  finalization remains incomplete;

When `knowledge_delta` is present, pass it directly to the issue phase and
report `capture_outcome=deferred` plus the owning Feature Spec ref. Otherwise
report `capture_outcome=no-durable-change`. The result is report-only; this
phase never persists it in the Feature Spec or reports domain knowledge as
captured.
