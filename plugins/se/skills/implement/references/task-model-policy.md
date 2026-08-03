# Implement Visible Task Model Policy

## Ownership

This file is the canonical owner of the model and reasoning policy for visible
Codex root and worker tasks created by `$se:implement`. The policy is fixed
runtime behavior, not a user option, Feature Spec field, Project Context value,
tracker artifact, run-manifest field, or SQLite fact.

The root/controller task always uses the fixed Study-compatible controller
profile below. The worker task created for each implementation-eligible Feature
Spec uses the adaptive profile below. Native `codex review` uses the installed
Codex CLI's review command with the worker's explicit model and resolved
thinking value; it is not a separate Implement Feature model selection or
run-state option.

## Controller Profile

| Field | Value |
| --- | --- |
| `model` | `gpt-5.6-sol` |
| `thinking` | `medium` |

The parent session passes both fields explicitly when creating the root. The
root must independently read back its task settings when the App exposes them.
Missing or conflicting model/reasoning telemetry is a setup limitation that
must be reported; observed settings drift blocks worker creation. The root
never inherits the parent session's model or reasoning settings.

## Worker Profile

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
When the live declaration exposes `create_thread.title`, pass the canonical
worker title in the creation call and independently read it back. If creation
does not yield the exact title, use the verified `set_thread_title` operation at
most once as the fallback and read the title back again when possible. If
`create_thread.title` is absent, use that same verified fallback when available.
Do not call `create_thread` as a probe: it creates a visible task and worktree.
If model, thinking, or any structural argument is absent or unverifiable from
read-only capability evidence, stop as `unsupported-runtime` before run state,
claims, tasks, or worktrees. Missing title support is a best-effort warning,
unless the user explicitly requires an exact title.

The startup disclosure names the controller profile and the adaptive worker
policy. `visible_app_task_permission=granted` is therefore the authorized
user's explicit request to create the disclosed root, workers, and bounded
scope-repair planner tasks with those exact profiles where applicable.

## Native review invocation

The worker maps its resolved App-task `thinking` value directly to the CLI's
`model_reasoning_effort` configuration override. The native review invocation
must pass the model and reasoning before the `review` subcommand so the review
does not inherit the caller's configured defaults:

```bash
codex --model gpt-5.6-sol \
  -c 'model_reasoning_effort="<resolved-thinking>"' \
  review --base <base-branch>
```

`<resolved-thinking>` is the exact worker value (`medium`, `high`, or
`xhigh`), not a literal placeholder. The model flag must remain before the
`review` subcommand; placing it after the subcommand is not supported by the
current CLI. If the installed CLI cannot parse or execute the explicit
model/reasoning invocation, report
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
it stable for that worker's lifetime. Pass the canonical `model` and resolved
`thinking` value to `create_thread` for both root and worker creation. On every
`send_message_to_thread` call, omit both override fields so the existing task
settings remain unchanged; never steer a root or worker with another profile.

The selected profiles are runtime-derived coordination behavior. Do not write
them to the run manifest or SQLite. Recovery resumes only the original visible
task, whose task settings remain authoritative. If authoritative task readback
shows an unavailable or conflicting profile, block as `unsupported-runtime`;
never replace the root or worker, silently reclassify it, or compensate with
another model.
