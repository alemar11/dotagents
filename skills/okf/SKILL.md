---
name: okf
description: Write, scaffold, inspect, and validate Open Knowledge Format markdown bundles with the shipped OKF CLI.
---

# OKF

## Goal

Use this skill to write and validate Open Knowledge Format bundles: directory
trees of UTF-8 markdown concept files with YAML frontmatter, plus optional
`index.md` and `log.md` reserved files.

This skill uses:
- a bundled copy of the official OKF spec in `assets/spec.md`
- focused writing and validation references under `references/`
- the shipped `scripts/okf` CLI for deterministic scaffolding and validation

## Quick Workflow

1. Read `references/README.md` for the current routing map.
2. Use `references/writing-okf.md` when creating or editing OKF markdown.
3. Author OKF v0.2. Write every timestamp-valued frontmatter key as an ISO
   8601 datetime with an explicit UTC offset. Keep `log.md` headings as
   `YYYY-MM-DD` dates. Use `generated.at` instead of the retired `timestamp`
   field, and record provenance in `sources` instead of a body `# Citations`
   list.
4. For deterministic checks, run
   `<okf-skill-root>/scripts/okf validate <bundle>`. Use
   `<okf-skill-root>/scripts/okf --json validate <bundle>` when another
   tool will consume the result.
5. For runtime diagnostics, run
   `<okf-skill-root>/scripts/okf --json doctor`.
6. When creating a new concept file, prefer:

   - one concept per non-reserved `.md` file
   - bundle-relative concept IDs such as `tables/orders`
   - absolute bundle-root links such as `/tables/customers.md`
   - concise frontmatter and structured markdown body sections

## Runtime Surface

- The supported runtime entrypoint is `scripts/okf` inside this skill package.
- If the current working directory is the skill root, run it as `./scripts/okf`.
- If invoking from another repo, resolve the skill path and run
  `<okf-skill-root>/scripts/okf`.
- The CLI is stdlib-first. If `PyYAML` is installed, validation uses it for
  exact YAML parsing. If not, the CLI uses a limited parser and reports that
  limitation in `doctor` and validation warnings.

## OKF Rules To Preserve

- Do not invent source facts just to fill frontmatter fields.
- Preserve unknown frontmatter keys when editing existing documents.
- Do not impose a central taxonomy for `type`; use descriptive values and
  tolerate unknown types.
- Treat broken cross-links as warnings unless the user asks for strict link
  validation.
- Keep `index.md` and `log.md` reserved; do not use them for concepts.
- Treat provenance, trust, lifecycle, and computation families as optional;
  their absence never makes a concept nonconformant.
- For `type: Attested Computation`, follow the exact contract in
  `assets/spec.md` and use a `# Computation` body section when the
  computation is inline.
- Keep runtime usage separate from spec refresh mechanics.

## References

- Read `references/README.md` first for the local reference map.
- Read `references/writing-okf.md` when authoring concepts, indexes, logs, and
  cross-links.
- Read `references/validation.md` for the conformance and CLI validation
  contract.
- Read `references/examples.md` for compact examples.
- Read `assets/spec.md` when exact official wording matters or when authoring
  an Attested Computation.

## Output Shape

When producing OKF content for a user, include:

- the intended bundle tree or changed concept path
- the frontmatter and markdown body
- the OKF version targeted and validation command used
- remaining warnings, especially omitted recommended fields or broken links

## CLI Maintenance

- The shipped artifact is `scripts/okf`; normal runtime must not depend on
  files outside this skill package or require network access.
- `VERSION` in `scripts/okf` is the CLI version source of truth.
- Use semantic versioning: major for incompatible commands, options, output,
  or validation contracts; minor for backward-compatible capabilities; patch
  for compatible fixes.
- Validate CLI changes with `python3 -m unittest discover -s tests`, plus the
  shipped `--help`, `--version`, `--json doctor`, and a safe scaffold/validate
  fixture.
