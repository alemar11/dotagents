---
name: plan-feature
description: Manually plan features into Feature Specs and agent-ready issues through full-flow, spec-only, or issues-from-existing-spec modes.
---

# Plan Feature

## Purpose And Invocation

Use this planning-only skill to turn feature intent into a durable Feature Spec
and, when requested, hardened vertical implementation issues. A Feature Spec is
the durable parent contract for one bounded product or system change.

The public pipeline is:

`Project Memory routing -> optional Idea discovery and source validation -> repo-backed clarification -> Feature Spec phase -> issue phase -> source reconciliation -> deferred domain-memory closeout`

Use it only when the user invokes `$plan-feature`, asks to run Plan Feature, or
a manually invoked parent workflow routes here. Do not auto-select it for an
ordinary planning, implementation, issue-splitting, or triage request. Never
implement the planned feature.

## Structured Option Contract

Load `references/options.md` before the first phase. It defines the complete
default-path run registry:

| Field | Values |
| --- | --- |
| `mode` | `full-flow`, `spec-only`, `issues-from-existing-spec` |
| `write_mode` | `apply`, `propose` |

Before validating selectable fields, inspect the current request and any
durable source Feature Spec for the non-App predicate. Load
`references/non-app-delivery.md` when the user explicitly requests a non-App
stopping point, or when a canonical source Spec already carries exactly one
`non_app_delivery_target` and exactly one resolvable
`explicit_instruction_ref`.
Validate that one conditional extension together with the default registry.
Otherwise reject every unregistered field or value, including
`non_app_delivery_target`. Project Memory owns tracker routing and repository
topology; Plan Feature consumes those as facts. Paths, slugs, refs, branches,
dependencies, and domain handoffs are data.

Resolve `mode` once:

- `full-flow`: default for new intent; produce the Feature Spec and issues.
- `spec-only`: stop after the Feature Spec only when explicitly requested.
- `issues-from-existing-spec`: split one durable existing Feature Spec.

Resolve `write_mode` once:

- `apply`: publish through the configured tracker.
- `propose`: perform no writes and return proposed bodies, target locations,
  metadata, and publication order. Do not return executable commands.

## Fixed Planning Contract

- Load `references/spec-phase.md` before Feature Spec work and
  `references/issue-phase.md` before issue work. Load templates only with their
  owning phase.
- Treat `tracker_backend` and `repository_layout` as Project Memory facts. Run
  the matching Project Memory routing slice when either fact is missing,
  stale, or contradictory.
- Load `references/idea-discovery.md` only when exact refs are absent and the
  user explicitly asks to discover captured Ideas. Never scan an Idea backlog
  during an ordinary planning request. Discovery is read-only until the user
  selects durable refs; it may load `references/idea-source.md` only in that
  reference's validation-only mode. Selection activates the full source
  contract. The final `source_idea_refs` remain execution data, not options.
  Accept marker-valid Ideas only in `full-flow` or `spec-only`; reject proposed
  refs and reject Idea input in `issues-from-existing-spec`.
- Keep one Plan Feature run bounded to one feature. Multiple selected Ideas may
  feed that feature, but unrelated Ideas require separate runs rather than one
  batch of unrelated Specs.
- Resolve one planning identity: `feature_slug` plus any selected product,
  workspace, context, or orchestrator-project identity.
- Withhold incomplete artifacts. Return concrete blockers instead of
  publishing or labeling partial work agent-ready.
- Use a durable `source_spec_ref` in every issue. A canonical single-repository
  or workspace-qualified proposed ref is allowed only with
  `write_mode=propose` and is never executable. In multi-repository work, every
  repo-scoped proposed ref includes its owning repository slug, and every
  applied ref identifies its owning repository, so sibling identities cannot
  collide.
- Give every issue exactly one `## Execution Contract` table with
  `source_spec_ref`, `feature_slug`, `affected_repositories`, `allowed_paths`,
  `target_branch_name`, and `dependency_ids`. Do not duplicate these values in
  another delivery, handoff, or option section.
- For every local Markdown issue, include the tracker-owning repository in
  `affected_repositories` and include both the exact active issue path and its
  exact derived `done/` destination in `allowed_paths`. This is execution scope,
  not a completion-method option. Both paths must resolve inside that affected
  Git repository so an App-managed checkout can own the move; otherwise withhold
  the issue as non-App-executable unless the explicit non-App contract applies.
