# SE

SE is a software-delivery workflow plugin for maintaining project knowledge,
capturing Ideas, planning Features, delivering reviewed pull requests, and
auditing active work without changing it.

Its skills are deliberately separated by responsibility:

- skills/feature/SKILL.md is the graph manifest and Mermaid overview.
- skills/feature/steps/*.md are workflow nodes with a shared front matter
  contract.
- skills/feature/templates/ contains authoring resources, not executable nodes.
- references/workflow-graph.md is the shared structural contract for Learn,
  Idea, Feature, Implement, and Audit workflow graphs. Feature owns the textual
  Feature Plan Set, sibling Feature registry, and local Macro Task graphs;
  Implement derives its technical execution units and runtime graph from that
  durable set.
- Every bundled skill owns `references/states.md`, a compact human-readable
  table that distinguishes workflow nodes from domain values, persisted
  statuses, checkpoints, modes, external observations, and output labels.
- references/task-preflight.md and references/task-handoff.md are root-level
  contracts shared by task-managed Feature and Implement runs. Explicit
  invocation authorizes exactly the required user-owned tasks without a second
  prompt and rejects subordinate delegation as a required-role substitute. The
  controller may request an application destination, but only stable task
  identity, authoritative bootstrap, and role-specific target evidence gate the
  role. Implement's orchestrator is a projectless control plane with one
  authoritative observation per selected repository and no primary-repository
  binding; Feature Workers remain fully repository/worktree bound. The
  contracts also require an explicit, complete role-profile request
  with no ambient
  inheritance plus an authoritative, assignment-specific comparison between
  requested and effective model/reasoning before normal task monitoring. They
  freeze the applicable control-plane or repository-bound target and require the
  assigned task to verify every required fact. Saved-project association,
  ambient checkout, and project-root metadata are optional
  diagnostics that are never compared or used as gates.
- references/workflow-contract.md owns the Idea hosted shape, while
  references/codex-dependency-preflight.md owns the G dependency gate for Idea,
  Feature, and Implement hosted handoffs.
- references/hosted-content-safety.md owns mandatory portable-content
  projection, exact single-line title normalization, and local-path correction
  before every SE-hosted issue, comment, PR, or review write, plus one bounded
  non-blocking repair after readback. SE owns semantics; G owns transport and
  readback.
- scripts/validate-hosted-content-safety checks the shared owner routes, removed
  Idea duplication, and hosted templates for machine-specific absolute paths.
- skills/idea/references/idea-source.md owns the typed transient handoff from
  Idea capture to later Feature Intake; it never adds an automatic runtime
  dependency between the skills.
- skills/learn/ is the explicit repository-knowledge entry point and owns a
  workflow registry for scope, evidence, confirmation, apply, and verification.
  Every invocation locally preflights the applicable AGENTS.md chain and
  CONTEXT.md routing; when authorized, it reconciles one concise pointer that
  tells future agents what shared context to maintain as the project evolves.
  It performs only authorized local-repository context changes and maintains
  evidence-backed Project Context, ADRs, localization memory, Code Review
  Rules, and proposal-first AGENTS.md compaction without external preflight,
  tracker, publication, task, or worker behavior. Invoke it explicitly as
  se:learn.
- skills/audit/ is the explicit read-only live-monitoring entry point. It
  exhausts every authoritative continuation or host/project partition before
  claiming complete inventory, deduplicates stable task identities, freezes an
  attributable active-session cohort, and marks capped or untraversable
  inventories partial. It reconstructs each observed SE workflow path from
  positive evidence and reports feedback, bugs,
  regressions, graph violations, and graph-design improvements. It never
  contacts monitored sessions, writes repositories, or persists audit state.
  Invoke it explicitly as `se:audit`.
- task-handoff.md binds typed effective-role and execution-target observations
  to planner, orchestrator, and Feature Worker task identity, then applies the
  established SE Implement emoji-title grammar with authoritative readback and
  at most one bounded correction before monitoring; titles remain display
  metadata. Each task receives one flat semantic prompt with a best-effort
  canonical-title hint; raw or escaped delegation envelopes are never nested.
- skills/implement/ accepts one or more explicit GitHub parent Feature issue
  references, verifies their authoritative Feature semantic contracts and
  sibling dependency context, records local Macro projections as complete,
  partial, or absent, and returns a
  verified standalone or stacked PR topology. Its graph owns Feature-level
  scheduling, derives technical execution units and assignment-scoped T-AC
  criteria from each parent Feature plus available Macro context, creates one
  observable user-owned orchestrator task, then one observable isolated Sol
  Feature Worker task and one PR per
  implementation-eligible Feature. Fresh runs create those tasks; validated
  resumes reuse only their exact retained task identities. Runtime
  guidance loads by role and phase: orchestration, Worker execution,
  publication, and delivery monitoring remain separate contracts. Implement
  may use bounded delegated support
  assignments for code analysis, execution-unit assistance, validation, or
  critique when delegation and capacity are observed; otherwise the parent
  Worker continues serially. Implement selects exactly the parent Feature
  issues supplied by the caller and never discovers, selects, validates, or
  gates Features through GitHub labels or Issue Types. Sibling registries are
  read for consistency and dependency evidence, not to expand the selected
  implementation set. The caller may select a starting branch per
  target repository; otherwise Implement uses that repository's provider
  default. The orchestrator refreshes and freezes the selected branch's exact
  upstream tip before each root worker wave and verifies every isolated
  worktree against that base before implementation begins. The orchestrator has
  no Git checkout or worktree binding and never invents a primary repository
  for a multi-repository run. Before its first
  candidate, the Worker owns its local phase through a semantic workflow
  boundary, uses cheap changed-surface checks and a conditional
  read-only invariant critic for materially risky drafts, consolidates that
  pass before repairing it coherently, and defers complete validation until the
  source and prerequisite HEADs are stable. The Worker then performs exact-HEAD
  in-session review under verified local-only isolation with network,
  GitHub/provider access, hosted operations, repository mutation, and Git
  transport unavailable before first publication; after exact readback of the
  first published PR, hosted review becomes authoritative and later fixes update the
  same PR without rerunning native review. The workflow selectively
  invalidates dependent evidence, handles stack reconciliation, and requires
  complete validation plus clean hosted review on the same final exact HEAD.
  Every same-repository Feature dependency is mandatory stack intent, while a
  cross-repository dependency remains scheduling-only and standalone. A
  stacked child may begin from its parent's verified `candidate-published`
  exact HEAD before that parent is delivery-ready when no applicable
  current-head CI check is confirmed failing. Pending CI is allowed; only a
  G-diagnosed infrastructure or flaky failure unrelated to candidate
  correctness may bypass a confirmed failure. The orchestrator centrally
  monitors hosted review, CI, exact-head state, and stack drift through
  material-delta observations. At each scheduling point it executes the sole
  eligible authorized effect directly, retains arbitration when several
  effects are eligible, and waits without a status relay when none is
  eligible. Published Feature Workers remain inactive but resumable. Required
  Orchestrator and Worker roles never fall back to subordinate in-task
  delegation.
  G owns PR publication and pairwise stack linking, while Send remains agnostic
  about whether an explicit PR base participates in a stack. GitHub interaction is
  mandatory end to end; there is no local-only or preview execution mode.
  Final verification uses only the closed exact-head publication, hosted review,
  CI or authoritative no-checks, clean-worktree/HEAD, body/closure-intent,
  topology/stack, and acceptance evidence owned by the workflow. Implement
  never invokes delivery-status or requests provider-policy classification;
  externally supplied policy observations remain report-only and never grant
  merge, auto-merge, bypass, or queue authority.
  Feature acceptance criteria use stable bracketed IDs rather than Markdown
  checkbox state; Feature Workers may derive T-AC criteria that specialize but
  never replace or weaken F-AC, and bind both to the same final candidate HEAD.
  Available Macro outcomes remain contextual evidence; missing Task
  projections do not block when the parent semantic contract is sufficient.
  The orchestrator aggregates evidence without rewriting the plan. The PR
  closing set is derived independently for each Feature as its parent Feature
  plus every verified existing associated local Macro Task; missing refs are
  reported and never invented, while sibling Features and their Tasks are
  never included. Semantic contradictions that require changing outcome,
  scope, F-AC, or Feature dependencies are surfaced to the user; missing task
  decomposition, acceptance specificity, and ordinary technical interpretation
  remain Implement-owned. Native GitHub dependency state is diagnostic in
  Implement and is never repaired or used to override the body-backed graph.
  SE-authored PR bodies remain concise and durable: outcome summary, compact
  validation command or check names, material operational notes when needed,
  and canonical closing lines, without routine test counts or internal
  delivery logs. Pre-publication native review uses the minimal supported
  base-scoped mode inside its verified local-only isolation boundary, while
  later candidates stay in the hosted review lineage;
  publication runs from the reverified Feature Worker worktree rather than an
  inherited or temporary directory.
  Its SQLite WAL ledger stores exclusive Feature claims, durable checkpoints,
  and side-effect idempotency. Incompatible ledgers retain explicit
  drop-and-recreate instead of migrations; exact stale or foreign claims use a
  scoped atomic CAS recovery with durable operation audit evidence and
  idempotent retry.
- skills/idea/ is the explicit capture entry point. It builds a transient
  session bundle and publishes verified hosted Ideas through the G-owned issue
  workflow by default. An explicitly requested preview remains entirely local
  and non-durable. It owns a workflow registry and can expose a transient
  idea-source handoff for later Feature planning; it never writes project memory
  or starts an application task.
  Invoke it explicitly as `se:idea`.
- The Feature planner stays in the invoking session's exact local repository
  checkout and local environment without a Git worktree; isolated worktrees
  belong only to the separate Implement workflow. Saved-project metadata is
  optional diagnostic context.
- repository context starts at AGENTS.md and follows the repository's own
  instruction hierarchy; no documentation system is imposed.
- Feature analyzes one or more source issues and classifies the planning depth.
  Substantial planning runs separate bounded study and independent critic
  assignments when delegation is available, with a serial fallback that keeps
  the same lenses. It presents one consolidated batch of material questions by
  default; skipping that batch requires a narrow simple request, a traceably
  complete brief confirmed by the critic, or explicit user direction with no
  material decision left to guess. Once the draft is complete, the critic
  reviews it before validation, independently delegated when available.
  Correctable findings return for one bounded revision and a hidden product
  decision may trigger one follow-up question batch. It then returns one
  evidence-backed textual Feature Plan Set with genuinely distinct sibling
  Features. Each Feature has ordinary list-item acceptance criteria with stable
  `F-AC-NN` identities, its own closed Macro Task registry, and optional
  hard-outcome Feature dependencies; use vertical Macro Tasks when an outcome
  admits coherent slices. Same-repository Feature dependencies
  project to stack intent; cross-repository dependencies project to scheduling
  only. Feature publishes every parent Feature, every local child Task, these
  relations, and the final set registry through one publication adapter by
  default; it never creates a container issue. The body and registries remain
  semantic authority. After exact issue publication, Feature always attempts
  to mirror every Feature edge and every same-parent Macro edge as a native
  GitHub `blocked by` relationship. Each attempt is recorded; a native failure
  is reported but does not block a complete body-backed publication. Feature
  then delegates optional label and native type classification to
  `g:github-tagger` for each issue. The tagger chooses the smallest relevant
  existing label set, including none, and zero or one available native type;
  Feature never presets `Feature`, `Task`, or any other metadata value. An
  empty assignment is valid and does not block semantic publication. Explicit
  preview remains local and non-durable. Hosted publication requires G
  preflight and read-after-write verification.
- Feature maintenance is an alternate entry into the same Plan Set graph:
  it rehydrates the existing sibling Features, reconciles an explicit
  indication, and republishes the revised projections when requested. It does
  not rehydrate or repair Implement execution units.
- task-managed Feature and Implement runs pass their skill-owned profiles to
  the shared preflight. Explicit invocation authorizes exactly their declared
  user-owned application-task topology without a second prompt; task creation
  scope and GitHub mutation scope remain independent. Feature delegation is
  conditional on live capability and falls back to serial planner analysis;
  substantial planning still runs both study and critic lenses, while every
  principal task role remains required.
- Idea, Feature, and Implement keep local control-plane records separate from
  hosted artifacts and apply one shared portable-content gate immediately
  before each hosted write, including content returned by workers and tools.

SE is the active repository-local design surface for these workflows.
