# Writing OKF

## Concept Documents

Create one concept per non-reserved `.md` file. The concept ID is the
bundle-relative path without `.md`, for example `tables/orders.md` becomes
`tables/orders`.

Every concept starts with YAML frontmatter:

```yaml
---
type: API Endpoint
title: Create Order
description: Creates a customer order from validated checkout data.
resource: https://api.example.com/openapi#/paths/~1orders/post
tags: [orders, checkout]
status: stable
generated: {"by": "process:catalog-refresh", "at": "2026-06-29T12:00:00Z"}
sources:
  - id: order-api
    resource: https://api.example.com/openapi
    title: Order API specification
---
```

Hard requirement for OKF v0.2 conformance:

- `type`

Recommended fields:

- `title`
- `description`
- `resource`
- `tags`

Optional standard families include:

- provenance: `sources` and `usage_window`
- trust: `generated` and `verified`
- lifecycle: `status` and `stale_after`
- Attested Computation fields: `runtime`, `parameters`, `computation`,
  `executor`, and `attester`

Every timestamp-valued frontmatter key uses an ISO 8601 datetime with an
explicit UTC offset, for example `2026-06-29T12:00:00Z` or
`2026-06-29T14:00:00+02:00`. This applies to `generated.at`, every
`verified[].at`, `stale_after`, every `sources[].last_modified`, and the
`from` and `to` values in shared or source-specific `usage_window` mappings.
Date-only and offsetless datetime values are not canonical OKF timestamps.

Use `generated.at` for the current content's last meaningful change. Do not
author the retired v0.1 `timestamp` field. Put source materials in `sources`;
when attributing a claim, use a markdown footnote whose label matches a
`sources[].id`.

When consuming an older v0.1 concept that has no `generated` mapping, treat its
legacy `timestamp` fallback as timestamp-valued and require the same explicit
UTC offset.

Preserve producer-defined and unknown fields when editing. Do not reject or
remove them.

The stdlib fallback parser accepts flat fields, scalar block lists, and
JSON-compatible flow values. Use `PyYAML` when validating block-form nested
mappings such as `sources`.

## Body Sections

The body is normal markdown. Use structure that helps humans and agents scan:

- `# Schema` for columns, fields, request/response shapes, or data contracts.
- `# Examples` for concrete queries, payloads, commands, or usage snippets.
- `# Computation` for the sanctioned inline computation of an
  `Attested Computation`.

These headings are conventional, not required.

Do not author a v0.1 `# Citations` list. Record provenance in `sources` and use
keyed footnotes for per-claim attribution.

## Attested Computations

Use `type: Attested Computation` only for a standalone sanctioned computation.
Read `../assets/spec.md` §10 before authoring one. `runtime` is required for
this type; keep the allowed inputs in `parameters`, provide either an inline
`# Computation` code block or a `computation` path, and keep `executor` and
`attester` as distinct contracts.

## Links

Prefer absolute bundle-root links:

```markdown
See [Orders](/tables/orders.md) for the primary sales fact table.
```

Relative links are valid. Broken links are allowed by the spec and should be
treated as warnings unless the user explicitly asks for strict link validation.

## Reserved Files

`index.md` may appear at any level and lists the current directory contents.
It normally has no frontmatter. The only permitted exception is a bundle-root
`index.md` declaring `okf_version: "0.2"`.

`log.md` may appear at any level and records dated updates with `YYYY-MM-DD`
headings, newest first. These headings group entries by day and remain
date-only; they are not timestamp-valued frontmatter keys.
