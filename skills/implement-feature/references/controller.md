# Typed Next-Action Controller

This file canonically owns post-registration phase routing. After registration,
the root runs only:

```text
scripts/ledger-cache --json controller next --ledger <absolute-ledger> --root-id <root-id> --expected-claim-fingerprint <64hex>
```

The command is a read-only, portfolio-scoped projection. Under the shared claim
store lock it proves that the supplied claim is still active and still owns the
ledger, then binds the result to the live root id, claim fingerprint, ledger
generation, and state fingerprint. A released, replaced, or stale claim fails
closed. Repeating the command against unchanged files is byte-for-byte
read-only and returns the same projection fingerprint.

The controller never infers implementation completion from prose, suppresses
claim heartbeats, creates a Goal, launches a task, performs a provider
mutation, or selects merge, enqueue, deploy, or post-merge work. Its
`packet_template` describes the next legal operation but is not launch or
mutation authority. Required external evidence remains a typed
`required_inputs` descriptor and is never guessed.

## Closed response

Every successful response has exactly: `ok`, `command`,
`controller_schema_version`, `tool_version`, `ledger_schema_version`, `ledger`,
`portfolio_key`, `root_id`, `binding`, `decision`, `phase`, `target`, `action`,
`action_owner`, `packet_template`, `allowed_transitions`,
`completion_criterion`, `blockers`, `required_contracts`, and
`projection_fingerprint`.

`decision` is `action`, `waiting`, `blocked`, or `terminal`. `target.scope` is
`portfolio`, `task`, `delivery`, or `closeout`. An action response has exactly
one action and an exact template; every non-action response has null action,
owner, and template plus no transitions or contracts. A waiting or blocked
decision uses an external-or-ledger completion predicate; only a terminal
decision uses `terminal-state`.

The template has exactly `schema_version`, `packet_kind`, `executor`,
`bound_arguments`, `required_inputs`, and `result_event_types`. Every required
input has exactly `name`, `type`, `source`, and `validation`. The base bound
arguments are always `ledger:absolute-path`, `root_id:identifier`,
`expected_claim_fingerprint:sha256`, `expected_generation:positive-integer`,
`expected_state_fingerprint:sha256`, and `target:target`. The per-action
`Arguments` column below is the complete additional field set; there are no
optional or unknown fields. `task-state-map` and `task-key-array` are sorted,
closed aggregates for all concurrent tasks selected in the same ranked phase.

## Action registry

The order below is the deterministic rank order. Recovery precedes baseline,
closeout, scheduling, delivery protocol operations, and visible-task phase
work. Within a predicate, tasks sort by source id then task key and deliveries
by delivery key. Concurrent tasks in the same selected visible phase are
aggregated; the controller never asks the caller to select a phase.

