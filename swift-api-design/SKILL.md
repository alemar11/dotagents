---
name: swift-api-design
description: Design or review Swift APIs using the official Swift API Design Guidelines, with focus on naming, argument labels, documentation comments, side effects, and call-site clarity.
---

# Swift API Design

## Goal

Design or review Swift APIs so they feel native to the language and are clear at the call site.

This skill uses:
- hand-written local summary pages for fast routing
- a bundled local copy of the upstream Swift API Design Guidelines in `assets/`
- a small manifest that tracks which upstream revision is bundled locally

## Trigger rules

- Use when the user asks to design, rename, review, or refactor a Swift API.
- Use when the task involves Swift method names, argument labels, initializer shape, protocol/type naming, documentation comments, or mutating/nonmutating pairs.
- Use when comparing multiple Swift API shapes and choosing the most idiomatic one.
- Do not use for general Swift implementation work unless the API surface itself is part of the request.

## Quick workflow

1. Start with [references/README.md](references/README.md).
2. Pick the shortest summary page that matches the task:
   - [references/core-principles.md](references/core-principles.md)
   - [references/naming-and-signatures.md](references/naming-and-signatures.md)
   - [references/common-api-shaping-patterns.md](references/common-api-shaping-patterns.md)
   - [references/review-checklist.md](references/review-checklist.md)
   - [references/official-guidelines.md](references/official-guidelines.md)
3. Start from the call site.
   - Sketch 2-3 realistic usages before judging the declaration.
   - Optimize for clarity at the point of use, not for declaration cleverness.
4. Classify the API surface.
   - Is it a type, protocol, property, method, initializer, factory, boolean query, mutating operation, or nonmutating transformation?
   - Apply the naming pattern that matches that role before tweaking labels.
5. Audit the signature.
   - Check the base name, first argument label, remaining labels, default arguments, parameter names, and whether the API reads fluently in code.
6. Audit semantics.
   - Side-effecting operations should read like verb phrases.
   - Nonmutating queries and values should read like noun phrases or assertions.
   - Mutating/nonmutating pairs should use consistent naming.
7. Write or review the doc comment.
   - Every public declaration should have a concise summary.
   - If the API is hard to explain simply, redesign it before polishing it.
8. Open [assets/api-design-guidelines.md](assets/api-design-guidelines.md) when you need the exact upstream wording or examples behind a recommendation.
9. Present recommendations with evidence.
   - Show before/after call sites.
   - Explain the change in terms of clarity, fluency, and guideline fit.

## References

- Read [README.md](references/README.md) first for scope, provenance, and best entrypoints.
- Read [core-principles.md](references/core-principles.md) first for the high-level design rules that should drive every decision.
- Read [naming-and-signatures.md](references/naming-and-signatures.md) when choosing names, argument labels, defaults, or overload shapes.
- Read [common-api-shaping-patterns.md](references/common-api-shaping-patterns.md) when cleaning up recurring API smells such as raw `Bool` parameters, weak domain types, options bags, or awkward method families.
- Read [review-checklist.md](references/review-checklist.md) when auditing an existing API or summarizing recommended changes.
- Read [official-guidelines.md](references/official-guidelines.md) when you want the local index page for the full bundled source.
- Read [assets/api-design-guidelines.md](assets/api-design-guidelines.md) when you need the exact upstream wording, examples, or section structure.
- Read [assets/manifest.json](assets/manifest.json) only when you need to confirm which upstream revision is bundled locally.

## Default review rubric

When reviewing a Swift API, check in this order:
- clarity at the call site
- correct noun/verb/assertion shape
- argument-label fluency
- side-effect signaling
- mutating/nonmutating consistency
- terminology and abbreviation quality
- documentation comment quality
- overload ambiguity and default-argument ergonomics

## Output shape

Prefer responses that include:
- the recommended signature
- 2-3 example call sites
- the specific guideline(s) motivating the change
- any tradeoff or ambiguity that remains
