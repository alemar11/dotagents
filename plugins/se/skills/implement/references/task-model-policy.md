# Implement Visible Task Model Policy

## Ownership

This file is the canonical owner of the model and reasoning policy for visible
Codex root and worker tasks created by `$se:implement`. The policy is fixed
runtime behavior, not a user option, Feature Spec field, Project Context value,
tracker artifact, run-manifest field, or SQLite fact.

The root/controller task always uses the fixed Study-compatible controller
profile below. The worker task created for each implementation-eligible Feature
Spec uses the adaptive profile below. Native review uses the worker's explicit
model and resolved reasoning profile; it is not a separate Implement Feature
model selection or run-state option.

## Controller Profile

| Policy | Value |
| --- | --- |
| Model | `gpt-5.6-sol` |
| Reasoning | `medium` |

The parent session requires this profile when creating the root. The root must
independently observe its active profile when the App exposes it.
Missing or conflicting model/reasoning telemetry is a setup limitation that
must be reported; observed settings drift blocks worker creation. The root
never inherits the parent session's model or reasoning settings.

## Worker Profile

| Policy | Value |
| --- | --- |
| Model | `gpt-5.6-sol` |
| Default reasoning | `medium` |
| Allowed reasoning | `medium`, `high`, `xhigh` |

Never select `none`, `minimal`, `low`, `max`, `ultra`, or another reasoning value.
Before startup authorization, verify that the destination Codex host supports
`gpt-5.6-sol` with all three allowed reasoning levels through read-only live
capability evidence. Request the canonical worker title during creation when
available and independently observe it. If creation does not yield the exact
title, use the verified title fallback at most once and observe the title again
when possible. Never create a task merely to probe capability: creation has a
visible task and isolated-checkout effect. If the required model, reasoning, or
structural outcome is absent or unverifiable, stop as `unsupported-runtime`
before run state,
claims, tasks, or worktrees. Missing title support is a best-effort warning,
unless the user explicitly requires an exact title.

The startup disclosure names the controller profile and the adaptive worker
policy. `visible_app_task_permission=granted` is therefore the authorized
user's explicit request to create the disclosed root, workers, and bounded
contract-repair planner tasks with those exact profiles where applicable.

## Native review profile

The worker runs native review with its exact `gpt-5.6-sol` model and resolved
medium, high, or extra-high reasoning profile so review never inherits ambient
defaults. If the current live Codex capability cannot execute native review
with that explicit profile and the required base branch, report
`blocked-app-capability` before implementation; never fall back to the
user's ambient model or reasoning settings.

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

Resolve the root profile before root creation and keep it stable for the root's
lifetime. Resolve each worker profile once before worker authorization and keep
it stable for that worker's lifetime. Require the canonical model and resolved
reasoning profile for both root and worker creation. Follow-up communication
must preserve the existing task profile; never steer a root or worker with
another profile.

The selected profiles are runtime-derived coordination behavior. Do not write
them to the run manifest or SQLite. Recovery resumes only the original visible
task, whose task settings remain authoritative. If authoritative task readback
shows an unavailable or conflicting profile, block as `unsupported-runtime`;
never replace the root or worker, silently reclassify it, or compensate with
another model.
