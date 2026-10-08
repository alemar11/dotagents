---
name: test-audit
description: "Use when writing, changing, reviewing, or pruning tests to prevent redundant, implementation-coupled, or low-value coverage. Supports focused audits and subsystem-wide pruning. Not needed merely to run tests."
---

# Test Audit

Keep tests that detect meaningful failures and remove maintenance cost that
adds no protection. Optimize for confidence, not deletion count.

For ordinary test writing or changes, apply the authoring gate, low-value
patterns, retention bar, and relevant validation only. Keep the reasoning
proportionate; no ledger, historical investigation, or suite inventory is
required. A request to write one test does not authorize a suite-wide cleanup.

Use the focused audit procedure when asked to assess or prune existing tests.
For a whole-subsystem audit or pruning request, also read
[campaign guidance](references/campaign.md). Review-only requests stay
read-only; authorized cleanup continues through edits and validation without
another approval checkpoint.

Use the target repository's instructions, test runner, CI configuration, and
existing review requirements. This skill requires no particular language,
framework, hosting service, or companion skill.

## Authoring gate

Before adding or changing a test, establish:

1. The observable behavior, invariant, or independent contract it protects.
2. A credible regression that would make it fail.
3. Why existing tests would miss that regression. Give each contract a primary
   test owner at a boundary that can observe it; another layer needs a distinct
   risk, such as transport, persistence, or lifecycle behavior.
4. Whether it needs a production export, flag, wrapper, or injection hook solely
   for the test. Prefer an existing real boundary; do not create unused public
   surface just to reach an implementation detail. Legitimate dependency
   boundaries and repository-required testability interfaces may still apply.

Resolve missing answers before adding a test. Extend a meaningful parameterized
case or shared fixture when that avoids duplicate setup. A test that breaks
under a behavior-preserving refactor needs a contract-based justification or a
rewrite at the boundary that owns the behavior.

For bug regressions, demonstrate failure on the pre-fix behavior for the
intended reason and success with the fix. Use an isolated checkout or reversible
control that preserves existing work. If that proof is unavailable, report the
limitation rather than claiming the regression is verified. Do not replay the
same scenario at every layer without a distinct failure mode.

## Low-value patterns

Check both new tests and audit candidates for:

- Execution without an assertion or other failure oracle, self-comparisons,
  or expected values computed by the implementation being tested.
- Copied fixtures, export lists, manifests, or flag declarations asserted
  against themselves rather than against an independent contract.
- Source-text, import, private-helper, or exact call-shape assertions that
  merely freeze implementation details.
- Repeated checks of the same shared behavior across wrappers or providers
  without exercising a distinct integration risk.
- Mocks that implement the behavior being asserted; fixtures that pre-supply
  the receipt, ordering, or state change the production owner should create;
  assertions against a store the production path never writes.
- Negative controls that pass because of an unrelated guard or never reach
  the condition they claim to exercise.
- Tests preserving otherwise-unused exports, reset hooks, globals, wrappers,
  or dead production code.

Judge the assertions and exercised path, including parameter rows, rather than
the test name. A matching pattern warrants investigation, not automatic deletion.

## Retention bar

Retain independent proof of public APIs, protocols, configuration, migrations,
storage, security, platform behavior, packaging, generated artifacts, or other
documented contracts. Ordering, exact bytes, defaults, and source structure can
be observable contracts too. Source inspection is legitimate when it is the
cheapest independent guard and survives unrelated identifier-only refactors.

Small, static, slow, or apparently implementation-like tests are not inherently
redundant. Keep distinct boundary failures even when they use similar inputs.
Coverage percentages alone cannot establish equivalent protection. Preserve
uncertain candidates and treat baseline failures as possible product defects,
not an excuse to remove tests.

## Focused audit

Inspect candidates before editing: read the full test and production owner,
relevant callers and callees, overlapping suites, CI selection, and the history
that explains their purpose. Inspect dependency source or types when the claimed
behavior depends on that dependency. Account for dynamic registration and
external consumers before treating a production entry point as unused.

For each proposed removal or consolidation, record enough evidence to identify:

- Exact test location and the failure it can detect.
- Remaining proof of that contract, or why no contract needs protection.
- Non-test consumers and the historical reason for any support seam it retains.
- Assertions to preserve, code or support that can be removed, risks, and the
  focused validation command.

Report the evidence before applying an authorized batch; this is a progress
update, not a new approval gate. Missing evidence means retain the candidate.
Move necessary assertions into their remaining owner and verify them before
deleting duplicate suites. Remove obsolete support and test-only production
surface only when its lack of consumers is established. Avoid replacement
abstractions or tests that recreate the same cost.

## Validation and result

For audits and pruning, establish the affected tests' baseline before edits.
For ordinary authoring, use the gate's regression proof where applicable.
Do not modify files while a test run is consuming them. Run the smallest
relevant owner and sibling suites, then the checks required by the repository or the change's remaining
risk. When replacing a source-text check, exercise the actual owning script,
build, or supported dry-run where feasible. Preserve test discovery and CI
routing when moving tests; do not lower gates to make a cleanup pass.

Inspect the complete diff for lost contracts and unrelated changes. Run
`git diff --check` in Git repositories. For ordinary authoring, summarize the
behavior protected and validation performed. For audits, also report what was
removed or consolidated, what protection remains, and uncertain candidates
retained. Disclose baseline failures and unavailable checks. For pruning,
separate production/tooling changes from test/support line counts; do not use
line reduction as proof of correctness. Follow existing authorization for
commits or publication; skill invocation alone grants neither.

## Attribution

Adapted from OpenClaw's [Test Audit](https://github.com/openclaw/openclaw/blob/80930af448ebabc84174146b56bc106d37fab3b4/.agents/skills/test-audit/SKILL.md)
and [Test-pruning campaign](https://github.com/openclaw/openclaw/blob/80930af448ebabc84174146b56bc106d37fab3b4/.agents/skills/test-audit/CAMPAIGN.md),
with repository-specific tooling and delivery assumptions removed.
