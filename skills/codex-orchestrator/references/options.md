# Codex Orchestrator Option Contract

Load this reference during `CLAIM`, before worker, publication, source, or
closeout decisions. It is the canonical registry for selectable orchestration
behavior. Statuses and runtime evidence are not options.

## Syntax

- Option field names use snake_case and match
  `^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$`.
- Enum values use lower-kebab-case and match
  `^[a-z0-9]+(?:-[a-z0-9]+)*$`. A one-word lowercase value already satisfies
  this rule.
- Counts, paths, refs, ids, timestamps, fingerprints, and evidence are data,
  not option values.
- Owner wording and source prose are selection evidence only. Normalize them
  once, persist the canonical field/value plus evidence, and never branch later
  on the original phrase.
- Emit only canonical option field names and values in ledgers, worker prompts,
  handoffs, recovery packets, and final reports. Read legacy aliases only for
  migration and rewrite them when touched.

## Session Registry

| Field | Allowed values | Default | Constraint |
| --- | --- | --- | --- |
| `delegation_mode` | `auto`, `disabled`, `bounded` | `auto` | `bounded` requires a positive `worker_limit`; `disabled` requires `worker_surface=root-thread`. |
| `worker_surface` | `auto`, `root-thread`, `cli-subagent`, `codex-app-thread` | `auto` | `codex-app-thread` requires `app_thread_consent=granted`. |
| `app_thread_consent` | `not-requested`, `granted`, `denied` | `not-requested` | Consent applies only to visible user-owned App tasks. |
| `raw_worktree_fallback` | `forbidden`, `owner-approved` | `forbidden` | Applies when the App cannot create the required managed worktree. |
| `active_root_takeover_policy` | `owner-approval`, `stale-ledger-check` | `owner-approval` | Controls overlapping-root recovery for the session. |
| `project_topology` | `single-repo`, `monorepo`, `multi-repo-workspace` | From project memory or safe repo evidence | Durable project layout. It is not an execution-order setting. |

`worker_limit` and `app_thread_limit` are data fields, not enums. Use a positive
integer when bounded; otherwise use `unbounded` for `worker_limit` and
`unspecified` for `app_thread_limit`. A positive limit must come from an
`owner-instruction` or evidence-preserving `legacy-migration` row and must
repeat the same scoped owner evidence as the corresponding
`delegation_mode=bounded` or `app_thread_consent=granted` row. A default source
may select only `unbounded` or `unspecified`.

## Per-Workstream Authority And Delivery Registry

Resolve these options independently for each stable workstream ID. One
workstream's authority or delivery value never applies to another by
inheritance. Discovery feeds use the narrower source registry below; a
registered issue, PR, checklist, file, commit, or CI item becomes an authority
scope only when it is registered as a workstream.

| Field | Allowed values | Default | Owner |
| --- | --- | --- | --- |
| `source_mutation_authority` | `none`, `propose`, `write` | `none` | Root resolves from the source and owner authority. |
| `publication_authority` | `none`, `explicit-owner-authorization`, `spec-backed-pull-request`, `blocked` | `none` | Feature Spec-backed delivery may supply `spec-backed-pull-request`. |
| `issue_mutation_authority` | `none`, `pr-body-closeout-only`, `explicit-direct-mutation` | `none` | Direct comments, labels, and closure require the explicit value. |
| `merge_authority` | `none`, `explicit-owner-authorization` | `none` | Merge remains root-owned. |
| `merge_policy` | `owner-approval`, `automatic-after-gates` | `owner-approval` | The automatic value requires matching explicit merge authority. |
| `caller_checkout_policy` | `preserve-current-branch`, `caller-checkout-approved`, `not-applicable` | `preserve-current-branch` | Checkout mutation is separate from publication authority. |
| `automation_authority` | `none`, `explicit-owner-authorization` | `none` | Authority applies only to the row's exact source/workstream automation target. |
| `temporary_source_execution` | `forbidden`, `owner-approved` | `forbidden` | Controls implementation dispatch from a non-durable `draft-spec:<...>` source; it never grants publication or issue mutation. |
| `completion_proof_policy` | `live-required`, `synthetic-accepted` | `live-required` | The exceptional value requires exact owner evidence naming the accepted proof gap and follow-up. |
| `delivery_mode` | `local-only`, `pull-request`, `direct-commit` | `local-only` for ad hoc sources | Feature Spec-backed sources inherit their canonical value. |
| `delivery_source` | `runtime-default`, `feature-level-inherited`, `issue-level-override`, `owner-instruction` | `runtime-default` for ad hoc sources | Source refs and authorization evidence remain separate data. |
| `workstream_project_topology` | `single-repo`, `monorepo`, `multi-repo-workspace` | From `issue_project_topology` for Feature Spec-backed work; session topology for ad hoc work | Preserves workstream topology separately from root session topology. |
| `pr_closeout` | `merge-ready`, `draft-only`, `not-applicable` | `merge-ready` for `pull-request`; otherwise `not-applicable` | `draft-only` requires canonical source or owner evidence. |
| `codex_review_policy` | `required`, `skip`, `not-applicable` | `required` for `pull-request` with `pr_closeout=merge-ready`; otherwise `not-applicable` | `skip` requires scoped owner-instruction evidence resolved to the exact workstream. |
| `pr_shape` | `single-pr`, `per-repo-pr`, `none` | Inherited for Feature Spec-backed work; `none` for ad hoc `local-only` | Repository refs and branch names remain separate data. |
| `closeout_mode` | `feature-pr-closes-issue`, `repo-pr-closes-issue`, `direct-commit-closes-issue`, `local-done-move-after-proof`, `not-applicable` | Inherited for Feature Spec-backed work; `not-applicable` for ad hoc work | Completion refs and proof remain separate data. |
| `integration_mode` | `single-repo-pr`, `repo-pr`, `direct-commit`, `not-applicable` | Inherited for Feature Spec-backed work; otherwise `not-applicable` | Integration refs and proof remain separate data. |

