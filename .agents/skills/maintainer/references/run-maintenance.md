# Repository Maintenance

Use for a bare `run` or unnamed maintenance request. The default inventory in
[task-menu.md](task-menu.md) includes reusable and project-local skills, optional
plugins, and coupled maintenance sources. An empty plugin marketplace is valid.

1. Inspect the inventory and directly coupled repository docs. Use
   [skill-health.md](skill-health.md) to identify concrete drift.
2. Shortlist safe, low-ambiguity improvements: stale paths, aligned metadata,
   duplicated description detail, or clearer wording that preserves behavior.
   Report strategic or behavior-sensitive candidates instead of applying them.
3. Apply shortlisted edits using [skill-upgrade.md](skill-upgrade.md).
4. Return package coverage, rationale, changed surfaces, and existing proof to
   the shared release checklist. It owns one alignment and validation pass for
   the batch; do not run a full closeout for every package.

Do not infer domain refresh, workflow hardening, package renames/moves/removals,
substantial reshapes, or new-package creation from a bare run. If inspection
finds no meaningful maintenance, finish as a verified no-op.
