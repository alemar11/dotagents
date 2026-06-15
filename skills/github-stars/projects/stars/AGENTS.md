# stars Project

## Purpose

- `projects/stars/` maintains the Python implementation behind
  `skills/github-stars/scripts/stars`.
- It owns authenticated-user star and GitHub user-list workflows only.

## Maintenance

- Edit source under `projects/stars/src/github_stars_cli/`.
- Keep the source `VERSION` aligned with `pyproject.toml`.
- Rebuild with:
  `python3 -m zipapp skills/github-stars/projects/stars/src -o skills/github-stars/scripts/stars -m 'github_stars_cli:main' -p '/usr/bin/env python3'`
- Restore executable mode with `chmod +x skills/github-stars/scripts/stars`.
