# Study CLI Runtime

Read this reference only when `study_surface=cli-session`. It owns same-session
control, current-directory context, immediate Grilling, and native subagent
delegation.

## Current-session controller

The invoking CLI session is the Study controller. Do not create a separate App
task, fork the session, or transfer the handoff elsewhere.

- Keep the controller's current model and reasoning profile. Study neither
  overrides nor gates that inherited profile.
- Use the current working directory and supplied discussion as the initial
  repository context. A saved App project is not required.
- Retain the curated handoff transiently as the authoritative Study brief. Do
  not write it to disk.
- Compose `$se:grilling` immediately and ask its first question directly in
  the current CLI session. There is no parent relay or setup-only turn.

Continue the interview in this session until its state is `refined`,
`user-stopped`, or `blocked`. Create no subagents while an answer is pending.
After a refined or stopped handoff, apply the shared worker planning rules in
[orchestration.md](orchestration.md).

The CLI branch has no App controller task identity, requested title, host or
saved-project task placement, App task telemetry, or App archival lifecycle.
Mark those state fields `not-applicable` internally and omit their report
sections.

## Native subagents

For each positive planned slot, create one native subagent under the current
CLI controller:

- Request `gpt-5.6-luna` with `max` reasoning explicitly.
- Keep the assignment in the current working-directory context.
- Supply the fixed `run_tag`, slot number, refined handoff slice, read-only
  boundary, evidence expectations, result shape, and recursion prohibition.
- Record the stable subagent identity and lineage returned by the current
  runtime. A label or assignment text is never identity.

Use only native subagents. If that transport is unavailable, a creation request
fails, or setup remains unresolved, retain the reserved slot and its failure.
Do not switch to an App task, external CLI process, or another delegation
mechanism. Never create a replacement beyond the reserved slot.

Monitor created subagents through the current session until each is
`completed`, `failed`, or explicitly `abandoned`. Capture the final memo when
available; otherwise record the terminal state, reason, error, and last
authoritative evidence. Profile telemetry may be recorded when exposed, but
missing telemetry is not a reason to invent a value or claim independent
verification.

Subagents have no App task title or archival fields. Keep their result ledger
in the current session and synthesize there. When one or more requested slots
fail, the controller may still perform direct read-only analysis and return a
`partial` result. It must not silently lower the planned count or describe
controller-only work as a successful worker result.
