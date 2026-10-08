# Blast radius

Read when requested or when the selected change suggests consequential effects
outside its immediate callers. Keep the same target and base as the main review.

## Trace indirect effects

Identify what behavior changes, including effects not obvious from the edited
lines. Follow the relevant consumers and contracts beyond symbol references:
persisted records and migrations, serialized payloads, cross-language readers,
dynamic registration, feature flags, and downstream assumptions.

For lifecycle or concurrency changes, trace ordering, cancellation, teardown,
retries, and shared ownership along the affected path. For dependency behavior,
inspect the pinned version and local patches rather than assuming the current
upstream API describes what the application ships. Select relevant paths from
the change; do not turn this into an unrelated repository-wide audit.

## Examine the safety assumptions

State the specific assumptions that make the change safe, such as an operation
having no side effects beyond removing dead entries, or a decoder accepting
records from the previous version. There may be several independent assumptions;
do not force every change into one claim.

For each consequential assumption, distinguish source evidence, reasoning about
whether the failure path is reachable, and existing runtime proof. Check that
runtime evidence covers the relevant scenario and revision. A convincing
explanation or a successful compile does not prove an untested runtime claim.
Static evidence can settle a question when the contract and path are sufficient;
do not demand execution merely to advance through an evidence checklist.

Use source, existing validation artifacts, and read-only observations. Do not
create tests or scripts, modify fixtures, start an app, or run a probe that
changes files, data, or external state. When a needed proof exceeds review
authority, return the smallest concrete verification to the caller: the input
or scenario, the real code or boundary to exercise, and the observable result
that would confirm or disprove the assumption. The caller owns execution.

## Incorporate into the review

Report supported risks through the main review's finding contract: reachable
failure mode, evidence, impact, confidence, and focused recommendation. Keep
material cleared concerns and the evidence that cleared them concise.

An unverified assumption is a coverage gap, not automatically a defect. State
the missing proof and its consequence for confidence. If it prevents the
requested review conclusion, use the caller's incomplete-review disposition
(normally `indeterminate`) rather than reporting a clean result. Do not invent
risks, numeric likelihoods, or findings to compensate for unavailable evidence.
