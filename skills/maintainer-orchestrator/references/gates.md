# Gates Reference

Use gates before declaring work owner-ready, merge-ready, release-ready, or
complete. Portfolio ledgers may add stricter gates, but they should not weaken
these defaults without explicit owner approval.

## Universal Gates

### Authorization Gate

Confirm the worker's requested action is covered by the current authorization
mode. Stop for owner approval before push, PR, merge, close, release, external
service mutation, destructive local changes, or broad scope changes.

### Live Proof Gate

For user-facing behavior, require proof from the real app, CLI, API, or
rendered artifact when feasible. Synthetic proof is acceptable only when live
proof is blocked and the blocker is reported.

### Autoreview Gate

After non-trivial code edits, run focused tests and `$autoreview`. Treat
findings as advisory, verify each accepted finding in real code, fix actionable
issues, then rerun focused tests and `$autoreview`.

### CI Gate

Before merge-ready or release-ready status, require current CI state or a clear
reason CI is unavailable. Failing checks need a short failure summary, link, and
owner-ready next action.

### Owner Decision Gate

When progress depends on product direction, risk acceptance, credentials,
budget, merge timing, release timing, or external coordination, produce a
decision brief with options and recommended next action.

### Release Gate

Before release-ready status, verify version, changelog or release notes, tags,
package artifacts, migration notes, rollback path, and CI. Use GitStack release
guidance for GitHub-backed releases.

### Public Model Identifier Gate

When work exposes model identifiers, tool names, public API fields, or user-
visible integration names, verify the exact spelling against source docs or
runtime metadata before shipping.

### Cross-Repo Integration Gate

For portfolios involving multiple repositories, require compatibility evidence
across repo boundaries before owner-ready status: shared API shape, version
pinning, migration order, deploy order, fixtures, or an explicit integration
test.

### Credential And Access Gate

If work requires credentials, paid service access, private repo permission, or
local secrets, stop and report the minimum missing access. Do not ask workers to
work around protected systems with unsafe local substitutes.
