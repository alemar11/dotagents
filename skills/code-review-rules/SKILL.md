---
name: code-review-rules
description: Manually discover, evaluate, and install evidence-backed Codex Code Review rules in the closest applicable AGENTS.md through the learn skill.
---

# Code Review Rules

## Purpose And Invocation

Use this skill to create or improve the exact `## Code Review Rules` contract
consumed by Codex Code Review. It turns verified repository knowledge into a
small set of consequential review rules, tests each candidate for scope and
noise, and delegates an approved durable write to `$learn`.

Use this skill only when the user explicitly invokes `$code-review-rules`, asks
to create or improve Codex Code Review rules, or a manually invoked parent
workflow explicitly routes here. Do not auto-select it for ordinary code
review, `AGENTS.md` maintenance, retrospective analysis, or general requests to
improve a repository. After reporting or applying the selected rules, stop.

This is not a code reviewer and does not run GitHub Code Review. It configures
repository guidance for later reviews. Rules remain advisory and never replace
tests, linters, branch protection, required approvals, or other deterministic
enforcement.

## Runtime And Ownership

This skill is Codex-dependent because its historical branch may inspect Codex
session, memory, or task evidence for the current repository. Repository files,
tests, accepted review findings, and current code remain the primary evidence.
When historical Codex evidence is unavailable, continue with repository
evidence and report the unavailable history instead of inventing rules.

`$learn` is the only writer and owns the confirmation boundary. This skill may
inspect, mine, filter, evaluate, and render exact proposed wording, but it must
not edit or create `AGENTS.md` directly. Once the proposal is ready, invoke
`$learn` with the full target path and exact wording so `$learn` can show them
and pause. After the user's later affirmative reply, continue `$learn`'s write,
duplicate/conflict check, and readback. Never propose and write in the same
turn, and never introduce a second approval prompt for the same unchanged
proposal.

Load `$learn` before rendering the final Markdown. Incorporate its required
placement and formatting conventions, including any required learning suffix,
into the wording shown to the user so the later write does not mutate an
already approved proposal. If `$learn` cannot preserve the intended Code Review
Rule contract, stop and report the composition conflict.

## Reference Routing

- Read [evidence-mining.md](references/evidence-mining.md) whenever inspecting
  previous sessions or other historical evidence, or when the repository has
  no `AGENTS.md` and candidates must be bootstrapped from evidence.
- Read [rule-evaluation.md](references/rule-evaluation.md) after at least one
  candidate exists and before showing proposed wording.
- Read [official-docs.md](references/official-docs.md) when verifying current
  Codex behavior, explaining why a rule belongs in `AGENTS.md`, or returning
  official documentation links or citations. Prefer the official sources in
  that reference over remembered product behavior.

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
  "follow best practices". If removing a candidate would not materially change
  the review, reject it.
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
3. Load [evidence-mining.md](references/evidence-mining.md) and inspect bounded
   repository-scoped history for additional candidates.

When the target does not exist:

1. Load [evidence-mining.md](references/evidence-mining.md).
2. Derive candidates from repository evidence and bounded repository-scoped
   history.
3. Propose creating the exact target only when at least one candidate survives
   the evidence and evaluation filters, or when the user explicitly requests
   an empty scaffold after being told that it adds no review behavior.

An evidence-poor repository returns a no-op. Never create an empty file or fill
it with generic starter rules by default.

### 3. Mine And Normalize Candidates

Follow [evidence-mining.md](references/evidence-mining.md). Treat prior sessions
as candidate evidence, not authority. A session statement becomes usable only
when its durable intent and repository truth are confirmed by accepted review
disposition, landed behavior, tests, current code, or explicit user approval.

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

Load and follow [rule-evaluation.md](references/rule-evaluation.md). For each
candidate, define a violating change, safe counterexample, unrelated change,
and ordinary bug-retention case. Reject or narrow rules that cannot distinguish
those cases.

When a representative forward run is available and authorized, execute it and
record the result. Otherwise perform the static case analysis, label the rule
as not forward-validated in the proposal, and do not claim runtime proof.

Limit the final set to the smallest non-overlapping group that changes review
behavior without creating predictable noise.

### 5. Hand The Exact Proposal To Learn And Pause

Pass this complete proposal to `$learn`, which must show:

- the absolute target `AGENTS.md` path and whether it exists;
- the exact Markdown block to create or update;
- one short evidence summary per rule;
- evaluation state and any history-coverage limitation;
- instruction-chain size and any scoping or truncation concern;
- whether companion deterministic enforcement is missing.

Then let `$learn` pause once. Silence, an unrelated reply, approval of only the
general idea, or the absence of an objection is not authority to write.

### 6. Apply Through Learn And Verify

After an affirmative approval of the target and wording already displayed by
`$learn`, continue that same `$learn` flow. Do not redraft the proposal or ask
for another approval. Follow `$learn`'s conflict, placement, and write rules. If
`$learn` requires clarification because repository state changed, stop and
return that conflict rather than selecting new wording independently.

After `$learn` writes:

1. Read the target back.
2. Confirm the exact heading, rule scope, safe path, and absence of duplicate or
   conflicting rules in the applicable chain.
3. Report whether the result was `applied`, `no-op`, or `blocked`, without
   claiming that GitHub Code Review executed.

## Output

For a proposal, report the target, exact Markdown, evidence summary, evaluation
state, history coverage, and next approval required. For a no-op, state why no
candidate survived. For an applied result, report the verified target and rule
count. Keep session provenance in the explanation only when useful and safe;
never persist it into the review rules.