- Keep intra-Spec ordering only in `dependency_ids`. Derive reverse edges when
  needed; do not persist them.
- Keep authored cross-Spec ordering only in the Feature Spec's mandatory
  `## Feature Dependencies` table. Every upstream edge waits for upstream
  merge and integration proof. Never convert those edges into issue IDs.
- Across the complete implementation-eligible bundle, give exactly one Feature
  Spec ownership of each `(affected_repository, target_branch_name)` pair. The
  same branch name may be used in different repositories, but two Specs must
  never claim the same pair, even when their paths are disjoint or dependencies
  would serialize them. Resolve collisions before publishing a new bundle; for
  an immutable existing source, stop instead of renaming its branch.
- Make ordinary output compatible with `$implement-feature`'s fixed reviewed,
  CI-clean, pull-request-ready flow. Do not select or grant implementation,
  publication, review, issue-mutation, or merge authority.
- Load `references/non-app-delivery.md` before drafting only when the current
  user explicitly requests a non-App stopping point, or a canonical durable
  source Spec carries exactly one target and one resolvable
  `explicit_instruction_ref`. The instruction ref is evidence data, not a run
  option or issue field. Artifacts carrying `non_app_delivery_target` are
  incompatible with `$implement-feature`.
- Carry an optional `knowledge_delta` data object with `decisions`,
  `target_surfaces`, and `evidence` lists. Absence means no durable change.
  Keep unresolved planning questions in a separate `planning_blockers` list.
- Normalize every `knowledge_delta.target_surfaces` entry to one affected
  repository plus one portable repo-relative path. The final closeout issue
  must name that repository in `affected_repositories` and cover that exact
  path in `allowed_paths`; reject absolute paths, `..` traversal, ambiguous
  repository ownership, and any delta that would require widening an immutable
  source. In `issues-from-existing-spec`, every target must already fit the
  unchanged Feature Spec repository/path scope or issue generation stops.
- Call `$grill-me-with-context` only with
  `capture_mode=defer-to-caller`. Planning may read durable context but must
  not update domain-memory surfaces.
- Never persist `knowledge_delta` or a `## Domain Knowledge Handoff` in a
  Feature Spec. Carry the optional delta directly between phases and persist its
  exact payload only on one final implementation/integration issue. For a
  single Spec, exclude that owner and its own `dependency_ids`, derive the
  no-dependent terminals in the remaining graph, then require the owner to
  depend directly on all of them and have no dependents itself. The final issue
  proves integrated behavior and invokes `$project-memory domain-memory` with
  `memory_slice=domain-memory` and
  `domain_operation=implementation-closeout` after implementation.
- Every multi-repository bundle gets exactly one distinct repo-owned integration
  partial whose
  Feature Dependencies wait for every implementation partial to merge. Generate
  at least one integration issue from it whether or not a knowledge delta
  exists. That issue must own a bounded repository/path change plus
  cross-repository proof so the App can produce a real PR; withhold the bundle
  when no such integration vehicle exists. Attach domain closeout only to its
  final issue when a delta exists. Derive the integration partial's branch by
  appending `-integration` to the resolved ordinary partial branch; never reuse
  the ordinary partial's branch in the same repository. With the default
  ordinary branch this yields `feature/<feature_slug>-integration`.
- Before freezing generated IDs or invoking `$plan-harder`, run the structural
  graph-compression gate from `references/vertical-slices.md` on every
  implementation-eligible Feature Spec. Compare the complete candidate graph,
  combine weak or coordination-heavy slices, remove artificial dependencies,
  and preserve required integration and domain-closeout ownership. Issue count
  is report data only and never determines whether the graph passes.
- Run `$plan-harder` one or more times per final retained issue with
  `planning_mode=issue-hardening` and `output_surface=caller`, beginning only
  after vertical boundaries, scope, compression, and graph ownership have
  stabilized. If hardening exposes a graph-level defect, discard affected
  hardening results, return to compression, and re-harden every materially
  changed issue. Persist only the final stable result and one provenance line.
