# GitHub project triage

Use this runbook for maintainer-facing triage of a GitHub repository's open
issues and pull requests. Keep it current-repo first and no-RepoBar: use direct
`gh` commands, not owner/org queue discovery helpers.

## Scope

- Default to the current GitHub checkout when the user says `triage`.
- Support an explicit `owner/repo` when the user names one.
- Do not broaden to all repos, owners, orgs, forks, or archived queues in this
  v1 workflow.
- This workflow is report-only. Do not implement, merge, close, rerun checks,
  comment, or mutate labels unless the user explicitly asks for that next step.
- Do not require a clean `main` branch or run `git pull` for read-only triage.
  If local branch or dirty state matters, report it as context only.

## Resolve The Repository

From a local checkout, prefer GitHub CLI's repo context:

```bash
repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || true)
if [ -z "$repo" ]; then
  url=$(git remote get-url origin 2>/dev/null || true)
  repo=$(printf '%s\n' "$url" |
    sed -E 's#^git@github.com:##; s#^https://github.com/##; s#\.git$##')
fi
printf '%s\n' "$repo"
```

If the user provided `owner/repo`, use that exact repo and do not infer a
broader owner scope.

## Initial Queue Scan

Start every current-repo triage report by scanning both open issues and open
PRs:

```bash
gh issue list --repo "$repo" --state open --limit 50 \
  --json number,title,author,labels,createdAt,updatedAt,url
gh pr list --repo "$repo" --state open --limit 50 \
  --json number,title,author,isDraft,reviewDecision,mergeStateStatus,createdAt,updatedAt,url
```

For small queues of about 10 open items or fewer, inspect every item. For larger
queues, inspect the priority slice that can be explained responsibly and state
how many issues or PRs were not expanded.

## Detail Reads

Inspect enough detail to explain every surfaced item:

```bash
gh issue view <number> --repo "$repo" \
  --json number,title,author,body,comments,labels,createdAt,updatedAt,url
gh pr view <number> --repo "$repo" \
  --json number,title,author,body,comments,files,commits,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup,createdAt,updatedAt,url
gh pr diff <number> --repo "$repo" --patch
```

Use `github-ci` or `<resolved-ghflow> ci inspect` only when a failing PR check
needs deeper log extraction. Keep ordinary PR status reads on `gh pr view` or
`gh pr checks`.

Treat clear maintainer or owner comments as authoritative routing input. If
there is no clear owner signal, say that the judgment is based on the evidence
inspected in the queue.

## Classification

Return these sections:

- `Autonomous candidates`: items that appear fixable, reviewable, or landable
  without more product input. This is a report-only candidate list, not
  permission to start work.
- `Needs owner`: items blocked on product direction, missing credentials,
  live-provider proof, security/privacy judgment, unclear maintainer intent, or
  other human decision.
- `Defer/close/supersede`: stale, duplicate, lower-quality, already-addressed,
  or overlapping items where likely action is not new code.

For each surfaced item, include:

- URL in the first line for the item.
- `What`: one plain-language sentence.
- `Type/Fit/Risk`: bug, feature, dependency, security, docs, or internal;
  good, mixed, or poor fit; low, medium, or high risk with one reason.
- `Trust`: factual author signal only, such as maintainer, bot, known
  contributor from visible repo activity, or unknown. Do not treat trust as
  proof.
- `Proof`: CI, repro, failing test, local source evidence, live proof, or
  missing proof.
- `Blocker`: none, missing key, failing check, unclear direction, stale branch,
  conflicts, no repro, or similar.
- `Next`: exact maintainer action, such as run tests, request repro, approve CI,
  ask owner, review diff, patch locally, close with evidence, or defer.

## Output Shape

Use this shape for current-repo triage:

```text
Repo: owner/name
Source: gh issue/pr list, gh issue/pr view, gh pr diff/checks where inspected

Autonomous candidates:
- https://github.com/owner/name/pull/123
  What: ...
  Type/Fit/Risk: bug; good; low because ...
  Trust: @login; bot/maintainer/known contributor/unknown based on visible repo activity.
  Proof: ...
  Blocker: ...
  Next: ...

Needs owner:
- https://github.com/owner/name/issues/124
  What: ...
  Type/Fit/Risk: ...
  Trust: ...
  Proof: ...
  Blocker: ...
  Next: ...

Defer/close/supersede:
- https://github.com/owner/name/issues/125
  What: ...
  Type/Fit/Risk: ...
  Trust: ...
  Proof: ...
  Blocker: ...
  Next: ...

Skipped:
- N older issues and M PRs were not expanded because ...
```

When the user asks for follow-up action after a report, route to the right
GitStack skill for that action: `github-ci` for failing checks, `github-reviews`
for review threads, `yeet` for local publish, or umbrella `github` for mixed
GitHub lifecycle work.
