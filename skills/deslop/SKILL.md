---
name: deslop
description: Audit and safely remove low-value repository code. Use only when explicitly invoked by the user.
---

# Deslop

Audit the requested scope for low-value code: redundant tests, trivial wrappers,
dead abstractions, duplicate helpers, stale comments, and unnecessary ceremony.
Verify each removal is safe, make the smallest cleanup, run focused tests and
lint, and report what changed with evidence. A review-only request stays read-only.

## Coverage and judgment

For a repository-wide request, inventory its major directories, including source,
tests, tooling, configuration and documentation. For a named path or component,
limit coverage to that scope and relevant callers. Inspect each area's purpose
and representative contents, then trace candidates through callers and dependencies.
Track coverage during the audit; report inaccessible or excluded areas and why.
Generated and vendored directories need an ownership check, not manual cleanup.
Do not claim a repository-wide audit is complete with major areas uninspected.

Small code is not automatically low-value. A wrapper may enforce a boundary, an
abstraction may encode a contract, and a simple test may protect a regression.
Remove only demonstrated redundancy or obsolete behavior, not unfamiliar style.
Zero changes is a valid result; retain uncertain candidates and explain material
uncertainty rather than manufacturing cleanup.

## Safe cleanup

Before each removal, verify callers, exports, public contracts, configuration,
and applicable dynamic discovery or registration. No search hits alone do not
prove code is unused. Check behavior and side effects before inlining wrappers
or consolidating helpers; avoid expanding the patch into an architectural rewrite.

For test removals, identify which remaining tests preserve the meaningful
assertions, scenarios and regression coverage. Passing tests alone do not prove
that deleting a test was safe. For comments, verify the statement is stale or
redundant and preserve rationale and non-obvious constraints.

When comments or documentation are within the requested scope:

- Replace vague claims with concrete behavior supported by the code or cited
  evidence. Do not invent mechanisms, measurements, or guarantees to sound precise.
- Remove filler and jargon that adds no meaning, preserving established domain
  terms, rationale, qualifications, and the intended tone.
- Keep sentences complete and easy to read. Shorten or split dense prose without
  turning it into fragments, unexplained abbreviations, or symbol shorthand.

Apply these criteria to relevant text only; do not expand a code cleanup into
a repository-wide editorial pass or impose blanket punctuation or vocabulary bans.

Make the smallest change for each verified finding, preserving observable
behavior and unrelated work. Run the affected tests and lint using repository
commands; include type or build checks when the changed boundary needs them.
Review the final diff for unintended behavior changes. If safety cannot be
established, leave the candidate unchanged; report unavailable checks and their
effect on confidence.

Report changed paths, why each cleanup is safe, the checks run and their results,
and major-directory coverage. Group related removals when they share evidence.
Ordinary invocation authorizes local cleanup unless the user limits it to review;
commits and publication require user
authorization. Execute in the current task without creating workers.
