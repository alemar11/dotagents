# Implement Task Profile

This is the skill-owned task profile for se:implement. Pass the complete
profile to the shared task preflight before starting any role.
Use [states.md](states.md) for the canonical distinction between persisted
assignment state and live Feature Worker or path-claim modes.

    task_profile: implementation-orchestration
    roles:
      - role: orchestrator
        model: gpt-5.6-sol
        reasoning: medium
        topology: single-orchestrator-task
        title_templates:
          singular: "🤖 Orchestrator · 1 Feature Plan Set"
          plural: "🤖 Orchestrator · <feature_set_count> Feature Plan Sets"
      - role: feature-worker
        model: gpt-5.6-sol
        default_reasoning: medium
        allowed_reasoning:
          - medium
          - high
          - xhigh
        topology: one-feature-worker-per-feature
        title_template: "🛠️ Feature Worker · <Feature outcome>"
    optional_roles:
      - role: feature-worker-support
        model: gpt-5.6-sol
        default_reasoning: medium
        allowed_reasoning:
          - medium
          - high
          - xhigh
        topology: bounded-feature-worker-support
    topology: orchestrator-with-feature-workers-and-optional-support

The orchestrator coordinates one or more authoritative Feature Plan Sets and
their verified sibling/Macro projections, then derives transient technical
execution units for each Feature. It also owns central exact-head PR
monitoring, stack-wide parent-drift reconciliation, assignment state, and
aggregate completion. The Feature Worker owns one complete
Feature member, its complete local Macro Task set, its derived execution
units, one verified repository/project destination, one isolated worktree,
and one PR.

The Feature Worker chooses technical design, implements and validates the
derived units, binds Feature acceptance criteria to the final exact HEAD, and
runs native review in the same task and worktree. Review is a phase of the
Feature Worker lifecycle, not another role or task.

After verified `delivery-pending @ candidate-published`, the Feature Worker
returns one bounded exact-HEAD handoff and becomes inactive but resumable. It
does not monitor its own PR. The orchestrator contacts that same Worker only
for an actionable fix, evidence repair, or rebase, after reacquiring the
Worker's path envelope.

The optional `feature-worker-support` role may be instantiated for bounded
code analysis, execution-unit assistance, validation, or critic review. It is
subordinate to the Feature Worker and never owns a Feature member, final
branch, ledger assignment, Feature Plan Set, or PR. The Feature Worker selects the useful
responsibilities and count from the plan, path envelopes, dependencies, and
observed capacity; no fixed helper count is required.

Resolve one reasoning value per Feature after its Plan Set passes hosted
readback and before worker startup. Select xhigh for multi-repository,
security, privacy, migration, concurrency, distributed-state, or
cross-system-contract work; high for several interacting components or
validation surfaces; medium for routine work. Issue count alone never selects
the level.

There is no model or reasoning fallback for the required orchestrator or
Feature Worker role. If the live runtime cannot verify the selected profile,
stop with unsupported-runtime before creating or monitoring the role.

Delegation is an optional capability of the Feature Worker topology. Record
one effective mode: `delegated-support` when bounded helpers were dispatched
and observed, `serial-fallback` when the parent performed the same support
work, `unavailable` when the runtime could not provide delegation, or `unknown`
when capability evidence was insufficient and no helper was claimed. A
missing optional capability never blocks the required orchestrator or Feature
Worker; the parent continues serially.
