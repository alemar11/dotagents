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
  and `references/image-guidance.md` own the output and study contracts; do not
  duplicate their detailed rules in this file.
- `tests/` protects the launcher, validation reports, HTML contract, and
  evidence/link behavior.

## Validation

- For runtime changes, run the focused unittest suite and verify
  `scripts/code-wiki --help`, `--version`, and a disposable local inventory,
  scaffold, or validate fixture through the shipped launcher.
- Keep generated wiki outputs and source caches outside the skill package's
  tracked runtime surfaces unless a user explicitly requests self-contained
  source storage under the documented output root.