| Rank | Action | Phase / owner / template | Arguments | Inputs | Allowed result -> events -> next phase | Completion | Required contracts |
|---:|---|---|---|---|---|---|---|
| 1 | `reconcile-command-attempt` | operation-recovery / root-orchestrator / execution-command:visible-task | `task_state:task-state`, `task_observation_fingerprint:nullable-sha256`, `revision_key:nullable-sha256`, `attempt_id:operation-id`, `attempt_state:lower-kebab` | `command_observation:object` from execution-manifest | reconciled -> launch-observed, cancellation-authorized, terminal-observed -> current-task-phase | selected command attempt terminal | recovery-validation |
| 2 | `reconcile-provider-mutation` | operation-recovery / root-orchestrator / gitstack-operation:visible-task | task state/observation, revision key, `reservation_id:sha256`, `attempt_state:lower-kebab` | `provider_observation:object` from GitStack readback | reconciled -> mutation-started, mutation-observed -> current-delivery-phase | provider journal terminal | review-mutation-authority, recovery-validation |
| 3 | `reconcile-autoreview-attempt` | operation-recovery / root-orchestrator / execution-command:visible-task | task state/observation, revision key, `reservation_id:sha256`, `attempt_state:lower-kebab` | `autoreview_observation:object` from attempt journal | reconciled -> attempt-observed, autoreview-observed -> delivery-autoreview | attempt and evidence terminal | autoreview-fix-loop, recovery-validation |
| 10 | `observe-root-title` | baseline-registration / root-orchestrator / app-operation:root-orchestrator | none | `title_observation:object` from App readback | recorded -> root-title-observed -> baseline-task-setup | current root title evidence | run-state |
| 20 | `dispatch-baseline-tasks` | baseline-task-setup / root-orchestrator / app-operation:root-orchestrator | `task_keys:task-key-array` | `task_creation_results:array` from App readback | recorded -> checkout/task observations -> baseline-task-setup | all selected task bindings | worker, baseline-validation |
| 30 | `observe-baseline-tasks` | baseline-task-setup / root-orchestrator / app-operation:root-orchestrator | `task_keys:task-key-array` | `task_observations:array` from direct full reads | recorded -> checkout/task observations -> baseline-validation | all baseline bindings current | worker, baseline-validation |
| 40 | `complete-implementation-baseline` | baseline-validation / root-orchestrator / worker-phase:visible-task | none | `baseline_receipts:array` from execution manifests | accepted -> baseline-accepted -> goal-activation; aborted -> preimplementation-aborted -> preimplementation-aborted | atomic baseline accepted or aborted | baseline-validation, worker |
| 50 | `activate-root-goal` | goal-activation / root-orchestrator / goal-operation:root-orchestrator | none | `goal_readback:object` from Goal readback | activated -> portfolio-goal-activated -> scheduling | matching root Goal active | run-state |
| 60 | `dispatch-ready-tasks` | scheduling / root-orchestrator / app-operation:root-orchestrator | `task_keys:task-key-array` | `dispatch_readbacks:array` from App readback | observed -> task-observed -> implementation | selected tasks have current full reads | worker, gates |
| 70 | `steer-implementation` | implementation / root-orchestrator / worker-phase:visible-task | `task_keys:task-key-array`, `task_states:task-state-map` | current implementation full reads | observed -> task-observed -> implementation-or-validation | selected tasks leave or complete implementation | worker |
| 71 | `steer-validation` | validation / root-orchestrator / worker-phase:visible-task | task keys/states | current validation full reads | observed -> task-observed -> validation-or-publication | selected tasks leave or complete validation | worker, gates |
| 72 | `steer-publication` | publication / root-orchestrator / worker-phase:visible-task | task keys/states | current publication full reads | observed -> task-observed -> publication-or-ready-transition | selected tasks leave or complete publication | worker, gates |
| 73 | `steer-ready-transition` | ready-transition / root-orchestrator / worker-phase:visible-task | task keys/states | current transition full reads | observed -> task-observed -> ready-transition-or-review | selected tasks leave or complete transition | worker, gates |
| 74 | `steer-review-fix` | review-fix / root-orchestrator / worker-phase:visible-task | task keys/states | current review-fix full reads | observed -> task-observed -> review-fix-or-review | selected tasks leave or complete finding repair | worker, autoreview-fix-loop, review-mutation-authority |
| 75 | `steer-ci` | ci / root-orchestrator / worker-phase:visible-task | task keys/states | current CI full reads | observed -> task-observed -> ci-or-tracker-closeout | selected tasks leave or complete CI | worker, gates |
| 76 | `steer-tracker-closeout` | tracker-closeout / root-orchestrator / worker-phase:visible-task | task keys/states | current tracker-closeout full reads | observed -> task-observed -> tracker-closeout-or-mergeability | selected tasks leave or complete tracker closeout | worker, gates |
| 77 | `steer-mergeability` | mergeability / root-orchestrator / worker-phase:visible-task | task keys/states | current mergeability full reads | observed -> task-observed -> mergeability-or-task-closeout | selected tasks leave or complete mergeability | worker, gates |
| 80 | `reserve-autoreview-action` | delivery-autoreview / root-orchestrator / ledger-event:root-orchestrator | task state/observation, revision key, `autoreview_projection:object`, `prior_evidence:nullable-object`, `hosted_obligation:nullable-object`, `reservation_event:object` | none | reserved -> autoreview-action-reserved -> delivery-autoreview-launch | active reservation | autoreview-fix-loop |
| 81 | `launch-autoreview-action` | delivery-autoreview-launch / visible-task / execution-command:visible-task | same exact AutoReview fields as reserve | none | observed -> attempt-observed, autoreview-observed -> delivery-autoreview | one terminal attempt for reservation | autoreview-fix-loop |
| 90 | `request-codex-review` | delivery-review-request / root-orchestrator / gitstack-operation:visible-task | task state/observation, revision key | `request_receipt:object` from typed GitStack readback | requested -> reservation/start/observation/wait-started -> delivery-review-wait | durable request and wait start | review-mutation-authority, gates |
| 91 | `invoke-review-wait` | delivery-review-wait / root-orchestrator / gitstack-operation:visible-task | task state/observation, revision key, wait start/deadline timestamps, `request_receipt:object` | `wait_invoked_at:timestamp` | invoked -> review-wait-invoked -> delivery-review-wait | single wait launch durable | gates, review-mutation-authority |
| 92 | `reconcile-review-wait` | delivery-review-wait / root-orchestrator / gitstack-operation:visible-task | task state/observation, revision key, wait start/deadline/invoked timestamps, `provider_timeout:nonnegative-integer`, request receipt | `review_observation:object` | observed -> review-observed/thread-resolved -> review-fix-or-ci | one current bound observation | gates, recovery-validation, review-mutation-authority |
| 100 | `apply-current-gate-evidence` | delivery-gates / root-orchestrator / ledger-event:root-orchestrator | task state/observation, revision key | `gate_evidence:array` | recorded -> gate/scope/nonregression observations -> current-task-phase | current gate evidence durable | gates, worker |
| 110 | `seal-task` | task-closeout / root-orchestrator / ledger-event:root-orchestrator | task state/observation, `revision_set_key:sha256`, `seal_candidate_fingerprint:sha256` | `seal_evidence_ref:string` | sealed -> task-terminal-sealed -> task-closeout | current revision set sealed | gates |
| 111 | `record-terminal-handoff` | task-closeout / root-orchestrator / ledger-event:root-orchestrator | task state/observation, `seal_fingerprint:sha256` | `handoff_evidence:object` | recorded -> terminal-handoff-recorded -> portfolio-closeout | unchanged seal handed off | gates |
| 120 | `verify-portfolio` | portfolio-closeout / root-orchestrator / ledger-event:root-orchestrator | `verification_fingerprint:sha256` | `verification_evidence_ref:string` | verified -> portfolio-terminal-verified -> portfolio-closeout | durable portfolio verification | gates |
| 130 | `complete-root-goal` | portfolio-closeout / root-orchestrator / goal-operation:root-orchestrator | `verification_fingerprint:sha256` | `goal_completion_readback:object` | completed -> portfolio-goal-completed -> portfolio-archive | matching Goal completion recorded | run-state, gates |
| 140 | `release-and-archive` | portfolio-archive / root-orchestrator / archive-operation:root-orchestrator | none | `archive_evidence_ref:string` | completed -> no ledger event -> terminal | claim released and ledger archived | run-state |

