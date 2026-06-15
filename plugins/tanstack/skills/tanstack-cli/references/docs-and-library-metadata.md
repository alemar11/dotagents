# Docs And Library Metadata

Use this guide when the task is to query TanStack CLI docs or library metadata before making tool-sensitive claims.

Owns:
- `tanstack doc`, `tanstack libraries`, and search-driven metadata discovery
- machine-readable preflight checks
- establishing current CLI-backed facts before framework-specific reasoning

Workflow:
1. Use CLI metadata or docs queries to establish current facts.
2. Prefer machine-readable discovery before making tool-sensitive claims.
3. Hand off to a framework or integration skill once the needed context is
   resolved.

Do not use this guide for framework implementation once the needed docs are
known, ecosystem add-on choice comparison, or general web research outside
CLI-backed discovery.

Verification: verify against current `@tanstack/cli` docs and metadata commands
when exact command names or JSON shapes matter.
