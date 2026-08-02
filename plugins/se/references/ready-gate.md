# Ready-for-Agent Execution Gate

`ready-for-agent` is the execution gate for SE. `plan` owns applying
the exact label after hardening the implementation issue; `implement` owns
reading and enforcing the gate; G owns GitHub transport and
read-after-write verification.

## Gate scope

- The gate applies to every final implementation issue in the selected
  Feature Spec issue graph.
- The parent Feature Spec is not itself required to carry the label.
- A label on one issue never authorizes a different issue.
- For a linked multi-repository Feature Spec Set, every member must pass before
  any member of the set is claimed or scheduled.

## Preflight behavior

Before startup authorization, run-state preparation, claims, task creation, or
worktree creation, `implement` must:

1. Load the canonical `ready-for-agent` value and GitHub transport from
   `workflow-contract.md`.
2. Read the complete authoritative Feature Spec and implementation issue graph
   through the G issue workflow, with complete pagination and no
   mutation fields.
3. Verify that every final implementation issue carries the exact
   `ready-for-agent` label.
4. Re-read the gate metadata immediately before the first state or claim
   mutation and fail closed on a race or incomplete read.

If any required issue is missing the label, report `not-ready-for-agent` with
the exact Feature Spec and issue refs that failed. Do not prepare run state,
acquire claims, create workers or worktrees, request startup authorization, or
perform any tracker mutation. Route the incomplete Spec back to `plan`.

`implement` never adds, removes, or repairs this label as part of the gate.
Discovery-only runs may list candidates without evaluating the gate, but must
state that execution readiness was not checked.
