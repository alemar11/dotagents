# Git Commit Workflows

## Fast Path

Use when changes are tiny, cohesive, and low risk:

```bash
git status --short --branch
git diff -- <path>
git add -- <path>
git diff --staged --stat
git diff --staged
git commit -F "$message_file"
git status --short --branch
git log -1 --pretty=fuller
```

## Safe Path

Use when the worktree is mixed, generated files are present, or validation
matters:

```bash
git status --short --branch
git diff --stat
git diff -- <path>
git add -- <explicit-paths>
git diff --staged --stat
git diff --staged
```

Do not commit if staged files and the commit message describe different work.

## Split Commits

Default to splitting when changes touch unrelated top-level roots or mix
independent concerns. Stage and verify one commit at a time.

## Issue-Closing Push-Only

Use when the owner explicitly authorizes committing directly to the current
branch, pushing, and closing GitHub issues through commit trailers instead of a
PR.

```bash
git status --short --branch
git diff --stat
git diff -- <explicit-paths>
git add -- <explicit-paths>
git diff --staged --stat
git diff --staged
git commit -F "$message_file"
git log -1 --pretty=fuller
git push
gh issue list --state open --limit 50 --json number,title,state,url
```

The commit message should use a concise imperative subject and include trailers
for only the issues actually satisfied by the staged diff:

```text
Implement workflow persistence API

Summary:
- Add persisted workflow storage and FE/AI read endpoints.
- Cover projection and validation behavior with backend tests.

Validation:
- npm test
- npm run build
- npm run lint

Closes #11
```

Do not add `Closes #N` for deferred or partially satisfied work. If the owner
asked to close a partial issue, route issue follow-up handling to
`github-triage` before committing or closing.
