---
name: okf
description: Write, scaffold, inspect, and validate Open Knowledge Format (OKF) markdown knowledge bundles. Use when working with OKF, Open Knowledge Format, knowledge bundles, markdown files with OKF YAML frontmatter, concept documents, bundle indexes/logs, or when converting structured knowledge into portable agent-readable markdown.
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
3. Choose the validation mode:
   - `spec`: OKF v0.1 conformance; only `type` is hard-required.
   - `reference-agent`: stricter compatibility with the official reference
     agent; requires `type`, `title`, `description`, and `timestamp`.
4. For deterministic checks, run:
   - `<okf-skill-root>/scripts/okf doctor`
   - `<okf-skill-root>/scripts/okf validate <bundle> --mode spec`
   - `<okf-skill-root>/scripts/okf validate <bundle> --mode reference-agent`
5. When creating a new concept file, prefer:
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
- Keep runtime usage separate from spec refresh mechanics.

## References

- Read `references/README.md` first for the local reference map.
- Read `references/writing-okf.md` when authoring concepts, indexes, logs, and
  cross-links.
- Read `references/validation-modes.md` when choosing `spec` versus
  `reference-agent` compatibility.
- Read `references/examples.md` for compact examples.
- Read `assets/spec.md` when exact official wording matters.

## Output Shape

When producing OKF content for a user, include:
- the intended bundle tree or changed concept path
- the frontmatter and markdown body
- the validation mode used
- remaining warnings, especially omitted recommended fields or broken links
