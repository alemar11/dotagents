# SE Plugin Maintenance

plugins/se/ is the repository's graph-first workflow package. Learn, Idea,
Feature, Implement, Implement Next, and Audit expose distinct workflow
surfaces; Feature owns the repository-scoped textual Feature Plan Set graph.
Keep SE as the sole active owner of these workflow contracts; do not
reintroduce a retired compatibility surface.

## Ownership map

- .codex-plugin/plugin.json owns SE identity, version, discovery metadata,
  and bundled-skill exposure.
- references/task-preflight.md owns the root-level live task capability for
  Feature and legacy Implement,
  explicit-profile request capability, assigned-task authoritative bootstrap
  capability, stable task-identity observation, execution-target verification,
  destination, authorization, display-title capability, update-relay, and
  recovery gates.
- references/task-handoff.md owns the Feature and legacy Implement task
  assignment, typed task-owned
  requested-versus-effective role observation, controller identity binding,
  assigned-task execution-target observation, flat semantic prompt projection,
  partial/final relay, deterministic emoji title grammar and first-prompt
  hint, bounded title reconciliation, and terminal-report evidence.
- references/workflow-contract.md owns the semantic Idea hosted shape for SE
  Idea capture.
- references/workflow-graph.md owns the shared workflow-graph vocabulary,
  registry rules, terminal meanings, authority boundaries, and validation
  expectations. It does not own Idea hosted metadata or Feature Plan semantics.
- references/codex-dependency-preflight.md owns the fail-closed availability
  gate before any SE workflow uses a required G-owned GitHub workflow.
- references/hosted-content-safety.md owns mandatory portable-content
  projection, exact single-line title-artifact normalization, and local-path
  correction before every hosted write produced by Idea, Feature, Implement,
  or Implement Next, plus one bounded non-blocking repair of the same artifact
  after readback. G owns transport and readback, not semantic cleanup.
- scripts/validate-hosted-content-safety owns the static owner-routing,
  duplicate-doctrine, and hosted-template path checks for that contract.
- skills/learn/SKILL.md owns independent durable repository-context routing,
  capture, localization, Code Review Rules, concise AGENTS.md Project Context
  pointer reconciliation, and AGENTS.md compaction proposals and its workflow
  registry; its references own branch-specific detail.
- skills/feature/SKILL.md owns the workflow graph manifest, Mermaid overview,
  node registry, Feature Plan Set, Feature identity, Feature-level dependency,
  and local Macro Task contracts, planning-depth and clarification routing,
  question-batch rules, conditional analysis roles, independent plan review,
  publication adapter, and terminal states.
- skills/feature/references/task-profile.md owns the required Feature planner,
  optional analyst roles, model/reasoning profiles, and topology selection.
- skills/feature/steps/ owns the Markdown node contracts. Every step file
  keeps the standard front matter and its declared transitions synchronized.
- skills/feature/templates/ owns reusable authoring templates and is not a
  node namespace.
- skills/implement/SKILL.md owns the GitHub-Feature-to-PR workflow registry and
  Mermaid projection. `references/orchestration.md` owns controller hierarchy,
  scheduling, topology, actionable-frontier selection, and compact handoffs;
  `references/worker-execution.md` owns Worker phase completion, optional
  support, pre-candidate convergence, candidate-bound validation, and
  hosted-finding repair semantics;
  `references/review-delivery.md` owns native review, publication, and stack
  reconciliation; `references/delivery-monitoring.md` owns hosted review, CI,
  provider diagnostics, repair observation, and final verification. The task
  profile and SQLite WAL references retain their existing profile and ledger
  ownership.
- skills/implement/scripts/run-state is the shipped checkpoint and idempotency
  CLI. Its version constants and schema are runtime sources of truth; focused
  tests live under skills/implement/tests/.
- skills/implement-next/SKILL.md owns the lightweight workflow graph and
  orchestration entrypoint. Its directly routed references own transition
  conditions, Feature-graph scheduling, repository claims, and its intentionally
  minimal state vocabulary. The entrypoint must not route
  through the legacy task preflight, task handoff, fixed profile, or run-state
  ledger contracts.
- skills/implement-next/scripts/repository-claims is the shipped host-local
  repository-ownership CLI. Its schema and version constants are runtime
  sources of truth; focused tests live under skills/implement-next/tests/.
