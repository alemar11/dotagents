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
timestamp: 2026-06-29T12:00:00Z
---
```

Hard requirement for OKF v0.1 conformance:
- `type`

Recommended fields:
- `title`
- `description`
- `resource`
- `tags`
- `timestamp`

Preserve producer-defined fields when editing. Do not reject or remove unknown
keys.

## Body Sections

The body is normal markdown. Use structure that helps humans and agents scan:

- `# Schema` for columns, fields, request/response shapes, or data contracts.
- `# Examples` for concrete queries, payloads, commands, or usage snippets.
- `# Citations` for external sources backing claims in the body.

These headings are conventional, not required.

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
`index.md` declaring `okf_version`.

`log.md` may appear at any level and records dated updates with `YYYY-MM-DD`
headings, newest first.
