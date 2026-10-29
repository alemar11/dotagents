---
name: skill-cli-creator
description: Create a skill that ships a CLI, refactor a skill's CLI, or check one against the shared skill CLI standard. Use when a skill or plugin needs a command-line tool, or when its CLI is added, changed, or reviewed.
---

# Skill CLI Creator

Every skill that ships a CLI follows one [standard](references/standard.md):
the same layout, `scripts/<skill>` as the only artifact, and the same
`--version`, `--json`, `doctor`, error, and exit-code contract. Read it before
writing or changing a skill CLI.

Run the tool from this skill's root; [CLI reference](references/cli.md) has
every option.

- New skill: `scripts/skill-cli-creator --json new <name> --into <skills-dir> --description "<what and when>"`,
  then replace the template's placeholder command with the real ones and fill
  `SKILL.md`, `references/cli.md`, and `agents/openai.yaml`. For the parts of a
  skill unrelated to its CLI (description, splitting references), follow the
  skill-creator skill when it is available.
- Existing skill: evolve its current artifact rather than adding a second one.
  Move a differently named script to `scripts/<skill>` and keep the flags its
  callers rely on.
- Before handing off: `scripts/skill-cli-creator --json check <skill-dir>` must
  pass, plus the skill's own tests.

Read [command design](references/command-design.md) when choosing commands,
and [compiled](references/compiled.md) only for a build project, multi-platform
binaries, persisted config, a cache, or a CLI inside a plugin.