- skills/idea/SKILL.md owns explicit session capture, the transient Idea bundle,
  workflow registry, preview/publish routing, and the capture-only terminal
  boundary. Its references own the canonical body, Idea source handoff, and
  publication recovery details.
- skills/audit/SKILL.md owns explicit-only active-session discovery, frozen
  cohort monitoring, evidence-calibrated graph-conformance reconstruction,
  finding classification, stopping behavior, and its read-only report.
- skills/audit/agents/openai.yaml owns Audit discovery metadata and must keep
  implicit invocation disabled. Audit has no scripts, ledger, task profile, or
  persistent output.
- .agents/plugins/marketplace.json owns repo-local discovery registration.

## Maintenance contract

- Keep Feature planning free of technical implementation authority. Feature
  publishes one complete Feature Plan Set containing only genuinely distinct
  sibling Features, each with a closed set of durable Macro Task projections.
  Use vertical slices when a Feature outcome admits coherent slices; never
  manufacture them by splitting technical layers. Feature-level `blocked_by`
  remains a planning-owned relation,
  but repository identity gives it a deterministic Implement projection: a
  same-repository edge is mandatory stack intent and a cross-repository edge
  is scheduling-only. Macro-local `blocked_by` remains planning-only and may be
  internalized by Implement while preserving every available Macro Task
  outcome. The Plan Set body and registries remain semantic authority for both
  relation levels. After exact hosted identities exist, Feature must always
  attempt one native GitHub `blocked by` projection per canonical edge:
  parent Feature to parent Feature, including exact URLs across repositories,
  and child Task to child Task only inside one parent Feature. A missing
  attempt or terminal result blocks publication, but a recorded `failed`,
  `unavailable`, or `unknown` provider result is a non-blocking warning and
  never invalidates the body-backed graph. Implement consumes each selected
  parent Feature as the required semantic contract, treats hosted Macro Tasks
  as `complete`, `partial`, or
  `absent` planning projections, derives technical execution units and T-AC
  criteria internally, and returns a verified standalone or stacked PR
  topology. A degraded Macro projection is reported but does not block when
  outcome, scope, F-AC, and Feature dependencies remain sufficient. Implement
  may derive missing execution coverage from the parent contract but never
  creates or repairs Task projections or native issue dependencies
  automatically. Native `blockedBy`/`blocking` state is diagnostic only in
  Implement and never changes scheduling or stack intent.
  Implement must not create an automatic plan-repair planner for ordinary
  technical interpretation.
- Keep Feature clarification proportional but explicit. Feature owns the
  derived `planning_depth` and `clarification_route` fields. Only a narrow,
  single-repository outcome with complete product boundaries and no material
  choice may be `simple`; every other request is `substantial`. A substantial
  request enters one consolidated clarification batch by default. It may skip
  that batch only when the user supplied a traceably complete decision brief
  and the independent critic confirms that no material product decision
  remains, or when the user explicitly requests no questions and the remaining
  uncertainty is safe to retain as assumptions. Material unresolved decisions
  still block rather than being guessed. When delegation is available,
  substantial planning must use separate bounded study and independent critic
  assignments; unavailable delegation falls back to the same serial lenses
  and never weakens the clarification gate.
- Require Plan Review between every complete Feature draft and Plan
  Validation. For substantial planning, reuse the independent critic
  assignment when delegation is available; otherwise record the serial critic
  fallback. The reviewer is read-only and the planner owns dispositions and
  revisions. Permit one bounded correct-and-rereview cycle for findings that
  need no user choice and at most one review-generated clarification batch.
  A repeated material finding, a second follow-up batch, or an unresolved
  disposition blocks before publication.
- Keep one human-readable `references/states.md` in every bundled SE skill.
  Each file is that skill's canonical state glossary: it must include every
  workflow node, separate workflow nodes from field-qualified domain or
  persisted states, and say explicitly when the skill owns no checkpoint or
  ledger. Do not present same-named values from different state domains as one
  shared state machine.
