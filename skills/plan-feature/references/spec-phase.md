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
- Treat GitHub routing and tracker mappings as Project Memory facts. Resolve the
  canonical `feature` type mapping before rendering or validating a Feature
  Spec. Require one supported GitHub transport.
- Publish only with `write_mode=apply`. With `write_mode=propose`, perform no
  write and return proposed bodies, locations, metadata, and publication order
  rather than executable commands.
- Do not create hosted-artifact mirrors or temporary planning trees.
- Load `idea-source.md` when selected new-source `source_idea_refs` or derived
  existing-source `bound_source_idea_refs` are present. Explicit discovery must
  already have completed and produced a selection before new-source drafting.
  Bound refs are immutable continuation evidence only; never draft from them.

## Phase Inputs

Receive:

- `write_mode` and the frozen derived `source_route`;
- the GitHub issue-type mapping for each affected repository, with explicit
  transport plus exact tracker value from that repository's Project Memory;
- planning identity: `feature_slug`, optional `planning_scope`, optional
  canonical lowercase UUID `feature_id`, and `context_files` containing every
  applicable available repository root and matched scoped context used for
  planning; `feature_id` is required and identical across every linked
  multi-repository Spec and omitted for a standalone Spec;
- affected repositories, allowed paths, per-Spec target branch, and linked-set
  membership;
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
- `project-memory/config/triage-labels.md`;
- root `CONTEXT.md` first when it exists, treating the current Git repository
  as a selected root; for cross-repository work, use explicit user scope or a
  durable linked Feature Spec Set to authorize repository identities, require
  candidate local Git roots separately, verify each root against one authorized
  identity, and read each available verified repository root context; then
  select every available scoped `CONTEXT.md` matched by affected paths in each
  selected root's `Scoped Contexts` table and read every available matched
  context before drafting. For a root or matched route with no context, use
  repository evidence without inventing terminology or a dangling context
  pointer;
- relevant ADRs, product documentation, source, and tests when they constrain
  the feature;
- repo-owned linked Feature Specs and named integration-gate evidence when the
  selected scope spans multiple Git repositories.

Do not broadly scan unrelated domain or localization material. Widen evidence
only when the current sources are incomplete or contradictory.

On the new-source route, when `source_idea_refs` are present, run ordinary
durable-artifact validation through `idea-source.md` before drafting. Read every
canonical Idea section and planning outcome, validate tracker ownership and
prior coverage Feature Spec refs, and derive the cumulative covered and
  remaining scope. Reject proposed refs, missing marker mappings, consumed or
  typed GitHub Ideas, and ambiguous repository ownership.

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

When root context routes multiple products or packages, resolve the selected
planning scope, applicable context files, and feature slug before drafting.
Stop rather than guess when more than one owner remains plausible.

### 2. Resolve Artifact Targets

Choose locations from the explicit affected Git repositories and each
repository's tracker facts:

| Affected Git repositories | Tracker | Feature Spec location |
| --- | --- | --- |
| One | GitHub Issues | `Feature Spec: <Feature Name>` issue in that repository. |
| Multiple | GitHub Issues per owning repository | One linked implementation-eligible Feature Spec in every affected repository. |

One Git repository may contain a monorepo; use `planning_scope`, affected paths,
and scoped contexts without adding a topology enum. Never synthesize another
Spec above the repo-owned linked set. Resolve every affected repository's
GitHub tracker facts independently; each gets a repo-owned hosted Feature Spec.

For multi-repository work:

1. Generate or preserve one canonical lowercase UUID `feature_id` and use it
   unchanged in every member. Give each member one stable lower-kebab
   `repository_key`, at most 48 characters, derived from its accepted canonical
   repository identity, unique inside the set, persisted in Planning Identity,
   and frozen with membership.
2. Produce every repo-owned member to obtain stable durable or proposed refs.
   In proposal mode use `proposed-spec:<feature_id>/<repository_key>` for each
   member.
   In apply mode, make every multi-repository ref globally unambiguous with
   `owner/repository#<number>` or a canonical hosted URL. Use those same refs in
   every member's `Feature Spec Set` and Feature Dependencies; bare `#<number>`,
   a bare repository key, and bare repo-relative paths are invalid in a
   multi-repository feature.