- Keep worker surfaces, task counts, App permissions, checkout paths, and
  runtime scheduling out of Feature Specs and generated issues.
- Publish only portable evidence: repo-relative paths, repo-qualified sibling
  paths, hosted links, or descriptive source labels. Never publish
  developer-machine absolute paths.

## Composed Skills

| Skill | Load when | Boundary |
| --- | --- | --- |
| `$project-memory` | Tracker routing, repository topology, or an explicitly required Idea marker mapping is missing, stale, or contradictory. | Use only `tracker-routing` or `project-layout`; a missing Idea mapping blocks only Idea capture, discovery, or consumption, and Plan Feature never performs domain closeout. |
| `$grill-me-with-context` | Repo-backed clarification is materially needed. | Always defer capture to the caller and consume its structured delta. |
| `$plan-harder` | For every final retained implementation issue after structural graph compression. | At least one issue-hardening call per retained issue, with only the final stable result persisted; Plan Feature owns artifact writes. |
| `$gitstack:github-issues` | The owning tracker backend is GitHub and explicit Idea discovery or a selected Idea needs exact reads, or `write_mode=apply` authorizes a tracker write. | Discovery and source validation are read-only in either write mode and omit mutation fields. For writes, translate each operation to `mutation_mode=apply`, the exact target, and one `issue_operation`; own safe transport, metadata, relationships, verification, cleanup, and partial recovery. Proposal mode never requests dry-run mutations or returns executable commands. |

After implementation begins, generated implementation-issue lifecycle
mutations belong to the selected executor, not Plan Feature. Terminal
source-Idea reconciliation remains planning closeout and occurs before
implementation begins.

## Workflow

### 1. Resolve Setup, Mode, Write Mode, And Identity

Read:

- `project-memory/config/issue-tracker.md`;
- `project-memory/config/project-layout.md`;
- `project-memory/config/triage-labels.md`;
- root `CONTEXT.md` first when it exists, treating the current Git repository
  as a selected root; in a coordination workspace, also select affected child
  roots from its `Repository Registry` and read each available child root
  context; then
  select every available scoped `CONTEXT.md` matched by affected paths in each
  selected root's `Scoped Contexts` table. Read every available matched context
  before drafting. For a root or matched route with no context, use repository
  evidence without inventing terminology or a dangling context pointer.

Run only the relevant Project Memory routing slice when setup is incomplete.
Do not bootstrap unrelated domain, localization, ADR, or agent-instruction
content.

Resolve `mode` and `write_mode` from `references/options.md`. Then resolve
`feature_slug`, affected repositories, allowed paths, and one target branch
shared only within each implementation-eligible Feature Spec,
and any product/workspace identity from accepted input and repository evidence.
For a multi-repository workspace, derive workspace behavior from
`repository_layout`; do not ask for another workspace-mode option.

Before ordinary Idea validation or discovery, inspect exact selected refs plus
the invocation or durable handoff for evidence that the complete requested
planning result already exists and only source reconciliation is incomplete.
When that evidence is present, load `references/idea-source.md` and run its
reconciliation-only recovery branch first. Do not enter ordinary source
validation, the Feature Spec or issue phases, reopen completed Ideas, or
republish planning artifacts. Stop after reporting the reconciled or still
missing operations.

Otherwise, when the invocation supplies `source_idea_refs`, load
`references/idea-source.md`, run ordinary validation for every durable ref and
tracker owner, read all canonical Idea sections and prior outcomes, and require
explicit selection before combining multiple Ideas.

When exact refs are absent but the user explicitly asks to discover captured
Ideas, load `references/idea-discovery.md`. Resolve tracker owners before
listing, show only validated candidates with their state and prior outcomes,
and require explicit selection. The selected refs become `source_idea_refs`,
then continue through `references/idea-source.md`; if the user asked only to
inspect the backlog, report and stop without drafting or mutation. Never
discover Ideas implicitly.

Stop when selected Ideas do not describe one bounded feature. Do not route a
missing Idea marker through implicit Project Memory writes; return the exact
setup prerequisite unless the user separately authorized that setup.

If an accepted parent/global Feature Spec is needed, produce it first. Resolve
each affected child repository's tracker and topology facts independently and
link every repo-scoped partial. Do not generate combined implementation issues
until all required source refs and cross-links exist. Proposed refs remain
non-executable.

