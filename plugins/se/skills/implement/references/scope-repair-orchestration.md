# Implement Scope Repair Orchestration

Use this branch only after a bootstrapped worker reports that a file required
by the accepted implementation lies outside the durable `allowed_paths`
envelope. This is not general replanning and it is not a file lease system.
The worker remains stopped and must not edit the requested path until the
protocol completes.

An explicit `$se:implement` execution request derives
`scope_repair_task_permission=granted` together with the general task-creation
grant. Root must not ask a later planner-task permission question. A denied
value can only result from an explicit task-creation denial; in that case the
assignment remains declaratively blocked without another question.

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
them before invoking `$se:feature`. Never put assignment IDs, task IDs,
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
3. If `scope_repair_task_permission=denied` because the user explicitly denied
   task creation, report the portable request and remain blocked. Do not ask
   another question.
4. Record and execute
   `create-scope-repair-task`. Resolve
   the assignment's authoritative saved repository project and host, and create
   once for the authorized operation. Create one separate visible Codex task
   without a worktree and do not use the
   prompt as title evidence. Independently observe the created
   task, verify its task ID, project, host, environment, state, and title, and
   record those facts plus the authoritative readback reference in the normal
   operation observation. If creation did not
   set the exact title, record and execute `set-scope-repair-title`, apply
   the available title fallback at most once with the exact title, and
   independently verify that readback
   when possible before invoking
`$se:feature` as the separate Feature task against the authoritative
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
5. If title initialization is missing, drifts, or cannot be independently
   verified, record `scope-repair-title-unverified` or
   `scope-repair-title-drift` and continue invoking `$se:feature` once the
   planner task identity, project, environment, and operational state are
   verified. Do not archive or keep the assignment blocked solely for title
   metadata. Require an exact title only when the user explicitly requested
   one, and never retry a title mutation to repair drift.
6. Wait for the planner task. Accept only the exact `scope_repair_result`
   contract from `$se:feature` with `repair_outcome=applied|no-op`, matching refs and
   repair ID, and a fresh authoritative readback proving the complete Spec and
   issue graph. `blocked` and `full-replan-required` leave the assignment
   blocked.
7. Recompute overlap from the newly read durable `allowed_paths`. When another
   same-root assignment still overlaps, wait for that assignment to finish and
   rerun the overlap check. Do not mutate the planning artifact again.
8. Build a typed scope-repair observation, then record and execute
   `send-scope-revision`. The follow-up targets the original worker task and
   contains the new complete stable contract, the planner result and readback
   refs, `contract_generation=N+1`, and the derived `scope_revision_id`.
9. Finish the recorded operation only after independent conversation readback
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

`create-scope-repair-task`, `set-scope-repair-title`, `archive-scope-repair-task`,
and `send-scope-revision` are protected recorded app operations. After
interruption, root reads the task or conversation before finishing or replaying
the same logical operation. A scope revision replay keeps the same operation
ID, repair ID, revision ID, and target generation. Never create a replacement
planner task, title operation, or revision operation for the same repair.

`assignment resume` remains limited to restoring the exact contract already
accepted by a blocked assignment. It never applies a scope expansion and never
changes `contract_generation`.
