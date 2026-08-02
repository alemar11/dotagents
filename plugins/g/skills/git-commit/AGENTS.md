# Git Commit Maintenance

This bundled skill owns the narrow commit operation contract. Keep invocation,
staging, fixup, and push behavior in `SKILL.md`, `references/workflows.md`, and
the shared G options reference.

## Owned surfaces

- `scripts/replace-amend-fixup-message` and
  `scripts/validate-fixup-target` are skill-local Python adapters. They are not
  alternate G runtimes and must remain noninteractive and target-safe.
- Commit transport and operation journaling belong to the shared
  `plugins/g/scripts/g` artifact and its maintenance project.

## Maintenance rules

- Preserve explicit path staging, exact fixup target resolution, and the
  boundary between commit-only work and `$g:send` publication.
- Do not add automatic autosquash, infer fixups from review prose, or duplicate
  shared option definitions in this skill.
- Validate adapter changes with syntax/fixture checks and the shared G
  focused test and shipped-artifact smoke lanes.
