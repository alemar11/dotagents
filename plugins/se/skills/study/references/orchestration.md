# Study Orchestration

Read this reference after Grilling returns `refined` or `user-stopped`. It owns
the shared worker-selection, assignment, monitoring, synthesis, and failure
policy for both Study surfaces. Surface references own transport-specific
setup and lifecycle behavior.

## Capacity selection

Record these facts before creating any worker:

- `original_requested_count`: the user's explicit number or `unspecified`;
- `planned_worker_count`: the count after applying the absolute five-worker
  cap;
- `created_worker_count`: the number of reserved slots with stable created
  identities;
- `full_capacity_mode`: `yes` exactly when the planned count is five;
- `full_capacity_source`: why five was selected, or `not-applicable`.

Explicit counts take precedence over efficiency. Honor zero through five
exactly. Normalize any larger request to five, disclose the cap before
creation, and retain both counts in the report.

For `original_requested_count=unspecified`, choose the smallest count that
gives every worker a distinct, bounded evidence surface:

- zero when no meaningful independent split exists;
- one or two for a focused question, one repository or source family, or one
  or two separable investigation surfaces;
- three for a genuinely multi-dimensional comparison, such as local contract,
  external subject, and comparative fit;
- four or five only for broad work with four or five independent tracks, such
  as runtime, architecture, maintenance, validation, and user or security
  concerns.

Prefer the lower count when evidence is borderline. Do not add workers merely
to reduce latency or duplicate the same review. A plan of five requires an
explicit report justification.

## Assignment contract

Reserve every planned slot before creation and number it once from 1 through
5. Each worker assignment must include:

- one bounded objective and its relation to the refined handoff;
- included evidence surfaces and explicit non-goals;
- concrete questions to answer;
- repository paths or source families to inspect;
- evidence and acceptance expectations;
- dependencies on other assignments, if any;
- a concise Markdown memo shape;
- the read-only boundary, fixed Luna/max profile, slot number, and `run_tag`;
- an absolute prohibition on invoking Study or creating child workers.

Assignments should be mutually distinct and collectively sufficient. Serialize
only those that truly depend on an earlier unstable finding. Workers report to
the active Study controller, not directly to another worker.

## Setup and no-replacement policy

Set `worker_transport` from the active surface before creation. One reserved
slot permits at most one creation request unless authoritative reconciliation
proves that the request had no effect and the same slot can safely complete
its original attempt.

For each slot:

1. Treat the immediate result as setup evidence, not proof beyond what it
   actually establishes.
2. Bind the slot only to a stable worker identity. Never correlate by title,
   label, prompt preview, assignment text, run tag, or timing.
3. A definitive failure proving no worker exists sets `creation-failed` and
   permits later reserved slots to proceed.
4. An uncertain effect sets `pending-setup`. Reconcile it through at most three
   bounded authoritative observations. Stop later creation until it resolves.
5. A stable worker in the wrong structural context sets
   `structural-verification-failed`; observed Luna/max drift sets
   `settings-drift`. Preserve the identity, create no replacement, and stop
   later creation.
6. Failed reconciliation sets `unresolved-setup`; leave later slots
   `not-started` with reason `creation-halted-after-uncertain-slot`.

A failed, drifted, unresolved, or abandoned slot is never freed, renumbered,
or replaced. Never start a second controller or a second worker layer to make
up capacity.

If a positive planned transport is unavailable before any creation request,
mark every reserved slot `creation-failed` with the shared transport blocker.
The controller may still complete direct analysis, but the overall outcome is
at most `partial`.

## Monitoring and evidence

Monitor all stable workers with bounded waits and authoritative observations;
do not busy-poll. Track progress and inspection positions separately when the
runtime exposes both, and deduplicate events by stable revision or event
identity rather than prose.

`needs-attention` and `monitoring-unavailable` are nonterminal. Preserve the
reason and last known state, surface the blocker to the owning user when human
input is possible, and resume only after authoritative observation recovers.
Only the user may direct abandonment of a worker that needs attention.

Do not finish merely because one worker completes. For every stable identity,
capture a final memo or the best available terminal state, reason, error, and
last evidence. Missing evidence is unavailable, never implicit success.

## Synthesis and outcome

The controller owns the final reasoning. It must compare worker claims against
the refined handoff and inspected evidence, resolve contradictions where
possible, and label remaining uncertainty. Worker memos are inputs, not
authority.

Use these overall outcomes:

- `completed`: the controller produced a usable synthesis and every planned
  slot completed with captured terminal evidence; a zero-worker plan may
  complete through controller analysis alone.
- `partial`: the controller produced a usable synthesis, but at least one
  planned slot failed, drifted, remained unresolved, was abandoned, or lacked
  terminal evidence.
- `failed`: no usable synthesis can be returned, including a blocked Grilling
  phase or failed App controller setup.

Read [output-template.md](output-template.md) immediately before reporting and
include only the branch-specific sections selected by `study_surface`.
