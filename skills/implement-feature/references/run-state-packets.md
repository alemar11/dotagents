# Run-State Packet Registry

This file owns writable registration and event packets. After registration,
`controller.md` independently owns the read-only next-action response and
`packet_template`; a template is not a writable packet or launch authority.

Load this file only immediately before a registration or event write. Packet
files are short-lived strict JSON inputs, not recovery state. Reuse one stable
32-character lowercase-hex `operation_id` only for retries of the same bytes.

## Bounds And Paths

Limit packets to 1 MiB, text/evidence fields to 4,096 UTF-8 characters, sources
to 64, deliveries per task to 8, allowed paths per delivery to 128, and each
batch to 64 events. State retains at most 512 operations, 256 reviews, and one
final observation per review, plus 64 command attempts per delivery; command
JSON output is at most 128 KiB.

## Registration Packet

Use exactly these top-level fields:

| field | value |
| --- | --- |
| `schema_version` | `7.0.0` |
| `bundle_sha256` | SHA-256 of exact immutable execution-bundle bytes |
| `execution_scope_fingerprint` | canonical complete delivery/path/validation-plan fingerprint |
| `authorization_fingerprint` | fingerprint of execution scope plus permission evidence |
| `root_task_ref` | calling App task ref |
| `root_checkout` | absolute root checkout |
| `objective` | freshly derived portfolio Goal text containing exact `CI when configured` |
| `objective_fingerprint` | its SHA-256 |
| `permission_evidence_ref` | authorization evidence |
| `repositories` | sorted canonical Git common directories |
| `repository_checkouts` | exact `{git_common_dir, checkout}` claim map |
| `sources` | nonempty task-source records below |

Each `sources[]` object has exactly:

```text
task_key, source_id, source_spec_ref, feature_spec_title, feature_slug,
source_state, source_fingerprint, planned_done_ref, tracker_backend,
tracker_repository, deliveries, dependency_ids, requires_domain_closeout,
task_model, task_thinking, thinking_reason, task_assignment_fingerprint
```

Each nonempty `deliveries[]` object has exactly:

```text
delivery_key, repository, github_repository, target_branch, default_base,
allowed_paths, ci_availability, preflight_key, preflight_evidence_ref,
validation_plan
```

Each nonempty `validation_plan[]` row has exactly
`validation_key`, `command_id`, `adapter`, `policy`,
`authored_argv_fingerprint`, `projected_argv_fingerprint`, and
`tool_identities_fingerprint`, and `execution_policy_fingerprint`.
Adapter/policy pairs are closed by
`baseline-validation.md`; callers cannot select a free-form parser or policy.

Keys and `feature_slug` are lower-kebab. `source_id` is the canonical claim/task
id; `source_spec_ref` preserves the authored ref. `tracker_backend` is `github`
or `local`, initial `source_state` is `ready-for-agent`, and hosted
`planned_done_ref` equals `source_spec_ref`. Local destinations are predeclared.
The task profile follows `task-model-policy.md` (`gpt-5.6-sol` and
`medium|high|xhigh`).

`github_repository` is canonical `owner/repository`; `default_base` is the
read-only discovered PR base. `ci_availability` is exactly `configured` or
`not-configured`. The preflight key is the SHA-256 of the canonical passed
capability observation. Unknown or blocked inspection is never registered.

Each repository occurs once; dependencies are acyclic and scope equals the live
claim. Takeover identity comes only from validated claim adoption. Creation
derives `root_task_title` and `portfolio_goal_state=pending`; bound identities are immutable.

## Event Batch

`--events-file` is a nonempty JSON array. Every event uses exactly the fields
below after `type`; required nullable fields remain present as `null`. Evidence
values are refs or digests, never pasted output.

