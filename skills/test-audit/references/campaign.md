# Subsystem test-pruning campaign

Read this for a request to audit or prune a whole subsystem. The authoring gate,
retention bar, candidate evidence, and validation in [Test Audit](../SKILL.md)
still apply. A broad audit remains read-only unless edits are authorized.

## Baseline and inventory

Define the subsystem by production ownership, including its cases in shared
suites, integration harnesses, and live or manual QA scenarios. Record the
starting revision and relevant existing work, test/support line counts, and
baseline results for every in-scope test file. Keep failures and tests that
cannot run separately visible; unavailable credentials or infrastructure mean
partial evidence, not a passing baseline. Do not run external or live scenarios
beyond the user's authorization.

Group the inventory by behavioral boundary. Assign each test to one group and
account for cross-boundary contracts explicitly. Keep a compact working ledger:
a decision table with one entry per test declaration, not a database or a
permanent repository artifact. Use the task's existing artifact location or a
non-shipped temporary file. Record whether to retain, repair its assertion,
consolidate into a named owner, or delete, with the evidence required by the
entrypoint. Split parameter rows only when they need different decisions.
Do not claim a complete campaign while declarations remain unexamined.

For example, one ledger entry could be:

| Test | Decision | Evidence and validation |
| --- | --- | --- |
| `auth.test.ts`: rejects expired tokens | retain | Only test exercising expiry rejection through the public login API; removing the expiry check makes it fail. Focused auth suite passes. |

Record observed evidence; an unperformed check remains unverified.

## Plan by contract

Recheck the ledger across entire layers before treating it as an edit list.
Several individually plausible suites may repeat the same mocked collaborator
while a real boundary suite provides stronger proof. Name the remaining suite
for each contract, assertions it must absorb, files to retire, and production
or support hooks that become unnecessary. Prefer a boundary that exercises the
real owner with controlled dependencies; a larger or more end-to-end test is
not automatically stronger for every failure mode.

Apply authorized changes in coherent groups. Transfer missing assertions and
verify their new owners before deleting old suites. Serialize shared harness
edits and keep test discovery, CI routing, and applicable inventories aligned.
Do not invent new line-count caps, branch policies, or repository-wide rules
as a side effect of pruning.

## Preservation review

Compare deleted assertions with the remaining suites contract by contract,
including fixtures and negative controls. Check that replacement tests can
fail for the intended reason. If an independent review is supplied or required
by the caller, give it the before/after tests and production owners; self-review
must not be reported as independent review.

For a restored gap or doubtful replacement assertion, make a small deliberate
fault in the production owner and confirm the retained test detects it, or use
the known pre-fix implementation as a control. Run controls in isolation and
restore the exact pre-control files, preserving existing edits. Do not leave
mutations behind. Report any missing failure proof as unresolved.

A retained baseline failure is a possible product defect. Reproduce it and
repair it only within the authorized scope; otherwise report it separately.
Never discard the test merely to obtain a green cleanup result.

## Reconcile and finish

If the base changes during the campaign, follow the repository's integration
policy. Reassess touched or deleted files and carry any new upstream contracts
into the appropriate remaining owner. Do not automatically favor either side
of a deletion conflict. Validate the actual final candidate, running the whole
subsystem suite when feasible and the repository-required gates.

In addition to the entrypoint's result, report inventory coverage, retired
layers and remaining owners, baseline/final test and support counts, production
changes separately, preservation gaps and control results, and unresolved
defects or unavailable checks. A deletion target never overrides contract
preservation; explain a smaller reduction rather than weakening the suite.
