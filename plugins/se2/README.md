# SE2

SE2 is an experimental issue-first, graph-first workflow plugin for durable
repository context, Idea capture, Feature planning, verified Feature
implementation, and read-only live session auditing.

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
- references/task-preflight.md and references/task-handoff.md are root-level
  contracts shared by task-managed Feature and Implement runs.
- references/workflow-contract.md owns the Idea hosted shape, while
  references/codex-dependency-preflight.md owns the G dependency gate for Idea,
  Feature, and Implement hosted handoffs.
- references/hosted-content-safety.md owns the portable-content projection and
  fail-closed check immediately before every SE2-hosted issue, comment, PR, or
  review write. SE2 owns semantics; G owns transport and readback.
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
  se2:learn.
- skills/audit/ is the explicit read-only live-monitoring entry point. It
  freezes an attributable active-session cohort, reconstructs each observed
  SE2 workflow path from positive evidence, and reports feedback, bugs,
  regressions, graph violations, and graph-design improvements. It never
  contacts monitored sessions, writes repositories, or persists audit state.
  Invoke it explicitly as `se2:audit`.
- task-handoff.md applies the established `se:implement` emoji-title grammar
  to planner, orchestrator, and Feature Worker tasks, with authoritative readback and
  at most one bounded correction before monitoring; titles remain display
  metadata.
- skills/implement/ accepts one or more complete authoritative GitHub Feature
  Plan Sets with verified sibling Feature/Macro projections and returns a
  verified standalone or stacked PR topology. Its graph owns Feature-level
  scheduling, derives technical execution units from each Feature and its
  local Macro Tasks, creates one isolated Sol Feature Worker and one PR per
  implementation-eligible Feature, and may use bounded delegated support
  assignments for code analysis, execution-unit assistance, validation, or
  critique when delegation and capacity are observed; otherwise the parent
  Worker continues serially. The Worker performs exact-HEAD in-session review
  and the workflow handles stack reconciliation and final exact-HEAD evidence.
  A stack represents a true same-repository code dependency, never serialization alone;
  G owns PR publication and pairwise stack linking, while Send remains agnostic
  about whether an explicit PR base participates in a stack. GitHub interaction is
  mandatory end to end; there is no local-only or preview execution mode.
  Final provider readiness comes from the exact-head
  `g:github-delivery-status` contract; `ready` and
  `ready-with-manual-action` are accepted without granting Implement any merge,
  auto-merge, bypass, or queue authority.
  Feature acceptance criteria use stable bracketed IDs rather than Markdown
  checkbox state; Feature Workers bind every Feature criterion and every local
  Macro Task to the same final candidate HEAD;
  the orchestrator aggregates plan evidence without rewriting the plan. The
  PR closing set is derived independently for each Feature as its parent
  Feature plus every associated local Macro Task; sibling Features and their
  Tasks are never included, regardless of internal technical decomposition.
  Product-level plan contradictions are surfaced to the
  user; ordinary technical interpretation does not relaunch Feature.
  Its SQLite WAL ledger stores exclusive Feature claims, durable checkpoints,
  and side-effect idempotency, with explicit drop-and-recreate instead of
  migrations.
- skills/idea/ is the explicit capture entry point. It builds a transient
  session bundle and publishes verified hosted Ideas through the G-owned issue
  workflow by default. An explicitly requested preview remains entirely local
  and non-durable. It owns a workflow registry and can expose a transient
  idea-source handoff for later Feature planning; it never writes project memory
  or starts an application task.
  Invoke it explicitly as `se2:idea`.
- The Feature planner stays in the invoking session's exact saved local
  project and local environment without a Git worktree; isolated worktrees
  belong only to the separate Implement workflow.
- repository context starts at AGENTS.md and follows the repository's own
  instruction hierarchy; no documentation system is imposed.
- the prototype analyzes one or more source issues, runs optional bounded
  read-only analysts and an independent critic when delegation is available,
  presents one consolidated batch of material questions, and returns one
  textual Feature Plan Set with genuinely distinct sibling Features. Each
  Feature has ordinary list-item acceptance criteria with stable `F-AC-NN`
  identities, its own closed macro-vertical Task registry, and optional
  Feature-level planning dependencies. Feature publishes every parent
  Feature, every local child Task, planning-only relations, and the final set
  registry through one publication adapter by default; it never creates a
  container issue. Explicit preview remains local and non-durable. Hosted
  publication requires G preflight and read-after-write verification.
- Feature maintenance is an alternate entry into the same Plan Set graph:
  it rehydrates the existing sibling Features, reconciles an explicit
  indication, and republishes the revised projections when requested. It does
  not rehydrate or repair Implement execution units.
- task-managed Feature and Implement runs pass their skill-owned profiles to
  the shared preflight; task creation scope and GitHub mutation scope remain
  independent. Feature delegation is optional and falls back to serial
  planner analysis, while the principal planner role remains required.
- Idea, Feature, and Implement keep local control-plane records separate from
  hosted artifacts and apply one shared portable-content gate immediately
  before each hosted write, including content returned by workers and tools.

SE2 is a parallel design surface and does not replace or mutate the existing
se plugin.
