# GitStack CLI Maintenance

This project is maintenance-only source for the plugin-shared `scripts/gitstack` artifact. Normal skill execution must run the shipped artifact from the plugin root and must not execute modules from `projects/gitstack/`.

## Runtime and boundaries

- Requires Python 3.11 or newer and uses only the standard library.
- Uses direct `git` for local repository state and `gh` for GitHub operations unavailable through the model-facing connector.
- The subprocess cannot invoke connector tools or access the GitHub App token.
- Reads and `doctor` never write config or caches. GitHub writes remain explicit named commands with dry-run support where applicable.
- Avoid heuristic provider-failure classification based on ad hoc lists of stderr substrings. Prefer structured results, stable typed errors, and fail closed when authentication or network state cannot be proven. (Codex learning)
- Treat the shipped CLI as production code: keep control flow simple, avoid speculative recovery logic, preserve secret-safe diagnostics, and require executable regression tests plus rebuilt-artifact smoke checks for behavior changes. (Codex learning)

## Build and test

- Run `python3 -m unittest discover -s tests -v` from this directory.
- Run `scripts/build-artifact` to produce `../../scripts/gitstack` as an executable Python zipapp.
- Run `scripts/reinstall-local` only when intentionally testing the versioned
  source through the configured `alemar11` marketplace and installed cache.
- Verify the shipped artifact with `--help`, `--version`, `--json doctor`, and a safe dry-run or read-only command.
- Do not run from `build/`; it is intermediate output.

## Versioning

`pyproject.toml` is the CLI version source of truth. Keep it aligned with the owning plugin manifest. Any runtime change requires a semver bump, rebuilt artifact, tests, and shipped-artifact smoke checks.