3. Assign each cross-repository boundary and every bundle-level acceptance or
   proof obligation to one existing implementation member
   that can execute the combined proof within its accepted repository, paths,
   tools, and validation budget. Multiple boundaries may have different owners:
   for example, web owns web-to-backend proof and mobile owns mobile-to-backend
   proof against the same backend revision. Name the required peer Specs in the
   owner's Feature Dependencies and include the executable Integration Execution
   Contract in that existing member. If no existing member can own a required
   feature-wide proof, withhold the feature; never create a dedicated integration
   Spec or future worker as a fallback.
4. Validate every implementation-eligible member as one feature: each
   `(affected_repository, target_branch_name)` pair must have exactly one
   Feature Spec owner. The same branch string may appear in different
   repositories, but two Specs in the same repository must not share it,
   even when paths are disjoint or dependencies serialize them. Resolve collisions
   before new publication; for an immutable existing source, stop rather than
   rename it.
5. Add an identical `## Feature Spec Set` table to every member. It has exactly
   the columns `feature_spec_ref | affected_repository | responsibility`,
   exactly one globally qualified row per member including self, non-empty
   responsibility, deterministic repository ordering, and exact normalized equality
   across the set. Final applied tables contain no proposed refs.
   Normalize by parsing the table, trimming surrounding whitespace in every
   cell, preserving case and content otherwise, rejecting duplicate refs or
   repositories, sorting rows bytewise by `affected_repository`, and rendering
   the exact canonical header and row sequence. Each self row must match that
   member's own durable ref and repository. Every normalized table and
   `feature_id` must then be byte-for-byte equal across the set. Give every
   linked acceptance criterion one globally unique
   `<repository-key>:ac-<NN>` ID rendered as the exact checklist prefix
   `- [ ] \`<repository-key>:ac-<NN>\` ` and every combined proof one
   `<repository-key>:proof-<slug>` ID rendered as the exact bullet
   `- Proof ID: \`<repository-key>:proof-<slug>\`.`. Render linked Planning
   Identity as exact `- Feature ID: \`<uuid>\`.` and
   `- Repository key: \`<repository-key>\`.` lines. Persist each criterion only
   in its owning member and each proof only in its owning Integration Execution
   Contract.
   The owning row's `responsibility` cell must contain every ID owned by that
   member as an exact inline-code token and no ID owned by another row. Across
   the complete set, require every declared criterion and proof ID to occur
   exactly once in member content and exactly once in the matching
   responsibility cell. Reject unbackticked IDs, malformed prefix/suffix
   matches, any acceptance checklist item without its canonical ID, and an
   Integration Execution Contract without at least one canonical Proof ID.
6. Freeze membership after publication. Any membership or responsibility
   change requires a separately authorized whole-set update.
7. Start issue generation only after the complete linked artifact set exists.

GitHub routing is fixed for every owning repository. Preserve one publication
plan ordered by member creation, linked-set finalization, then generated issues.
Proposed refs are inspection-only and never agent-executable. In apply mode,
place every role in one recoverable hosted publication transaction and use
staging when refs are unknown. Never persist an issue that points to a staging
identity.

#### Allowed Path Scope Contract

Use this canonical table when defining Feature Spec and implementation-issue
`allowed_paths`:

| scope_case | allowed_path_rule |
| --- | --- |
| `feature-owned-work` | `complete-safe-prefixes` |
| `exact-file-boundary` | `exact-path` |
| `unrelated-pre-existing-failure` | `excluded` |

`complete-safe-prefixes` means the smallest complete and reasonably predictable
repo-relative or repo-qualified envelope needed to implement, integrate, test,
validate, and document the accepted outcome. Prefer stable directory or
subsystem prefixes over guessed file lists. Include foreseeable supporting
tests, fixtures, adapters, configuration, generated-contract inputs, and
technical documentation when the accepted requirements or validation can
reasonably need them. Use `exact-path` only when one file is genuinely the
complete safe boundary.

Do not widen to a repository-wide wildcard without evidence that the repository
is small or the accepted change is genuinely cross-cutting. Exclude unrelated
pre-existing failures merely encountered by a broad validation command; give
those failures an evidence-backed baseline or failure policy, or block planning
when the required terminal result cannot remain truthful. Never narrow a
complete envelope merely to make issue scopes appear disjoint or increase
parallel scheduling.

