# Capture Idea Option Contract

Load this reference before extracting or publishing candidates. It is the sole
owner of selectable Capture Idea behavior.

## Syntax And Hard Cut

- Field names use snake_case and enum values use lower-kebab-case.
- User wording is selection evidence, never an alternative field or value.
- Reject every field or value not listed in the Run Registry. Do not accept
  aliases, retired syntax, or compatibility mappings.
- Keep tracker backend, explicit repository scope, tracker owner, marker and state
  mappings, candidate decisions, queue intent, names, slugs, paths, refs,
  duplicate state, and evidence as facts or execution data.

## Run Registry

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `write_mode` | `apply`, `propose` | `apply` for an explicit Capture Idea request to save durable Ideas | `apply` writes through the configured tracker; `propose` performs no writes. |

Resolve `write_mode` once before candidate selection:

- Any request that forbids writes, asks for a dry run, or asks to inspect the
  Ideas before saving resolves to `write_mode=propose`.
- An explicit Capture Idea request to save Ideas defaults to
  `write_mode=apply`.
- `write_mode=propose` returns complete proposed bodies, target locations,
  intended marker and optional state metadata, deterministic refs, and
  publication order. It does not write a local file, create a GitHub label or
  issue, or return executable publication commands.
- Never silently downgrade an authorized `apply` run after a blocker. Return
  the blocker and preserve the resolved mode.

## Execution Data

Carry, but do not persist as option fields:

- `tracker_backend`: `github` or `local`, loaded from Project Memory;
- repository layout and exactly one tracker-owning repository per candidate;
- the configured concrete mapping for `artifact_marker: idea`;
- the configured concrete `needs-triage` mapping when queueing was explicit;
- final candidate decision, name, lowercase kebab-case slug, body, queue intent,
  target, source evidence, and duplicate/collision result;
- applied durable ref, or proposal ref
  `proposed-idea:<idea-slug>` for one selected repository and
  `proposed-idea:<repository-slug>/<idea-slug>` when multiple repository owners
  are in scope.

An applied GitHub ref is `owner/repository#<number>` or its canonical hosted
URL. An applied local ref is
`<repository-slug>/planning/ideas/<idea-slug>.md`. Proposed refs are never
durable planning input.