- Keep Feature acceptance criteria as ordinary list items with stable bracketed
  `F-AC-NN` identities, never Markdown checkbox state. Feature owns Plan Set
  identity, stable Feature identities, criterion identity, monotonic retirement
  high-water marks, source and question provenance, Feature-level dependency
  relations, each closed Macro Task registry, macro-local planning relations,
  and the durable parent/child projection. Implement owns technical
  execution-unit decomposition, assignment-scoped T-AC criteria, exact-head
  implementation evidence, and one source-derived closing set per Feature.
  T-AC may specialize but never replace, weaken, or reinterpret F-AC. Macro
  Tasks are planning views of the same Feature outcome; every verified existing
  local child is included with that parent Feature, while missing or
  quarantined projections are reported and never invented. Sibling Features
  and their Tasks are never included. The uppercase
  bracketed IDs are an explicit rendered-contract syntax exception to
  lower-kebab values.
- Keep Implement execution waves separate from PR delivery topology.
  Serialization, capacity, and path overlap do not create a stack. Every
  same-repository Feature `blocked_by` edge does create mandatory stack intent,
  independently of whether implementation otherwise runs serially or in
  parallel. Cross-repository edges remain scheduling-only. A stacked child may
  start from a verified `candidate-published` parent branch and exact HEAD
  before that parent is delivery-ready only when no applicable current-head CI
  check is confirmed failing. Pending CI is non-blocking; bypass a confirmed
  failure only when G-owned diagnosis verifies it as exclusively infrastructure
  or flaky and unrelated to candidate correctness. Multi-parent work remains
  blocked until one immediate parent candidate contains every required
  same-repository prerequisite HEAD. G owns publication and pairwise stack linking. Parent
  drift invalidates descendant evidence, and each worker owns its own
  bottom-to-top rebase and review cycle.
- Keep Feature Worker support delegation subordinate to the parent Worker.
  Delegation is optional and must fall back to serial parent execution when
  unavailable, unknown, or capacityless. Support assignments may return
  bounded evidence or scoped changes, but never own a Feature member, final
  candidate, PR, Feature Plan Set, GitHub mutation, or ledger state. Do not run
  overlapping writes in one worktree. Preserve the separate required-role
  topology: explicit Implement invocation authorizes the required hierarchy
  without a second prompt. A fresh run creates one observable user-owned
  application-task orchestrator and one observable user-owned Worker per
  Feature; a validated resume reuses only exact retained identities. Optional
  or subordinate delegation can never replace either required role;
  unavailable or unverifiable required tasks fail closed before role-owned
  effects. Saved-project routing and visibility are not role evidence.
- Keep the Implement ledger a minimal recovery index, not a second workflow
  engine. Preserve five tables, including exclusive active Feature claims,
  SQLite WAL, explicit drop-and-recreate for incompatible ledgers, scoped
  audited CAS recovery for exact stale/foreign claims, and the boundary against
  prompts, message logs, findings, and routine worker state. Scoped recovery
  must reuse atomic operation audit rows, exact owner/revision and authority
  evidence, unresolved-effect guards, and idempotent retry; it must never become
  a migration or claim-stealing shortcut. The orchestrator is the only runtime
  client; workers supply evidence but never access the ledger.
- Keep Implement Next's public runtime contract in its `SKILL.md` and directly
  routed references. Its repository-claims CLI remains an ownership-only
  implementation detail and the sole source of truth for its exact schema and
  version; workflow position must never be persisted there. Do not duplicate
  those runtime contracts in maintenance guidance.
- Keep Implement Next separate from the legacy task preflight, task handoff,
  fixed-profile, per-Feature-worker, title-reconciliation, and run-state ledger
  contracts. Maintenance must preserve that boundary and validate the owners
  named in the package ownership map.
- Keep Feature-level scheduling and derived execution-unit dependency edges
  separate. A Feature `blocked_by` edge may cross repositories. Implement maps
  every same-repository edge to mandatory stack intent and every
  cross-repository edge to scheduling-only context; it never treats capacity,
  path overlap, or preferred order as stack authority. A downstream stacked
  candidate must contain every exact same-repository prerequisite HEAD through
  one verified immediate-parent ancestry chain. `candidate-published` plus the
  absence of a confirmed applicable current-head CI failure, not PR readiness,
  is the development-unblock boundary. Pending CI remains non-blocking, with
  only verified infrastructure or flaky failures unrelated to candidate
  correctness exempt from the failure gate. Macro Task `blocked_by`
  relations remain planning context: Implement may combine, reorder, or
  internalize them only while preserving every available Macro Task outcome
  and every Feature acceptance criterion.
