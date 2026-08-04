# Implement Task Profile

This is the skill-owned task profile for `se2:implement`. Pass the complete
profile to the root task preflight before starting any role. The preflight must
verify the orchestrator and every concrete Feature Worker profile required by
the selected Feature set before implementation begins.

## Required roles

```yaml
task_profile: implementation-orchestration
roles:
  - role: orchestrator
    model: gpt-5.6-sol
    reasoning: medium
    topology: single-orchestrator-task
    title_templates:
      singular: "🤖 Orchestrator · 1 Feature"
      plural: "🤖 Orchestrator · <feature_count> Features"
  - role: feature-worker
    model: gpt-5.6-sol
    default_reasoning: medium
    allowed_reasoning:
      - medium
      - high
      - xhigh
    topology: one-feature-worker-per-feature
    title_template: "🛠️ Feature Worker · <Feature outcome>"
```

The orchestrator coordinates the selected Feature set with the fixed Sol/medium
profile. Each Feature Worker owns one complete authoritative Feature, one
independently verified repository/project destination, and all Tasks in that
Feature with `gpt-5.6-sol` and one resolved reasoning level from the allowed
set. The orchestrator and Feature Worker role classes are mandatory; neither is
a fallback for the other.

The Feature Worker implements its Task DAG serially inside one isolated
worktree, then runs exact-HEAD native review in the same session and worktree
with its already resolved `gpt-5.6-sol` reasoning level. Review is a phase of
the Feature Worker lifecycle, not another task profile or topology role.

The orchestrator uses the singular title when the authoritative selected
Feature set contains one Feature and the plural title when it contains more
than one. Freeze `<feature_count>` from that selected set before scheduling;
the count includes selected Features whose Tasks are waiting or blocked. It is
not a Feature Worker count, completed-Feature count, or execution-mode marker,
and the title must not change as waves or statuses change. Serial and parallel
execution use the same title rule.

## Feature Worker reasoning resolution

Resolve one reasoning value for each implementation-eligible Feature after its
complete Feature and Task bundle passes read-only intake and before startup
authorization. Evaluate the whole Feature, including interactions among its
Tasks, and keep that value stable for the Feature Worker's lifetime.

1. Select `xhigh` for risky or cross-system work:
   - multi-repository behavior or integration across independently deployed
     systems;
   - authentication, authorization, privacy, security, payments, or material
     data-loss risk;
   - schema or data migration, backward compatibility, or difficult rollback;
   - concurrency, distributed state, ordering, retries, idempotency, or other
     coordination-sensitive behavior;
   - architectural changes to externally consumed contracts across system
     boundaries.
2. Select `high` for complex work when no `xhigh` trait applies:
   - multiple interacting components or layers within one repository;
   - correctness depends on several state transitions, failure modes, or
     substantial behavioral edge cases;
   - nontrivial implementation tradeoffs across established contracts;
   - coordinated validation across multiple test or runtime surfaces.
3. Select `medium` for routine work when neither higher-level rule applies.

Issue count, changed-file count, or path count alone never selects a level.
Missing, stale, ambiguous, or contradictory execution evidence remains a
planning blocker; additional reasoning effort must not compensate for an
incomplete Task contract. If the selected model or reasoning value cannot be
verified from live capability evidence before Feature Worker creation, fail
closed with `unsupported-runtime`.

The title templates reuse the established planner, orchestrator, and worker
emoji convention. Keep `🛠️` and render every implementation task as
`🛠️ Feature Worker · <Feature outcome>`. Replace only the Feature outcome with
a short, concrete, deterministic result; do not use titles as task identity or
recovery evidence.

There is no automatic model, reasoning, or topology fallback. If the live
runtime cannot verify the Sol/medium orchestrator or an adaptive Sol Feature
Worker that can also run in-session review at the resolved reasoning level before
startup, fail closed with `unsupported-runtime` and do not launch any role.
