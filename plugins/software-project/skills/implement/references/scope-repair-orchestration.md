# Implement Scope Repair Orchestration

Use this branch only after a bootstrapped worker reports that a file required
by the accepted implementation lies outside the durable `allowed_paths`
envelope. This is not general replanning and it is not a file lease system.
The worker remains stopped and must not edit the requested path until the
protocol completes.

## Worker Request

The worker reports one structured request to root:

```yaml
scope_repair_request:
  assignment_id: "<assignment-id>"
  contract_generation: <integer>
  requested_paths:
    - "<repository-relative-path-or-complete-prefix>"
  reason: "<why the accepted contract requires these paths>"
  contract_evidence_refs:
    - "<acceptance-or-execution-contract-ref>"
  evidence_refs:
    - "<repository-or-diagnostic-ref>"
```

Paths are repository-relative, portable, and limited to the assignment's
repository. The request may identify current runtime facts, but root must strip
them before invoking `$software-project:plan`. Never put assignment IDs, task IDs,
worktrees, generations, claims, or worker state in the planning request.

Root rejects a request when it changes outcome, repository, source, target
branch, dependencies, acceptance, safety, validation constraints, GitHub PR
delivery, or any field other than a monotonic `allowed_paths` expansion. Exactly
one automatic repair is allowed per assignment. A second scope miss returns
`full-replan-required` and remains blocked.

## Root Protocol

1. Record `assignment scope-block` with the expected assignment revision. This
   preserves the same worker task, worktree, branch, bootstrap ID, and Feature
   Spec claim while placing the assignment in `blocked-scope-repair`.
2. Recompute same-root scheduling overlap using the requested paths and every
   active assignment's complete current `allowed_paths`. Missing path evidence
   conflicts. This is a scheduling check, not a persisted file claim.
3. If `scope_repair_task_permission=denied`, report the portable request and
   remain blocked. Do not ask another question.
4. Record and execute
   `create-scope-repair-task`. Create one separate visible Codex task in the
   assignment's saved repository project without a worktree. Set and verify its
   exact title as `🧭 Scope Repair · <Feature Spec title>`. Invoke
   `$software-project:plan` as the separate Plan task against the authoritative
   `source_spec_ref` and
   implementation issue using only this portable packet:

```yaml
scope_repair_request:
  repair_id: "<repair-id>"
  source_spec_ref: "<source-spec-ref>"
  implementation_issue_ref: "<implementation-issue-ref>"
  requested_paths:
    - "<repository-relative-path-or-complete-prefix>"
  reason: "<reason>"
  contract_evidence_refs:
    - "<contract-evidence-ref>"
  evidence_refs:
    - "<evidence-ref>"
```

   Root does not edit the Spec or issue itself. The planner task may publish
   only the monotonic `allowed_paths` expansion and then returns its result to
   root.
5. Wait for the planner task. Accept only the exact `scope_repair_result`
   contract from `$software-project:plan` with `repair_outcome=applied|no-op`, matching refs and
   repair ID, and a fresh authoritative readback proving the complete Spec and
   issue graph. `blocked` and `full-replan-required` leave the assignment
   blocked.
6. Recompute overlap from the newly read durable `allowed_paths`. When another
   same-root assignment still overlaps, wait for that assignment to finish and
   rerun the overlap check. Do not mutate the planning artifact again.
7. Build a typed scope-repair observation, then record and execute
   `send-scope-revision`. The follow-up targets the original worker task and
   contains the new complete stable contract, the planner result and readback
   refs, `contract_generation=N+1`, and the derived `scope_revision_id`.
8. Finish the recorded operation only after independent conversation readback
   proves the worker accepted that exact revision. The runtime atomically
   increments the assignment generation and restores its pre-block state.

Root, not the planner task, restarts the worker by sending the reconciled scope
revision. The planner has no worker identity or task authority.

## Worker Revision Rules

The worker accepts a scope revision only when all of these are true:

- the `bootstrap_id` is unchanged;
- `contract_generation` is exactly the previously accepted generation plus
  one;
- the `scope_revision_id` is present and has not been accepted before;
- the durable change is only a monotonic `allowed_paths` expansion;
- the requested paths are contained by the new envelope;
- the source and audit readback refs match the planner result.

For the same revision ID and identical generation and contract, acknowledge a
replay and continue without reapplying initialization. Reject the same ID with
different content, a skipped or stale generation, a different bootstrap ID, or
any other stable-field change. The worker then rereads the complete sources,
continues in the same checkout, and binds all later evidence to the new
generation.

## Recovery

`create-scope-repair-task` and `send-scope-revision` are protected recorded app
operations. After interruption, root reads the task or conversation before
finishing or replaying the same logical operation. A scope revision replay
keeps the same operation ID, repair ID, revision ID, and target generation.
Never create a replacement planner task or replacement revision operation for
the same repair.

`assignment resume` remains limited to restoring the exact contract already
accepted by a blocked assignment. It never applies a scope expansion and never
changes `contract_generation`.
