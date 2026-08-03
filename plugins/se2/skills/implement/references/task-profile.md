# Implement Task Profile

This is the skill-owned task profile for `se2:implement`. Pass the complete
profile to the root task preflight before starting either role. The preflight
must verify every required role before the implementation run begins.

## Required roles

```yaml
task_profile: implementation-orchestration
roles:
  - role: orchestrator
    model: gpt-5.6-sol
    reasoning: medium
    topology: single-orchestrator-task
    title_template: "🤖 Implement Feature · <Feature outcome>"
  - role: worker
    model: gpt-5.6-luna
    reasoning: max
    topology: one-worker-per-task
    title_template: "🛠️ Implement Task · <Task outcome>"
```

The orchestrator coordinates the selected Task set. Each worker executes one
eligible Task in its independently verified repository/project destination.
The orchestrator and worker roles are both mandatory; the orchestrator is not
a worker fallback and a worker is not an orchestrator fallback.

The title templates reuse the existing `se:implement` planner/controller and
worker emoji convention. Replace only the outcome placeholder with a short,
concrete, deterministic result; do not use titles as task identity or recovery
evidence.

There is no automatic model, reasoning, or topology fallback. If the live
runtime cannot verify either the Sol/medium orchestrator role or the Luna/max
worker role before startup, fail closed with `unsupported-runtime` and do not
launch the orchestrator or any worker.
