# Existing Specs

Read when revising a saved spec. The content contract remains [specification.md](specification.md).

## Revision

Load the authoritative spec and every affected task before drafting. Preserve
their exact logical and saved identities, retired IDs, unrelated
content, and executor-owned status, checkboxes, comments, and progress. Record
the smallest semantic change; increment `spec_revision` once for the accepted
semantic bundle revision. A save retry or unchanged revision does not increment it.
Preserve unrelated provider metadata during publication; Spec does not own or
modify labels or delivery authorization. Ordinary revisions change only the
accepted semantic bundle and affected task contracts.
Before reshaping active work, reconcile material changes against existing delivery
assignments and the user's granted scope. Marker-only edits are nonsemantic.

Reordering or renaming preserves task identity. New tasks receive unused IDs.
If a task's outcome is replaced rather than refined, retire its old identity
explicitly and allocate another. Keep a compact record of retired task IDs so later runs cannot reuse them,
and describe materially replaced or removed acceptance obligations; use the
[revision note](../templates/maintenance-changelog.md) when useful. Do not silently remove already
implemented obligations or reshape active work; surface material conflicts
with observed execution for user direction.

Update the spec index and affected task details together, preserving
unaffected fields. Verify that no task, criterion, or dependency is orphaned.
Retiring a task removes it from the active index with an explicit historical
reference; preserve its identity and attributable execution history.
Retirement invalidates any prior delivery evidence relying on it.

For a pre-existing spec with separate task issues, read all linked contracts and
consolidate them into the same spec issue when revising. Preserve task IDs,
progress, and historical source links; verify complete incorporation before
treating the embedded sections as authoritative. Do not create more task issues,
close or delete old ones, or remove old relationships without explicit scope.
Reconcile active delivery assignments before transferring their progress owner.

When an older spec includes cross-repository work or links, do not split it or
create companion issues. Draft a local-only revision for its owner repository.
Removing accepted obligations requires revision authority and reconciliation
with active assignments; report material conflicts rather than silently dropping
work. Move superseded cross-repository relationships out of the active plan only
within that authority. Preserve historical source attribution, executor-owned
content and provider relationships; these are historical records, not permission
to add or refresh cross-repository issue links. If narrowing is outside the
request, report the affected scope and exact decision needed before publishing it.

For published specs, GitHub is the saved authority. Before publication, the
refined spec exists only in the current conversation; Spec does not maintain or
export a second local copy. Preserve attribution and source content.