| event | exact fields after `type` |
| --- | --- |
| `root-title-observed` | `title`, `evidence_ref` |
| `portfolio-goal-activated` | `goal_evidence_ref`, `objective_fingerprint` |
| `implementation-baseline-accepted` | `expected_generation`, `expected_state_fingerprint`, `expected_claim_fingerprint`, `execution_scope_fingerprint`, `baselines`, `evidence_ref` |
| `portfolio-preimplementation-aborted` | `reason`, `task_stop_evidence`, `evidence_ref` |
| `managed-checkouts-observed` | `task_key`, `task_ref`, `managed_checkouts`, `evidence_ref` |
| `delivery-preflight-observed` | `task_key`, `delivery_key`, `github_repository`, `target_branch`, `default_base`, `ci_availability`, `preflight_key`, `evidence_ref` |
| `execution-command-reserved` | `task_key`, `delivery_key`, `attempt_id`, `command_id`, `operation`, `manifest_sha256`, `execution_policy_fingerprint`, `attempt_file`, `receipt_file`, `task_observation_fingerprint`, `evidence_ref` |
| `execution-command-launch-observed` | `task_key`, `delivery_key`, `attempt_id`, `attempt_fingerprint`, `evidence_ref` |
| `execution-command-cancellation-authorized` | `task_key`, `delivery_key`, `attempt_id`, `reason`, `task_observation_fingerprint`, `evidence_ref` |
| `execution-command-terminal-observed` | `task_key`, `delivery_key`, `attempt_id`, `status`, `receipt_sha256`, `cleanup_verified`, `evidence_ref` |
| `task-observed` | `task_key`, `model`, `reasoning_effort`, `thinking_reason`, `task_title`, `task_title_evidence_ref`, `task_assignment_fingerprint`, `state`, `outcome`, `attention_reason`, `summary_ref`, `observation` |
| `task-dependency-wait-started` | `task_key`, `resume_state`, `reason`, `summary_ref`, `task_observation_fingerprint`, `evidence_ref` |
| `task-dependency-wait-resolved` | `task_key`, `resume_state`, `task_observation_fingerprint`, `evidence_ref` |
| `review-provider-mutation-reserved` | `task_key`, `delivery_key`, `reservation`, `packet_fingerprint`, `evidence_ref` |
| `review-provider-mutation-started` | `task_key`, `delivery_key`, `reservation_id`, `operation_id`, `packet_fingerprint`, `evidence_ref` |
| `review-provider-mutation-observed` | `task_key`, `delivery_key`, `reservation_id`, `operation_id`, `attempt_state`, `result_fingerprint`, `receipt_ref`, `recovery_state`, `evidence_ref` |
| `committed-revision-observed` | `task_key`, `delivery_key`, `target`, `evidence_ref` |
| `revision-observed` | `task_key`, `delivery_key`, `repository`, `github_repository`, `pr_number`, `pr_url`, `head_sha`, `base_ref`, `merge_base_sha`, `evidence_ref` |
| `delivery-observed` | `task_key`, `delivery_key`, `revision_key`, `pr`, `committed`, `published`, `evidence_ref` |
| `validation-nonregression-observed` | `task_key`, `delivery_key`, `validation_key`, `revision_key`, `adapter`, `policy`, `argv_fingerprint`, `tool_identities_fingerprint`, `diagnostics`, `diagnostic_set_fingerprint`, `evidence_ref` |
| `delivery-scope-observed` | `task_key`, `delivery_key`, `revision_key`, `changed_paths`, `untracked_paths`, `evidence_ref` |
| `source-moved` | `task_key`, `from_ref`, `to_ref`, `source_fingerprint`, `tracker_repository`, `revision_set_key`, `evidence_ref` |
| `review-wait-started` | `task_key`, `delivery_key`, `revision_key`, `request_receipt` |
| `review-wait-invoked` | `task_key`, `delivery_key`, `revision_key`, `request_receipt`, `wait_invoked_at`, `provider_timeout` |
| `review-observed` | `task_key`, `delivery_key`, `revision_key`, `request_receipt`, `request_binding`, `provider_state`, `failure_kind`, `provider_error_code`, `observation_fingerprint`, `disposition`, `finding_count`, `finding_comment_ids`, `evidence_ref`, `warning_ref`, `warning_posted_at`, `warning_fingerprint` |
| `review-thread-resolved` | `task_key`, `delivery_key`, `finding_revision_key`, `resolution_revision_key`, `reply_receipt`, `resolution_receipt` |
| `autoreview-hosted-finding-obligated` | `task_key`, `delivery_key`, `obligation` |
| `autoreview-action-reserved` | `task_key`, `delivery_key`, `reservation_id`, `expected_state_fingerprint`, `projection` |
| `autoreview-reservation-released` | `task_key`, `delivery_key`, `reservation_id`, `reason` |
| `autoreview-attempt-observed` | `task_key`, `delivery_key`, `reservation_id`, `attempt_id`, `attempt_state`, `model_call_started`, `candidate_fingerprint`, `operation_id`, `evidence_ref` |
| `autoreview-lineage-reset-authorized` | `task_key`, `delivery_key`, `authority`, `reason`, `evidence_ref`, `prior_evidence_fingerprint`, `next_review_target_key`, `next_committed_revision_key` |
| `autoreview-observed` | `task_key`, `delivery_key`, `reservation_id`, `candidate_fingerprint`, `operation_id`, `evidence_ref`, `evidence` |
| `gate-observed` | `task_key`, `delivery_key`, `gate`, `state`, `binding_key`, `task_observation_fingerprint`, `evidence_ref` |
| `task-terminal-sealed` | `task_key`, `revision_set_key`, `seal_fingerprint`, `evidence_ref` |
| `terminal-handoff-recorded` | `task_key`, `seal_fingerprint`, `handoff_kind`, `authority`, `evidence_ref`, `next_action` |
| `portfolio-terminal-verified` | `verification_fingerprint`, `evidence_ref` |
| `portfolio-goal-completed` | `goal_evidence_ref`, `completion_evidence_ref`, `verification_fingerprint` |
| `post-terminal-drift-recorded` | `task_key`, `delivery_key`, `seal_fingerprint`, `drift_fingerprint`, `reason`, `evidence_ref` |