`branch_name` is required scoped data, not an enum option. Record it in the
same six-column resolution table for every workstream scope; use
`not-applicable` only with `delivery_mode=local-only`.
`current_pr_ref` is parallel runtime-derived scoped data. Use canonical
`<owner>/<repo>#<number>` after publication, `pending` before a pull-request
vehicle exists, and `not-applicable` for non-PR delivery. Refresh it from live
GitHub state before any review-policy action.
`scope_transfer_ref` is also required scoped data. Use `not-applicable` when no
generated-issue authority transfer exists; otherwise use the exact
`issue:<NN>` scope whose current handoff supplied the preserved authority.
`issue_mutation_transfer_ref` is the parallel required data row for separately
authorized issue mutation evidence. Use `not-applicable` unless an explicit
generated-issue mutation grant is transferred to the workstream.

## Discovery Source Registry

Each authoritative `## Discovery Sources` row has exactly one matching
`source:<Source ID>:source_mutation_authority` option row. No delivery,
publication, issue-mutation, merge, worker, branch, or scope-transfer option is
valid at a discovery-source scope. Those fields are resolved only after a
surfaced item is registered as a workstream.

Worker capability values are the `worker_authorization` registry in
`worker.md`; gate and lifecycle statuses are derived state, not selectable
options.

## Resolution Record

Record exactly one row per Session Registry field and one row each for
`worker_limit` and `app_thread_limit` before any dispatch. Record exactly one
row per Discovery Source Registry field for every `source:<Source ID>`. Record
exactly one row per Per-Workstream Registry field for every
`workstream:<id>`, plus `branch_name`, `current_pr_ref`, `scope_transfer_ref`,
and `issue_mutation_transfer_ref` data rows, before dispatch or mutation in that
workstream; use the canonical default or
`not-applicable` value instead of omitting an inactive field:

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `session:<field>` | `session` | `<Session Registry field>` | `<canonical value>` | `default`, `owner-instruction`, `runtime-capability`, or `legacy-migration` | `<instruction or tool ref or none>` |
| `source:<Source ID>:source_mutation_authority` | `source:<Source ID>` | `source_mutation_authority` | `<canonical value>` | <allowed source for this field/value below> | `<instruction, source, or tool ref or none>` |
| `<scope_id>:<field>` | `workstream:<id>` | `<Per-Workstream Registry field>` | `<canonical value>` | <allowed source for this field/value below> | `<instruction, source, or tool ref or none>` |
| `<scope_id>:branch_name` | `workstream:<id>` | `branch_name` | `<exact branch or not-applicable>` | <allowed branch source below> | `<source or owner evidence>` |
| `<scope_id>:current_pr_ref` | `workstream:<id>` | `current_pr_ref` | `<owner/repo#number, pending, or not-applicable>` | `runtime-derived` | `<current PR URL or none>` |
| `<scope_id>:scope_transfer_ref` | `workstream:<id>` | `scope_transfer_ref` | `<issue:<NN> or not-applicable>` | `source-contract`, `default`, or `runtime-derived` | `<exact source handoff evidence or none>` |
| `<scope_id>:issue_mutation_transfer_ref` | `workstream:<id>` | `issue_mutation_transfer_ref` | `<issue:<NN> or not-applicable>` | `source-contract`, `default`, or `runtime-derived` | `<exact source mutation evidence or none>` |

