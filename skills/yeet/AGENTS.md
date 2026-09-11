# Yeet Maintenance

This skill owns publication orchestration over focused commit and GitHub
workflows. Keep the executable publish contract in `SKILL.md` and
`references/workflows.md`.

## Ownership boundaries

- Delegate local staging and commit authoring to `$git-commit`, issue lifecycle
  to `$github-issues`, and review follow-up to `$github-review-threads`. Do not
  duplicate those transports here.
- `scripts/publish` owns structured local preflight, snapshot, and PR creation;
  file-backed authenticated `gh` operations own existing-PR lifecycle changes.
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

## Executable maintenance

- `scripts/publish` is the shipped runnable artifact (`preflight`, `open`,
  `snapshot`, `doctor`).
- `scripts/publish_lib/` holds the implementation. Provider-protocol modules
  (`common.py`, `repository.py`, `integrity.py`, `provider_text.py`) are synced
  copies of `projects/github-tools/src/github_provider_protocol/`; run
  `projects/github-tools/scripts/sync-provider-protocol` after protocol edits
  and never hand-edit the copies.
- Naming: `publish_lib` uses underscores as the Python import-syntax
  compatibility exception; the public skill (`yeet`) and command (`publish`)
  stay lower-kebab.
- Validate with `python3 -m unittest discover -s skills/yeet/tests -v` and
  `scripts/publish --help|--version|--json doctor`.
