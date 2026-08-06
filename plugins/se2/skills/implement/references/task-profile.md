# Implement Task Profile

This is the skill-owned task profile for se2:implement. Pass the complete
profile to the shared task preflight before starting any role.

    task_profile: implementation-orchestration
    roles:
      - role: orchestrator
        model: gpt-5.6-sol
        reasoning: medium
        topology: single-orchestrator-task
        title_templates:
          singular: "🤖 Orchestrator · 1 Feature Plan"
          plural: "🤖 Orchestrator · <plan_member_count> Feature Plans"
      - role: feature-worker
        model: gpt-5.6-sol
        default_reasoning: medium
        allowed_reasoning:
          - medium
          - high
          - xhigh
        topology: one-feature-worker-per-plan-member
        title_template: "🛠️ Feature Worker · <Feature outcome>"

The orchestrator coordinates one or more authoritative Feature Plans and
derives transient execution units for each plan member. The Feature Worker
owns one complete plan member, its derived execution units, one verified
repository/project destination, one isolated worktree, and one PR.

The Feature Worker chooses technical design, implements and validates the
derived units, binds Feature acceptance criteria to the final exact HEAD, and
runs native review in the same task and worktree. Review is a phase of the
Feature Worker lifecycle, not another role or task.

Resolve one reasoning value per plan member after its plan passes hosted
readback and before worker startup. Select xhigh for multi-repository,
security, privacy, migration, concurrency, distributed-state, or
cross-system-contract work; high for several interacting components or
validation surfaces; medium for routine work. Issue count alone never selects
the level.

There is no model or reasoning fallback for the required orchestrator or
Feature Worker role. If the live runtime cannot verify the selected profile,
stop with unsupported-runtime before creating or monitoring the role.
