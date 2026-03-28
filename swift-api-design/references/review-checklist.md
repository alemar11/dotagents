# Review Checklist

Use this checklist when reviewing or refactoring a Swift API. Open the bundled
source in [api-design-guidelines.md](../assets/api-design-guidelines.md) when
you need the exact official wording or examples behind a finding.

## Call-site clarity

- Does the API read clearly in 2-3 realistic examples?
- Would a reader understand what each argument means without jumping to the declaration?
- Is any word missing that would prevent ambiguity?
- Is any word present only because it repeats type information?

## Semantic shape

- Is this API a noun, verb, assertion, initializer, or factory?
- Does the name match whether the operation mutates or returns a new value?
- For boolean APIs, does the call read like a true/false statement?

## Labels and parameters

- Does the first argument label follow Swift conventions?
- Do later labels explain role, not type?
- Are parameter names good enough to support natural documentation?
- Are default arguments simplifying common use rather than hiding behavior?

## Naming quality

- Are terms established in Swift or the problem domain?
- Are abbreviations truly standard and easy to recognize?
- Are protocols named as identities or capabilities appropriately?
- Are names based on role rather than concrete type names?

## Documentation

- Is there a short summary comment for each public declaration?
- Does the summary say what the API does, returns, creates, accesses, or is?
- Did writing the doc comment reveal missing semantics or confusing naming?

## Overloads and ergonomics

- Are overloads meaningfully related?
- Could type inference make an overload ambiguous?
- Is a method family better expressed as one API with defaults?
- Is any overload distinguished only by return type?

## Suggested response format

When you recommend changes, prefer:
1. current signature
2. proposed signature
3. before/after call sites
4. short explanation tied to one or more guideline themes

## Common fixes

- Add a missing first argument label to remove ambiguity.
- Remove a redundant type word from the base name.
- Rename a side-effecting method so it reads like an action.
- Split a confusing overload set into more explicit names.
- Replace method families with defaulted parameters when the behavior is truly the same.
- Rename protocol or type surfaces so they read naturally as identities or capabilities.

## Cross-Checks

- Use [core-principles.md](core-principles.md) when the problem is mostly about
  semantics, terminology, or call-site clarity.
- Use [common-api-shaping-patterns.md](common-api-shaping-patterns.md) when the
  review keeps surfacing the same cleanup moves across different APIs.
- Use [naming-and-signatures.md](naming-and-signatures.md) when the problem is
  mostly about labels, defaults, overloads, or mutating/nonmutating pairing.
