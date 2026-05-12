# ghflow resolution

Use this before running any GitStack `ghflow` helper command.

`ghflow` is an embedded GitStack plugin artifact, not a required host binary.
Do not assume the bare `ghflow` command exists on `PATH`, and do not treat a
missing bare command as noteworthy by itself. Resolve the installed artifact
first, then run that path directly.

## Normal runtime

From any consuming repository, resolve the installed GitStack artifact:

```bash
resolved_ghflow="$(
python3 - <<'PY'
from pathlib import Path
import re

cache = Path.home() / ".codex" / "plugins" / "cache"
semver = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")
candidates = []
for path in cache.glob("*/gitstack/*/scripts/ghflow"):
    match = semver.match(path.parent.parent.name)
    if match and path.is_file():
        candidates.append((tuple(int(part) for part in match.groups()), str(path)))
if candidates:
    print(max(candidates)[1])
PY
)"
test -n "$resolved_ghflow" && test -x "$resolved_ghflow"
"$resolved_ghflow" --version
```

Use `"$resolved_ghflow" ...` for commands shown elsewhere as
`<resolved-ghflow> ...`.

## Maintenance runtime

When maintaining this plugin from the GitStack source checkout, verify the
workspace artifact directly:

```bash
plugins/gitstack/scripts/ghflow --version
plugins/gitstack/scripts/ghflow --help
```

Do this only for source-tree maintenance and release checks. Normal GitStack
usage in another repository should use the installed artifact resolved above.

## Failure boundary

- Missing bare `ghflow`: expected in embedded-host usage; resolve the installed
  artifact and continue.
- Missing installed artifact: broken GitStack install or plugin exposure drift;
  stop before mutating GitHub state.
- Present but non-executable artifact: broken installed artifact; stop and
  repair or reinstall GitStack before continuing.
