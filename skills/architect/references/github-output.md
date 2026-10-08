# GitHub Output

Read only for optional GitHub publication. The content contract is
[specification.md](specification.md). Use authenticated `gh` directly; Architect owns
the semantic projections. Pass bodies through files and API payloads through
structured JSON input, preserving literal text without shell interpolation.

## Projection

Title the spec issue `Spec: <spec title>` in `owner_repository`.
Apply the prefix exactly once; it is display metadata,
not identity, and a prefix-only change does not increment `spec_revision`.
Keep body headings unprefixed. Use the [spec template](../templates/spec.md) and
[rendering contract](specification.md#rendering). For legacy specs, apply
[existing-specs.md](existing-specs.md) before choosing which existing artifacts
to update; preserve separate task issues unless consolidation is in scope.
Never create task issues or sub-issue relationships, modify labels, or start
delivery.

## Spec dependencies

The [specification contract](specification.md#identity-and-authority) owns
prerequisite semantics. Verify exact repository and artifact identities for
authored links; reject new cross-repository links, self-dependencies and cycles
without creating placeholder issues. Preserve historical references under the
revision rules. Existing native relationships remain untouched; explicitly
requested blocker changes use `gh` outside Architect, with a separate result.

## Publish and verify

Before hosted reads or writes, apply the
[GitHub access check](../SKILL.md#refine-and-optionally-publish).
Before each write, apply [hosted-content safety](hosted-content-safety.md)
to the exact final content, including worker- or provider-originated content.

Resolve the owning repository and any supplied issue URL. For an existing spec,
verify the exact issue and its content before updating it. Before creating a new
issue, inspect plausible existing matches against the selected requirements and
source references; a matching title alone is insufficient. Reuse a verified
match and resolve material ambiguity before creation.
Create or update only the selected artifacts and read each back. Verify identity,
title, revision, every task and anchor, acceptance coverage, prerequisites, and
preserved foreign or executor-owned content. Preserve provider relationships and
unrelated metadata. Report completion only under [states.md](states.md), including
hosted-content conformity; for legacy revisions, report each artifact's result
so partial publication cannot appear complete.

Reconcile an ambiguous operation against the same issue before retrying.
Retry only after proved non-application and stop on unresolved ambiguity. Report
completed and remaining effects; never recreate the issue or substitute a local
publication after partial publication. Publication does not close this spec or any source or
prerequisite issue. Separately authorized closure or notification follows verified
publication through its owner and requires its own reconciliation.