- Keep PR observation centralized in the Implement orchestrator. After
  `candidate-published`, the Feature Worker becomes inactive but resumable and
  the assignment remains `delivery-pending`; the orchestrator monitors exact
  PR heads, hosted review, CI, and parent drift. It contacts
  the same Worker only for actionable fixes, evidence repair, or rebase, and
  retains sole ledger and aggregate-completion authority.
- Keep review authority one-way. Native review is the exact-HEAD gate before
  the first PR publication. Once first-PR publication readback verifies its
  identity and HEAD, hosted review is authoritative for every later SHA:
  repair, validate, update the same PR, and request hosted re-review without
  invoking native review again.
  Invalidate only evidence that depends on the changed HEAD, body, base,
  topology, monitor lineage, or external effect; preserve unrelated durable
  identities and resolved receipts. Require complete validation and clean
  hosted review on the same final exact HEAD.
- Keep native review local-only. Its execution boundary must make network,
  GitHub/provider access, hosted workflows and operations, repository mutation,
  and Git transport unavailable while permitting read-only inspection of the
  frozen candidate and local scratch outputs. Bind verified isolation to the
  exact review lineage and candidate. Missing isolation blocks before launch;
  crossed or ambiguous isolation discards the entire review result and requires
  G-owned reconciliation of any suspected external effect.
- Keep Implement's completion evidence closed to exact-HEAD PR publication,
  hosted review, CI or authoritative no-checks evidence, clean Worker
  worktree/HEAD, body and source-derived closure intent, topology/stack, and
  Feature acceptance evidence. Implement never invokes delivery-status or
  requests branch-protection, ruleset, mergeability-policy, merge-queue,
  auto-merge, or provider-policy classification. Externally supplied policy
  observations are report-only and never affect a transition or checkpoint.
- Keep deterministic task-title initialization shared by task-managed Feature
  and legacy Implement. Compute the title before creation and include it as a
  best-effort plain-text hint in the flat creation prompt, without treating the
  hint as metadata or evidence. After stable identity readback, require one
  bounded reconciliation outcome before monitoring: exact verification or an explicit
  `title-unverified`/`title-drift` warning. Never use a title as identity,
  repeat an adjustment, or create a replacement task for title failure.
- Keep task prompts as flat semantic handoffs. Preserve bounded intent,
  constraints, source references, destination, validation, and return evidence,
  but unwrap raw task/delegation transport envelopes, escaped wrapper markup,
  parent prompts, and transcripts before creating a child task. Never use a
  transport wrapper as user intent or durable evidence.
- Keep effective task-profile verification shared by task-managed Feature and
  legacy Implement. The invoking skill owns requested role, model, reasoning,
  and topology; the shared preflight owns explicit-request, stable task-identity
  observation, and assigned-task bootstrap capability; and the shared handoff owns one typed
  assignment-specific self-comparison bound to the controller-observed task
  identity. Required profiles must be actively requested in full; ambient or
  configured-default inheritance is prohibited even when it happens to produce
  matching effective values. Reuse existing workflow outcomes, never persist
  this evidence in the Implement ledger, and never create a replacement after a
  mismatch or unobservable required profile.
  The task controller owns pre-effect capability verification, task creation or
  resume, independent stable identity observation, and bootstrap-result binding;
  the assigned planner, orchestrator, or Worker owns the authoritative,
  non-recursive bootstrap self-check before role work. Never compare the
  controller's own profile with the assigned child profile. Reject generic or
  unstructured self-report, but accept the typed bootstrap only when its
  authoritative evidence identity exactly matches the controller-observed task.
  Keep `unsupported-runtime` for unavailable or unobservable exact-task
  bootstrap evidence and use `effective-profile-mismatch` when present
  authoritative values for the exact assigned task differ from the request.
  Use `task-identity-mismatch` when present authoritative bootstrap evidence is
  bound to another task.
