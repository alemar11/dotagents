# GitHub Issues Maintenance

This bundled skill owns lifecycle operations for individual GitHub issues. Keep
the user-facing workflow in `SKILL.md` and `references/workflows.md`; keep
canonical option ownership in the plugin-level references.

## Maintenance boundaries

- Use the official GitHub connector for supported operations and the shared
  `scripts/g` artifact only for documented connector gaps and typed
  verification. Do not create a second issue transport here.
- Preserve the separation between issue lifecycle mechanics and repository-wide
  triage, investigation, review, Actions, release, or submission workflows.
- Keep content-based selection of existing labels and native issue types, plus
  read-only proposals for missing taxonomy, in `../github-tagger/`; this
  package receives exact metadata operations and owns their provider mutation
  and readback only.
- Keep free-form provider text file-backed and secret-safe; direct `gh` paths
  must remain explicit, dry-run capable, and independently verified.
- Keep native dependency result meanings in `references/states.md`; workflow
  references may route to them but must not define a second registry.
- Validate shared CLI changes through `projects/g/AGENTS.md`; validate
  issue workflow edits with read-only or dry-run fixtures before any authorized
  remote write.