### 3. Gate An Existing Source Or Draft

Use user conversation, clarification output, existing issues or documents,
project memory, and relevant repository behavior as sources. Ask only for
decisions that materially change scope, acceptance, dependencies, validation,
or repository ownership.

On the existing-source route, do not draft or update the source unless the
invocation contains the exact `scope_repair_request` accepted by
`scope-repair.md`. For that one exception, delegate request validation,
monotonic path expansion, mutation ordering, audit, recovery, and result to that
reference and preserve every other stable and executor-owned field.

Without `scope_repair_request`, carry the
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

When the intake source is any member of a multi-repository feature, require its
canonical lowercase UUID `Feature ID`, traverse its `Feature Spec Set`, and
load the complete connected implementation Spec set. Validate every body's
stable fields and ref through the same gates, preserving current acceptance
checkbox markers. Pass every implementation-eligible member to issue
generation. A missing, ambiguous, disconnected, differently identified, or
incompatible linked source blocks the run instead of being drafted or repaired.

A missing or unequal `Feature Spec Set`, Feature Dependency, or other
relationship represented inside an immutable Feature Spec body is a
source-contract failure. Do not hand it to the issue phase as a repairable
tracker relationship.

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
`## Source`. In a multi-repository feature, include a ref in every member whose
scope derives from that Idea, and omit it from unrelated members. Preserve the
Idea body and keep its refs and transient coverage maps
out of generated implementation issues.

GitHub Issues and pull-request delivery are fixed workflow boundaries. Do not
render a provider or delivery selector in the Feature Spec; the executor owns
branch and merge details.

### 4. Validate Feature Dependencies

On the new-source route, create the mandatory `## Feature Dependencies` table
with exactly `upstream_feature_spec_ref` and `dependency_reason`. On the
existing-source route, require and validate that exact existing section without
adding, removing, or rewriting anything.

For every edge:

- require a unique durable upstream ref, or a proposed ref only in
  `write_mode=propose`;
- in a multi-repository applied bundle, require every upstream ref to identify
  its owning repository through `owner/repository#<number>` or a canonical
  hosted URL;
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

On the new-source route, replace machine-local filesystem evidence with portable
references before return or publication. On the existing-source route, validate
without modifying the body; any nonportable evidence blocks issue generation
until a separate explicitly authorized source update lands.

Portable forms are:

- current repository: `path/to/file` or `path/to/file:line`;
- peer repository: `<repo-slug>/<repo-relative-path>`;
- hosted evidence: URL, issue, PR, or `owner/repo:path`;
- descriptive source label when no stable identity exists.

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
- every implementation-eligible Spec uses the fixed GitHub pull-request delivery
  boundary without adding a provider or delivery field;
- open questions are empty or proven non-blocking;
- a present phase-level knowledge delta has explicit portable decisions,
  targets, and evidence, while no Feature Spec body contains `knowledge_delta`
  or a `## Domain Knowledge Handoff` section;
- every knowledge target has one unambiguous repository owner and lies inside
  the accepted Feature Spec repository/path scope, so the final issue can cover
  it without a later scope expansion;
- every cross-repository acceptance boundary names one or more existing
  implementation members as combined-proof owners and the exact peer Feature
  Dependencies required by each owner;
- every implementation member that owns combined proof contains an executable
  `## Integration Execution Contract` covering component roles and start
  commands, endpoint/environment wiring, collision-safe ports, health checks,
  integration/E2E proof, timeout/retry/material budget, retained evidence,
  cleanup, exact input SHA vector, pre/post HEAD rereads by each owning worker,
  required terminal outcome, and an explicit assignment of each component to
  the proof-owner task or its peer task; each worker must stay inside its own
  worktree and the proof owner must use peer-exposed component boundaries;
- the body contains no workflow status field such as `Status: Draft`;
- GitHub and proposed bodies contain no tracker header;
- every selected Idea ref appears only in the `## Source` section of each
  relevant Feature Spec and nowhere in generated issue contracts;
- every material selected-Idea element has exactly one candidate destination:
  a current Spec section, explicit non-goal, remaining-scope item, or blocking
  question; any blocking destination withholds the artifact.