- Keep role-specific execution-target verification shared by task-managed
  Feature and legacy Implement. Preflight freezes either `repository-bound`
  Git/worktree facts or a `control-plane` repository-observation set. The
  Implement orchestrator uses a
  projectless control plane with no repository/worktree/primary-repository
  binding and one authoritative observation per selected repository. Every
  Feature Worker remains bound to its exact repository, remote, base
  branch/SHA, head branch, isolated worktree, and path envelope. Missing
  required observations select `unsupported-runtime`; present target-kind,
  repository-set, or bound-fact differences select
  `execution-target-mismatch`. Application routing, ambient checkout,
  saved-project association, and project-root metadata are optional diagnostics
  only: never infer, compare, refresh, retry, or block on them.
- For Implement Feature Workers, distinguish the selected integration
  `base_branch` from the worker-owned `head_branch`. An application-managed
  worktree may bootstrap detached at the exact frozen base SHA. Require the
  worker to establish and read back its Feature branch only after the
  assigned-task bootstrap and before the durable `worker-bootstrap`
  checkpoint or repository content writes. Apply the same rule when a stacked
  child starts from its parent's exact candidate SHA.
- Keep Idea capture independent from Feature Plan and Implement semantics while
  using the shared workflow-graph vocabulary. Session context may be assembled
  in transient run state, but only an explicitly published hosted issue is
  durable; Idea must not write project memory or create application tasks.
- Keep Idea hosted output behind the G-owned issue workflow and the shared
  fail-closed dependency gate. Never add a direct tracker transport or a
  compatibility alias for a missing dependency.
- Keep internal orchestration records distinct from hosted content. Internal
  records may retain local task/project/worktree facts; every hosted projection
  must pass references/hosted-content-safety.md immediately before write,
  including worker/tool-originated content. Correct or remove local paths before
  transport; if readback still exposes one, attempt one bounded update of the
  same artifact and retain a non-blocking warning when repair is unavailable,
  failed, or ambiguous.
- Keep hosted titles as exact non-empty single-line semantic values. Remove
  only serialization-added final line terminators before G transport, reject
  interior line breaks, and leave intentional multiline body content intact.
- Keep pre-publication native review and publication on verified execution boundaries. Select
  the minimal supported base-scoped review mode, avoid unsupported optional
  combinations and unrelated strict overrides. Reconcile a disconnected or
  interrupted delivery stream against the same review lineage and exact
  candidate before retry: accept matching terminal content independently of
  generic transport status, wait when the review remains active, and fail
  closed when identity, result, isolation, or binding is ambiguous. Run
  publication only
  from the independently re-observed Feature Worker worktree rather than an
  inherited or temporary-artifact directory.
- Keep Feature preview local-only. Route Feature maintenance or existing-source
  hosted Plan Set rehydration through the shared G dependency gate before
  hosted reads, and route default publication through the single publication
  adapter and G-owned issue workflow before any hosted mutation. Publication
  creates every sibling parent Feature, every local child Macro Task, their
  planning relations, and the final set registry readback without a container
  issue. After identities are final, attempt every exact native Feature and
  same-parent Macro dependency through `g:github-issues`, recording one
  verified, no-op, failed, unavailable, or unknown result per edge. Native
  failure does not downgrade a complete semantic publication. Then delegate
  optional label and native type selection to `g:github-tagger`; Feature must
  not preselect metadata values. Preserve the tagger's smallest-set policy:
  zero or more relevant labels and zero or one relevant type, with empty
  selections valid. Preview is opt-in and must never be selected implicitly
  when publish authority or G is unavailable.
- Keep Implement GitHub-backed end to end. It accepts authoritative published
  parent Feature semantic contracts with verified sibling context, tolerates
  `complete`, `partial`, or `absent` Macro projections, derives technical
  execution units and stable assignment-scoped T-AC criteria in the Implement
  control plane, and returns one
  verified hosted PR topology per Feature whose `closing_issue_refs` contains
  only that Feature's parent and every verified existing associated local Macro
  Task, with that intent carried by the PR body. GitHub
  `closingIssuesReferences` is optional
  diagnostic provider data and never a gate. It has no local-only or preview
  implementation mode.
- Keep SE-authored Implement PR bodies limited to a concise outcome summary,
  compact validation command or check names, material operational notes only
  when needed, and G-rendered closing lines. Keep routine test counts, pass
  totals, raw output, internal execution evidence, and mutable delivery
  diagnostics in exact-HEAD run evidence rather than hosted PR content. G
  preserves repository templates and unrelated existing author content.