Keep `row_id` unique across the resolution set. This section is the sole owner
of the exact six-column schema: `row_id`, `scope_id`, `field`, `value`,
`source`, and `evidence`. Trim only outer cell whitespace and encode a literal
`|` in evidence data as `%7C`; never omit or reorder the leading ID columns.
Ledger tables project this schema, and recovery validation verifies it without
redefining its ownership.

If input wording is ambiguous between canonical values, ask for the field
choice. Once resolved, downstream logic reads the field, not the evidence text.

## Resolution Source Constraints

Resolution sources are field- and value-specific:

| Field/value | Allowed sources |
| --- | --- |
| `delegation_mode=auto`, `worker_surface=auto`, `app_thread_consent=not-requested`, `raw_worktree_fallback=forbidden`, or `active_root_takeover_policy=owner-approval` | `default`, `owner-instruction`, or `legacy-migration` |
| `delegation_mode=disabled` or `bounded` | `owner-instruction`, or `legacy-migration` preserving owner evidence |
| `worker_surface=root-thread` | `owner-instruction`, `runtime-capability`, or `legacy-migration` |
| `worker_surface=cli-subagent` or `codex-app-thread` | `owner-instruction`, or `legacy-migration` preserving owner evidence and required consent |
| `app_thread_consent=granted` or `denied` | `owner-instruction`, or `legacy-migration` preserving owner evidence |
| `raw_worktree_fallback=owner-approved` | `owner-instruction` |
| `active_root_takeover_policy=stale-ledger-check` | `owner-instruction` |
| `project_topology` | `project-layout-config`, `runtime-derived`, `owner-instruction`, or `legacy-migration` |
| `worker_limit=unbounded` or `app_thread_limit=unspecified` | `default`, `owner-instruction`, or `legacy-migration` |
| Positive `worker_limit` or `app_thread_limit` data | `owner-instruction`, or `legacy-migration` preserving the matching bounded-delegation or App-thread-consent owner evidence |
| `workstream_project_topology` | `source-contract`, `runtime-derived`, or `legacy-migration` |
| `automation_authority=none` | `default` or `runtime-capability` |
| `automation_authority=explicit-owner-authorization` | `owner-instruction` naming the exact source/workstream target |
| `temporary_source_execution=forbidden` | `default`, `runtime-capability`, or `source-contract` |
| `temporary_source_execution=owner-approved` | `owner-instruction` naming the exact draft source and execution scope |
| `completion_proof_policy=live-required` | `default` or `source-contract` |
| `completion_proof_policy=synthetic-accepted` | `owner-instruction` naming the exact proof gap and owner-visible follow-up |
| `source_mutation_authority=none` | `default`, `runtime-capability`, or `legacy-migration` |
| `source_mutation_authority=propose` or `write` | `owner-instruction`, or `legacy-migration` preserving owner evidence |
| `publication_authority=none` or `blocked` | `default`, `runtime-capability`, or `owner-instruction` |
| `publication_authority=spec-backed-pull-request` | `source-contract` or `legacy-migration` preserving the source contract |
| `publication_authority=explicit-owner-authorization` | `owner-instruction`, or `source-contract` preserving the exact scoped owner authorization evidence for `direct-commit` |
| `issue_mutation_authority=none` | `default` or `runtime-capability` |
| `issue_mutation_authority=pr-body-closeout-only` | `source-contract` |
| `issue_mutation_authority=explicit-direct-mutation` | `owner-instruction`, or `source-contract` preserving the exact scoped direct-commit closeout authority |
| `merge_authority=none` | `default`, `runtime-capability`, or `legacy-migration` |
| `merge_authority=explicit-owner-authorization` | `owner-instruction`, or `legacy-migration` preserving exact scoped owner evidence |
| `merge_policy=owner-approval` | `default` or `legacy-migration` |
| `merge_policy=automatic-after-gates` | `owner-instruction`, or `legacy-migration` preserving exact scoped owner evidence |
| `caller_checkout_policy=preserve-current-branch` or `not-applicable` | `default` or `runtime-derived` |
| `caller_checkout_policy=caller-checkout-approved` | `owner-instruction` |
| `delivery_mode=local-only` | `default` or `runtime-derived` |
| `delivery_mode=pull-request` | `source-contract` or `owner-instruction` |
| `delivery_mode=direct-commit` | `owner-instruction` naming the exact instruction, workstream scope, and target branch; or `source-contract` preserving that same owner evidence and branch data |
| `branch_name=not-applicable` | `default` or `runtime-derived` |
| Other `branch_name` data | `source-contract`, `owner-instruction`, `runtime-derived`, or `legacy-migration` |
| `current_pr_ref` | `runtime-derived` from the current GitHub PR vehicle, or `not-applicable` for non-PR delivery |
| `scope_transfer_ref=not-applicable` | `default` or `runtime-derived` |
| `scope_transfer_ref=issue:<NN>` | `source-contract` with the exact current generated-issue evidence |
| `issue_mutation_transfer_ref=not-applicable` | `default` or `runtime-derived` |
| `issue_mutation_transfer_ref=issue:<NN>` | `source-contract` with the exact current generated-issue mutation evidence |
| `delivery_source=runtime-default` | `default` or `runtime-derived` |
| `delivery_source=feature-level-inherited` | `source-contract` |
| `delivery_source=issue-level-override` or `owner-instruction` | `source-contract` with explicit authorization evidence, or `owner-instruction` |
| `pr_closeout=merge-ready` | `default`, `source-contract`, or `legacy-migration` |
| `pr_closeout=draft-only` | `source-contract`, `owner-instruction`, or `legacy-migration` preserving owner evidence |
| `pr_closeout=not-applicable` | `runtime-derived` from `delivery_mode`, or `legacy-migration` |
| `codex_review_policy=required` | `default` or `legacy-migration` |
| `codex_review_policy=skip` | `owner-instruction` preserving `owner-ref`, `scope-ref`, `target-ref`, and `pr-ref` evidence tokens; both scoped refs equal the exact workstream, while `pr-ref` is `not-applicable` for a workstream-scoped instruction or the immutable canonical PR named by a PR-scoped instruction |
| `codex_review_policy=not-applicable` | `runtime-derived` from `delivery_mode` and `pr_closeout`, or `legacy-migration` |
| `pr_shape`, `closeout_mode`, and `integration_mode` | `source-contract`, `runtime-derived`, or `legacy-migration` |

