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
  Idea, Feature, Implement, and Audit workflow graphs.
  Feature owns the textual Feature Plan Set, sibling Feature registry, and local
  Macro Task graphs; Implement uses a small transient delivery graph
  reconstructed from live evidence.
- Every bundled skill owns `references/states.md`, a compact human-readable
  table that distinguishes workflow nodes from domain values, persisted
  statuses, checkpoints, modes, external observations, and output labels.
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
- skills/learn/ is the repository-knowledge entry point and owns a
  workflow registry for scope, evidence, confirmation, apply, and verification.
  Every invocation locally preflights the applicable AGENTS.md chain and
  CONTEXT.md routing; when authorized, it reconciles one concise pointer that
  tells future agents what shared context to maintain as the project evolves.
  It performs only authorized local-repository context changes and maintains
  evidence-backed Project Context, ADRs, localization memory, Code Review
  Rules, and proposal-first AGENTS.md compaction without external preflight,
  tracker, publication, task, or worker behavior. Explicit requests to
  remember, save, or preserve a hard repository rule select Learn
  automatically; when minimal project context is missing, Learn creates it
  before capturing the rule. In monorepos, the root owns shared knowledge while
  evidenced first-class subprojects may own local `AGENTS.md`, `CONTEXT.md`,
  optional localization memory, topics, and ADRs; authorized hierarchy updates
  move subproject-only material to its local owner. Learn can also be invoked
  explicitly as `se:learn`.
- skills/audit/ is the explicit read-only live-monitoring entry point. It
  exhausts every authoritative continuation or host/project partition before
  claiming complete inventory, deduplicates stable task identities, freezes an
  attributable active-session cohort, and marks capped or untraversable
  inventories partial. It reconstructs each observed SE workflow path from
  positive evidence and reports feedback, bugs,
  regressions, graph violations, and graph-design improvements. It never
  contacts monitored sessions, writes repositories, or persists audit state.
  Invoke it explicitly as `se:audit`.
- skills/implement/ is the explicit implementation entry point. One visible
  graph orchestrator follows a small transient workflow graph, owns an immutable
  selected repository set, and chooses serial or concurrent execution.
  Repository-bound workers are reusable lanes:
  serial Features may reuse a clean worker worktree, while concurrent work gets
  additional isolated lanes. Every Feature delta still gets its own branch and
  pull request; same-repository dependencies stack and cross-repository
  dependencies schedule standalone pull requests. Its one-table SQLite
  registry stores only host-local repository ownership. Workflow position,
  Feature, worker, Git, pull-request, review, and CI truth remain external, with
  no workflow ledger, persisted checkpoint graph, fixed task profile, or title
  gate. A newly published draft is intermediate: the worker makes the stable
  exact-head PR ready, waits for the automatic Codex review through the G-owned
  ready lineage, and cannot complete until current-head review is terminal
  clean; later fix SHAs use explicit G-owned re-review.
- skills/idea/ is the explicit capture entry point. It builds a transient
  session bundle and publishes verified hosted Ideas through the G-owned issue
  workflow by default. An explicitly requested preview remains entirely local
  and non-durable. It owns a workflow registry and can expose a transient
  idea-source handoff for later Feature planning; it never writes project memory
  or starts an application task.
  Invoke it explicitly as `se:idea`.
- Feature creates or resumes one visible planner task in a direct local project
  checkout without a Git worktree or fork. It explicitly passes
  `gpt-5.6-sol` with `high` reasoning, accepts the stable task receipt, and
  starts Intake in the planner's first turn. It has no bootstrap-only turn,
  effective-profile readback, identity self-attestation, title gate,
  execution-target comparison, or goal. One readback is reserved for a
  genuinely ambiguous creation effect.
- repository context starts at AGENTS.md and follows the repository's own
  instruction hierarchy; no documentation system is imposed.
- Feature analyzes one or more source issues and asks one consolidated batch
  only when material product decisions remain. Complete briefs, delegated
  choices, and safe explicit assumptions proceed directly. Optional read-only
  helpers may study or review; unavailable or prohibited delegation uses a
  serial planner lens. Clarification waits nonterminally. Once the draft is
  complete, Review verifies semantic quality plus stable identity, F-AC
  coverage, closed registry, dependency DAG, boundary, projection, and
  maintenance-preservation invariants. Correctable findings return to Plan
  while progress is made, and a hidden product decision returns to
  Clarification. There is no separate Plan Validation node or review-round
  state machine. Feature then returns one
  evidence-backed textual Feature Plan Set with genuinely distinct sibling
  Features. Each Feature has ordinary list-item acceptance criteria with stable
  `F-AC-NN` identities, its own closed Macro Task registry, and optional
  hard-outcome Feature dependencies; use vertical Macro Tasks when an outcome
  admits coherent slices. Same-repository Feature dependencies
  project to stack intent; cross-repository dependencies project to scheduling
  only. Feature publishes every parent Feature, every local child Task, these
  relations, and the final set registry through one publication adapter by
  default; it never creates a container issue. After exact identities exist,
  it reconciles every parent body in place with the final sibling and child
  mappings and reads the result back. The body and registries remain semantic
  authority. Feature then always attempts
  to mirror every Feature edge and every same-parent Macro edge as a native
  GitHub `blocked by` relationship. Each attempt is recorded; a native failure
  is reported but does not block a complete body-backed publication, while a
  missing attempt or result does. Existing-source maintenance removes only
  prior SE-owned native edges explicitly retired from the revised plan and
  preserves foreign edges. Optional
  label and native type classification may then use `g:github-tagger`. The
  tagger chooses the smallest relevant existing label set, including none, and
  zero or one available native type; Feature never presets `Feature`, `Task`,
  or any other metadata value. Classification never gates semantic publication.
  Explicit
  preview remains local and non-durable. Hosted publication requires G
  preflight and read-after-write verification.
- Feature maintenance uses the same graph: Intake rehydrates exact identities,
  Analysis bounds the requested change, Plan applies the smallest semantic
  patch, Review verifies preserved content and executor progress, and Publish
  updates and reads back the same issues. Any explicitly requested downstream
  handoff must reconcile before completion. Feature does not rehydrate or
  repair implementation execution units.
- Idea, Feature, and Implement keep local control-plane records
  separate from hosted artifacts and apply one shared portable-content gate
  immediately before each hosted write, including content returned by workers
  and tools.

SE is the active repository-local design surface for these workflows.
