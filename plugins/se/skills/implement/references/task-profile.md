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

The explicit se:implement invocation selects these role profiles as required
runtime inputs. Actively request both the resolved model and reasoning for the
orchestrator, every Feature Worker, and any optional support role instantiated
as its own application task. Never omit either value or rely on the invoking
session, application, project, host, or provider default. The orchestrator is
always requested as `gpt-5.6-sol` with `medium` reasoning; each Feature
Worker uses the assignment-specific reasoning resolved below.

The invoking task controller creates or resumes the orchestrator,
independently observes that exact task's stable identity, and verifies the
orchestrator's bootstrap identity binding. The orchestrator first reads its own
authoritative task-scoped execution context, performs the shared assigned-task
bootstrap self-check, and never creates or resumes another orchestrator for
the same run. After bootstrap, the orchestrator becomes the task controller
for every Feature Worker: it requests each Worker profile, independently
observes the stable Worker identity, and verifies the Worker's authoritative
self-bootstrap before implementation. A controller's own profile is never
compared with the assigned child profile.

The orchestrator coordinates one or more authoritative parent Feature semantic
contracts and their verified sibling context, records each Macro projection as
`complete`, `partial`, or `absent`, then derives transient technical execution
units and assignment-scoped T-AC criteria for each Feature. It also owns central exact-head PR
monitoring, stack-wide parent-drift reconciliation, assignment state, and
aggregate completion. The Feature Worker owns one complete
Feature member, its observed Macro projection and available local Task context,
its derived execution units and T-AC criteria, one verified repository target,
one isolated worktree, and one PR.

The Feature Worker chooses technical design, implements and validates the
derived units, binds F-AC and mapped T-AC criteria to the final exact HEAD, and
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

Actively request and freeze the resolved model and reasoning in each
orchestrator or Feature Worker handoff before creation or resume. Require the
shared handoff's explicit profile-request evidence; a matching value obtained
through ambient inheritance does not satisfy this invariant. After stable task
identity readback, require the exact assigned task to return the shared
handoff's typed `assigned_task_bootstrap` with authoritative effective values
that exactly match the request and an `evidence_task_identity` equal to the
stable identity observed by its controller. A request, creation receipt, or
unstructured self-report is not proof. A missing or unobservable exact-task
value is `unsupported-runtime`; present authoritative exact-task values that
differ from the assignment request are `effective-profile-mismatch`. Preserve
the observed task and do not create a replacement. A present evidence task
identity that differs from the controller-observed task is
`task-identity-mismatch`; a present repository, remote, worktree, or base
difference is `execution-target-mismatch`. Apply the same rule to optional
support only when it is instantiated as its own application task; subordinate
in-task delegation continues to use the delegation evidence below.

There is no model or reasoning fallback for the required orchestrator or
Feature Worker role. If the live runtime cannot actively request the selected
profile, observe the stable assigned-task identity, or receive the task's
authoritative bootstrap result, stop with unsupported-runtime before
role-owned effects or monitoring.

An Orchestrator or Feature Worker already running from a valid handoff applies
only the shared assigned-task bootstrap for its own role. It does not rerun the
controller's creation preflight against itself. Its structured authoritative
bootstrap is the operational profile gate, and its actual Git execution target
is compared separately with the frozen handoff. Its controller verifies
identity binding and does not duplicate the raw task-scoped profile read.

Delegation is an optional capability of the Feature Worker topology. Record
one effective mode: `delegated-support` when bounded helpers were dispatched
and observed, `serial-fallback` when the parent performed the same support
work, `unavailable` when the runtime could not provide delegation, or `unknown`
when capability evidence was insufficient and no helper was claimed. A
missing optional capability never blocks the required orchestrator or Feature
Worker; the parent continues serially.
