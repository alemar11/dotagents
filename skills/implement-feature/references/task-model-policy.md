# Visible Task Model Policy

## Ownership

This file is the canonical owner of the model and reasoning policy for visible
ChatGPT desktop app tasks created or steered by `$implement-feature`. The policy is fixed
runtime behavior, not a user option, Feature Spec field, Project Memory value,
or tracker artifact. Update model generations and the bounded reasoning set
here instead of duplicating them across the runtime docs.

The policy applies only to the root-owned visible App task for each Feature
Spec. Internal subagents remain governed by the parent task contract.

## Canonical Profile

| Field | Value |
| --- | --- |
| `model` | `gpt-5.6-sol` |
| `thinking_default` | `high` |
| `thinking_allowed` | `medium`, `high`, `xhigh` |

Never pass `none`, `minimal`, `low`, `max`, `ultra`, or another thinking value.
Never substitute a different model or thinking value when the canonical profile
is unavailable. After the mandatory App surface gate, verify that
`codex_app__create_thread` and `codex_app__send_message_to_thread` both expose
the canonical model and every allowed thinking value. If that support is absent
or unverifiable, abort as `unsupported-runtime` before asking permission,
claiming scope, creating a ledger, or creating a task.

The mandatory authorization question discloses this exact model and adaptive
thinking policy. A grant of
`visible_app_task_permission=granted-by-authorized-user` therefore supplies the
explicit user request required to pass the model and thinking arguments.

## Per-Spec Thinking Resolution

Resolve one thinking value per implementation-eligible Feature Spec after its
complete bundle passes read-only intake and before CLAIM. Apply the rules in
this order:

1. Select `xhigh` when the execution-ready Spec has any of these traits:
   - multi-repository implementation or integration;
   - architectural change spanning multiple subsystems or externally consumed
     contracts;
   - schema or data migration, backward compatibility, or difficult rollback;
   - authentication, authorization, privacy, security, payments, or material
     data-loss risk;
   - concurrency, distributed state, ordering, retries, idempotency, or other
     coordination-sensitive behavior.
2. Select `medium` only when all of these are true:
   - one repository and one bounded subsystem;
   - localized, routine behavior with no architectural change;
   - explicit deterministic acceptance criteria and validation;
   - no `xhigh` trait, migration, compatibility boundary, or irreversible
     operation.
3. Select `high` for every other execution-ready Spec and whenever the evidence
   does not justify either exception.

Issue count, changed-file count, or path count alone never selects a level.
Missing, stale, ambiguous, or contradictory implementation evidence remains
`planning-required`; extra reasoning must not compensate for an incomplete
Spec.

## Application And Evidence

Resolve the profile once and keep it stable for the visible task's lifetime.
Pass the canonical `model` and resolved `thinking` value to
`codex_app__create_thread` when creating the task and to every
`codex_app__send_message_to_thread` call that steers or resumes it. Never omit
either argument on those calls, because omission can inherit the calling root's
settings instead of preserving the task profile.

Record the exact model, thinking value, decision reason, and creation evidence
in the Feature Spec Task Registry. Recovery and takeover reuse that recorded
profile for the original task. Source drift before task creation reruns intake
and profile resolution; after creation, never reclassify the task, replace it,
or silently change its profile.
