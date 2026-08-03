---
name: github-investigation
description: Investigate a GitHub issue, pull request, or proposed fix using repository evidence. Use to understand behavior, find the root cause, evaluate whether a fix is sound, and identify remaining risk; use $g:github-review-threads for hosted review feedback.
---

# GitHub Investigation

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../references/network-execution.md).
Connector calls and local-only commands do not use shell escalation.

## Transport

Prefer the required GitHub connector for supported remote reads and writes. Use
`gh` for connector gaps. An authorized connector write may fall back
automatically only when the operation and repository are identical, `gh`
authentication and access succeed, and the transport switch is reported.

Before the first provider-facing direct `gh` or shared CLI fallback, load
[`../../references/gh-dependency-preflight.md`](../../references/gh-dependency-preflight.md)
and require its host and authentication checks.


## Role

Review a GitHub issue, pull request, bug report, or proposed fix when the user
needs an evidence-backed technical judgment rather than queue triage or review
thread replies.

Use this skill for questions like:

- `review this PR deeply`
- `is this issue real?`
- `what is the root cause?`
- `is this the best fix?`
- `did main already fix this?`
- `should we close this issue?`

Use `$g:github-repository-triage` for current-repo queue summaries, `$g:github-issues` for
authorized issue lifecycle changes, `$g:github-actions` for Actions failures, and
`$g:github-review-threads` for listing, drafting, or posting replies to PR review
threads.

## Start

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md` before invoking the shared CLI.

Prefer connector-backed PR or issue context plus local repo evidence over web
browsing. Use `gh` for connector gaps and local branch discovery:

```bash
gh issue view <number> --json number,title,state,author,body,comments,labels,updatedAt,url
gh pr view <number> --json number,title,state,author,body,comments,reviews,files,commits,statusCheckRollup,mergeStateStatus,headRefName,headRepositoryOwner,url
gh pr diff <number> --patch
git status --short --branch
git fetch origin
git log --oneline --decorate -20
```

When automated-review freshness is relevant, use the one-shot provider-neutral
check as evidence and keep analysis read-only:

```bash
<plugin-root>/scripts/g --json reviews check --provider codex --repo <owner/repo> --pr <number> --head <sha>
```

Route review work to `$g:github-review-threads` with the exact repository
and PR plus one operation per invocation: `review_operation=check|wait` for
read-only freshness, or `review_operation=reply|request|resolve` with
`mutation_mode=apply` only after the matching write is authorized. A Codex
`request` uses G's typed full-head/request-key operation and persists its
complete receipt before any wait; it has no legacy text fallback.

Read local instructions, issue workflows, test guidance, and maintainer runbooks
before deciding. If the repository is not checked out locally, clone or fetch it
only when the review requires code-path evidence that `gh` cannot provide.

## Review Contract

Always answer these points when they apply:

- URL/ref: issue or PR number and affected surface.
- Bug or behavior: what is being reported or changed.
- Cause: the real code path and confidence, or the exact missing evidence.
- Provenance: who or what introduced, exposed, or carried the behavior forward
  when bounded history can identify it.
- Fix quality: whether the proposed or likely fix belongs at the right
  ownership boundary.
- Refactor call: whether a slightly larger change would improve correctness,
  clarity, or future maintenance.
- Proof: tests, live repro, CI, docs, dependency source, or shipped/current
  behavior checked.
- Risk: what remains unverified or brittle.

Do not approve, comment, close, merge, push, or land unless the user explicitly
asks for that action. Route authorized GitHub issue comments, labels, type
changes, or closure through `$g:github-issues` after normalizing each
write to `mutation_mode=apply`, the exact repository and issue target, and one
canonical `issue_operation`.

## Code Reading Depth

Read beyond the first touched file. Follow the real path:

- entrypoint -> validation/parsing -> routing/dispatch -> owner module ->
  shared helper -> persistence/network/runtime boundary
- config/schema/docs -> runtime usage -> doctor/fix path
- provider/channel/plugin owner code -> generic core only when multiple owners
  need the same invariant
- tests around the touched surface plus adjacent regression tests

When behavior depends on a dependency, read the current package docs, source,
types, or installed metadata before assuming the contract.

Prefer current source and executable proof over issue comments. Treat stale
comments, old CI, and old release behavior as hints until rechecked.

## Provenance

For bug or regression reviews, include a compact provenance answer when feasible:

- Use `git log -S/-G`, `git blame`, linked PRs/issues, and tests.
- Separate original author, committer/merger, and current PR author when they
  differ.
- Phrase as `introduced by`, `made visible by`, or `carried forward by`.
- Include confidence: `clear`, `likely`, or `unknown`.
- For features, docs, refactors, or untraceable issues, write `N/A` or say what
  evidence is missing.

## Fix Quality Bar

Good fixes usually:

- live at the ownership boundary where the bug belongs;
- preserve public behavior unless the task is explicitly about changing it;
- add a regression test at the smallest meaningful seam;
- avoid broad special cases, hidden conversions, semantic sentinels, and
  provider/channel IDs in generic core;
- update docs or changelog when user-visible behavior changes;
- fail clearly in runtime paths and repair through doctor paths
  when that is the established contract.

Call out symptom-level fixes. Recommend a larger refactor only when it makes
the invariant clearer or materially reduces future bugs without widening risk.

## Output Shapes

For PR reviews, lead with findings ordered by severity. Each finding needs a
file/line/symbol reference and concrete failure mode. If there are no blocking
correctness issues, say that clearly and list the strongest proof plus residual
risk.

For issue reviews, reconstruct the reporter's scenario, check current `main`,
reproduce or build a minimal proof when feasible, then identify the root cause
and recommended disposition.

Use this compact shape for "what is this about", "is this the best fix", or
"what did we fix":

```text
Ref: #123 / PR #456
Surface: <runtime/CLI/provider/channel/docs>
Bug: <one or two sentences>
Cause: <code path + confidence>
Provenance: <introduced/made visible/carried forward by commit/PR/date, or N/A/unknown>
Best fix: <what should change and why>
refactor_disposition: <required|optional|not-required>
refactor_shape: <specific shape|not-applicable>
Proof: <tests/live/CI/source/dependency docs>
Risk: <remaining uncertainty>
```

Use the canonical invocation fields from `../../references/options.md` for
routed G operations. `refactor_disposition` is a judgment returned by
this skill, not an invocation option: derive it from the review evidence and do
not ask the user to select it. Keep the explanation of why a refactor is or is
not warranted in the surrounding prose.
