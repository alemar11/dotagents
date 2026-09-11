# GitHub Stars Executable Maintenance

Runtime prose and metadata are owned elsewhere.

## Executable maintenance

- `scripts/stars` is the shipped runnable artifact (`lists assign` / `lists unassign`, `doctor`).
- `scripts/stars_lib/` holds the implementation and local helpers.
- Naming: `stars_lib` uses underscores as the Python import-syntax
  compatibility exception; the public skill (`github-stars`) and command
  (`stars`) stay lower-kebab.
- Validate with `python3 -m unittest discover -s skills/github-stars/tests -v` and
  `scripts/stars --help|--version|--json doctor`.
