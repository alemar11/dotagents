# Yeet Workflows

## Publish New Work

```bash
git status --short --branch
git diff --stat
git add -- <explicit-paths>
git diff --staged
git commit -F <message-file>
git push -u origin HEAD
gh pr create --draft --fill
```

Use explicit pathspecs for staging. If the branch already has a PR, update that
PR instead of creating a duplicate.

## No Publishable Local Work

Use this branch when the user invokes `yeet` but the task is issue-only hygiene
or the checkout has no intended code/docs changes to publish.

```bash
git status --short --branch
gh auth status
gh issue list --state open --limit 50 --json number,title,state,url
```

If there are no relevant local changes to stage, do not create an empty commit,
branch, push, or PR. Route issue creation, comments, labels, or closure to
`github` or `github-triage`, then verify the result with `gh issue view` or
`gh issue list`.

Close out by saying explicitly:

- full `yeet` was not applicable because there was no publishable local change;
- which GitHub issue mutations were performed;
- current branch/worktree state;
- any untracked files intentionally left alone.

## Existing PR

```bash
gh pr status
gh pr view --json number,title,url,isDraft,headRefName,baseRefName
gh pr edit <number> --title "<title>" --body-file <body-file>
```

## Closeout

Return:

- branch name
- commit hash
- PR URL
- whether the PR is draft or ready
- validation performed before publishing

If CI fails or review comments need follow-up, route to `github-ci` or
`github-reviews` after the publish step.
