# Code Wiki Maintenance

`skills/code-wiki/` owns the public `scripts/code-wiki` launcher and the
internal `scripts/code_wiki/` implementation. Runtime workflow and output
requirements remain in `SKILL.md` and its references.

## Owned surfaces

- `scripts/README.md` is the artifact-first command map; keep it aligned with
  the launcher and public command names.
- `scripts/code_wiki/version.py` owns the helper version used by
  `scripts/code-wiki --version`.
- `references/wiki-html-contract.md`, `references/repo-study-playbook.md`,
  and `references/image-guidance.md` own output and study contracts; do not
  duplicate their detailed rules here.
- `tests/` protects the launcher, validation reports, HTML contract, and
  evidence/link behavior.

## Maintenance contract

- Keep final wiki outputs outside `.cache`. Default clones and temporary
  analysis artifacts belong under `~/.cache/dotagents/skills/code-wiki/`;
  requested self-contained source storage belongs under the documented wiki
  output root with its ignore-all source cache.
- Preserve the Codex-dependent boundary and keep image generation and
  subagent use optional only where the runtime contract provides a fallback.

## Validation

- Run the focused unittest suite for runtime changes.
- Verify `scripts/code-wiki --help`, `--version`, and a disposable local
  inventory, scaffold, or validate fixture through the shipped launcher.
