# Feature Planner Task Profile

This profile owns the one required application-task launch for `se:feature`.
It is intentionally separate from the legacy Implement task preflight and
handoff contracts.

```yaml
task_profile: feature-planner
role: planner
model: gpt-5.6-sol
reasoning: high
topology: single-planner-task
title_template: "📚 Plan Feature Set · <set outcome>"
execution: direct-local-project
```

Resolve and pass `model` and `reasoning` explicitly when creating or resuming
the planner. Do not rely on ambient inheritance. These values are required
request inputs, not a post-effect attestation protocol: retain what was
requested, but do not require the planner to read back or self-certify its
effective profile.

Explicit `se:feature` invocation authorizes exactly one visible planner task.
Request the deterministic title when the runtime supports it, but never gate
planning on title observation or correction. Run in the caller-selected direct
local project checkout without a worktree or fork. The planner may inspect
every repository explicitly in scope; application project metadata does not
establish repository identity or constrain the Plan Set.

An accepted creation or resume receipt with a stable task identity starts the
planner. Its first turn begins `intake` and performs role work immediately. Do
not request an `assigned_task_bootstrap`, effective-profile comparison,
execution-target self-check, goal, title reconciliation, or a second planner.

When the task effect is ambiguous, inspect that same attempt once. Resume the
observed identity when it exists. Create another planner only after
authoritative evidence proves the original effect did not apply. If creation
is rejected or remains ambiguous, report the launch blocker without beginning
publication.

The planner may use subordinate read-only helpers for study or review. They
inherit the planner's execution context unless the caller explicitly requests
another supported profile, never become required application tasks, and always
fall back to serial planner work when unavailable or prohibited.
