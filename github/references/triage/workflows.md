# GitHub triage workflows

Use this reference for triage-domain GitHub flows inside the consolidated
`github` skill.

## stars-manage

Purpose: list, star, and unstar repositories for the authenticated GitHub user.

### Operator policy

- Treat stars as authenticated-user scope, not repository-scope mutations.
- Allow non-project execution; explicit `owner/repo` targets are required for writes.
- Keep batch star and unstar runs best-effort and report per-repo outcomes.

### Preferred helper

```bash
scripts/triage/stars_manage.sh --list-stars [--by-list <slug-or-name>|--list-id <id>] [--limit N|--all] [--json]
scripts/triage/stars_manage.sh --star|--unstar [--repo <owner/repo>]... [--repos-file <path>] [--dry-run] [--json]
```

## star-lists-manage

Purpose: inspect, create, delete, and manage membership for GitHub star lists.

### Operator policy

- Treat star lists as authenticated-user scope and allow non-project execution.
- Resolve `--list` by exact slug first, then exact name; require `--list-id` when the selector is ambiguous.
- Use read-modify-write list membership updates so unrelated list memberships stay intact.
- Keep batch assign and unassign runs best-effort and report per-repo outcomes.

### Preferred helper

```bash
scripts/triage/lists_manage.sh --list-lists [--limit N|--all] [--json]
scripts/triage/lists_manage.sh --list-items [--list <slug-or-name>|--list-id <id>] [--limit N|--all] [--json]
scripts/triage/lists_manage.sh --create --name <text> [--description <text>] [--private|--public] [--dry-run] [--json]
scripts/triage/lists_manage.sh --delete [--list <slug-or-name>|--list-id <id>] [--dry-run] [--json]
scripts/triage/lists_manage.sh --assign|--unassign [--list <slug-or-name>|--list-id <id>] [--repo <owner/repo>]... [--repos-file <path>] [--dry-run] [--json]
```

## pr-update-metadata

Purpose: update PR title, body, or base without getting blocked by the recent
`gh pr edit` project-scope read behavior.

### Operator policy

- Prefer `scripts/triage/prs_update.sh` over ad-hoc `gh pr edit`.
- If `gh pr edit` fails with `missing required scopes [read:project]`, the
  helper retries through `gh api` for title/body/base-only updates.
- Run `scripts/core/preflight_gh.sh --expect-repo <owner/repo>` from the target repo
  root before mutation.

### Preferred helper

```bash
scripts/triage/prs_update.sh --pr <number> [--title <text>] [--body <text>] [--base <branch>] [--repo <owner/repo>]
```

## issue-copy-or-move

Purpose: continue issue work in another repository without losing source
context.

### Operator policy

- Choose copy when the source issue should stay open.
- Choose move when work should continue only in the target repository.
- Use `references/triage/issue-workflows.md` for move-note shape and
  source-close behavior.

### Preferred helpers

```bash
scripts/triage/issues_copy.sh --issue <number> --source-repo <owner/repo> --target-repo <owner/repo> [--dry-run]
scripts/triage/issues_move.sh --issue <number> --source-repo <owner/repo> --target-repo <owner/repo> [--dry-run]
```

## issue-close-with-evidence

Purpose: close an issue with traceable implementation evidence.

### Operator policy

- Verify the issue is still open before mutation.
- Add the evidence comment before closing the issue.
- Prefer commit and PR links together when both exist.

### Preferred helper

```bash
scripts/triage/issues_close_with_evidence.sh --issue <number> --commit-sha <sha> [--commit-url <url>] [--pr-url <url>] [--repo <owner/repo>] [--dry-run]
```

## pr-patch-inspect

Purpose: inspect PR changed files or a file-specific patch without leaving the
umbrella triage path.

### Operator policy

- Prefer `scripts/triage/prs_patch_inspect.sh` over ad-hoc pull-request file API
  calls.
- Use `--path` when the user only cares about one file.

### Preferred helper

```bash
scripts/triage/prs_patch_inspect.sh --pr <number> [--repo <owner/repo>] [--path <file>] [--include-patch] [--json]
```

## reactions-manage

Purpose: list or mutate reactions on PRs, issues, issue comments, or PR review
comments.

### Operator policy

- Keep reactions in the umbrella, including PR review comment reactions.
- Use `--dry-run` before writes when the user wants a preview.

### Preferred helper

```bash
scripts/triage/reactions_manage.sh --resource pr|issue|issue-comment|pr-review-comment --repo <owner/repo> [--number <n>|--comment-id <id>] [--list|--add <reaction>|--remove <reaction-id>] [--dry-run]
```

## issue-create-label-suggestions

Purpose: suggest labels for a new issue before creation.

### Operator policy

- Suggest existing repo labels first.
- Only create fallback reusable labels when explicitly enabled.
- Treat suggestion output as informational until the user confirms selection.

### Preferred helper

```bash
scripts/triage/issues_suggest_labels.sh --repo <owner/repo> --title <text> [--body <text>] [--max-suggestions N] [--min-score <float>] [--allow-new-label] [--new-label-color <rrggbb>] [--new-label-description <text>] [--json]
```

## commit-with-issue-close

Purpose: preview or execute commit wording that closes an issue with a close
token when that intent is clear.

### Operator policy

- Default to preview with `--dry-run`.
- Preserve an existing close token when one is already present.
- Surface ambiguity instead of guessing when multiple issue candidates appear.

### Preferred helper

```bash
scripts/triage/commit_issue_linker.sh --message <text> [--context <text>] [--branch <name>] [--repo <path|owner/repo>] [--issue-number <number>] [--token <fixes|closes|resolves>] [--dry-run|--execute] [--json]
```