### 2. Clarify Only Material Unknowns

In `full-flow` and `spec-only`, run `$grill-me-with-context` only when supplied
intent plus repository evidence cannot support a complete Feature Spec or safe
issue graph. Resolve one blocking decision at a time.

For every selected Idea, normalize the seven canonical sections into transient
planning evidence and a per-element coverage map through
`references/idea-source.md`. Tentative directions remain tentative until
supported by repository evidence or explicit clarification. A blocked element
withholds the requested result; an intentionally deferred element may support
partial coverage only after at least one material element is durably covered.
With `write_mode=propose`, build the separate report-only intended projection;
never treat a proposed Spec as durable coverage.

Do not mutate an Idea merely because an interactive clarification is active.
Only a terminal run exit waiting for one specific requester answer may
reconcile that Idea to `needs-info` under `write_mode=apply`.

For `issues-from-existing-spec`, inspect open questions only to validate whether
the durable source can be consumed unchanged. Accept `knowledge_delta` only as
explicit accepted invocation data supplied separately from the source; never
infer it from the Feature Spec or rewrite the source to carry it. Require every
target surface in that data to resolve inside the source's unchanged affected
repositories and allowed paths; reject the delta instead of widening source or
issue scope. A persisted
`knowledge_delta` or `## Domain Knowledge Handoff` is incompatible input. If any
answer, schema repair, or content correction would change the source, stop and
require a separate explicitly authorized Feature Spec update; do not fold that
update into issue generation. Keep `planning_blockers` separate and do not
capture durable knowledge during planning.

### 3. Run The Feature Spec Phase

Always run the canonical source-contract validation from
`references/spec-phase.md`, including the exact Feature Dependencies heading
and columns. With `issues-from-existing-spec`, require one unchanged durable
Feature Spec. After validation passes, return its original body and ref to the
issue phase without drafting or publication. If it needs any change, stop and
require a separate explicitly authorized Feature Spec update; do not switch
modes. For `full-flow` or `spec-only`, load `references/spec-template.md`, then
pass:

- `mode`, `write_mode`, and Project Memory facts;
- planning identity and repository scope;
- source-ref state and cross-Spec dependency rows;
- optional validated `source_idea_refs`, normalized Idea evidence, prior
  partial-outcome refs, transient durable coverage maps or report-only intended
  projections, and their per-Spec relevance mapping;
- optional `knowledge_delta` plus separate `planning_blockers`;
- `non_app_delivery_target` and `explicit_instruction_ref` only after explicitly
  loading the conditional reference; keep the latter as source evidence data.

Require a durable local or hosted `source_spec_ref` for `write_mode=apply`, or
a deterministic proposed ref and publication-order note for
`write_mode=propose`. The sole exception is `spec-only` with a nonempty
`knowledge_delta`: withhold every write under either resolved write mode, return
only a blocked non-durable preview and the exact delta, and require a later
explicit `full-flow` run for durable publication. Never persist a delta marker
in the Spec or silently downgrade `write_mode`. Route new blockers back through clarification. In
`full-flow`, pass the optional delta directly to the issue phase without adding
it to any Feature Spec body. For `spec-only`, continue only to terminal Idea
source reconciliation and the completion report after every requested Feature
Spec is durable and verified.

### 4. Run The Issue Phase

Load `references/issue-phase.md`, `references/issue-body-template.md`, and
`references/vertical-slices.md`. Pass the same identity, facts, write mode,
source ref, optional knowledge delta, workspace links, and validated cross-Spec
graph.

The issue phase owns vertical splitting, structural graph compression, one or
more `$plan-harder` passes per final retained issue, mapped metadata, intra-Spec
dependency validation, the single Execution Contract, tracker writes or
proposed output, and final reporting. It persists only the final stable
hardening result.

If `knowledge_delta` is present in a single Spec, reuse or add a final
integration issue, exclude it and its own `dependency_ids` while deriving the
remaining graph's no-dependent terminals, then make it depend directly on all
of them and reject any dependent of the owner. In a
multi-repository bundle, generate at least one issue from the dedicated
integration partial after its
merge-wait Feature Dependencies cover every implementation partial; keep its
issue dependencies local. Attach the delta only to the final integration issue
when present. Harden and validate the selected final issue like every other
issue.

