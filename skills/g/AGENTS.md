# G Skill Maintenance

This reusable skill is the repository's sole G package. Keep its runtime,
maintenance source, metadata, and installation surfaces self-contained under
`skills/g`.

## Owned surfaces

- `SKILL.md` owns selection, routing, shared safety rules, and the immediate
  result contract.
- `references/states.md` is the sole canonical state registry. Workflow
  references may link to its namespace headings but must not recreate local
  state registries.
- `references/workflows/<name>/` owns branch-specific runtime detail migrated
  from the corresponding bundled plugin skill.
- `scripts/g` is the shipped runtime. `projects/g/` is its complete
  maintenance-only CLI project; normal skill execution never imports or runs
  modules from the project tree.
- Root-level helper scripts, assets, and tests are owned by their routed
  workflows and remain separate from the shared CLI project.

## CLI lifecycle

- `projects/g/pyproject.toml` is the standalone CLI version source of truth.
  Keep `src/g/__init__.py`, version assertions, and the rebuilt `scripts/g`
  artifact aligned with it; do not align it with the plugin manifest.
- Scope persisted recovery data under `~/.cache/dotagents/skills/g/`.
- Any CLI behavior change requires a semantic version update, the project test
  suite, a rebuilt artifact, and shipped-artifact smoke checks.
- Run `projects/g/scripts/build-artifact` from the skill checkout. Do not add a
  plugin installation or cache-refresh helper to this project.

## Validation

- Validate the package with the skill-creator validator.
- Run `python3 -m unittest discover -s tests -v` from `projects/g/` and from
  the skill root.
- Verify `scripts/g --help`, `--version`, `--json doctor`, and
  `--json stack ensure`; keep smoke checks read-only.
- Verify all local Markdown links and run `git diff --check` before handoff.
