---
name: plan-feature
description: Manually converge feature intent or a durable Feature Spec into a complete Feature Spec bundle with hardened agent-ready implementation issues.
---

# Plan Feature

## Purpose And Invocation

Use this planning-only skill to converge feature intent or a durable Feature
Spec into one complete, internally consistent bundle: the Feature Spec set,
hardened vertical implementation issues, tracker metadata, and relationships.
A Feature Spec is the durable parent contract for one bounded product or system
change.

The public pipeline is:

`Project Memory routing -> source-route resolution -> optional Idea discovery and validation -> repo-backed clarification -> Feature Spec phase -> issue-graph convergence -> source reconciliation -> deferred domain-memory closeout`

Use it only when the user invokes `$plan-feature`, asks to run Plan Feature, or
a manually invoked parent workflow routes here. Do not auto-select it for an
ordinary planning, implementation, issue-splitting, or triage request. Never
implement the planned feature.

## Structured Option Contract

Load `references/options.md` before the first phase. It defines the complete
default-path run registry:

| Field | Values |
| --- | --- |
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
- Load issue-type and workflow-state tracker values with their explicit Project
  Memory transports. Reject a missing, unknown, or backend-incompatible
  transport instead of inferring mutation mechanics from the value.
- Load `references/idea-discovery.md` only when exact refs are absent and the
  user explicitly asks to discover captured Ideas. Never scan an Idea backlog
  during an ordinary planning request. Discovery is read-only until the user
  selects durable refs; it may load `references/idea-source.md` only in that
  reference's validation-only mode. Selection activates the full source
  contract. The final `source_idea_refs` remain execution data, not options.
  Require `label` for GitHub Idea marker/workflow mappings and `local-header`
  for local mappings; reject missing or incompatible transports.
  Accept marker-valid Ideas as planning input only on the new-source route,
  when no durable `source_spec_ref` exists. Reject proposed Idea refs. On the
  existing-source route, derive `bound_source_idea_refs` only from exact
  `- Source Idea:` lines in the immutable Feature Spec set. Any explicitly
  supplied `source_idea_refs` must equal that complete bound set; reject
  additional, missing, different, or unbound refs.
- Keep one Plan Feature run bounded to one feature. Multiple selected Ideas may
  feed that feature, but unrelated Ideas require separate runs rather than one
  batch of unrelated Specs.
- Resolve one planning identity: `feature_slug` plus any selected product,
  workspace, context, or orchestrator-project identity.
- Derive `source_route=new-source` when no durable `source_spec_ref` is supplied
  or discovered, including an exact continuation of one recognized
  multi-repository publication transaction. Derive
  `source_route=existing-source` from one canonical final durable source ref.
  Foreign or ambiguous partial-publication artifacts block. This is execution
  data, never a selectable option.
- Converge only to a complete Feature Spec bundle. Never return or publish a
  standalone Feature Spec as a successful terminal result. A request to stop
  before issue generation is incompatible with this skill and returns a
  blocker, not a partial planning artifact.
- Require at least one final implementation issue for every
  implementation-eligible Feature Spec. A coordination-only parent is the sole
  zero-issue artifact; if a purported implementation Spec has no implementable
  outcome, block instead of treating the bundle as complete.
- Before issue-graph synthesis, enumerate the complete durable bundle. Seed the
  candidate graph with contract-equivalent existing issues as fixed IDs/slices,
  synthesize only uncovered scope, create only missing artifacts, repair only
  missing mapped tracker metadata or parent/sub-issue attachment, and return a
  verified no-op when the bundle is already complete. Never renumber or
  regenerate a retained issue. Dependency data and source-body sibling or
  cross-Spec relationships must already match; stop on stale, conflicting,
  duplicate, or extra implementation artifacts instead of rewriting them or
  creating parallel replacements.
- Immediately before any issue mutation, no-op, or proposal return, re-read the
  owning Feature Spec, Project Memory mapping transports, and complete issue,
  metadata, and relationship state. Recompute or block on drift, and verify
  exact absence again before each create. Revalidate every mapped native type;
  provision only exact missing mapped labels through verified `create-label`
  operations under `write_mode=apply`; proposal mode reports them without
  mutation.
- For any multi-repository new-source apply, treat initial Spec creation and
  exact cross-link finalization as one recoverable publication transaction.
  Predeclare every role, parameterized final-body template, and allowed ref
  slot plus the optional exact final-only body-metadata insertion. Stage only
  hosted roles whose refs are not yet known without that final metadata, resolve
  every durable or deterministic ref, materialize and hash the final bodies,
  finalize only the predeclared ref substitutions and metadata insertion, and
  verify the complete Spec set before issue generation. In a mixed-backend bundle, keep local bodies
  unwritten until hosted refs and bodies are final. In an all-local bundle,
  resume only exact missing predeclared file creates. A recognized
  same-transaction artifact is not a foreign race; any other appeared or
  changed target blocks.
