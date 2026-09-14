# Yeet Maintenance

This skill owns publication orchestration over focused commit and GitHub
workflows. Keep the publication contract in `SKILL.md` and
`references/workflows.md`.

## Ownership boundaries

- Delegate local staging and commit authoring to `$git-commit` and review
  follow-up to `$github-review-threads`. Use authenticated `gh` directly for
  explicitly requested issue lifecycle operations.
- Git and authenticated `gh` own execution; this skill ships no CLI. Keep
  preflight, file-backed text transport, and publication readback in the workflow.
- `$github-stacked-pr` owns the explicit two-PR stack relationship; Yeet publishes
  one branch/PR and never infers or invokes that relationship. Yeet retains
  ownership of the current branch push, PR body, draft-state preservation, and
  publication handoff. Do not route publication through `gh stack submit`.
- Keep caller-provided closing-issue references, base selection, and PR body
  construction in the yeet workflow references. Stack topology, merge, and
  post-merge work remain outside this skill.

## Validation

- Validate publish prose and path contracts without performing a push or PR
  mutation unless explicitly authorized.
- Preserve exact-head revalidation immediately before publication and the
  recovery/read-back evidence required after ambiguous remote results.
