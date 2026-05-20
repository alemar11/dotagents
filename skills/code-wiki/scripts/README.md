# code-wiki Helper Scripts

`scripts/code-wiki` is the only public executable surface for this skill.

The `scripts/code_wiki/` package is shipped internal runtime code used by that
launcher. Skill docs, tests, and examples should call `scripts/code-wiki ...`
instead of running Python module files directly.

Public commands:

- `scripts/code-wiki --version`
- `scripts/code-wiki inventory --repo <repo-path> --out <wiki-out>/data/inventory.json`
- `scripts/code-wiki scaffold --out <wiki-out> --title <repo-name>`
- `scripts/code-wiki evidence-link --repo <repo-path> --evidence <path:start-end> [--html]`
- `scripts/code-wiki validate --wiki <wiki-out>`

