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