- Keep Audit strictly observational. Attribute SE use only from task-visible
  evidence, treat missing visibility as indeterminate, and never add task
  contact, repository/GitHub mutation, delegation, or persistent audit state.
- Keep repository context discovery rooted at AGENTS.md hierarchy and generic:
  do not add a global context-document taxonomy. Feature records normative
  context separately from the critic analyst's independent first pass and
  reports conflicts rather than silently overriding repository instructions.
- Keep node IDs lower-kebab-case, unique, and consistent across front matter,
  each skill registry, Mermaid node names, and transition targets.
- Treat the node header and registry as the structural contract. Mermaid is a
  maintained projection of that contract, not an independent source of edges.
- Any committed change under this plugin requires a semantic version update in
  .codex-plugin/plugin.json.

## Validation

- Follow the repository testing rule: Python tests must exercise executable
  behavior or structured always-loaded metadata. Never assert Markdown wording,
  heading names, table layout, section placement, or moved prose. Use a bounded
  forward-model check when semantic workflow behavior cannot be established by
  executable tests or structured validation.
- Parse the plugin manifest as JSON.
- Validate the Idea skill front matter and UI metadata, canonical references,
  explicit-only invocation, and independent hosted-output boundary.
- Validate that every table-owned registry row matches its declared field order
  and arity, every registered local node exists, every local transition targets
  a registered node, and every step has the standard front matter.
- Validate Learn and Idea registry/projection reconciliation, terminal
  reachability, and the absence of outgoing transitions from terminal nodes.
- Validate Learn's invocation preflight, canonical AGENTS.md pointer shape,
  read-first routing, evolution-rule projection, and no-dangling-pointer rule.
- Validate Feature Plan Set graph reachability, genuinely distinct sibling
  Feature boundaries, Feature registry coverage, Feature-level acyclic
  planning relations, each local Macro Task registry, same-parent-only macro
  relations, planning-depth classification, substantial-feature clarification
  routing, question-free exception evidence, the question-batch wait boundary,
  conditional delegation and serial fallback, mandatory post-draft review,
  honest delegated-versus-serial reviewer provenance, bounded
  revision/re-review, at-most-one review clarification loop,
  publication-before-hosted-access, parent/child publication and readback,
  mandatory native-dependency attempts for every canonical edge, non-blocking
  native failure outcomes, reconciliation to `complete` or `blocked`, and the
  absence of side effects or outgoing edges on terminal nodes.
- Validate Idea default-publish/explicit-preview routing, Learn's local-only
  boundary, and Implement's mandatory hosted-source and PR-output path.
- Validate Implement registry/projection reconciliation, registered transition
  targets, terminal reachability, terminal nodes without outgoing edges, and
  the delivery gate, Feature-level scheduling, optional Feature Worker
  delegation fallback, exact sibling readback, degraded Macro projection
  tolerance, diagnostic-only native dependency drift without repair or gates,
  per-Feature source-derived closing sets, deterministic
  same-repository stack intent, F-AC-to-T-AC evidence mapping,
  `candidate-published` child unblocking, orchestrator-owned delivery
  monitoring, resumable Worker repair, and stack-reconcile paths.
- Validate exclusive Implement phase routing: the entrypoint remains the
  compact invariant/router, each role loads only its current phase owner,
  shared task-handoff remains the change-driven relay owner, and no moved
  doctrine is duplicated across orchestration, Worker execution, publication,
  and delivery monitoring. Validate complete initial Worker handoffs,
  role-local progress to an existing-node boundary, material-delta resumptions,
  and actionable-frontier behavior for exactly one, several, or zero eligible
  effects. These rules add no mode, node, status, checkpoint, or ledger field.
- Validate Implement's minimal durable PR-body projection, exclusion of routine
  execution counts, preservation of external template/author content, and
  exact closure-intent readback.
- Validate pre-candidate convergence inside `implement-validate`: risk-based
  critic selection, optional serial fallback, one completed consolidated set
  per pass, coherent repair, gap-driven checks, frozen-base reconciliation,
  isolated parallel validation, and complete candidate-bound validation. Keep
  the critic advisory, add no workflow or ledger state, and never weaken the
  mandatory exact-HEAD native-review gate or its invalidation rules.
