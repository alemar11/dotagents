# Postgres Maintenance

`skills/postgres/` owns the artifact-first Postgres runtime package. Runtime
usage, safety, and compatibility behavior remain in `SKILL.md` and its
references; this file records the shipped-package maintenance boundary.

## Owned surfaces

- `scripts/postgres` is the stable platform launcher. It selects the supported
  OS/architecture binary from `scripts/bin/` and must not import or execute
  maintenance source from `projects/postgres/`.
- `projects/postgres/` is maintenance-only source for the platform binaries;
  its build and release contract is in `projects/postgres/AGENTS.md`.
- `assets/` and `references/` are shipped runtime inputs. In particular,
  `references/options.md` is the canonical compatibility exception for the
  Postgres option surface and must remain aligned with help, config, and JSON
  output.

## Maintenance contract

- Keep the launcher, supported binary names, platform dispatch, and project
  build outputs aligned. Do not add a second runtime entrypoint or a PATH-only
  command.
- Treat bundled images, configuration examples, and reference assets as
  package inputs; refresh them only through the owning maintenance workflow.

## Validation

- Run shell syntax checks and the project-scoped build/tests for binary changes.
- Verify the shipped launcher with `--help`, `--version`, `--json doctor`, and a
  safe local or offline fixture without touching a remote database.
