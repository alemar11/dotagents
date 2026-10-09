# Targeted Maintenance

Use for requested maintenance of existing skills, plugins, or coupled projects,
including explicit renames, moves, merges, replacements, and removals. Preserve
intent and invocation policy except where the requested change alters them.
Make only changes with a concrete rationale. Review-only requests produce findings
without edits.

Inspect the target's entrypoint, metadata, relevant references, and nearest
`AGENTS.md`. Follow scripts, editable `projects/*` sources, tests, assets, and
callers only where they own affected behavior. Include directly coupled README,
install, manifest, and marketplace entries; absent plugins are not drift.

Define the intended improvement, then apply the smallest coherent change.
Typical targets are trigger clarity, instruction ownership, reference routing,
metadata alignment, and dependency or portability wording. Keep detailed
procedures out of discovery descriptions. Update `AGENTS.md` only for durable
maintenance rules, not runtime behavior.

Do not refresh bundled domain sources without refresh authority. For package
changes that substantially reshape public behavior or responsibility, use the
appropriate creator workflow first, then resume targeted maintenance here.

When the request changes a package's identity, location, or existence, identify
the old and new owners and any intentionally removed capability. Update source,
metadata, callers, README, install prompts, registries, and repository-owned
symlinks together; include plugin manifests and marketplace entries when present.
Remove retired surfaces without aliases, preserving unrelated installations.
Before deleting an old surface, establish its verified replacement or confirm
that removing the capability is the requested outcome. Do not infer these
changes from a generic maintenance run.

Return changed surfaces, rationale, and any focused proof to the shared release
checklist. The caller owns batch alignment and validation; do not repeat those
passes inside each target upgrade. A standalone upgrade uses the same shared
closeout once.
