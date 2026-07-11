# GitHub Review Workflows

## List Review Context

Resolve `<plugin-root>` as two directories above the directory containing the owning
`SKILL.md` before using these commands.

```bash
<plugin-root>/scripts/gitstack reviews address --repo <owner/repo> --pr <number>
<plugin-root>/scripts/gitstack --json reviews address --repo <owner/repo> --pr <number>
```

By default, resolved or outdated review threads are omitted. Add
`--include-resolved` only when the user asks for full history.

## Reply To Selected Comments

First list comments, then reply by displayed selection or comment id:

```bash
<plugin-root>/scripts/gitstack reviews address --repo <owner/repo> --pr <number> --selection "1 3" --reply-body-file <message-file> --dry-run
<plugin-root>/scripts/gitstack reviews address --repo <owner/repo> --pr <number> --comment-ids "123456" --reply-body-file <message-file>
```

Write reply text to a UTF-8 file outside the repository. Do not interpolate
arbitrary comment text into `--reply-body` in a shell command. Remove temporary
message files after the action is verified.

Use `--dry-run` for batch replies unless the user already approved posting or a
calling skill assignment names the exact PR, selected comments, reply body, and
posting authority.

## Post Top-Level PR Discussion Comments

Use the helper for normal PR discussion comments, including simple review
requests:

```bash
<plugin-root>/scripts/gitstack reviews comment --repo <owner/repo> --pr <number> --body-file <message-file> --dry-run
<plugin-root>/scripts/gitstack reviews comment --repo <owner/repo> --pr <number> --body-file <message-file>
```

Use `--dry-run` unless the user explicitly asked to post the discussion comment
or a calling skill assignment names the exact PR, comment body, and posting
authority. `$codex-orchestrator` may use resolved
`publication_authority=prd-backed-merge-ready-pr` or
`publication_authority=explicit-owner-authorization` with those actions named
to post the top-level `@codex review` request and any required root-supplied PR
discussion disposition for that assigned PR.

## Fallback Direct Commands

Use direct `gh` only when `<plugin-root>/scripts/gitstack reviews` is unavailable, broken, or lacks the
needed operation. State the fallback reason in the response.

```bash
gh pr comment <number> --repo <owner/repo> --body-file <message-file>
gh pr view <number> --repo <owner/repo> --comments
```
