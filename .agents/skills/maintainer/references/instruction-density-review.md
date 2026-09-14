# Instruction Quality and Density Review

Use this playbook for skill instruction audits and refactoring. Review-only
requests return proposals. A request to review and fix, update, or refactor
authorizes local edits within that scope; no second approval is required.
Preserve invocation policy and real operational constraints. Ask only when a
material change to intent or scope remains unresolved.

## Inspect the active path

Resolve named targets, or use the repository inventory for a repo-wide request.
Read each entrypoint and discovery metadata, then follow references that govern
the relevant behavior. Include callers, templates, and local AGENTS.md when
they repeat or contradict the contract. Keep generated domain assets and runtime
scripts outside an instruction-only refactor unless separately in scope.

Assess these decisions:

- **Selection:** Does the description identify the actual task and avoid broad
  topic matches? Put decisive trigger wording early and retain only useful
  exclusions. Check nearby skills for overlap; preserve explicit-only policy.
- **Loading:** Does each mandatory reference change the selected operation?
  Keep shared constraints in the entrypoint and conditional detail under one
  linked owner. A self-contained skill needs no router. Moving text to a file
  that every invocation still reads does not reduce the active path.
- **Procedure:** Is each fixed step needed for a contract, permission boundary,
  fragile operation, or the explicitly selected experience? Preserve those
  reasons and remove generic coaching, repeated checks, and obsolete workarounds.
- **Authority:** Do user instructions and existing authorization remain
  effective across composed skills? Separate required input, unavailable
  capability, and missing permission. Make a necessary pause traceable to its
  actual instruction; continue unaffected authorized work.
- **Completion:** Can the agent identify the requested outcome, relevant proof,
  and stopping point? Avoid ending at the first draft when implementation and
  verification are in scope, or demanding more tests without a remaining risk.
- **Audience:** Which models and callers use the skill? Keep shared invariants
  and externally consumed result shapes; use model-specific procedures only
  for an evidenced need. Do not weaken a real constraint merely because Astra
  is more capable.

## Decide and apply

For each finding, identify the observable failure or unnecessary work and the
smallest correction. Distinguish safe trims, conditional extraction, intentional
behavior changes within the request, and wording that should remain. Size is a
diagnostic, never a quota or a reason to rewrite an otherwise clear skill.

Prepare concrete edits, preserving scope, exceptions, ownership, and meaningful
completion criteria. Apply them when authorized; otherwise return the proposed
diff and unresolved decisions. Keep identity, metadata, references, state
contracts, and coupled catalog entries aligned. Domain refresh, package removal,
commit, and publication still need their own applicable authority.

## Verify and report

Use the relevant lanes in [validation-matrix.md](validation-matrix.md). Inspect
representative positive and negative triggers, conditional loading, existing
authorization, and completion from the resulting instructions. Static review
and metadata/link checks are enough for clear prose changes; use a bounded
runtime scenario only for a behavioral uncertainty static inspection cannot
resolve. Stop after the affected checks pass unless new evidence warrants more.

Report coverage, concrete changes or proposals, preserved constraints, checks,
and remaining limitations. For size questions, distinguish discovery metadata,
entrypoint size, and the references loaded by a representative invocation;
[skill-health.md](skill-health.md) owns those measurements.