`runtime-capability` may restrict execution or select a blocked/none value; it
never grants mutation, publication, checkout, automation, or merge authority.
`legacy-migration` must preserve the original authority evidence and cannot
upgrade a default or ambiguous legacy value into a grant.

For `delivery_mode=direct-commit`, both the delivery and `branch_name` rows use
evidence containing these machine-readable tokens:
`owner-ref=<ref>;scope-ref=<scope_id>;target-ref=<source-or-mutation-target>;target-branch=<branch_name>`.
A source contract may preserve the tokens but must not synthesize them from
prose.
The effective `delivery_mode`, `delivery_source`, `branch_name`, and required
`publication_authority` rows must preserve identical delivery owner, scope,
target, branch, and applicable `scope-transfer-ref` tokens. A separately
authorized `issue_mutation_authority` row may preserve a different owner ref,
but its scope, target, branch, and transfer tokens must match the delivery
target.

Every authority-bearing value requires non-empty `owner-ref`, exact
`scope-ref`, and non-empty `target-ref` tokens. This includes raw-worktree/App
consent grants, write/propose authority, explicit publication or issue
mutation, merge authority or automatic merge policy, caller-checkout approval,
automation authority, temporary-source execution, synthetic-proof acceptance,
and owner-authorized delivery overrides. Generic evidence text is not scoped
authority.

A Feature Spec-backed scope transfer is valid only when the generated issue evidence
contains an exact issue `scope-ref`, preserved owner, target, and branch tokens,
and current source evidence. Feature-level inherited evidence also requires
the Feature Spec's preserved `target-ref` and `scope-transfer-ref=run`; issue-level
override evidence instead preserves its exact issue-scoped owner authorization.
When registering that issue as a workstream, the root may replace only
`scope-ref` with the exact `workstream:<id>` and set `scope-transfer-ref` to the
source issue scope in each evidence record; the workstream must point to that
same generated issue. Store the original delivery and issue-mutation evidence
in their separate transfer rows. Each owner, target, and branch token remains
unchanged.

