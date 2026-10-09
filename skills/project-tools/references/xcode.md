# Xcode

For requested skill installation or updates, export the selected Xcode
installation's embedded skills into the target repository. Choose the directory
from the [client destinations](../SKILL.md#clients): `.agents/skills/` for
Codex, Cursor, and Pi; `.claude/skills/` for Claude Code. Respect an explicitly
requested project-local destination; otherwise resolve the current repository
root. A request for MCP setup alone does not authorize skill export.

For requested project-local MCP configuration, read
[xcode-configuration.md](xcode-configuration.md). Follow both workflows when both are requested;
a failure in one does not prevent independent work in the other.

## Export and update

Confirm macOS, the target repository, and the selected Xcode with
`xcodebuild -version` and `xcode-select -p`. Inspect
`xcrun agent skills export --help` before exporting; use its supported syntax.
If the user selects another Xcode, scope `DEVELOPER_DIR` to each Xcode command
without changing global selection. If export is unavailable, report the
selected Xcode and the failure rather than substituting downloaded skills.

The commands are:

```sh
# Codex, Cursor, or Pi; replace /absolute/path/to/repo.
xcrun agent skills export --output-dir /absolute/path/to/repo/.agents/skills

# Claude Code.
xcrun agent skills export --output-dir /absolute/path/to/repo/.claude/skills

# Refresh existing exported skill directories.
xcrun agent skills export --replace-existing --output-dir /absolute/path/to/repo/.agents/skills
```

Run only the commands for the requested destinations. Apply `--replace-existing`
to either destination only after the collision checks below. For multiple
clients, reuse one temporary export and reconcile each distinct destination;
do not export three copies for clients sharing `.agents/skills/`.

Quote paths containing spaces. The destination requires `--output-dir`, not a
positional argument. The export command may launch Xcode internally; a launch
failure is not proof the command is unsupported. If host permissions or Xcode
onboarding prevent export, report the prerequisite and leave host setup unchanged.

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
or failures. File installation alone does not prove the active client has
reloaded discovery; verify visibility separately if requested. In Pi, use
`/reload` and inspect skill discovery without executing the installed workflows.

## Client discovery sources

- [Cursor skill directories](https://cursor.com/docs/skills)
- [Pi skills](https://pi.dev/docs/latest/skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
