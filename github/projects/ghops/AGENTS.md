# ghops Project

## Purpose

- `projects/ghops/` is the maintained Python implementation behind the shipped runtime artifact at `github/scripts/ghops`.
- Normal runtime usage must stay on `github/scripts/ghops`.

## Runtime Surface

- Shipped artifact: `github/scripts/ghops`
- Version check: `github/scripts/ghops --version`
- Readiness check: `github/scripts/ghops --json doctor`

## Source Of Truth

- CLI semver source of truth: `projects/ghops/pyproject.toml`
- Bump policy:
  - major for breaking CLI contract changes
  - minor for backward-compatible new features or meaningful capability additions
  - patch for backward-compatible bug fixes and corrections

## Safe Maintenance

- Edit Python implementation under `projects/ghops/src/ghops/`.
- Keep `scripts/ghops` as a thin wrapper only.
- Do not treat any virtualenv or build directory as a supported runtime entrypoint.
- Treat `projects/ghops/src/ghops/` as the runtime source of truth.
- No legacy runtime helper layer should remain outside `projects/ghops/src/ghops/`.

## Verify

- `python3 -m py_compile github/projects/ghops/src/ghops/*.py github/projects/ghops/tests/test_ghops.py`
- `python3 -m unittest discover -s github/projects/ghops/tests -p 'test_*.py'`
- `github/scripts/ghops --help`
- `github/scripts/ghops --version`
- `github/scripts/ghops --json doctor`

## Rebuild

- No bundling step is required right now.
- If the runtime wrapper changes, keep `github/scripts/ghops` importing from `projects/ghops/src/`.
