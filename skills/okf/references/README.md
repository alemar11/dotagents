# OKF Reference Map

Use this page first after the `okf` skill loads.

## Sources

- `../assets/spec.md` is the bundled official OKF spec copy.
- `../assets/manifest.json` records the upstream repository, ref, resolved
  commit, content hash, detected spec version, and download time for that copy.

## Read The Smallest Useful File

- `writing-okf.md`: authoring concept documents, indexes, logs, links, and
  frontmatter.
- `validation-modes.md`: choosing between OKF spec conformance and stricter
  reference-agent compatibility.
- `examples.md`: compact concept, index, and log examples.

## Core Shape

An OKF bundle is a directory tree of markdown files. Every non-reserved `.md`
file is a concept document with YAML frontmatter and a markdown body. The
reserved filenames are `index.md` and `log.md`.
