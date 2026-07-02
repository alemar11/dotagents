# Vertical Slices

Use this reference when turning a PRD into implementation issues. The default
is always vertical slicing. Use a horizontal issue only when a vertical slice is
not practical and the exception rules below are satisfied.

## Definition

A vertical issue delivers one independently verifiable product or system
outcome. It may touch UI, API, storage, tests, docs, jobs, migrations, and
configuration in one issue when those changes belong to the same outcome.
In an orchestrator workspace, one vertical issue may span multiple independent
repos when the outcome is cross-repo by nature.

A good vertical issue:

- changes one user-visible or system-verifiable behavior,
- can be validated on its own,
- includes the minimum layers needed to make that behavior real,
- names the product/workspace context in monorepos or the affected repos and
  integration gates in orchestrator workspaces,
- links back to the Source PRD for delivery mode and states how the issue
  can run in parallel,
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
- one cross-repo contract is introduced and consumed by at least one affected
  repo,
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
`03` depends on issue `01` but not issue `02`, say that directly. Do not rely
on issue numbering alone to imply ordering.

## Dependency Rules

Dependencies must be explicit, minimal, and implementable:

- Use `None` when the issue can start immediately.
- Reference generated issue IDs such as `01` or `02` when a prior generated
  issue must land first. Include the issue title as explanatory prose when it
  improves readability, but keep the ID as the stable dependency handle.
- Explain what dependency is needed, such as "uses the draft creation endpoint
  from Issue 01."
- Do not create circular dependencies or retain cycles that can lock the
  issue queue.
- Do not depend on a broad phase such as "backend complete" or "frontend
  complete."
- If the issue depends on an unresolved decision, withhold it and return the
  blocker by default instead of publishing a partial issue. Emit `needs-info`
  only when the user explicitly authorizes partial non-agent-ready output.
  If it depends only on another generated implementation issue being completed,
  it may still be `ready-for-agent`; queue consumers must wait for the listed
  dependency to finish before starting it.

## Avoid Horizontal Tickets

Avoid issues whose only goal is:

- build the backend,
- build the frontend,
- add tests,
- update docs,
- add fixtures,
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

## Verticality Gate

Before generated implementation issues are written, returned, or published,
review the final hardened issue bodies as the source of truth. This is a
blocking gate, not a summary pass.

For each issue, confirm that:

- the title and goal name a user-visible or system-verifiable outcome,
- acceptance criteria prove the outcome instead of listing internal tasks,
- validation can prove the issue independently after its direct dependencies
  are complete,
- tests, docs, fixtures, migrations, configuration, and observability work are
  inside the vertical issue whose outcome they prove unless an enabling-slice
  exception applies,
- any enabling-slice exception lists the later issue IDs it unlocks and why no
  useful vertical issue can land before it,
- dependencies use generated issue IDs and remain direct, minimal, and
  acyclic,
- orchestrator or multi-repo issues name affected repos, integration gates, and
  proof required for closeout.

If an issue fails the gate, repair the issue set before output:

- merge chore-only work into the vertical issue that needs it,
- split mixed work by independently verifiable behavior instead of code layer,
- reframe infrastructure work only when it is a real independently verifiable
  system outcome,
- keep separate enabling work only when all exception rules above are satisfied,
- withhold unresolved anomalies instead of publishing them as
  `ready-for-agent`.

After any repair, rerun hardening for materially changed issues and revalidate
the final graph before issue bodies are returned or published.

## Ready vs Blocked

Mark an issue `ready-for-agent` only when it has:

- a clear vertical outcome,
- non-goals,
- direct dependencies,
- product/workspace/context scope when the PRD comes from a multi-context repo
  or monorepo,
- affected repos and integration gates when the issue is an orchestrator
  workspace issue,
- a durable `Source PRD` pointer and copied feature-level `Delivery mode`
  metadata,
- parallelization status, expected closeout path, and any delivery or
  integration exception,
- a `## Orchestrator Handoff` section that restates the dispatchable source
  PRD, feature slug, delivery mode, affected repos or product scope, scope,
  start rule, dependencies, validation, and closeout,
- acceptance criteria,
- validation steps,
- implementation guidance enriched by `$plan-harder`,
- no unresolved product, technical, access, API, data, or validation blocker.

A `ready-for-agent` issue may list dependencies on other ready issues. That
means it is specified enough for an agent queue, not that it is immediately
startable before those dependencies are complete.

Only publish or return a `needs-info` issue when the user explicitly authorized
partial non-agent-ready output. Otherwise withhold the issue and report the
blocking question. When partial output is authorized, mark the issue
`needs-info` when any of these remain unclear:

- product behavior or user outcome,
- selected product/workspace/context in a multi-context repo or monorepo,
- required source of truth,
- API contract or schema,
- permissions or roles,
- migration or compatibility policy,
- access to credentials, services, fixtures, or test data,
- validation command or acceptance signal,
- Source PRD, delivery mode inheritance or exception, or whether the issue is
  safe to implement in parallel.

If the source PRD has open questions that affect scope, acceptance criteria,
dependency ordering, validation, permissions, publication target, data
contracts, or cross-repo contracts, stop and resolve them before returning or
publishing `ready-for-agent` issues. A deferred question is safe only when it
is explicitly classified as non-blocking for the generated issue set.

For orchestrator issues, expected repo PR slots or pre-implementation
placeholders may appear before implementation starts when all other
implementation details are agent-ready. Treat those placeholders as scheduling
expectations, not completion proof. Completion remains an orchestrator closeout
responsibility and requires real PR links or equivalent integration proof before
the issue moves to `done` or closes.

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
- start `## Implementation Plan` with the standard provenance line
  `Plan-hardening: $plan-harder issue-hardening pass completed for this issue only.`,
- synthesize the implementation-relevant guidance under `## Implementation Plan`,
- merge acceptance criteria, validation, dependency, and blocker details into
  the matching top-level issue sections,
- keep any `$plan-harder` blocker visible,
- do not mark the issue `ready-for-agent` until blockers are resolved,
- do not batch multiple issues into one `$plan-harder` call.

Do not paste the `$plan-harder` output wholesale if doing so duplicates
sections already present in the issue body.

Because `$plan-harder` is chat-output-only, the issue phase owns any later
issue tracker or local markdown writes.

## Good Split Example

For a PRD that adds team invitations:

1. `01 Create pending invitation`
   - Outcome: admin can invite an email and see a pending invite.
   - Dependencies: `None`.
2. `02 Accept invitation into team`
   - Outcome: invited user can accept and join the team.
   - Dependencies: `01 Create pending invitation`.
3. `03 Handle expired or revoked invitation`
   - Outcome: invalid invite links fail with the correct user-facing state.
   - Dependencies: `01 Create pending invitation`.
4. `04 Show invitation audit trail`
   - Outcome: admin can see invite lifecycle events.
   - Dependencies: `01 Create pending invitation`, `02 Accept invitation into
     team`, `03 Handle expired or revoked invitation`.

Bad split:

- `Build invitation backend`
- `Build invitation frontend`
- `Add invitation tests`
- `Update invitation docs`

The bad split blocks parallel understanding and forces agents to coordinate
across layers without a verifiable product increment.
