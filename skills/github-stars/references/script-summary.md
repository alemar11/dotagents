# Star-list Membership Helper

Complete the skill host and authentication checks before the first membership helper call. Invoke only:

```bash
<skill-root>/scripts/stars --json lists assign <list-id> <owner/repo>
<skill-root>/scripts/stars --json lists unassign <list-id> <owner/repo>
```

Use `--list <exact-slug-or-name>` instead of the positional ID when necessary.
Batch targets use repeated `--repo` or a newline-delimited `--repos-file`.
`--dry-run` performs reads and reports intended changes without mutations.
Use `stars lists assign --help` for available flags.

The helper preserves existing unrelated memberships and refuses to assign an
unstarred repository. It does not star repositories or delete lists. JSON mode
uses the shared success/error envelope; inspect each target's result and failure
count even when other targets succeeded. Read [states](states.md) to interpret
helper results. Follow the workflow's independent
readback requirement before reporting completion.
