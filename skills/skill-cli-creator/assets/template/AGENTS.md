# __TITLE__ Maintenance

`skills/__SKILL__/` owns the shipped `scripts/__SKILL__` artifact, its
reference in `references/cli.md`, and its tests.

- `VERSION` in `scripts/__SKILL__` is the CLI version source of truth. Major
  for a breaking change to commands, JSON, or exit codes, minor for a
  compatible capability, patch for a fix.
- Validate CLI changes from the skill root with
  `python3 -m unittest discover -s tests`, `scripts/__SKILL__ --help`,
  `--version`, `--json doctor`, and
  `../skill-cli-creator/scripts/skill-cli-creator --json check .`.
