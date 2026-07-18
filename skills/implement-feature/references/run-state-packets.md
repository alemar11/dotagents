# Run-State Packet Registry

Load this reference immediately before writing a registration or event packet.
Packet files are short-lived command inputs, not active state or recovery
evidence. Write strict JSON, invoke `ledger-cache`, retain the bounded result,
and discard the packet after success. Use a stable 32-character lowercase hex
`operation_id` for retries of the same packet.

## Registration Packet

Use exactly these fields:

```json
{
  "schema_version": "1.0.0",
  "root_task_ref": "<calling App task ref>",
  "root_checkout": "<absolute root checkout>",
  "objective": "<exact portfolio Goal objective>",
  "objective_fingerprint": "<sha256 of objective UTF-8 bytes>",
  "permission_evidence_ref": "<run authorization evidence>",
  "repositories": ["<canonical Git common directory>"],
  "repository_checkouts": [
    {"repository": "<same canonical repository>", "checkout": "<absolute checkout>"}
  ],
  "sources": [
    {
      "task_key": "<stable lower-kebab task key>",
      "source_id": "<exact canonical claim source id>",
      "source_spec_ref": "<authored durable Feature Spec ref>",
      "feature_spec_title": "<exact authored title>",
      "feature_slug": "<lower-kebab slug>",
      "repository": "<canonical Git common directory>",
      "source_state": "ready-for-agent",
      "source_fingerprint": "<sha256>",
      "planned_done_ref": "<exact local done ref or unchanged hosted ref>",
      "tracker_backend": "github",
      "target_branch": "<exact branch>",
      "allowed_paths": ["<repository-qualified allowed path>"],
      "dependency_ids": [],
      "requires_domain_closeout": false,
      "task_model": "gpt-5.6-sol",
      "task_thinking": "high",
      "thinking_reason": "<bounded evidence-backed reason>",
      "task_goal_objective_fingerprint": "<sha256>"
    }
  ]
}
```

`repositories`, `repository_checkouts`, and sorted `source_id` values must equal
the live claim. `tracker_backend` is `github` or `local`. `task_thinking` is
`medium`, `high`, or `xhigh` under `task-model-policy.md`. Dependencies name
other `task_key` values and must be acyclic. The helper derives
`root_task_title`, `portfolio_goal_state=pending`, task identities awaiting App
creation, and empty mutable registries; do not include those projections in the
packet.

## Event Batch

The file passed through `--events-file` is a nonempty JSON array. Every object
uses exactly the fields listed below; every evidence field is an external ref or
digest, never pasted command output.

| event | exact fields after `type` |
| --- | --- |
| `claim-rebound` | `previous_claim_fingerprint`, `claim_fingerprint`, `evidence_ref` |
| `root-title-observed` | `title`, `evidence_ref` |
| `portfolio-goal-activated` | `goal_evidence_ref`, `objective_fingerprint` |
| `portfolio-goal-paused` | `goal_evidence_ref`, `pause_evidence_ref`, `heartbeat_id`, `target_thread_id`, `due_at` |
| `portfolio-goal-resumed` | `goal_evidence_ref`, `heartbeat_id`, `resume_evidence_ref` |
| `portfolio-goal-completed` | `goal_evidence_ref`, `completion_evidence_ref` |
| `task-observed` | `task_key`, `task_ref`, `checkout`, `model`, `reasoning_effort`, `thinking_reason`, `task_title`, `task_title_evidence_ref`, `goal_objective_fingerprint`, `goal_state`, `goal_evidence_ref`, `goal_completion_evidence_ref`, `state`, `outcome`, `attention_reason`, `summary_ref`, `pr` |
| `source-moved` | `task_key`, `from_ref`, `to_ref`, `source_fingerprint`, `evidence_ref` |
| `revision-observed` | `task_key`, `repository`, `pr_number`, `pr_url`, `head_sha`, `base_ref`, `merge_base_sha`, `evidence_ref` |
| `review-wait-started` | `task_key`, `revision_key`, `request_ref` |
| `review-wait-invoked` | `task_key`, `revision_key`, `request_ref`, `wait_invoked_at`, `provider_timeout` |
| `review-observed` | `task_key`, `revision_key`, `request_ref`, `provider_state`, `observation_fingerprint`, `disposition`, `evidence_ref` |
| `review-monitoring-scheduled` | `task_key`, `revision_key`, `request_ref`, `pause_evidence_ref` |
| `review-monitoring-resumed` | `task_key`, `revision_key`, `request_ref`, `resume_evidence_ref` |
| `gate-observed` | `task_key`, `gate`, `state`, `revision_key`, `evidence_ref` |
| `external-handoff-recorded` | `task_key`, `handoff_kind`, `evidence_ref`, `next_action` |

`task-observed.pr` is either `null` or exactly:

```json
{
  "repository": "<canonical Git common directory>",
  "number": 233,
  "url": "<exact PR URL>",
  "state": "open",
  "is_draft": false,
  "head_sha": "<head SHA>",
  "base_ref": "<default base ref>",
  "merge_base_sha": "<merge-base SHA>",
  "mergeable": true,
  "merge_state": "clean",
  "closing_refs": ["<armed tracker ref>"]
}
```

Task lifecycle values are `pending`, `created`, `implementing`, `validating`,
`draft-pr`, `marking-ready-for-review`, `review-polling`, `review-monitoring`, `fixing-review`, `ci`,
`preparing-tracker-closeout`, `checking-mergeability`, `merge-ready`, `blocked`,
`needs-owner`, and `failed`. Task Goal values are `pending`, `active`, `paused`, and
`complete`. Once observed, the task ref, checkout, title, model, thinking,
reason, and PR identity cannot change; title and Goal observation evidence may
refresh when the underlying identity remains exact.

Review provider states are `waiting`, `findings`, `clean`, and `failed`;
dispositions are `pending`, `fix-required`, `accepted`, and `blocked`. A clean
result must be accepted. `review-wait-started` derives one 30-minute deadline.
`review-wait-invoked.provider_timeout` must equal the positive whole seconds
remaining between its supplied UTC `wait_invoked_at` and that deadline.
`review-monitoring-scheduled` requires the deadline's final pending observation,
pauses the worker Goal, and derives the next `due_at` 30 minutes after the event.
`review-monitoring-resumed` requires an active root Goal and a due schedule; it
resumes the worker for one check without changing or relaunching the waiter.

Static gate names are `pr-preflight` and `dependency-integration`; their
`revision_key` is `null`. Revision-bound names are `scope-acceptance`,
`focused-validation`, `full-validation`, `autoreview`, `publication`,
`codex-review`, `ci`, `pr-ready`, `tracker-closeout`, optional
`domain-closeout`, `mergeability`, and `terminal`; they require the current
derived revision key. Gate state is `passed` or `failed`. Passing `terminal`
requires every preceding applicable gate. Completing a task Goal and moving the
task to `merge-ready` additionally requires current clean review, exact open
non-draft clean/mergeable PR evidence, and local source closeout when applicable.
The root Goal completes only after every task is merge-ready and its external
handoff is recorded.
