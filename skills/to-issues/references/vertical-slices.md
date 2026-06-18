# Vertical Slices

Use this reference when turning a PRD into implementation issues. The default
is always vertical slicing. Use a horizontal issue only when a vertical slice is
not practical and the exception rules below are satisfied.

## Definition

A vertical issue delivers one independently verifiable product or system
outcome. It may touch UI, API, storage, tests, docs, jobs, migrations, and
configuration in one issue when those changes belong to the same outcome.

A good vertical issue:

- changes one user-visible or system-verifiable behavior,
- can be validated on its own,
- includes the minimum layers needed to make that behavior real,
- has explicit dependencies and no hidden ordering assumptions,
- gives the implementation agent enough local context to start,
- has acceptance criteria written as outcomes, not internal chores.

## Slice Boundary Heuristics

Choose issue boundaries by behavior, not by code layer. Prefer these boundary
types:

- one actor can complete one workflow path,
- one state transition becomes possible,
- one permission or policy rule is enforced,
- one integration path works end to end,
- one validation or failure mode is handled,
- one migration or compatibility step becomes verifiable,
- one observable system behavior changes.

When a PRD contains CRUD work, do not create one issue per technical operation
by default. Split by meaningful workflow path instead, such as "user can create
and see a draft" before "user can publish a draft" before "user can archive a
published item."

## Ordering Strategy

Order issues so an agentic loop can implement them sequentially with minimal
backtracking:

1. **Walking skeleton**: the smallest end-to-end path that proves the main
   architecture, route, state, permissions, and validation surface can work.
2. **Primary happy path**: the core user or system behavior from the PRD.
3. **Required variants**: important alternate actors, states, integrations, or
   data shapes.
4. **Failure and edge paths**: validation failures, permission denials,
   retries, empty states, and compatibility fallbacks.
5. **Operational polish**: observability, docs, cleanup, or migration follow-up
   only when tied to a concrete delivered behavior.

Each issue must list only direct prerequisites in `## Dependencies`. If issue
3 depends on issue 1 but not issue 2, say that directly. Do not rely on issue
numbering alone to imply ordering.

## Dependency Rules

Dependencies must be explicit, minimal, and implementable:

- Use `None` when the issue can start immediately.
- Reference issue titles or numbers when a prior issue must land first.
- Explain what dependency is needed, such as "uses the draft creation endpoint
  from Issue 01."
- Do not create circular dependencies.
- Do not depend on a broad phase such as "backend complete" or "frontend
  complete."
- If the issue depends on an unresolved decision, mark it `needs-info` instead
  of `ready-for-agent`.

## Avoid Horizontal Tickets

Avoid issues whose only goal is:

- build the backend,
- build the frontend,
- add tests,
- update docs,
- refactor shared utilities,
- create database tables,
- wire configuration,
- add observability.

Those tasks usually belong inside a vertical issue. A separate enabling issue
is allowed only when all of these are true:

- no useful vertical slice can be implemented before it,
- it unblocks at least one named later vertical issue,
- it is independently verifiable,
- it has clear acceptance criteria,
- it is small enough for one focused implementation pass,
- its dependencies and consumers are listed explicitly.

Name allowed enabling issues by the capability they unlock, not by the layer.
Prefer "Enable authenticated draft storage for Issue 02 and Issue 03" over
"Add database tables."

## Ready vs Blocked

Mark an issue `ready-for-agent` only when it has:

- a clear vertical outcome,
- non-goals,
- direct dependencies,
- acceptance criteria,
- validation steps,
- an embedded `$plan-harder` implementation brief,
- no unresolved product, technical, access, API, data, or validation blocker.

Mark an issue `needs-info` when any of these remain unclear:

- product behavior or user outcome,
- required source of truth,
- API contract or schema,
- permissions or roles,
- migration or compatibility policy,
- access to credentials, services, fixtures, or test data,
- validation command or acceptance signal.

Mark an issue `ready-for-human` when the next step requires human judgment,
business approval, design approval, or manual operational access before an
agent can safely proceed.

## Plan Harder Handoff

Every issue must be hardened after the vertical slice is drafted and before it
is returned or published.

For each issue:

- pass only that draft issue body plus the minimum relevant PRD context to
  `$plan-harder`,
- request issue-hardening mode,
- embed the returned brief under `## Implementation Plan`,
- keep any `$plan-harder` blocker visible,
- do not mark the issue `ready-for-agent` until blockers are resolved,
- do not batch multiple issues into one `$plan-harder` call.

Because `$plan-harder` is chat-output-only, `$to-issues` owns any later issue
tracker or local markdown writes.

## Good Split Example

For a PRD that adds team invitations:

1. `Create pending invitation`
   - Outcome: admin can invite an email and see a pending invite.
   - Dependencies: `None`.
2. `Accept invitation into team`
   - Outcome: invited user can accept and join the team.
   - Dependencies: `Create pending invitation`.
3. `Handle expired or revoked invitation`
   - Outcome: invalid invite links fail with the correct user-facing state.
   - Dependencies: `Create pending invitation`.
4. `Show invitation audit trail`
   - Outcome: admin can see invite lifecycle events.
   - Dependencies: `Create pending invitation`, `Accept invitation into team`,
     `Handle expired or revoked invitation`.

Bad split:

- `Build invitation backend`
- `Build invitation frontend`
- `Add invitation tests`
- `Update invitation docs`

The bad split blocks parallel understanding and forces agents to coordinate
across layers without a verifiable product increment.