`managed_checkouts` is the complete registered delivery set. Every item has
exactly `delivery_key`, `repository`, absolute App-managed `checkout`, matching
absolute `git_top_level`, registered `target_branch`, 40-hex
`baseline_revision`, and `isolation_evidence_ref`.
It also has `baseline_tree_sha`, `baseline_status_fingerprint`, and
`execution_scope_fingerprint`.

Each baseline CAS row has exactly `task_key`, `delivery_key`, `validation_key`,
absolute `manifest_file`, `manifest_bytes_sha256`, absolute `receipt_file`, and
`receipt_bytes_sha256`. Its set must equal every registered validation tuple.
`task_stop_evidence` is sorted complete task coverage with exact `task_key`,
`task_ref`, and `evidence_ref`.
`execution-command-terminal-observed.receipt_sha256` may be null only when a
controller crash yields `interrupted` or `cleanup-failed`; all other terminal
statuses require the verified receipt hash.

AutoReview lifecycle details are branch-loaded from `autoreview-fix-loop.md`.
`revision-observed` binds canonical repository, PR, head, base, and merge base.
`delivery-observed` requires that key. Its `pr` object has exactly
`repository`, `github_repository`, `number`, `url`, `state`, `is_draft`, `head_sha`, `base_ref`,
`merge_base_sha`, `mergeable`, `merge_state`, and `closing_refs`; its tuple
must equal the revision. Terminal truth requires `"state": "open"`,
`"is_draft": false`, `"mergeable": true`, `"merge_state": "clean"`,
`"committed": true`, and `"published": true`. Only such an observation for a
newer revision clears `source-moved` tracker dirt.

Terminal handoff uses `handoff_kind=pull-request-ready` and
`authority=external-merge-required`. A review wait never creates a handoff.

`request_receipt` is complete; binding failure exits 4, never stale or timeout.

## States And Gates

Task states are `pending`, `created`, `implementing`, `validating`, `draft-pr`,
`marking-ready-for-review`, `review-polling`, `fixing-review`, `ci`,
`preparing-tracker-closeout`, `checking-mergeability`,
`terminal-sealed`, `merge-ready`, `blocked`, `needs-owner`, and `failed`. Goal
states are `pending`, `active`, and `complete`.
`implementation_baseline` is `pending`, `accepted`, `planning-required`, or
`blocked`; before acceptance, task state may only remain `created`.
Review provider/disposition values are `waiting|findings|clean|failed` and
`timeout-accepted|fix-required|accepted|blocked`.
Nonfailed observations use null failure fields; failed values follow the closed
GitStack mapping in `review-reconciliation.md` and cannot be relabeled.

`autoreview-observed.evidence` is the complete current-schema envelope validated
by the shared protocol module; see `autoreview-fix-loop.md`.

| gate scope | gates | required identity |
| --- | --- | --- |
| `task-static` | `dependency-integration` | both keys null |
| `delivery-revision` | `focused-validation`, `full-validation`, `autoreview`, `publication`, `codex-review`, conditional `ci`, `pr-ready`, `tracker-closeout`, `mergeability` | delivery key + current delivery evidence key as binding |
| `task-revision-set` | `scope-acceptance`, `integration-validation`, optional `domain-closeout` | delivery null; complete revision-set key as binding |

Gate state is `passed` or `failed`. The delivery evidence key hashes its current
revision and preflight keys. A task revision-set key digests sorted
`(delivery_key, delivery_evidence_key)` pairs. When CI is `not-configured`, the
`ci` gate is inapplicable and any such event is rejected.

The deadline is `wait_started_at+45m`. Before the provider call, persist
nonfuture `wait_invoked_at` and
`provider_timeout=max(0,floor(wait_deadline-wait_invoked_at))`; zero means one
no-wait check. One observation completes review. Valid pairs
are `clean/accepted`, `findings/fix-required`, `failed/blocked`, and
`waiting/timeout-accepted`. Only the last permits warning fields: a canonical
stored-PR issue-comment URL, post time between deadline and observation, and
the `codex-review-closeout.md` body fingerprint. It is invalid before deadline;
other pairs use null warnings. Never reschedule, pause a Goal, or heartbeat.

Terminal seal requires all gates and a complete accepted review set; timeout
acceptance stays a warning, never clean. Worker completion and handoff require
the unchanged seal; root completion requires every verified task handoff. Only
post-terminal drift may mutate sealed evidence; it blocks archive without
reopening Goals.