Event names in the table are abbreviated only for readability; the executable
registry and `result_event_types` emit the canonical ledger event names. Every
normal route loads at most three listed contract files; recovery loads at most
four. Callers cannot select or add contracts.

## AutoReview composition

`reserve-autoreview-action` embeds AutoReview protocol 2.0.0's unchanged pure
`next_projection` in `bound_arguments.autoreview_projection`. After the exact
reservation event is durably applied, `launch-autoreview-action` carries the
same bound subprojection in the controller envelope. Managed AutoReview 3.0.0
accepts only that envelope plus the active ledger reservation. There is no
standalone AutoReview projection route. Evidence/protocol remains 2.0.0,
attempt records remain 2.1.0, the initial-plus-terminal full-review rules stay
unchanged, and invalid structured output still permits only one bounded repair.

## Authority and recovery

CAS mutation commands must use the projected generation and state fingerprint;
a changed state requires rerunning the controller. A template alone grants no
App launch, Goal mutation, ledger mutation, AutoReview launch, or GitStack
provider mutation. GitStack operations still require their existing typed
request and, for physical mutation, the durable started-journal authority.

Unfinished execution commands, provider mutations, AutoReview attempts, and
review waits route to their exact reconciliation action before new work. An
ambiguous or consumed physical attempt blocks or reconciles; it never launches
a second physical attempt. Dependency-only portfolios return `waiting` with an
external-or-ledger predicate. Owner-required, failed, drifted, stale-claim, and
invalid-evidence states fail closed. Terminal output stops at a pull request
ready for the external merge workflow; this controller never merges.
