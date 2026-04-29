---
name: tanstack-cli-query-docs-library-metadata
description: Use the TanStack CLI to query machine-readable docs, library metadata, and discovery surfaces before making library-specific claims.
---

# TanStack CLI Query Docs Library Metadata

Use this skill when the task is specifically about querying TanStack CLI metadata or docs surfaces for discovery and preflight validation.

## Owns

- `tanstack libraries`, `tanstack doc`, and `tanstack search-docs`.
- Machine-readable discovery and preflight validation.
- Using CLI metadata to avoid stale assumptions.

## Does Not Own

- Framework implementation once the needed docs are known: use the relevant framework skill.
- Ecosystem add-on choice comparison: use `tanstack-cli-choose-ecosystem-integrations`.
- General web research outside CLI-backed discovery.

## Workflow

1. Use CLI metadata or docs queries to establish current facts.
2. Prefer machine-readable discovery before making tool-sensitive claims.
3. Hand off to a framework or integration skill once the needed context is resolved.

## Verification

Verify against current `@tanstack/cli` docs and metadata commands when exact command names or JSON shapes matter.
