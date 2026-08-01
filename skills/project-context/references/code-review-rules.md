# Code Review Rules

Use this reference when `memory_slice=code-review-rules` is explicitly
selected to create or improve the exact `## Code Review Rules` contract
consumed by Codex Code Review. Turn verified repository knowledge into a small
set of consequential review rules, evaluate each candidate for scope and noise,
and update the closest applicable `AGENTS.md` through Project Context.

This operation is not a code reviewer and does not run GitHub Code Review. It
configures repository guidance for later reviews. Rules remain advisory and
never replace tests, linters, branch protection, required approvals, or other
deterministic enforcement.

## Operation And Ownership

Select this operation only when the user explicitly asks to create, improve,
install, or review Codex Code Review rules, or when a manually invoked parent
workflow passes the same explicit scope. Do not infer it from ordinary code
review, `AGENTS.md` maintenance, retrospective analysis, or general repository
improvement requests. Do not infer it from `full-setup` unless the user also
explicitly requests Code Review Rules.

Project Context owns repository resolution, candidate discovery, evidence
filtering, scope selection, evaluation, exact proposal rendering, and the
authorized `AGENTS.md` write. Repository files, tests, accepted review
findings, and current code remain the primary evidence. Historical Codex
session, memory, or task evidence is optional candidate evidence; when it is
unavailable, continue from repository evidence and report the limitation.

For inspection, recommendation, dry-run, or draft requests, return the exact
target and wording without writing. An explicit request to create or update the
rules authorizes the selected `AGENTS.md` write. Before writing, show the
intended target and meaningful before/after block. Do not introduce a second
approval flow outside Project Context's normal request boundary.

If the user explicitly needs durable explanatory material, keep it as optional
detail in the consumer repository's flat `project-context/code-review-rules.md`
and index it from `CONTEXT.md`. Never move the active invariant, consequence,
or safe path out of `AGENTS.md`, and never make the optional file a prerequisite
for the rule to apply.

## Reference Routing

- Read [code-review-rules/evidence-mining.md](code-review-rules/evidence-mining.md)
  when inspecting previous sessions or other historical evidence, or when a
  repository has no `AGENTS.md` and candidates must be bootstrapped from
  evidence.
- Read [code-review-rules/rule-evaluation.md](code-review-rules/rule-evaluation.md)
  after at least one candidate exists and before showing proposed wording.
- Read [code-review-rules/official-docs.md](code-review-rules/official-docs.md)
  when verifying current Codex behavior, explaining why a rule belongs in
  `AGENTS.md`, or returning official documentation links or citations.

## Fixed Rule Contract

- Use the exact `## Code Review Rules` heading. Optional `###` headings group
  rules by a stable concern such as compatibility, privacy, or data boundaries.
- Start with at most three new rules in one run. Prefer one strong rule over a
  broad checklist.
- Every rule must identify a consequential, non-obvious invariant, why a
  violation matters, and a safe path or valid exception.
- Prefer durable outcomes, boundaries, and wire contracts over function names
  or implementation details likely to change.
- Exclude formatting, lint, generated-file drift, schema checks, and other
  deterministic requirements that CI can enforce reliably.
- Do not add generic advice such as "review security", "write tests", or
  "follow best practices". If removing a candidate would not materially
  change the review, reject it.
- Put repository-wide rules in the root `AGENTS.md`. Put package- or
  service-specific rules in the closest applicable nested `AGENTS.md`. Do not
  move unrelated existing instructions merely to add review rules.
- Check the root-to-target instruction chain for duplicates and conflicts.
  More-specific wording must narrow or clarify broader guidance, not silently
  reverse it.
- Measure and report the existing instruction-chain size. The documented local
  Codex default is a combined 32 KiB limit, but do not claim that this local
  limit also governs hosted GitHub Code Review unless current official docs say
  so.

## Workflow

### 1. Resolve The Repository And Scope

Find the current Git repository root. Inventory root and relevant nested
`AGENTS.md` files, then identify the code paths the requested rules would
govern. Read the applicable instruction chain plus relevant code, tests,
contracts, and architecture documentation.

If the requested scope is ambiguous and different targets would change which
review rules apply, ask for the scope before mining. Do not default to the root
merely because it already contains an `AGENTS.md`.

### 2. Choose The Existing Or New-File Path

When the target `AGENTS.md` exists:

1. Read the complete applicable `## Code Review Rules` section, if present.
2. Identify duplicates, superseded wording, conflicts, and nearby durable
   invariants that are not yet review rules.
3. Load [evidence-mining.md](code-review-rules/evidence-mining.md) and inspect
   bounded repository-scoped history for additional candidates.

When the target does not exist:

1. Load [evidence-mining.md](code-review-rules/evidence-mining.md).
2. Derive candidates from repository evidence and bounded repository-scoped
   history.
3. Propose creating the exact target only when at least one candidate survives
   the evidence and evaluation filters, or when the user explicitly requests
   an empty scaffold after being told that it adds no review behavior.

An evidence-poor repository returns a no-op. Never create an empty file or fill
it with generic starter rules by default.

### 3. Mine And Normalize Candidates

Follow [evidence-mining.md](code-review-rules/evidence-mining.md). Treat prior
sessions as candidate evidence, not authority. A session statement becomes
usable only when its durable intent and repository truth are confirmed by
accepted review disposition, landed behavior, tests, current code, or explicit
user approval.

Normalize every surviving candidate into:

```yaml
scope: <repo-relative path set>
unsafe_change: <behavior to flag>
consequence: <why it matters>
safe_path: <supported alternative or exception>
evidence:
  - <repository or accepted historical evidence>
confidence: high | medium
```

Reject low-confidence candidates. Never copy secrets, credentials, private
conversation content, session paths, task IDs, or provenance annotations into
the emitted `AGENTS.md` rule.

### 4. Evaluate The Candidate Set

Load and follow [rule-evaluation.md](code-review-rules/rule-evaluation.md). For
each candidate, define a violating change, safe counterexample, unrelated
change, and ordinary bug-retention case. Reject or narrow rules that cannot
distinguish those cases.

When a representative forward run is available and authorized, execute it and
record the result. Otherwise perform the static case analysis, label the rule
as not forward-validated in the proposal, and do not claim runtime proof.

Limit the final set to the smallest non-overlapping group that changes review
behavior without creating predictable noise.

### 5. Draft And Apply Through Project Context

Show this complete proposal before an authorized apply write:

- the absolute target `AGENTS.md` path and whether it exists;
- the exact Markdown block to create or update;
- one short evidence summary per rule;
- evaluation state and any history-coverage limitation;
- instruction-chain size and any scoping or truncation concern;
- whether companion deterministic enforcement is missing.

For inspection or recommendation requests, stop after returning the proposal.
For an explicit update request, update only the selected target and preserve
unrelated instructions, comments, overrides, and existing memory pointers.
Create a missing `AGENTS.md` only when at least one evidence-backed rule
survives, or when the user explicitly requested an empty scaffold after being
told that it adds no review behavior.

### 6. Verify The Result

After an authorized write:

1. Read the target back.
2. Confirm the exact heading, rule scope, consequence, safe path, and absence
   of duplicate or conflicting rules in the applicable chain.
3. Report `applied`, `no-op`, or `blocked` without claiming that GitHub Code
   Review executed.

## Output

For a proposal, report the target, exact Markdown, evidence summary, evaluation
state, history coverage, and next authority required. For a no-op, state why no
candidate survived. For an applied result, report the verified target and rule
count. Keep session provenance in the explanation only when useful and safe;
never persist it into the review rules.
