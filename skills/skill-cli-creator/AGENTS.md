# Skill CLI Creator Maintenance

`skills/skill-cli-creator/` owns the skill CLI standard
(`references/standard.md`), the template in `assets/template/`, and the shipped
`scripts/skill-cli-creator` that creates and checks skills.

- The standard has one owner, `references/standard.md`. The template, the
  `check` command, and `references/cli.md` follow it; change them together.
- `VERSION` in `scripts/skill-cli-creator` is the CLI version source of truth.
  A stricter `check` that fails skills which passed before is a major change.
- Validate with `python3 -m unittest discover -s tests`, the artifact's
  `--help`, `--version`, `--json doctor`, and `--json check .`. The tests
  create a skill from the template and check it.