### 5. Reconcile Selected Idea Sources

Skip this step when no `source_idea_refs` were supplied. Otherwise load
`references/idea-source.md`. With `write_mode=apply` and a new durable result,
determine cumulative `partial` or `full` coverage separately for every selected
Idea from verified prior Specs plus that result. With `write_mode=propose`, or
when another branch returned only a non-durable preview, leave the durable map
unchanged and report only `intended_coverage`, `intended_covered_scope`,
`intended_remaining_scope`, and intended transitions from the separate
projection.

With `write_mode=apply`, a terminal wait for one specific requester answer may
reconcile the affected Ideas to `needs-info` before a planning result exists.
Reconcile coverage only after the complete requested result is durable and
verified: every requested Feature Spec for `spec-only`, or every Feature Spec,
implementation issue, metadata mutation, and relationship for `full-flow`. A
technical, validation, configuration, or partial publication failure normally
preserves each Idea's prior state. When the requester has answered a prior
`needs-info` blocker, prevent that stale state from surviving a later technical
failure by reconciling it to `needs-triage` at terminal exit.

Partial coverage writes the canonical cumulative planning-outcome block and
returns the Idea to `needs-triage`; full coverage writes the canonical
cumulative block, clears actionable states, and closes the GitHub Idea or marks
the local Idea consumed. Apply each decision independently and retry only
missing operations after partial source reconciliation. On resume, use the
reconciliation-only branch and treat a closed GitHub Idea or local full outcome
as already reconciled only when its complete canonical record exactly matches
the verified cumulative Spec set and coverage result.

### 6. Report Completion

Return:

- resolved `mode` and `write_mode`;
- Feature Spec ref or proposed ref, title, and target location;
- planning identity and Project Memory facts used;
- generated issue refs or proposed refs in publication order;
- graph and verticality validation, including candidate and final issue counts,
  compression repairs, retained-slice reasons, and avoided initial hardening
  calls;
- applied tracker metadata when writes occurred;
- discovered candidate refs when discovery ran, selected Idea refs, verified
  prior outcome refs, per-Idea cumulative durable `coverage`, `covered_scope`,
  and `remaining_scope`, or the distinct `intended_coverage`,
  `intended_covered_scope`, and `intended_remaining_scope`; plus applied or
  proposed lifecycle transitions and any missing reconciliation operations;
- domain closeout owner when present and the derived `capture_outcome`;
- blockers and withheld artifacts;
- explicit App incompatibility when `non_app_delivery_target` is present.

When `knowledge_delta` is present and the issue phase runs, report
`capture_outcome=deferred` plus its actual or proposed final issue ref. For
`spec-only`, return the exact delta as non-persisted report data and only the
deterministic `future_closeout_issue_source_spec_ref`; no final issue ref exists.
Report publication as withheld and state that no durable source was created.
The preview is not App-executable until a later explicit `full-flow` run carries
the exact delta again. Otherwise report
`capture_outcome=no-durable-change`. This result is report-only and never
persisted in the Feature Spec. Plan Feature never reports domain knowledge as
captured.

## References

- `references/options.md`: the complete default-path run registry and execution
  data shape.
- `references/idea-discovery.md`: explicitly requested read-only backlog
  discovery and selection before durable Idea-source intake.
- `references/idea-source.md`: selected durable Idea validation, intent
  normalization, cumulative coverage, Feature Spec projection, outcome records,
  and terminal lifecycle reconciliation.
- `references/non-app-delivery.md`: load for an explicitly requested non-App
  stopping point or a canonical durable source carrying exactly one target and
  one resolvable `explicit_instruction_ref`.
- `references/spec-phase.md`: Feature Spec drafting, routing, and publication.
- `references/spec-template.md`: default Feature Spec shape.
- `references/issue-phase.md`: issue splitting, hardening, graph validation,
  and publication.
- `references/issue-body-template.md`: generated issue shape and single
  Execution Contract.
- `references/vertical-slices.md`: slicing and readiness gates.
- `references/full-flow-dry-run.md`: non-mutating `write_mode=propose` fixture.
