# OKF Maintenance

`skills/okf/` owns the reusable OKF writer and validator, its bundled local
specification assets, and the shipped `scripts/okf` artifact. Authoring and
validation behavior belongs in `SKILL.md` and `references/`.

## Owned surfaces

- `scripts/okf` is the only public executable. Its `VERSION` is the CLI version
  source of truth; `SPEC_VERSION` identifies the OKF contract and is separate.
- `assets/spec.md` and `assets/manifest.json` are the bundled specification
  inputs. Keep them synchronized when the approved local spec is refreshed.
- `references/` owns writing, examples, and validation guidance; `tests/` owns
  executable regression coverage.

## Validation

- For CLI changes, run the focused unittest suite and verify the shipped
  artifact with `--help`, `--version`, `--json doctor`, and a safe scaffold or
  validate fixture without network access.
- Official spec refreshes and their integrity checks are maintenance work; do
  not change bundled spec assets as an incidental runtime edit.
