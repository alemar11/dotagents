# Git Commit Maintenance

This skill owns the narrow commit operation contract. Keep invocation, staging,
fixup, and push behavior in `SKILL.md`, `references/workflows.md`, and the
invocation fields in `SKILL.md`.

## Owned surfaces

- `scripts/replace-amend-fixup-message` and `scripts/validate-fixup-target` are
  skill-local Python adapters. They are not alternate runtimes and must remain
  noninteractive and target-safe.
- Commit transport uses direct `git`; the local adapters do not stage or commit.

## Maintenance rules

- Preserve explicit path staging, exact fixup target resolution, and the
  boundary between commit-only work and `$yeet` publication.
- Do not add automatic autosquash, infer fixups from review prose, or duplicate
  foreign option registries in this skill.