- Until that transaction and the complete bundle converge, every partial-
  failure handoff must retain the complete parameterized body templates and
  hashes, allowed ref and body-metadata slots, role-to-target/ref map, selected
  `source_idea_refs` plus verified prior outcome refs, completed operations, and
  exact missing operations. A retry resumes only when that payload exactly
  matches current state; a hash without its reconstructable template is
  insufficient recovery evidence.
- Withhold incomplete artifacts. Return concrete blockers instead of
  publishing or labeling partial work agent-ready. The uniquely marked staging
  issues inside an authorized hosted publication transaction are temporary
  non-executable transport, not Feature Specs or successful Plan Feature output.
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
  source. On the existing-source route, every target must already fit the
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
- Until that final issue is durable and verified, every partial-failure report
  must return an exact continuation handoff containing `feature_slug`, the
  durable or staged Spec refs, any applicable multi-repository
  publication-transaction identity, and the complete `knowledge_delta`. A retry
  must require exact-match continuation data; omission or mismatch blocks
  rather than silently dropping closeout.
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
- Run `$plan-harder` one or more times per missing final issue with
  `planning_mode=issue-hardening` and `output_surface=caller`, beginning only
  after vertical boundaries, scope, compression, and graph ownership have
  stabilized. Retain a contract-equivalent durable issue only when it already
  carries valid final hardening provenance and matches the stable desired
  contract. If new
  hardening exposes a graph-level defect, discard affected results, return to
  compression, and re-harden every materially changed unpublished issue.
  Persist only the final stable result and one provenance line.
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
| `$plan-harder` | For every missing final implementation issue after structural graph compression and durable-state reconciliation. | At least one issue-hardening call per missing issue, with only the final stable result persisted; contract-equivalent durable issues are validated and retained, and Plan Feature owns artifact writes. |
| `$gitstack:github-issues` | The owning tracker backend is GitHub and Idea or planning-bundle convergence needs exact reads, or `write_mode=apply` authorizes a tracker write. | Discovery, source validation, and convergence inspection are pure reads in either write mode and omit mutation fields; require complete all-state pagination through connector pagination or GitStack's read-only direct-`gh` gap fallback, never a fixed-limit listing, or block. For writes, translate each supported operation to `mutation_mode=apply`, the exact target, and one `issue_operation`; own safe transport, mapped metadata, parent/sub-issue attachment, verification, cleanup, and partial recovery. Proposal mode never requests dry-run mutations or returns executable commands. |

After implementation begins, generated implementation-issue lifecycle
mutations belong to the selected executor, not Plan Feature. Terminal
source-Idea reconciliation remains planning closeout and occurs before
implementation begins.

## Workflow

### 1. Resolve Setup, Write Mode, Source Route, And Identity

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

Resolve `write_mode` from `references/options.md`, then resolve enough accepted
planning identity to locate the canonical Feature Spec target. Inspect any
supplied ref and that exact target before freezing the route. One canonical
final durable Spec derives `source_route=existing-source` only when it is not a
member of an exact recognized incomplete transaction. No durable Spec derives
`source_route=new-source`; an exact recognized multi-repository publication
transaction, including its staged or final members, derives a continuation of
that route. Multiple, conflicting, foreign, or ambiguous candidates block.
Proposed refs never select the existing-source route. Then finish resolving
`feature_slug`, affected repositories, allowed paths, one target branch shared
only within each implementation-eligible Feature Spec, and any
product/workspace identity from accepted input and repository evidence.
For a multi-repository workspace, derive workspace behavior from
`repository_layout`; do not ask for another workspace-mode option.

On the existing-source route, collect the union of exact `- Source Idea:` refs
from the unchanged intake Spec and every required linked partial as
`bound_source_idea_refs`. Treat this as derived continuation evidence, never as
an option or permission to draft from an Idea again. When the invocation also
supplies `source_idea_refs`, require exact set equality with the bound set. An
additional, missing, different, proposed, or otherwise unbound ref blocks. No
bound refs means the existing-source route has no Idea lifecycle work.

Before ordinary Idea validation or discovery, inspect exact selected refs plus
the invocation or durable handoff for evidence that the complete requested
planning result already exists and only source reconciliation is incomplete.
When that evidence is present, load `references/idea-source.md` and run its
reconciliation-only recovery branch first. Do not enter ordinary source
validation, the Feature Spec or issue phases, reopen completed Ideas, or
republish planning artifacts. Stop after reporting the reconciled or still
missing operations.

Otherwise, when the existing-source route has `bound_source_idea_refs`, load
`references/idea-source.md` and run its immutable continuation validation. Read
the bound Ideas and prior outcomes only to verify their exact relationship to
the unchanged Spec set and to prepare lifecycle reconciliation after bundle
convergence; never normalize them into new requirements or draft from them.
On the new-source route, when the invocation supplies `source_idea_refs`, load
`references/idea-source.md`, run ordinary validation for every durable ref and
tracker owner, read all canonical Idea sections and prior outcomes, and require
explicit selection before combining multiple Ideas.

