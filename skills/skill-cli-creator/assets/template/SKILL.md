---
name: __SKILL__
description: __DESCRIPTION__
---

# __TITLE__

Run `scripts/__SKILL__ --json <command>` from the skill root. Read the
[CLI reference](references/cli.md) for every command and its JSON.

- Check readiness with `scripts/__SKILL__ --json doctor` only when a command
  fails or a dependency may be missing.

Rules:

- Use `--json` when reading the output.
- Report a failed command's `error.code` and `message`; do not guess around it.
