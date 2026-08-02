# Implement Visible Worker Model Policy

## Ownership

This file is the canonical owner of the model and reasoning policy for visible
Codex worker tasks created by `$se:implement`. The policy is fixed runtime
behavior, not a user option, Feature Spec field, Project Context value, tracker
artifact, run-manifest field, or SQLite fact.

The policy applies only to the visible worker task created for each
implementation-eligible Feature Spec. Native `codex review` uses the installed
Codex CLI's review command and is not a separate Implement Feature model
selection or run-state option.

## Canonical Profile

| Field | Value |
| --- | --- |
| `model` | `gpt-5.6-sol` |
| `thinking_default` | `medium` |
| `thinking_allowed` | `medium`, `high`, `xhigh` |

Never pass `none`, `minimal`, `low`, `max`, `ultra`, or another thinking value.
Before startup authorization, verify that the destination Codex host supports
`gpt-5.6-sol` with all three allowed thinking values from the discovered
`create_thread` tool contract or another read-only host capability surface. The
inspection must also verify the exact fields available for title initialization.
This protocol keeps that initialization in the separately recorded
`set_thread_title` operation; an optional `create_thread.title` field may be
present, but must never be assumed or passed without checking the live
declaration. Do not call `create_thread` as a probe: it creates a visible task
and worktree. If model, thinking, title initialization, or any required
argument is absent or unverifiable from read-only capability evidence, stop as
`unsupported-runtime` before run state, claims, tasks, or worktrees.

The startup disclosure names this exact model and adaptive thinking policy.
`visible_app_task_permission=granted` is therefore the authorized user's
explicit request to create the disclosed workers with those exact profiles.

## Per-Spec Thinking Resolution

Resolve one thinking value per implementation-eligible Feature Spec after its
complete bundle passes read-only intake and before startup authorization. Apply
these rules in order:

1. Select `xhigh` for risky or cross-system work:
   - multi-repository behavior or integration across independently deployed
     systems;
   - authentication, authorization, privacy, security, payments, or material
     data-loss risk;
   - schema or data migration, backward compatibility, or difficult rollback;
   - concurrency, distributed state, ordering, retries, idempotency, or other
     coordination-sensitive behavior;
   - architectural changes to externally consumed contracts across system
     boundaries.
2. Select `high` for complex work when no `xhigh` trait applies:
   - multiple interacting components or layers within one repository;
   - correctness depends on several state transitions, failure modes, or
     substantial behavioral edge cases;
   - nontrivial implementation tradeoffs across established contracts;
   - correctness requires coordinated validation across multiple test or
     runtime surfaces.
3. Select `medium` for routine work when neither higher-level rule applies.

Issue count, changed-file count, or path count alone never selects a level.
Missing, stale, ambiguous, or contradictory execution evidence remains
`planning-required`; additional thinking effort must not compensate for an
incomplete Feature Spec.

## Application And Recovery

Resolve the profile once before authorization and keep it stable for the
worker's lifetime. Pass the canonical `model` and resolved `thinking` value to
`create_thread` when creating the visible worker. On every
`send_message_to_thread` call, omit both override fields so the existing task
settings remain unchanged; never steer a worker with another profile.

The selected profile is runtime-derived coordination behavior. Do not write it
to the run manifest or SQLite. Recovery resumes only the original visible task,
whose task settings remain authoritative. If authoritative task readback shows
an unavailable or conflicting profile, block as `unsupported-runtime`; never
replace the worker, silently reclassify it, or compensate with another model.
