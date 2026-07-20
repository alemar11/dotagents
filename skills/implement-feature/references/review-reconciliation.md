# Exact-Head Review Reconciliation

Load this reference only when the current exact-revision review has completed
as `failed/blocked` with `failure_kind=request-correlation-failure`. This is a
high-impact edge case observed in two monitored uses, not a normal review path.

## Eligibility

The source observation remains immutable. Reconciliation is eligible only when
all of these stored values agree with GitStack's machine result:

- the delivery revision and full PR head are unchanged;
- `provider_state=failed` and `disposition=blocked`;
- `failure_kind=request-correlation-failure`;
- `provider_error_code=request_correlation_failure`;
- `request_binding` is `invalid` or `unknown`;
- no task terminal seal exists; and
- no prior reconciliation exists.

Never reconcile unbound or legacy plain requests, head drift, stale or
mismatched-head evidence, pending or timeout-accepted results, findings,
provider terminal errors, ambiguous evidence, or API, authentication, and
configuration failures.

## Provider Verification

Run exactly one read-only GitStack proof operation against the stored request:

```text
<plugin-root>/scripts/gitstack --json reviews terminal-evidence --provider codex --repo <github_repository> --pr <pr_number> --head <full-40-sha> --request-receipt-file <absolute-request-receipt-json>
```

GitStack must re-prove the exact typed request comment and receipt, current full
head, request interval, provider identity, terminal comment identity and body
fingerprint, provider `outcome=clean`, and absence of conflicting evidence. A later or
overlapping request, edited/deleted request, duplicate or multiple plausible
artifact, inline finding, findings/error formal review, mismatched head, or
other terminal outcome conflict fails closed. Do not use `check`, start another
wait, request again, retry a mutation, or change the deadline.

Success returns the complete
`gitstack-terminal-provider-evidence:v1` receipt. Persist no separate actor,
artifact, outcome, or body claim.

## Ledger Transition

Apply one `review-reconciled` event containing only the current task, delivery,
revision, source observation fingerprint, and complete GitStack terminal
evidence receipt. The helper validates the full closed receipt shape and
recomputes provider, artifact, and receipt fingerprints.

| Event | Exact fields |
| --- | --- |
| `review-reconciled` | `task_key`, `delivery_key`, `revision_key`, `source_observation_fingerprint`, `terminal_evidence_receipt` |

The event appends one `reviews[].reconciliations[]` item. It never changes the
stored request receipt, observation, wait start, wait deadline, invocation time,
provider timeout, or warning fields. Projection derives
provider review `clean/accepted` for the exact revision with
`effective_source=terminal-provider-evidence`; then apply
the ordinary delivery-bound `codex-review` gate with the verified artifact ref.
No unrelated gate changes automatically.

The same source plus byte-identical receipt is a no-op even under a new
operation id. A different source, artifact, receipt, provider, target, or
outcome conflicts. Terminal seal makes reconciliation permanently invalid.

## Historical Motivation Only

PR `ambrogio-dev/yn-ai-workflows#237`, head
`03dca5ad3e5603be343c9b927e372e25f5671f1e`, plain request comment
`5016644000`, and provider `outcome=clean` comment `5016657271` are non-executable
motivating metadata. That schema-5/plain-request incident is never imported,
migrated, adopted, or repaired. Executable replay uses only schema-8 state, a
valid typed exact-head request receipt, and a simulated correlation defect.
