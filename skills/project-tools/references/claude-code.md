# Claude Code shared skill directory

Use this procedure when Claude Code is the current or requested client.
Installed skill files remain in the canonical `.agents/skills/` directory;
Claude discovers them through `.claude/skills`. Reuse already-installed skills
when only adding Claude support; do not re-download or export them.

## Create or reconcile the link

Inspect `.agents`, `.agents/skills`, `.claude`, and `.claude/skills` before
writing. Resolve their paths and reject links outside the repository. If the
destination is absent (neither a file nor a symlink), run from the repository root:

```sh
mkdir -p .agents/skills .claude
ln -s ../.agents/skills .claude/skills
```

If the existing link already resolves to the canonical directory, keep it.
Never use force-link replacement over an existing path. For an existing real
`.claude/skills` directory, reconcile its entries into `.agents/skills`:
move non-conflicting entries, preserve their full contents, and consolidate
identical duplicates only after comparison. For differing same-name entries or
an unexpected link, preserve both and resolve ownership before replacing
anything. Remove only the emptied old directory, then create the link. Report
unresolved collisions while completing unaffected requested work.

## Verify

Verify that `.claude/skills` is a symlink resolving to this repository's
`.agents/skills`, with the same readable skill trees. Re-running setup must
reuse that link and the installed skills. MCP configuration remains in each
client's own configuration files. Dependency-loaded skills such as TanStack
Intent stay with their packages; do not copy them into a second catalog merely
to create the link.
