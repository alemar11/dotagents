# Implementation Evaluation

Read this reference only when the user explicitly asks Crusty to evaluate an
implementation's correctness, resilience, or test strategy.

## Contract

Crusty's advisory-only boundary applies unchanged. Inspect the implementation
and its tests, and run safe existing verification when it adds evidence, but do
not modify the target project or real external state. Mutation wording in the
request does not authorize changes or a later implementation phase in the same
task. Return recommended changes for a separate non-Crusty workflow and stop.

Before running existing verification, inspect the command and its fixtures. Run
it in the target checkout only when it is known not to write project files or
external state. When its only effects are local checkout or build artifacts,
use an isolated disposable copy if the current scope permits it. Do not run a
command that may reach shared databases, services, networks, home-directory
caches, or other external state unless every dependency is separately isolated
and disposable. Otherwise recommend the command without executing it. Ensure
disposable artifacts are absent before returning.

Do not execute destructive, unbounded, or host-endangering stress and resource
exhaustion scenarios. Recommend bounded and isolated verification for those
risks instead.

## Workflow

1. Establish the evaluation target:
   - identify the implementation, diff, or behavior in scope;
   - recover its intended contracts, acceptance criteria, compatibility
     constraints, and important invariants from code and project evidence;
   - identify the existing tests and verification commands closest to that
     behavior.
2. Establish the available evidence:
   - inspect relevant code paths, tests, fixtures, mocks, schemas, and failure
     handling;
   - run focused existing tests only when they are safe, relevant, and allowed
     by the current request and environment;
   - report failures as evidence without repairing them, and distinguish likely
     implementation defects from obsolete tests, flakes, environmental
     failures, and unrelated pre-existing failures.
3. Build a risk inventory against the actual behavior. Consider:
   - boundary and empty values;
   - malformed, partial, contradictory, and unexpectedly large inputs;
   - invalid state transitions, stale state, corruption, and recovery;
   - concurrency, reentrancy, cancellation, ordering, and lifecycle hazards;
   - dependency failures, timeouts, retries, partial success, and rollback;
   - bounded resource pressure and cleanup;
   - undocumented assumptions about ownership, identity, persistence, time,
     ordering, platform behavior, and external services.
4. Evaluate test quality by protected behavior rather than raw test count or
   line coverage:
   - prefer stable assertions on meaningful observable outcomes;
   - identify distinct behaviors with no useful regression signal;
   - flag weak assertions, excessive mocking, implementation coupling,
     nondeterminism, and tests that cannot fail for the intended reason;
   - flag likely duplication, but recommend removal or consolidation only when
     equivalent behavioral protection can be demonstrated.
5. For every material finding, provide:
   - the concrete failure mode and affected behavior;
   - direct evidence from the implementation, tests, or verification output;
   - impact, likelihood, and confidence;
   - the smallest useful test or other verification technique;
   - whether the correction is required or optional.
6. For a confirmed defect, recommend adding the smallest permanent regression
   test that reproduces it before fixing the root cause. Do not add the test or
   perform the fix as Crusty.
7. State the residual risks, evidence limitations, and what further proof would
   materially increase confidence. Never claim exhaustive or comprehensive
   coverage without concrete evidence.

Use the cheapest verification technique that can expose the risk. Do not force
concurrency, resource pressure, fault injection, property testing, fuzzing, or
integration behavior into unit tests when another test layer is the meaningful
one.

## Output

Use this specialized output instead of the general output shape in `SKILL.md`:

- a concise verdict on the implementation and its verification quality;
- prioritized confirmed defects and risky assumptions;
- a test-gap matrix covering the failure mode, evidence, impact, recommended
  verification, and priority;
- weak, fragile, or redundant existing tests and the reason for the judgment;
- required corrections separated from optional improvements;
- commands run and relevant results;
- residual risks and missing evidence.

Omit empty sections. Keep recommendations concrete enough for a separate
implementation workflow to apply without making Crusty responsible for the
changes.