When the new-source route has no exact refs but the user explicitly asks to
discover captured Ideas, load `references/idea-discovery.md`. Resolve tracker owners before
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

On the new-source route, run `$grill-me-with-context` only when supplied intent
plus repository evidence cannot support a complete Feature Spec and safe issue
graph. Resolve one blocking decision at a time.

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

On the existing-source route, inspect open questions only to validate whether
the durable source can be consumed unchanged. Accept `knowledge_delta` only as
explicit accepted invocation data or an exact continuation handoff supplied
separately from the source; never infer it from or write it into the Feature
Spec. Require every target surface to resolve inside the unchanged source scope;
reject the delta instead of widening source or issue scope. A persisted delta or
`## Domain Knowledge Handoff` is incompatible input. If any answer or repair
would change the source, require a separately authorized Feature Spec update.
Keep `planning_blockers` separate and capture no durable knowledge in planning.

### 3. Run The Feature Spec Phase

Always run the canonical source-contract validation from
`references/spec-phase.md`, including the exact Feature Dependencies heading
and columns. On the existing-source route, start from any intake member and
traverse its links to require the complete connected unchanged Spec set. Return
each original body and ref without drafting or publication; a coordination-only
parent owns no issues. If any source needs a change or the set is incomplete,
require a separately authorized update. On the new-source route, load
`references/spec-template.md`, then pass:

- `write_mode`, derived `source_route`, and Project Memory facts;
- planning identity and repository scope;
- source-ref state and cross-Spec dependency rows;
- optional validated `source_idea_refs`, normalized Idea evidence, prior
  partial-outcome refs, transient durable coverage maps or report-only intended
  projections, and their per-Spec relevance mapping;
- optional `knowledge_delta` plus separate `planning_blockers`;
- optional exact multi-repository publication-continuation handoff with its
  reconstructable templates, slots, selected Idea/prior-outcome refs, and
  completed plus missing operations;
- `non_app_delivery_target` and `explicit_instruction_ref` only after explicitly
  loading the conditional reference; keep the latter as source evidence data.

Require a durable local or hosted `source_spec_ref` for `write_mode=apply`, or
a deterministic proposed ref and publication-order note for
`write_mode=propose`. Never persist a delta marker in the Spec or silently
downgrade `write_mode`. Route new blockers back through clarification. Always
pass the optional delta directly to the issue phase without adding it to any
Feature Spec body.

### 4. Run The Issue Phase

Load `references/issue-phase.md`, `references/issue-body-template.md`, and
`references/vertical-slices.md`. Pass the same identity, facts, write mode,
source ref, optional knowledge delta, workspace links, and validated cross-Spec
graph, plus any exact continuation handoff.

The issue phase owns vertical splitting, structural graph compression, durable
discovery before synthesis, fixed-ID reuse, uncovered-scope synthesis, missing
artifact output, `$plan-harder` passes per missing final issue, race
revalidation, metadata, dependencies, the Execution Contract, and reporting.
Existing issues must match the stable graph and body contract; conflicts stop
the run, while a complete matching applied bundle returns a verified no-op.

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

### 5. Reconcile Idea Sources

Skip this step when neither selected new-source `source_idea_refs` nor derived
existing-source `bound_source_idea_refs` are present. Otherwise load
`references/idea-source.md`. With `write_mode=apply` and a complete durable
result, determine cumulative `partial` or `full` coverage separately for every
selected or bound Idea from verified prior Specs plus that result. With
`write_mode=propose`, or
when another branch returned only a non-durable preview, leave the durable map
unchanged, leave every selected or bound Idea unchanged, and report only
`intended_coverage`, `intended_covered_scope`,
`intended_remaining_scope`, and intended transitions from the separate
projection.

With `write_mode=apply`, a terminal wait for one specific requester answer may
reconcile the affected Ideas to `needs-info` before a planning result exists.
Reconcile coverage only after every Feature Spec, implementation issue,
metadata mutation, and relationship in the complete applied bundle is durable
and verified. A
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

- resolved `write_mode` and derived `source_route`;
- Feature Spec ref or proposed ref, title, and target location;
- planning identity and Project Memory facts used;
- retained, created, or proposed issue refs in publication order, repaired
  mapped metadata or parent/sub-issue attachment, and verified no-op state when
  applicable;
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
- exact continuation handoff when publication is incomplete, including every
  created or staged Spec ref, any applicable multi-repository
  publication-transaction identity and its complete predeclared body templates,
  selected Idea and prior-outcome refs, completed and missing operations, and
  the complete `knowledge_delta` until its final owner issue is durable and
  verified;
- blockers and withheld artifacts;
- explicit App incompatibility when `non_app_delivery_target` is present.

When `knowledge_delta` is present, report `capture_outcome=deferred` plus its
actual or proposed final issue ref. Otherwise report
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
- `references/complete-bundle-proposal.md`: non-mutating complete-bundle
  `write_mode=propose` fixture.
