# Baseline Validation

Run the accepted baseline inside each newly bound App-managed worktree before
that worker receives implementation authority. The root Goal is already active;
Goal state is not edit authority.

## Worker Procedure

1. Verify the exact assignment, thread, checkout, Git top-level, checkout
   branch, baseline head, allowed paths, and literal validation commands.
2. Record current dirty state and relevant tool identity immediately before the
   command. Do not duplicate these checks in root bootstrap.
3. Execute the literal command through the App's normal sandbox and approval
   surface. Never infer safety from an executable name or silently rewrite it.
4. Record exit status, bounded output evidence, head, and dirty state after the
   command.
5. Report the exact baseline result to root without editing, committing,
   publishing, invoking reviews, or using Goal/task-management tools.

Exit zero with expected observations passes. A known existing failure may pass
only when the immutable Feature Spec explicitly defines exact non-regression
handling and the observed failure matches. Unknown, environmental, newly
mutating, unsupervised, or scope-drifting results do not pass.

## Root Fan-In And GO

Read the task and checkout before accepting its baseline. Record a passed result
with `run-state task baseline`; there is no generic event or model-selected
receipt.

For each dispatch wave, fan in all wave baselines before authorizing any worker
in that wave. When all pass, follow `app-orchestration.md` to journal and send
the explicit implementation-authorized message, then call `task authorize`.

If the first wave fails before any task is authorized, reconcile every created
task with `task abort`, finish the run as `preimplementation-aborted`, and
normally restart from current source after fixing transient setup. If an earlier
wave already implemented, preserve the run and repair or retry the same pending
task; do not discard completed work as a start-over shortcut.