## Cross-Field Validation

- `delegation_mode=disabled` requires `worker_surface=root-thread` and no active
  delegated worker.
- `delegation_mode=bounded` requires `worker_limit` to be a positive integer.
  Both rows must preserve identical non-empty `owner-ref`, `scope-ref=session`,
  and `target-ref` evidence tokens.
- Other `delegation_mode` values require `worker_limit=unbounded`.
- `worker_surface=root-thread` requires zero active delegated workers.
  `worker_surface=cli-subagent` permits only active `cli-subagent` workers, and
  `worker_surface=codex-app-thread` permits only active `codex-app-thread`
  workers. `worker_surface=auto` may use either delegated surface only within
  the matching consent and limit rows.
- `app_thread_consent=granted` requires a positive `app_thread_limit`, including
  when `worker_surface=auto`, and the consent and limit rows must preserve
  identical non-empty `owner-ref`, `scope-ref=session`, and `target-ref`
  evidence tokens. Other consent values require
  `app_thread_limit=unspecified`. `worker_surface=codex-app-thread` additionally
  requires the granted tuple before creating a visible task.
- `raw_worktree_fallback=owner-approved` is required before a raw Git worktree
  fallback in an App session.
- `project_topology=multi-repo-workspace` or a registered source/handoff with
  `workspace_context=multi-repo-workspace` requires the root to load
  `references/multi-repo-workspace.md` before worker dispatch. Other topology
  values must not load that reference unless workspace context selects it or a
  source contradiction needs owner-facing diagnosis.
- A matching scoped row with
  `automation_authority=explicit-owner-authorization` is required before an
  automation mutation for that exact workstream target.
- `temporary_source_execution=owner-approved` is required before dispatch from
  a `draft-spec:<...>` source. Publication and issue mutation still require
  their own scoped authority rows.
- `completion_proof_policy=synthetic-accepted` requires owner evidence naming
  the exact live-proof gap and owner-visible follow-up.
- `merge_policy=automatic-after-gates` requires
  `merge_authority=explicit-owner-authorization` for the named PR or PR set.
- `delivery_mode=pull-request` requires
  `pr_closeout=merge-ready` or `pr_closeout=draft-only` and requires
  `pr_shape=single-pr` or `pr_shape=per-repo-pr`, plus a `current_pr_ref` of
  `pending` or the canonical live PR. Its `delivery_source` must be
  `feature-level-inherited`, `issue-level-override`, or `owner-instruction`.
- `delivery_mode=pull-request` with `pr_closeout=merge-ready` requires
  `codex_review_policy=required` or `codex_review_policy=skip`.
  `codex_review_policy=skip` requires owner-instruction evidence scoped to the
  exact workstream, with both `scope-ref` and `target-ref` equal to that
  workstream. Preserve `pr-ref=not-applicable` for a workstream-scoped
  instruction. For a PR-scoped instruction, preserve its immutable canonical
  `<owner>/<repo>#<number>` as `pr-ref` and require it to equal the refreshed
  `current_pr_ref`; a changed PR invalidates the row and resets the policy to
  `required`. It never applies to another workstream by inheritance.
- `delivery_mode=pull-request` with `pr_closeout=draft-only`, and every
  non-`pull-request` delivery mode, requires
  `codex_review_policy=not-applicable`.
- `delivery_mode=local-only` requires `delivery_source=runtime-default`.
- `delivery_mode=direct-commit` requires `delivery_source` to be
  `feature-level-inherited`, `issue-level-override`, or `owner-instruction`.
- Other delivery modes require `pr_closeout=not-applicable` and
  `pr_shape=none`, plus `current_pr_ref=not-applicable`.
- `delivery_mode=pull-request` permits `integration_mode=single-repo-pr`,
  `integration_mode=repo-pr`, or `integration_mode=not-applicable`.
- `delivery_mode=direct-commit` permits `integration_mode=direct-commit` or
  `integration_mode=not-applicable`; `delivery_mode=local-only` requires
  `integration_mode=not-applicable`.
- `delivery_mode=direct-commit` requires separate `branch_name` data equal to
  the exact target branch named in the scoped owner evidence.
