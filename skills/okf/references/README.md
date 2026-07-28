# OKF Reference Map

Use this page first after the `okf` skill loads.

## Sources

- `../assets/spec.md` is the bundled official OKF spec copy.
- `../assets/manifest.json` records the upstream repository, ref, resolved
  commit, content hash, detected spec version, and download time for that copy.

## Read The Smallest Useful File

- `writing-okf.md`: authoring concept documents, indexes, logs, links, and
  frontmatter.
- `validation.md`: OKF v0.2 conformance, parser limits, strict-link checks, and
  machine-readable CLI output.
- `examples.md`: compact concept, provenance/trust, computation, index, and log
  examples.

## Core Shape

An OKF bundle is a directory tree of markdown files. Every non-reserved `.md`
file is a concept document with YAML frontmatter and a markdown body. The
reserved filenames are `index.md` and `log.md`.
