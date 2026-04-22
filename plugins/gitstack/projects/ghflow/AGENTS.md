# ghflow Project

## Purpose

- `projects/ghflow/` is the maintained Python implementation behind the shipped runtime artifact at `plugins/gitstack/scripts/ghflow`.
- Normal runtime usage must stay on `plugins/gitstack/scripts/ghflow`.
- The shipped artifact is a Python executable zipapp, not a hand-written wrapper.

## Runtime Surface

- Shipped artifact: `plugins/gitstack/scripts/ghflow`
- Version check: `plugins/gitstack/scripts/ghflow --version`
- Runtime surface check: `plugins/gitstack/scripts/ghflow --help`

## Source Of Truth

- CLI semver source of truth: `projects/ghflow/pyproject.toml`
- Bump policy:
  - major for breaking CLI contract changes
  - minor for backward-compatible new features or meaningful capability additions
  - patch for backward-compatible bug fixes and corrections

## Safe Maintenance

- Edit Python implementation under `projects/ghflow/src/ghflow/`.
- Keep `scripts/ghflow` as a rebuilt executable artifact generated from this
  project.
- Do not treat any virtualenv or build directory as a supported runtime entrypoint.
- Treat `projects/ghflow/src/ghflow/` as the runtime source of truth.
- No legacy runtime helper layer should remain outside `projects/ghflow/src/ghflow/`.
- When changing the runtime, rebuild `scripts/ghflow` from this project before
  considering the work done.

## Verify

- `python3 -m py_compile plugins/gitstack/projects/ghflow/src/ghflow/*.py plugins/gitstack/projects/ghflow/tests/test_ghflow.py`
- `python3 -m unittest discover -s plugins/gitstack/projects/ghflow/tests -p 'test_*.py'`
- `plugins/gitstack/scripts/ghflow --help`
- `plugins/gitstack/scripts/ghflow --version`
- `PYTHONPATH=plugins/gitstack/projects/ghflow/src python3 -m ghflow --help`

## Rebuild

- Rebuild the shipped artifact with:
  - `python3 -m zipapp plugins/gitstack/projects/ghflow/src -o plugins/gitstack/scripts/ghflow -m 'ghflow:main' -p '/usr/bin/env python3'`
- After rebuilding, restore the executable bit with:
  - `chmod +x plugins/gitstack/scripts/ghflow`
- For local Python installs, `projects/ghflow/pyproject.toml` also exposes a
  native console-script entry point:
  - `ghflow = "ghflow:main"`
