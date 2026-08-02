# Architecture Candidate Report

Use this shape when the architecture candidate set is large enough to need an
artifact. Keep the report self-contained and outside the repository unless the
user asks to save it in the project.

## Location

Write to the OS temp directory:

- `$TMPDIR` when set,
- otherwise `/tmp` on Unix-like systems,
- otherwise `%TEMP%` on Windows.

Use a unique name such as `architecture-review-<timestamp>.html`.

## Content

Each candidate should include:

- files and modules involved,
- problem,
- proposed architectural move,
- benefits for locality, testability, and change safety,
- risks or migration cost,
- `recommendation_strength=strong|worth-exploring|speculative`, with separate
  prose explaining the classification,
- source evidence links or file paths,
- a simple before/after relationship diagram when it clarifies the move.

End with a top recommendation and the question:

```text
Which candidate would you like to explore?
```

## Visual Guidance

- Prefer plain HTML and CSS that works locally without a build step.
- Use Mermaid via CDN only when graph, sequence, or flow relationships are the
  clearest representation.
- Keep prose sparse; diagrams and file evidence should carry the report.
- Do not use the report as a substitute for source-backed reasoning.
