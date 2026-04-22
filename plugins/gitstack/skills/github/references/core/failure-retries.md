# GitHub failure retry matrix

Use this reference when a `gh` command or `ghflow` command fails and you want the
next retry command without re-deriving the fallback path.

- Runtime path errors (`ghflow`: no such file or directory):
  - Retry command:
    rerun the same command through the installed plugin path,
    `ghflow ...`, instead of assuming the current checkout
    owns the `gitstack` plugin files.
- Auth/session errors (`gh auth status` fails, 401/403 auth):
  - Retry command:
    `gh auth login && gh auth status`
- Repository context errors (not a git repo, cannot resolve repo):
  - Retry command: `gh repo view --json nameWithOwner` in the target repo
    directory, or `gh repo view owner/repo --json nameWithOwner` from
    elsewhere.
- Repository mismatch errors (current checkout does not match the target
  repository):
  - Retry command:
    rerun the same `ghflow ... --repo owner/repo` command from the
    correct repo root, or switch to raw `gh issue view`, `gh issue create`,
    `gh issue comment`, and `gh issue close` commands with explicit
    `--repo owner/repo` arguments for cross-repo issue transfers.
- Invalid JSON field errors (for example `Unknown JSON field: "projects"`):
  - Retry command: replace with supported fields, e.g.
    `gh issue view <n> --json number,title,state,projectItems,projectCards`.
- PR edit scope errors (`gh pr edit` fails with
  `missing required scopes [read:project]`):
  - Retry command:
    retry with plain `gh api`, for example
    `gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -f title=... -f body=... -f base=...`
    from the target repo root when the change is limited to
    title/body/base fields.
- Transient API/network failures (502/503/timeouts):
  - Retry command: re-run the same `gh ...` command after a short delay; keep
    scope unchanged.
