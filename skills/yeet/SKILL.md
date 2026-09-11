---
name: yeet
description: "Commit and push scoped changes, then create or update one PR while preserving existing draft state."
---

# Yeet

Before remote `git`, `gh`, registry, or skill helper commands that contact the
network, use the runtime's narrowest network-enabled context for that command
family. Keep local-only git sandboxed. Verify `gh` is runnable (`command -v gh`,
`gh --version`) and authentication with:

```sh
gh auth status --active --hostname github.com --json hosts \
  --jq '.hosts["github.com"] | map(select(.active == true) | {state, scopes})'
```

Require exactly one active account with `state=success`. Treat
restricted-environment network failures as inconclusive. Do not install or
refresh `gh` without explicit authorization. Network permission is not
mutation authority.

## Role

Publish one branch and PR. Compose `$git-commit` for commit authoring; Yeet owns
the push, base selection, PR body, and publication readback. Reuse an existing
suitable commit and matching PR.

Resolve `<skill-root>` as the absolute path of the directory containing this
`SKILL.md`. Use `<skill-root>/scripts/publish --json preflight` and
`<skill-root>/scripts/publish --json open` for a new PR; use file-backed
`gh api --input` for existing title/body changes. Keep provider text out of
shell strings and argv. Worktree fingerprints use
`<skill-root>/scripts/publish --json snapshot`.

For issue-only work or no publishable changes, use the relevant owning skill
instead of running publication. Single-PR publication does not imply stack
management. Yeet does not infer, verify, link, or manage a stack; a caller that
needs a parent/child relationship invokes `$github-stacked-pr` separately after
Yeet's publication receipt. Do not use `stack submit` as a Yeet fallback.

## Invocation fields

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `mutation_mode` | `apply`, `dry-run` | `dry-run` | Write-shaped publication preview versus apply. Omit for pure reads. |

An explicit request to publish resolves to `mutation_mode=apply` within the
requested scope. A preview, dry-run, or local-only request resolves to
`mutation_mode=dry-run`: inspect and prepare the publication evidence without
committing, pushing, or changing GitHub. Pure reads omit the field.

Callers must normalize planning policy before invocation. Reject
caller-owned planning, tracker, orchestration, delivery, permission, or phase
fields. Compose `$git-commit` with its own `commit_operation` /
`commit_kind` fields.

## Base Selection And Existing PR Reuse

Resolve the PR base branch before committing or pushing. Use the explicit base
branch supplied by the caller for a new PR; otherwise use the repository default
branch. A non-default explicit base is valid and is not evidence of a stack.
Never treat the worker or feature head branch as the PR base merely because it
is named `target_branch_name`.

When the current branch already has exactly one matching open PR, that PR is the
publication target. Without an explicit base, preserve its read-back
`baseRefName`; with an explicit base, require it to equal that existing base.
Stop on a missing or ambiguous base instead of retargeting the PR or silently
falling back to the default branch. Preserve its current `isDraft` value.

## Issue Linkage Contract

Accept `closing_issue_refs` as caller-owned factual input: the exact GitHub
issues whose accepted scope is fully satisfied by this PR. Validate every
candidate against its exact GitHub repository and issue before PR mutation.
Yeet must not derive an issue from a bare number, branch name, commit subject,
nearby issue, parent Feature Spec, dependency, or partial implementation.

When `closing_issue_refs` is nonempty:

- include one canonical `Closes` line per deduplicated issue under `## Issues`
  in the PR description, using `Closes #<number>` for the PR repository and
  `Closes <owner>/<repository>#<number>` for another repository;
- preserve and union valid closing references already present when updating a
  PR, without replacing unrelated template or author content;
- stop on conflicting, ambiguous, missing, or only partially satisfied issue
  evidence rather than adding a closing keyword that could close the wrong
  issue.

The selected PR base does not change this validation. Yeet carries the exact
caller-provided issue set to the PR body and verifies the resulting body and
provider references; it does not decide whether the current delivery topology
will make GitHub close those issues or mutate an issue directly. A composing
caller owns the standalone/stacked interpretation and any separate
post-publication delivery verification.

When no issue is confirmed, omit `## Issues` rather than inventing a placeholder
or asking merely to fill the section. Report the empty linkage result in the
closeout.

## Workflow

Open [references/workflows.md](references/workflows.md) for publish, existing-PR,
retry, and no-publishable-work procedures. Yeet must not request or wait for an
automated Codex review; a composing caller that needs one invokes
`$github-review-threads` separately using the exact repository, PR, and full
published head SHA from Yeet's publication evidence.

## Skill Dependencies

- `$git-commit` for local commit authoring when a new commit is required.

## References

- `references/workflows.md`: publish, existing-PR, and retry workflows.
