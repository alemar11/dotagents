# Task, Baseline, And Command Event Contract

Load only for baseline setup/acceptance, task dispatch/steering, command
recovery, dependency waits, delivery observation, source move, or AutoReview
obligation. `ledger-cache` owns the generic envelope, common binding fields,
CAS, canonical encoding, and typed template. This file owns these event
families' phase-specific inputs and evidence.

| event | phase-specific inputs and evidence |
| --- | --- |
| `checkouts-observed` | Task identity plus the complete registered delivery checkout map and evidence. |
| `baseline-accepted` | Current CAS/scope binding, every registered baseline manifest and receipt byte digest, and acceptance evidence. |
| `preimplementation-aborted` | Closed reason, complete task-stop evidence, unchanged-checkout proof, and abort evidence. |
| `preflight-observed` | Exact delivery/GitHub/branch/default-base identity, definitive CI availability, preflight key, and evidence. |
| `command-reserved` | Delivery, one-attempt command/manifest/policy identity, attempt/receipt refs, current task observation, and evidence. |
| `command-launched` | Same attempt identity, durable launch fingerprint, and evidence. |
| `command-cancel-authorized` | Same attempt, closed cancellation reason, current observation, and evidence. |
| `command-finished` | Same attempt, closed terminal status, receipt digest when applicable, cleanup verdict, and evidence. |
| `task-observed` | Exact `model`, `reasoning_effort`, `thinking_reason`, `task_title`, `task_title_evidence_ref`, `task_assignment_fingerprint`, `observation`, `state`, `outcome`, `attention_reason`, `summary_ref`, and bounded direct full-read evidence. |
| `dependency-wait-started` | Exact current resume phase, reason/summary, current observation, and evidence. |
| `dependency-wait-resolved` | Same bound resume phase, current observation, and evidence. |
| `revision-observed` | Exact `repository`, `github_repository`, `pr_number`, `pr_url`, `head_sha`, `base_ref`, `merge_base_sha`, delivery/task binding, and evidence. |
| `delivery-observed` | Current revision key, exact PR lifecycle object, committed/published truth, and evidence. |
| `source-moved` | Exact task, predeclared from/to refs, unchanged source fingerprint, tracker repository, prerequisite revision-set key, and evidence. |
| `hosted-finding-obligated` | Delivery, obligation ref, source result fingerprint, and evidence. |

The managed checkout map contains every delivery exactly once and binds
repository, absolute App checkout/Git top-level, target branch, baseline
revision/tree/status, execution scope, and isolation. Baseline acceptance
contains every registered `(task,delivery,validation)` tuple exactly once;
partial acceptance changes nothing.

Command statuses are `passed`, `failed`, `timed-out`, `cancelled`,
`output-limit`, `interrupted`, and `cleanup-failed`. A null receipt digest is
valid only for interrupted or cleanup-failed controller loss. One command id
never receives another physical attempt.

Task states are `created`, `implementing`, `validating`, `draft-pr`,
`readying-pr`, `review-wait`, `fixing-review`, `ci`,
`tracker-closeout`, `mergeability`, `dependency-wait`,
`sealed`, `merge-ready`, `blocked`, `needs-owner`, and `failed`.
Before baseline acceptance, a task remains `created`.

The PR object binds repository identities, number/URL, lifecycle/draft,
head/base/merge-base, mergeable/merge-state, and closing refs. A newer current
committed and published observation is required to clear local tracker dirt.