Withhold the artifact and return blockers when the gate fails.

### 6. Apply Or Propose

On the existing-source route, skip body drafting and publication. Resolve the
configured transport for canonical `feature` metadata before comparing state.
For GitHub, use `issue_operation=set-type` only for a
`native-type` mapping, `issue_operation=add-label` for a `label` fallback, or
the exact `body-field` convention when that convention is already satisfied by
the immutable source. Under `write_mode=apply`, repair only the missing hosted
native type or label; under `write_mode=propose`, report that exact intended
repair. A conflicting native type or mapped fallback blocks. Never invent or
attempt an unsupported native type operation when GitHub Issue Types are
disabled. Immediately before reporting or applying a repair, re-read the exact
source body/ref, current metadata, and mapping row; restart validation or block
on any drift rather than mutating against a stale immutable source. Then return the
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
multi-repository transaction, artifacts created by its own verified hosted
operations are expected and do not trigger this foreign-race guard.
Immediately before each hosted staging or direct create, re-read that exact
target plus its source and mapping inputs and prove the target remains absent.
Use non-overwrite semantics, stop on a foreign or ambiguous appearance, and
verify each successful create before continuing.

For any multi-repository apply, use one recoverable publication transaction.
Hosted roles require staging because final issue numbers are unavailable before
creation:

1. Before any mutation, validate every role-keyed parameterized final-body
   template and predeclare the complete member, `Feature Spec Set`, and Feature
   Dependency ref slots plus the exact optional configured
   body-metadata slot and value. Generate one transaction identity and record
   each role, exact target, title, complete reconstructable template, allowed
   ref slots, and allowed body-metadata insertion. Materialize final bodies only
   after every ref used by that body is resolved and the optional final-only
   body metadata is inserted. Do not compute whole-body tracker digests.
2. Re-read every target, then immediately re-read and prove exact-target absence
   before each missing predeclared hosted-role create with
   `issue_operation=create`. A hosted staged body contains all final content
   except the predeclared ref substitutions and optional final-only
   `body-field` metadata, plus a unique transaction/role marker and an explicit
   non-executable staging notice. Do not apply final feature metadata, generate issues, or
   present a staged issue as a Feature Spec.
3. After every hosted ref is known, materialize every final body. Invoke
   `issue_operation=edit` only to replace the predeclared ref slots, insert the
   exact predeclared final-only `body-field` metadata when configured, remove the
   staging marker and notice, and produce that predeclared final body. Reject every
   other body difference. Verify a body convention as part of that final body;
   apply any native Issue Type or label transport only after the body verifies.
4. Verify every hosted final body and globally qualified ref before ending the
   transaction or starting issue generation.

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
Resume only missing `create`, predeclared `edit`, or metadata operations. A
partial hosted set without sufficient exact recovery evidence blocks; never
adopt it as an immutable existing-source bundle or create duplicates. Once every Spec is final
and verified, a later retry derives the ordinary existing-source route from any
member and traverses the whole connected set.

- `write_mode=apply`, GitHub: for a single Spec, publish the final sanitized
  body directly as `Feature Spec: <Feature Name>`. For a multi-repository
  feature, publish each implementation member through the transaction
  above, then finalize each hosted body through the authorized `edit`. Translate each write to
  GitStack-owned `mutation_mode=apply`, its exact target, and one canonical
  `issue_operation`; apply the configured feature metadata transport only after
  the final body verifies, and retain the hosted issue number or URL as
  `source_spec_ref`. In multi-repository work, store
  `owner/repository#<number>` or the canonical URL, never a bare issue number.
- `write_mode=propose`: write nothing. Return the sanitized body, intended
  repository target, mapped metadata, and deterministic source identity:
  `proposed-spec:<feature_slug>` for a single Feature Spec,
  or `proposed-spec:<feature_id>/<repository_key>` for a linked
  multi-repository member.
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
- `write_mode`, derived `source_route`, optional `feature_id`,
  and selected context identity;
- affected repositories, allowed paths, and each per-Spec target branch;
- validated Feature Spec dependencies and acyclicity result;
- linked Feature Spec refs and publication order when applicable;
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
