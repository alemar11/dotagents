# Submit Maintenance

This bundled skill owns publication orchestration over the focused GitStack
commit and GitHub workflows. Keep the executable publish contract in `SKILL.md`
and `references/workflows.md`.

## Ownership boundaries

- Delegate local staging and commit authoring to `$gitstack:git-commit`, issue
  lifecycle to `$gitstack:github-issues`, and review follow-up to the focused
  review skill. Do not duplicate those transports here.
- `scripts/gitstack publish` owns structured local preflight and PR creation;
  connector-backed operations own supported existing-PR lifecycle changes.
- Keep closing-issue references and PR body construction in the submit workflow
  references. Merge and post-merge work remain outside this skill.

## Validation

- Validate publish changes with a clean disposable/local preflight and the
  shared CLI tests and shipped-artifact smoke checks. Do not perform a push,
  PR mutation, or review request during validation without explicit authority.
- Preserve exact-head revalidation immediately before publication and the
  recovery/read-back evidence required after ambiguous remote results.
