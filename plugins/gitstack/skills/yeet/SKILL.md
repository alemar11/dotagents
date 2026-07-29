---
name: yeet
description: Publish local work to GitHub. Use when the user explicitly requests the complete flow to confirm scope, commit, push the branch, open a draft or update an existing pull request without changing its draft state, and request a current-head Codex review.
---

# Yeet

## Role

Publish local work from a checkout. This skill composes bundled GitStack
skills, direct `git`, the shared CLI, and connector-backed PR operations:

- Use `$gitstack:git-commit` for staging and commit authoring.
- Use `<plugin-root>/scripts/gitstack publish preflight` for structured local
  readiness and `publish open --title-file --body-file` for new PRs. Use the
  connector for supported existing-PR lifecycle operations. Do not put PR
  title or body text in argv or a shell string.
- Use `$gitstack:github-issues`, `$gitstack:github-repository-triage`, `$gitstack:github-investigation`, `$gitstack:github-actions`,
  or `$gitstack:github-review-threads` only for focused follow-up GitHub work.

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md`. The CLI cannot invoke connector tools; it uses direct `git` and
authenticated `gh` for its preflight and fallback commands.

If there is no local work to publish, or the request is only GitHub issue
hygiene such as creating, commenting on, labeling, or closing issues, do not run
the full publish flow. Route that work to `$gitstack:github-issues`, perform the
authorized GitHub issue operation with resolved `mutation_mode=apply|dry-run`,
the exact repository and issue target, and one canonical `issue_operation`, and
state that full `yeet` was not applicable.

Prefer the shortest publish path that matches the state in front of you:

- If a good local commit already exists, reuse it instead of reopening commit
  authoring.
- If the branch already has a PR, update that PR instead of treating the run as
  a fresh publish. Preserve its current draft or ready state, then request a
  Codex review for the newly published head.
- If there is no publishable local change, stop early and route issue-only
  follow-up to `$gitstack:github-issues`.

## Workflow

1. Run the complete publish preflight before any push: require a named branch,
   reject the repository default branch, verify `gh` authentication, verify the
   `origin` repository and any configured upstream match the current branch,
   and look up an existing open PR for that branch.
2. Inspect worktree state and confirm the intended scope when it is mixed.
3. Reuse the current commit when it already represents the intended scope.
   Otherwise create one through `$gitstack:git-commit` with
   `commit_operation=commit-only`; Yeet retains ownership of push. Do not
   override Git Commit's `commit_kind` selection: it defaults to `regular` and
   may select a targeted fixup only from the explicit request or
   target-repository instructions with an exact target.
4. Rerun the complete publish preflight immediately before pushing. Use a
   normal push to the verified upstream, or `git push -u origin HEAD` only when
   no upstream exists. Never infer permission to force-push.
5. Re-check for an existing PR after push. Open a draft PR only when none
   exists; otherwise update the existing PR without changing its `isDraft`
   value. In particular, a ready PR must remain ready; never call a draft
   conversion or the draft-only creation path for an existing PR. After an
   ambiguous create failure, look up the PR again before retrying so a
   successful first request cannot create a duplicate.
6. For both a newly created PR and an existing PR, hand a current-head Codex
   review request to `$gitstack:github-review-threads` with the exact repository
   and PR, `provider=codex`, and the full published head SHA. Use
   `review_operation=request` with `mutation_mode=apply` and a fresh
   Yeet-owned request key for this logical publish invocation; preserve that
   key for reconciliation, then persist the complete typed request receipt.
   This request is part of Yeet's authorized publish flow; do not require a
   separate caller gate. Do not substitute an untyped PR comment.
7. Use one operation per invocation. Run
   `review_operation=wait` with the persisted complete receipt only when the
   user or composing caller also requested bounded review monitoring. Do not
   duplicate provider detection or polling inside Yeet.
8. Return branch, PR URL, commit hash, Codex review request status and receipt
   identity, and verification performed. If the review request fails after the
   push or PR mutation succeeded, preserve and report the successful publish
   evidence separately; do not repeat the push, PR creation, or review request
   blindly.

## References

- `references/workflows.md`: publish, existing-PR, and retry workflows.
- `../../references/options.md`: shared canonical GitStack options.
