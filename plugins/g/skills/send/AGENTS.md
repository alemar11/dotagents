# Send Maintenance

This bundled skill owns publication orchestration over the focused G
commit and GitHub workflows. Keep the executable publish contract in `SKILL.md`
and `references/workflows.md`.

## Ownership boundaries

- Delegate local staging and commit authoring to `$g:git-commit`, issue
  lifecycle to `$g:github-issues`, and review follow-up to the focused
  review skill. Do not duplicate those transports here.
- `scripts/g publish` owns structured local preflight and PR creation;
  connector-backed operations own supported existing-PR lifecycle changes.
- `scripts/g stack link` owns the explicit two-PR stack relationship; Send
  publishes one branch/PR and never infers or invokes that relationship. Send
  retains ownership of the current branch push, PR body, draft-state
  preservation, and publication handoff. Review requests remain owned by the
  focused review skill and its composing caller. Do not route publication
  through `gh stack submit`, which publishes every branch in a local stack.
- Keep caller-provided closing-issue references, base selection, and PR body
  construction in the send workflow references. Stack topology, merge, and
  post-merge work remain outside this skill.

## Validation

- Validate publish changes with a clean disposable/local preflight and the
  shared CLI tests and shipped-artifact smoke checks. Do not perform a push,
  PR mutation, or review request during validation without explicit authority.
- Preserve exact-head revalidation immediately before publication and the
  recovery/read-back evidence required after ambiguous remote results.
