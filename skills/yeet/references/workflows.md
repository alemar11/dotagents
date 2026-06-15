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