- Validate native review's verified local-only isolation, minimal supported
  fallback, interrupted-stream reconciliation against the same exact candidate
  without duplicate review,
  and publication from the exact re-observed Feature Worker worktree rather
  than inherited or temporary directories.
- Validate the one-way native-to-hosted review handoff: published repair and
  rebase candidates must bypass native review, preserve the existing PR and
  hosted lineage, selectively invalidate dependent evidence, and recover
  complete validation plus clean hosted review on the same final HEAD.
- Validate that every bundled skill routes to `references/states.md`, every
  graph node appears in its skill's state table, Implement's documented
  persisted values exactly match the run-state capability registry, and
  Implement Next's small workflow registry, transition conditions, and Mermaid
  projection agree while every workflow node remains absent from
  repository-claim storage.
- Run scripts/validate-hosted-content-safety and validate that Idea, Feature,
  Implement, Implement Next, and their write-owning references route through
  the one canonical hosted-content owner without duplicate Idea doctrine.
  Include exact single-line title artifacts without serialization-added
  terminators.
- Validate that Feature and legacy Implement both route every created task
  through the shared typed assigned-task bootstrap, controller identity
  binding, and title-reconciliation outcome before normal monitoring or update relay;
  require the assigned task's non-recursive authoritative self-check before
  role-owned work; exclude the controller's own profile from child comparison;
  reject unstructured self-report and profile evidence bound to a different
  task identity; distinguish `unsupported-runtime`,
  `effective-profile-mismatch`, and `task-identity-mismatch`; and ensure resume
  paths cannot repeat an uncertain adjustment or create a replacement after a
  mismatch.
- Validate role-specific target freezing and assigned-task observation: the
  orchestrator control plane has a complete peer repository-observation set and
  no primary repository, while every Feature Worker retains exact Git/worktree
  bindings. Require `execution-target-mismatch` for present target-kind,
  repository-set, or bound-fact differences and `unsupported-runtime` for
  missing required observations. Verify that
  application routing, saved-project association, and project-root metadata
  remain outside required records and never trigger comparison, a second read,
  project inventory refresh, replacement task, or blocked outcome.
- Validate flat prompt projection, best-effort canonical-title prompt hints,
  mandatory title readback/correction, and removal of nested or escaped
  transport envelopes without losing semantic constraints.
- Validate the canonical bracketed Feature acceptance syntax, monotonic
  high-water marks, plan publication/readback, malformed and legacy-checkbox
  rejection, question-batch completeness, and Implement evidence bound to the
  current candidate SHA.
- Validate that Feature publication delegates label and native type selection
  only after exact issue readback, never presets metadata values, and preserves
  the tagger cardinalities of zero or more labels and zero or one type.
- Validate Audit explicit-only metadata, frozen-cohort and stopping rules,
  registry/projection reconciliation, exact transition-condition coverage, the
  intentional refresh loop, terminal reachability, exhaustive stable inventory
  traversal before complete coverage, explicit partial coverage at capped or
  untraversable boundaries, evidence classifications, and prohibited mutation
  behavior.
- Run the Implement run-state CLI help, version, read-only doctor, and focused
  standard-library tests against temporary databases.
- Run the Implement Next repository-claims CLI help, version, read-only absent
  doctor, and focused standard-library tests. Validate atomic overlap rollback,
  same-token acquisition reuse, immutable repository sets, exact whole-group
  bind and release, corruption detection, file permissions, and the absence of
  WAL, TTL, heartbeat, force-release, and execution-state storage.
- Use bounded forward-model scenarios to validate Implement Next selection
  scope, workflow-graph traversal, visible orchestrator placement,
  orchestrator-owned concurrency, serial worker reuse, same-repository stacks,
  cross-repository scheduling, resume reconstruction through `reconcile`, claim
  conflict behavior, and mutation boundaries.
- Check that the marketplace path and plugin metadata point to this package.
- Validate Learn front matter, UI metadata, routed references, explicit-only
  invocation, and the absence of retired compatibility surfaces.
- Scan Idea sources for direct provider access, durable-memory routing, model
  profile selection, and dependencies on the other plugin's Idea surface.
- Scan Learn sources for direct provider or tracker access, task/profile
  selection, stale legacy invocation names, and unowned local references.
- Run git diff --check before handoff.
