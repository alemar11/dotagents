# SE2

SE2 is an experimental issue-first, graph-first workflow plugin for durable
repository context, Idea capture, Feature planning, and verified Task handoff.

Its skills are deliberately separated by responsibility:

- skills/feature/SKILL.md is the graph manifest and Mermaid overview.
- skills/feature/steps/*.md are workflow nodes with a shared front matter
  contract.
- skills/feature/templates/ contains authoring resources, not executable nodes.
- references/workflow-graph.md is the shared structural contract for Learn,
  Idea, and Feature workflow graphs. Feature keeps its separate Feature/Task
  dependency DAG; Learn and Idea do not become Task graphs.
- references/task-preflight.md and references/task-handoff.md are root-level
  contracts shared by task-managed Feature and Implement runs.
- references/workflow-contract.md and references/codex-dependency-preflight.md
  are the SE2-owned contracts for Idea metadata and the G dependency gate.
- skills/idea/references/idea-source.md owns the typed transient handoff from
  Idea capture to later Feature Intake; it never adds an automatic runtime
  dependency between the skills.
- skills/learn/ is the explicit repository-knowledge entry point and owns a
  workflow registry for scope, evidence, confirmation, apply, and verification.
  It maintains evidence-backed Project Context, ADRs, localization memory,
  Code Review Rules, and proposal-first AGENTS.md compaction without tracker,
  publication, task, or worker behavior. Invoke it explicitly as se2:learn.
- task-handoff.md applies the established `se:implement` emoji-title grammar
  to planner, orchestrator, and worker tasks; titles remain display metadata.
- skills/implement/ is the Task execution entry point and owns its task
  profile and topology instead of inheriting the Feature profile; its required
  orchestrator and worker roles are checked before startup.
- skills/idea/ is the explicit capture entry point. It builds a transient
  session bundle, previews non-durable Ideas entirely locally, or publishes
  verified hosted Ideas through the G-owned issue workflow as its terminal
  operation. It owns a workflow registry and can expose a transient
  idea-source handoff for later Feature planning; it never writes project memory
  or starts an application task.
  Invoke it explicitly as `se2:idea`.
- The Feature planner stays in the invoking session's exact saved local
  project and local environment without a Git worktree; isolated worktrees
  belong only to the separate Implement workflow.
- repository context starts at AGENTS.md and follows the repository's own
  instruction hierarchy; no documentation system is imposed.
- the prototype returns one Feature plus vertical Task dependency graphs,
  including multi-repository Feature links and local dependency waves, without
  implementing code; GitHub publication is the internal final operation and
  requires explicit authorization plus read-after-write verification.
- Feature maintenance is an alternate entry into the same graph: it rehydrates
  the current Feature/Task bundle, reconciles it, and emits a lateral Feature
  changelog comment for each significant published change.
- task-managed Feature and Implement runs pass their skill-owned profiles to
  the shared preflight; task creation authorization and GitHub mutation
  authorization remain independent, with no runtime fallback for a missing
  required role.

SE2 is a parallel design surface and does not replace or mutate the existing
se plugin.
