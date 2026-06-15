# GitHub Failure Retries

## Missing Tools

- Missing `git`: install Git before repository operations.
- Missing `gh`: install GitHub CLI and rerun `gh auth status`.

## Authentication

For `401`, `403`, or auth-scope errors, run:

```bash
gh auth status
gh auth refresh
```

If a PR metadata edit fails because of project scopes and the change is only
title/body/base, prefer a narrow REST call:

```bash
gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -f title="<title>"
```

## Repository Context

When a command cannot infer the repository, pass `--repo <owner/repo>` or run
from a checkout with a valid `origin` remote.