- `delivery_mode=local-only` and `delivery_mode=pull-request` require
  `scope_transfer_ref=not-applicable` and
  `issue_mutation_transfer_ref=not-applicable`.
- `delivery_mode=direct-commit` with `delivery_source=owner-instruction`
  requires `scope_transfer_ref=not-applicable`. With
  `delivery_source=feature-level-inherited` or
  `delivery_source=issue-level-override`, it requires the exact generated issue
  `scope_transfer_ref` and current source evidence described above.
- `delivery_mode=direct-commit` with `delivery_source=owner-instruction`
  requires `issue_mutation_transfer_ref=not-applicable`. A transferred
  `explicit-direct-mutation` grant requires
  `issue_mutation_transfer_ref` to equal `scope_transfer_ref`, with its own
  current source evidence and independently preserved owner ref.
- `closeout_mode=direct-commit-closes-issue` requires
  `issue_mutation_authority=explicit-direct-mutation` with the same scope,
  target, branch, and applicable transfer evidence as the direct-commit
  delivery tuple while preserving its independent closeout owner ref.
- Every non-`not-applicable` `branch_name` must pass
  `git check-ref-format --branch <branch_name>`.
- `delivery_mode=pull-request` requires
  `closeout_mode=feature-pr-closes-issue`,
  `closeout_mode=repo-pr-closes-issue`, or
  `closeout_mode=local-done-move-after-proof` as selected by tracker and
  `pr_shape`. `delivery_mode=direct-commit` requires
  `closeout_mode=direct-commit-closes-issue` for hosted sources or
  `closeout_mode=local-done-move-after-proof` for local markdown.
  `delivery_mode=local-only` requires `closeout_mode=not-applicable`.

## Legacy Input Normalization

Read these older fields only for compatibility and rewrite them when touched:

| Legacy field/value | Canonical replacement |
| --- | --- |
| `Session CLI subagents consented: authorized-by-invocation` | `delegation_mode=auto`; `worker_surface=auto` |
| `Session CLI subagents consented: disabled` | `delegation_mode=disabled`; `worker_surface=root-thread` |
| `Session CLI subagents consented: limited` | `delegation_mode=bounded`; preserve the numeric `worker_limit` |
| `Session Codex App threads consented: true; max=<positive integer>` | `app_thread_consent=granted`; preserve the numeric `app_thread_limit` |
| `Session Codex App threads consented: true; max=unspecified` | `app_thread_consent=granted`; `app_thread_limit=1` from the legacy one-visible-worker default |
| `Session Codex App threads consented: false; max=<n or unspecified>` | `app_thread_consent=denied`; `app_thread_limit=unspecified` |
| `delegated_worker_surface=none` | `worker_surface=root-thread` |
| `delegated_worker_surface=cli-subagent` | `worker_surface=auto` for the invocation-authorized legacy default; use `worker_surface=cli-subagent` only when the legacy row preserves explicit owner selection evidence |
| `delegated_worker_surface=codex-app-thread` | `worker_surface=codex-app-thread`; preserve legacy consent evidence |
| `actual_workstream_surface=no-delegation` | `actual_workstream_surface=root-thread` |
| `actual_workstream_surface=cli-subagent` | Preserve on the matching workstream only when worker evidence exists |
| `actual_workstream_surface=codex-app-thread` | Preserve on the matching workstream only when worker evidence exists |
| `Takeover policy: owner-approval or stale-ledger-check` | `active_root_takeover_policy=<same canonical value>` in the session row |
| `Merge authority: none` | Create `merge_authority=none` for each active workstream |
| `Merge authority: explicit-owner-authorization` plus exact merge evidence naming a PR/workstream | Create the explicit merge row only for that matching workstream with `source=legacy-migration` and the preserved owner evidence; use `none` elsewhere |
| Global or ambiguous explicit merge authority/evidence | Do not scope the grant; create `merge_authority=none` rows and stop the affected merge as `needs-owner` |
| `Merge policy: owner-approval` | Create `merge_policy=owner-approval` for each active workstream |
| `Merge policy: automatic-after-gates` | Preserve only on the same exactly scoped workstream as a valid explicit merge grant; otherwise normalize to `owner-approval` and require owner reauthorization |
| Hyphenated assignment keys such as `merge-authority` | The matching snake_case key such as `merge_authority` |

Legacy prose and booleans are read aliases, not valid current output values.
