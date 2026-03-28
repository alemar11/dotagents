# Swift API Design References

Curated local references for the `swift-api-design` skill.

## How To Use This Set

- Start with the shortest summary that matches the task.
- Open the bundled source in `../assets/api-design-guidelines.md` when you need
  the exact upstream wording, examples, or section structure.

## Best Entry Points

- [core-principles.md](core-principles.md): first read for naming philosophy,
  call-site clarity, terminology, and semantic role checks.
- [naming-and-signatures.md](naming-and-signatures.md): fastest path for method
  names, argument labels, defaults, overloads, and mutating pairs.
- [common-api-shaping-patterns.md](common-api-shaping-patterns.md): common
  cleanup moves such as `Bool` to enum, stronger domain types, options bags,
  and small API-shape choices.
- [review-checklist.md](review-checklist.md): audit flow for reviewing an
  existing Swift API surface.
- [official-guidelines.md](official-guidelines.md): provenance, section map, and
  the handoff to the full local source.

## Layout

- `../assets/api-design-guidelines.md`: bundled upstream source from
  `swiftlang/swift-org-website`.
- `../assets/manifest.json`: bundled-source provenance and revision metadata.
- `official-guidelines.md`: local index page for the canonical source.
- `core-principles.md`, `naming-and-signatures.md`,
  `common-api-shaping-patterns.md`, and `review-checklist.md`: thin curated
  summaries for common API-design tasks.

## Scope

- In scope: Swift naming, labels, defaults, doc comments, side effects,
  mutating or nonmutating pairs, terminology, and review guidance.
- Out of scope: general Swift implementation work where the API surface is not
  part of the request, compiler internals, and Swift Evolution policy debates.
