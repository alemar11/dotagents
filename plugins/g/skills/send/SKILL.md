---
name: send
description: Send local work to GitHub. Use when the user explicitly requests the complete flow to confirm scope, commit, push the branch, include caller-provided resolved issue references for automatic closure, and open or update one pull request without changing its draft state.
---

# Send

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../references/network-execution.md).
Connector calls and local-only commands do not use shell escalation.

## Role

Publish local work from a checkout. This skill composes bundled G
skills, direct `git`, the shared CLI, and connector-backed PR operations:

- Use `$g:git-commit` for staging and commit authoring.
- Use `<plugin-root>/scripts/g publish preflight` for structured local
  readiness and `publish open --title-file --body-file` for new PRs. Use the
  connector for supported existing-PR lifecycle operations. Do not put PR
  title or body text in argv or a shell string.
- When the publish path is selected, load
  [`../../references/gh-dependency-preflight.md`](../../references/gh-dependency-preflight.md)
  before the first `gh`-dependent command. The shared reference owns the
  `gh` availability and authentication checks; stack-specific readiness belongs
  to `$g:github-stack`.
- Use `$g:github-issues`, `$g:github-repository-triage`, `$g:github-investigation`, `$g:github-actions`,
  or `$g:github-review-threads` only for focused follow-up GitHub work.

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md`. The CLI cannot invoke connector tools; it uses direct `git` and
authenticated `gh` for its preflight and fallback commands.

If there is no local work to publish, or the request is only GitHub issue
hygiene such as creating, commenting on, labeling, or closing issues, do not run
the full publish flow. Route that work to `$g:github-issues`, perform the
authorized GitHub issue operation with resolved `mutation_mode=apply|dry-run`,
the exact repository and issue target, and one canonical `issue_operation`, and
state that full `send` was not applicable.

Prefer the shortest publish path that matches the state in front of you:

- If a good local commit already exists, reuse it instead of reopening commit
  authoring.
- If the branch already has a PR, update that PR instead of treating the run as
  a fresh publish. Preserve its current draft or ready state and return the
  exact publication read-back.
- If a target base is explicitly supplied, publish or update the current PR
  against that exact branch. Whether that base participates in a stack is a
  separate `$g:github-stack` concern.
- If there is no publishable local change, stop early and route issue-only
  follow-up to `$g:github-issues`.

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

Send does not infer, verify, link, or manage a stack. A caller that needs a
parent/child relationship invokes `$g:github-stack` separately after Send's
publication receipt. Do not use `stack submit` as a Send fallback.

## Issue Linkage Contract

Accept `closing_issue_refs` as caller-owned factual input: the exact GitHub
issues whose accepted scope is fully satisfied by this PR. Validate every
candidate against its exact GitHub repository and issue before PR mutation.
Send must not derive an issue from a bare number, branch name, commit subject,
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

The selected PR base does not change this validation. Send carries the exact
caller-provided issue set to the PR body and verifies the resulting body and
provider references; it does not decide whether the current delivery topology
will make GitHub close those issues or mutate an issue directly. A composing
workflow such as Implement owns the standalone/stacked interpretation and any
separate post-publication delivery verification.

When no issue is confirmed, omit `## Issues` rather than inventing a placeholder
or asking merely to fill the section. Report the empty linkage result in the
closeout. See `references/workflows.md` for body construction and verification.

## Workflow

1. Run the complete publish preflight before any push: require a named branch,
   reject the repository default branch, verify `gh` authentication, verify the
   `origin` repository and any configured upstream match the current branch,
   and look up an existing open PR for that branch. The shared network execution
   contract applies to the complete GitHub-dependent preflight from the outset.
2. Resolve the intended base using **Base Selection And Existing PR Reuse**.
   Capture the existing PR's exact base when reusing it; stop on explicit-base
   drift and repeat the base read-back after the commit/preflight boundary.
3. Inspect worktree state and confirm the intended scope when it is mixed.
4. Receive and validate the caller's exact `closing_issue_refs`. Read an
   existing PR body when present, preserve its valid closing references, and
   prepare the complete template-aware PR body. Do not impose a default-base
   requirement in Send.
5. Reuse the current commit when it already represents the intended scope.
   Otherwise create one through `$g:git-commit` with
   `commit_operation=commit-only`; Send retains ownership of push. Do not
   override Git Commit's `commit_kind` selection: it defaults to `regular` and
   may select a targeted fixup only from the explicit request or
   target-repository instructions with an exact target.
6. Rerun the complete publish preflight immediately before pushing and repeat
   the existing-PR/base read-back. The selected base must still agree with the
   explicit target or preserved existing PR; otherwise stop and reconcile the
   changed remote state. Use a normal push to the verified upstream, or `git push
   -u origin HEAD` only when no upstream exists. Never infer permission to
   force-push.
7. Re-check for an existing PR after push. Open a draft PR only when none
   exists; otherwise update the existing PR without changing its `isDraft`
   value. In particular, a ready PR must remain ready; never call a draft
   conversion or the draft-only creation path for an existing PR. After an
   ambiguous create failure, look up the PR again before retrying so a
   successful first request cannot create a duplicate. Read back the PR body
   and require the exact canonical `Closes` line for every resolved
   `closing_issue_ref`. Preserve the existing PR's base and draft state; never
   retarget it implicitly.
8. Stop after publication and its read-backs. Send must not request or wait for
   an automated Codex review. If a composing workflow needs one, it must invoke
   `$g:github-review-threads` as a separate operation using the exact repository,
   PR, and full published head SHA from Send's publication evidence. The ready
   transition and any automatic provider review remain outside Send.
9. Return branch, PR URL, commit hash, PR base, canonical
   `closing_issue_refs`, issue-linkage verification, exact published head,
   draft-state read-back, and verification performed. If post-publication
   verification fails after the push or PR mutation succeeded, preserve and
   report the successful publish evidence separately; do not repeat the push or
   PR creation blindly.

## References

- `references/workflows.md`: publish, existing-PR, and retry workflows.
- `../../references/options.md`: shared canonical G options.
