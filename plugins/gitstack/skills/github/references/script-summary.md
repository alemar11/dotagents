# GitHub script summary

Use this as the top-level runtime and command-map index referenced by the
bundled `github` skill.

## Public runtime

- Start with `references/core/ghflow-resolution.md`, then run
  `<resolved-ghflow> --version`.
- Treat `ghflow` as a narrow shared-helper surface, not as a replacement for
  `gh` or `git`.
- Treat bare `ghflow` in command lists as display shorthand for the resolved
  installed artifact path, not as a `PATH` requirement.
- Prefer plain `gh` and `git` for routine repository, issue, PR, CI, and
  release work.

## Shared `ghflow` helpers

- Failing-PR CI inspection: `<resolved-ghflow> ci inspect`
- Review-thread triage and reply routing: `<resolved-ghflow> reviews address`
- Authenticated-user stars and star lists:
  `<resolved-ghflow> stars <list|add|remove>`,
  `<resolved-ghflow> stars lists <list|items|delete|assign|unassign>`
- Already-pushed current-branch PR context and open-or-reuse:
  `<resolved-ghflow> publish context`, `<resolved-ghflow> publish open`

## Domain catalogs

- Core setup, auth, artifact resolution, and retry helpers:
  `references/core/installation.md`, `references/core/ghflow-resolution.md`
- Triage helpers: `references/triage/script-summary.md`
- Review helpers: `references/reviews/script-summary.md`
- CI guidance: `references/ci/script-summary.md`
- Release guidance: `references/releases/script-summary.md`
- Publish helpers: `references/publish/script-summary.md`
