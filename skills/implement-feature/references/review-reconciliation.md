# Exact-Head Review Reconciliation

Load only when the current-head review result is ambiguous or GitStack reports
request-correlation failure.

Reconciliation is eligible only when repository, PR, full head, request
identity, provider, and original operation key remain unchanged and the task is
not terminal. Never reconcile a plain or unbound request, head drift, pending
or warned-timeout state, findings, authentication/configuration failure, or
ambiguous multiple artifacts.

Use GitStack's read-only terminal-evidence or mutation-reconciliation path
against the stored request. It must prove the exact request, provider artifact,
head, outcome, and absence of conflicting evidence. Do not request again,
restart a wait, repeat a mutation, or change the deadline.

Finish the original `unknown` run-state operation with the verified result and
append a factual `review-reconciled` observation. Preserve the original false
or stale observation in history. A changed target or different result conflicts
and requires owner attention.
