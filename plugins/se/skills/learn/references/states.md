# Learn State Reference

This reference is the human-readable inventory of state used by `$se:learn`.
Keep workflow position separate from selectable fields, derived facts, result
values, persisted repository content, and presentation-only controls. Reused
words such as `deferred`, `blocked`, and `not-applicable` are meaningful only
with their owning field or surface.

Learn has no persisted workflow checkpoint, run-state ledger, generic
`run_mode`, or persisted write preference. Workflow nodes and run results exist
only for the current invocation. The repository documents Learn updates are
durable, but they do not persist the workflow's current node.

## Workflow nodes

| Node | Kind | Plain description |
| --- | --- | --- |
| `scope` | Action | Resolve the explicit knowledge request, repository scope, and smallest applicable memory slice. |
| `inspect` | Action | Read the applicable context surfaces and only the evidence needed for the selected operation. |
| `draft` | Decision | Prepare the exact targets, wording, evidence, unknowns, and links for the result or proposed change. |
| `confirm` | Decision | Determine whether the exact durable write has the required user or caller authority. |
| `apply` | Action | Apply only the authorized local documentation changes. |
| `verify` | Validation | Read the changed surfaces back and validate links, indexes, preserved content, and the diff. |
| `reported` | Terminal | Return a read-only or otherwise non-durable result. |
| `deferred` | Terminal | Stop coherently because a required user decision or confirmation is still pending. |
| `complete` | Terminal | Finish after an authorized local write has been verified. |
| `blocked` | Terminal | Stop because required evidence, authority, or verification is unavailable. |

## Field-qualified and domain states

| Owner | Values | Class and lifetime | Meaning |
| --- | --- | --- | --- |
| `memory_slice` | `domain-memory`, `durable-capture`, `translation-memory`, `agents-pointers`, `agents-compaction`, `code-review-rules`, `full-setup` | Selectable run field; transient | Selects the smallest Learn-owned knowledge surface. |
| `domain_operation` | `not-applicable`, `setup-bootstrap`, `inline-update`, `implementation-closeout`, `periodic-review` | Selectable run field; transient | Selects the domain-memory operation. Non-domain slices use `not-applicable`. |
| `capture_mode` | `inline`, `defer-to-caller` | Selectable handoff field; transient | Either perform an explicitly authorized composed capture or return the capture decision to the caller. |
| `execution_context` | `fresh-setup`, `existing-project-bootstrap`, `current-project` | Derived run fact; transient | Distinguishes no established context, an existing surface awaiting first accepted population, and established context being read or updated. The caller cannot select it. |
| `capture_outcome` | `captured`, `deferred`, `no-durable-change` | Result field; transient report | Reports whether every accepted item was verified, some item remains unresolved, or no durable update was needed. This `deferred` is not the workflow node unless the run also terminates there. |
| Project Context pointer state | `current`, `missing`, `stale`, `duplicated`, `not-applicable` | Derived repository fact; transient report | Describes the managed AGENTS.md pointer. Over-copied guidance is a reason for `stale`, not a separate canonical state. |
| Evolution-rule result | `current`, `updated`, `deferred` | Result fact; transient report | Reports whether the managed evolution guidance was already correct, changed, or left for later authority. |
| Translation-memory decision | `enabled`, `not-applicable`, `needs-confirmation` | Derived decision; transient report | Reports whether evidence supports TRANSLATION.md, localization does not apply, or a material question remains. |
| Code Review Rules evaluation | `forward-validated`, `statically-evaluated`, `rejected` | Result field; transient report | Records the candidate-rule evaluation. “Not forward-validated” is explanatory wording for the absence of runtime evidence, not another enum. |
| Code Review Rules apply result | `applied`, `no-op`, `blocked` | Result field; transient report | Reports the local rule-update operation without claiming that hosted review ran. This `blocked` is distinct from the workflow terminal unless the run also terminates there. |
| AGENTS.md compaction band | `< 50%`, `>= 50% and < 75%`, `>= 75% and < 90%`, `>= 90%` of 32 KiB | Derived measurement; transient report | Selects recommendation urgency only; crossing a threshold never grants write authority. |
| Compaction section disposition | keep in AGENTS.md, move to `project-context/<topic>.md`, never move out of AGENTS.md | Proposal decision; transient | Separates always-active rules from conditional detail while preserving the normative Code Review Rules contract. |
| ADR `Status` | `Accepted` | Persisted domain state | Learn creates only accepted, load-bearing ADRs and records this status in the ADR index. |
| Setup presentation | `Unknown`, `keep-current`, `done` | Presentation only; transient | `Unknown` marks absent or ambiguous display data; the other values control the setup conversation. They are not workflow or domain states. |
| `allow_implicit_invocation` | `false` | Persisted skill metadata | Requires an explicit Learn request. |

`knowledge_delta`, `write_authority`, destinations, evidence, confirmation,
before/after blocks, and unresolved questions are run data rather than enum
states. Never persist them as workflow configuration merely because they are
reported during a run.
