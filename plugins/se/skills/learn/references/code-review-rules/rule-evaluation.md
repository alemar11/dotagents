<!-- SE-owned reference derived from the durable repository-context contract. -->

# Rule Evaluation

Read this reference after candidate discovery and before proposing or applying
Code Review Rules.

## Candidate Quality Gate

For every candidate, answer:

| Dimension | Required evidence |
| --- | --- |
| Consequence | A concrete compatibility, privacy, authorization, data, safety, or operational failure. |
| Specificity | Repository behavior that a generic review would not reliably infer. |
| Scope | The narrowest root, package, or service path governed by the invariant. |
| Safe path | A supported alternative or explicit exception that avoids the failure. |
| Durability | Outcome-oriented wording that remains useful after ordinary refactors. |
| Enforceability | A reason this belongs in review judgment instead of only deterministic CI. |

Reject any candidate missing consequence, scope, or safe path. Move a fully
deterministic requirement to tests or CI rather than duplicating it as a review
rule.

## Four-Case Matrix

Build this matrix before showing exact wording:

| Case | Expected review behavior |
| --- | --- |
| Violation | The rule produces one actionable finding tied to the changed behavior. |
| Safe counterexample | The documented safe path or exception produces no finding. |
| Unrelated change | A nearby change outside the invariant produces no finding. |
| Ordinary bug retention | A serious defect unrelated to the custom rule remains reviewable. |

Describe concrete diffs or fixtures for all four cases. Do not use abstract
labels alone. If a candidate would flag the safe or unrelated case, narrow the
scope or wording. If it suppresses ordinary bug finding, split or remove it.

## Forward Validation

Learn is local-repository-only and never creates a branch, pull request, or
hosted review run to validate a rule. If the caller supplies prior hosted
evidence, record it as external evidence without contacting or mutating the
provider. Otherwise return the local static matrix and label the proposal
`not forward-validated`.

The evaluation result is one of:

- `forward-validated`: representative runtime evidence matched the matrix;
- `statically-evaluated`: the matrix is complete but no hosted run occurred;
- `rejected`: the candidate failed consequence, scope, safe-path, or restraint
  checks.

These are result states, not user-selectable options.

## Rule Rendering

Render accepted rules under the exact external contract:

```md
## Code Review Rules

### <Stable concern>

- Flag <unsafe behavior> because <consequence>.
  Safe path: <supported alternative or exception>.
```

Use direct language and the smallest sufficient explanation. Do not embed the
evaluation matrix, confidence score, provenance, issue IDs, or session IDs in
`AGENTS.md`.
