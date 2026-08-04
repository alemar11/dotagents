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
  Idea, Feature, Implement, and Audit workflow graphs. Feature keeps its separate
  Feature/Task dependency DAG; the Implement workflow consumes that DAG without
  becoming or rewriting it.
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
- skills/implement/ accepts one or more complete authoritative GitHub Features
  and returns a verified standalone or stacked PR topology. Its graph owns
  multi-Feature scheduling, a separate delivery projection, one isolated Sol
  Feature Worker and one PR per implementation-eligible Feature, serial Task-DAG
  execution inside that Feature worktree, exact-HEAD in-session review, Contract Repair through Feature
  maintenance, stack reconciliation, and final exact-HEAD evidence. A stack
  represents a true same-repository code dependency, never serialization alone;
  G owns PR publication and pairwise stack linking, while Send remains agnostic
  about whether an explicit PR base participates in a stack. GitHub interaction is
  mandatory end to end; there is no local-only or preview execution mode.
  Final provider readiness comes from the exact-head
  `g:github-delivery-status` contract; `ready` and
  `ready-with-manual-action` are accepted without granting Implement any merge,
  auto-merge, bypass, or queue authority.
  Feature and Task acceptance criteria use stable bracketed IDs rather than
  Markdown checkbox state; Feature Workers bind every Task criterion to the
  same final Feature candidate HEAD and the orchestrator aggregates Feature
  coverage without rewriting issue bodies. Zero-delta Features route through
  Contract Repair and never receive empty commits, cosmetic edits, or empty PRs.
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
- the prototype consolidates caller-proposed same-repository Feature splits
  that lack exclusive observable outcomes, then returns one minimal Feature
  plus vertical Task dependency graphs, including multi-repository Feature
  links and local dependency waves, without implementing code. Acceptance
  criteria are ordinary list items with stable
  `F-AC-NN` and `T-AC-NN` identities and explicit coverage. Feature publishes
  through an explicit terminal
  preview/publish subgraph with publish as the default and preview only by
  explicit request. Hosted publication requires the G preflight and
  read-after-write verification; the explicit SE2 request implicitly
  authorizes the exact in-scope GitHub writes.
- Feature maintenance is an alternate entry into the same graph: it rehydrates
  the current Feature/Task bundle, reconciles it, and emits a lateral Feature
  changelog comment for each significant published change.
- task-managed Feature and Implement runs pass their skill-owned profiles to
  the shared preflight; task creation scope and GitHub mutation scope remain
  independent, with no runtime fallback for a missing required role.
- Idea, Feature, and Implement keep local control-plane records separate from
  hosted artifacts and apply one shared portable-content gate immediately
  before each hosted write, including content returned by workers and tools.

SE2 is a parallel design surface and does not replace or mutate the existing
se plugin.
