---
name: adversarial-review
description: "Use when explicitly asked to pressure-test a software change or when a composed workflow needs an independent read-only review of a fixed code snapshot."
---

# Adversarial Review

Pressure-test the selected software change as a skeptical shipment reviewer.
Review the complete supplied change and its relevant code paths, then return
evidence-backed findings or a clean result. This skill is read-only: it never
edits the target, fixes findings, performs Git mutations, or publishes hosted
content.

## Review handoff

Use the caller's verified target, base, repository instructions, and optional
focus areas. When a composed workflow supplies an immutable snapshot, preserve
its exact identity and review the whole delta rather than only the latest turn
or commit. Keep the review independent from the implementation conversation
when the caller requires independent review.

Apply only lenses relevant to the actual change. Consider material correctness
risks, hidden assumptions, authorization or permission errors, data loss or
corruption, concurrency, retries and idempotency, migration and compatibility
hazards, rollback and partial failure, degraded dependencies, observability,
and whether a safer or simpler approach is warranted. Do not manufacture
findings to satisfy the posture.

## Result

Return one disposition selected by the calling workflow, normally `clean`,
`findings`, or `indeterminate`, plus severity-ordered findings. Each finding
identifies the concrete failure mode, affected file and tight line range when
available, supporting evidence, confidence, and a focused recommendation.
State the reviewed target and any material coverage or execution limitation.

The reviewer never fixes its own findings. A caller may use findings to decide
whether to repair, rebut, defer, or block; a clean result only authorizes the
caller-specific next step.
