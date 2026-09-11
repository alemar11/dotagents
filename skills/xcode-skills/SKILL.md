---
name: xcode-skills
description: Install or update Xcode's embedded agent skills in a target repository for Codex.
---

# Xcode Skills

Export the selected Xcode installation's embedded skills into the target
repository's `.agents/skills/`. Invocation authorizes installing missing skills
and updating existing Xcode exports there. Respect an explicitly requested
repository or destination; otherwise resolve the current repository root.

## Export and update

Confirm macOS, the target repository, and the selected Xcode with
`xcodebuild -version` and `xcode-select -p`. Inspect
`xcrun agent skills export --help` before exporting; use its supported syntax.
If the user selects another Xcode, scope `DEVELOPER_DIR` to each Xcode command
without changing global selection. If export is unavailable, report the
selected Xcode and the failure rather than substituting downloaded skills.

The commands are:

```sh
# Default export into ./xcode-skills (not Codex's repository discovery path).
xcrun agent skills export

# Install into the target repository; replace /absolute/path/to/repo.
xcrun agent skills export --output-dir /absolute/path/to/repo/.agents/skills

# Refresh existing exported skill directories.
xcrun agent skills export --replace-existing --output-dir /absolute/path/to/repo/.agents/skills
```

Quote paths containing spaces. The destination requires `--output-dir`, not a
positional argument. Xcode may need to launch for export; a launch failure is
not proof the command is unsupported. Resolve an execution-permission failure
through the available approval mechanism, then retry the same scoped export.

First export into a fresh temporary directory to discover the current skill
names and inspect the payload before replacing repository content. Do not
hardcode the bundled skill list. Compare those names with the destination:
install absent entries and update identifiable prior Xcode exports. Preserve
unrelated skills, and ask about same-name custom skills or locally modified
exports whose replacement is not already authorized. Do not follow destination
symlinks outside the target repository. Where some entries conflict, install
or update the unaffected entries from the temporary export and report the
remaining conflicts; do not run blanket replacement over them.

Use `--replace-existing` against the target only after checking all colliding
entries. Do not delete skills missing from a newer export without a separate
removal request. Keep Apple's exported names and content intact; do not add
Codex metadata to or rewrite the exported skills. This operation does not
configure MCP, enable headless access, install user-global skills, or commit.

## Verify

Check that each installed skill has a readable `SKILL.md` and that its full
file tree matches the temporary export. Inspect the scoped repository diff
and confirm unrelated skills remain intact. Report the selected Xcode,
absolute destination, installed or updated names, and any skipped conflicts
or failures. File installation alone does not prove the current Codex task
has reloaded discovery; verify visibility separately if requested.
