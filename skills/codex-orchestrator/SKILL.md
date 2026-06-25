---
name: codex-orchestrator
description: Coordinate Codex workers, portfolio ledgers, gates, autoreview, Git/GitHub companion skills, and owner-ready closeout.
---

# Codex Orchestrator

## Overview

Use this Codex-dependent skill as the control plane for maintainer work across
one or more repositories. It coordinates named portfolio ledgers, read-only
standalone Git/GitHub companion skills, visible Codex App worker threads,
CLI/subagent worker threads, heartbeat monitoring, gates, `$autoreview`, and
owner-ready status reports.

This skill is not a worker. It delegates scoped work, monitors progress, keeps
the ledger current, and decides when a task is ready for owner review, commit,
PR, release, or another explicit decision. Keep the root orchestrator thread
lightweight: it owns routing, lifecycle, integration, gates, ledger updates,
and final publication, while delegated workers own substantial repository
inspection or implementation whenever delegation is authorized and useful.

## Root Ownership Contract

- The root orchestrator owns routing, ledger updates, worker lifecycle,
  integration choice, gate evaluation, and final closeout decisions.
- Workers own one scoped repository or workstream plus focused validation and a
  clear final report.
- Worker-reported statuses such as `done`, `blocked`, `needs-owner`, or
  `ready-for-review` are inputs to the root thread, not final lifecycle
  decisions.
- If no inspectable worker surface is available, delegation is not explicitly
  authorized, or the work is too small or overlapping, keep the work in the
  root thread.

## Workstream Sources

A workstream is the orchestration unit. It may come from a user-provided plan,
GitHub issue, PR review, CI failure, release checklist, local TODO, audit
result, ledger item, or ad hoc owner request. GitHub issues and PRs are trigger
sources, not the only planning model.

New feature planning is not a shortcut through orchestration decomposition. If
the source is rough feature or product intent without a durable PRD and
generated implementation issues, route it through `$plan-feature` before
scheduling implementation. If the source is an existing PRD without generated
implementation issues, route it through `$plan-feature` in
`issues-from-existing-prd` mode before implementation scheduling unless the
owner only asked for inspect-only review. Generated
issues, PRs, CI failures, bugs, local checklists, and explicit implementation
requests can become orchestrator source items directly.

Treat every task source as a source item before it becomes a workstream. A
source item needs a stable source id, source reference, acceptance criteria,
current source status, closeout target, and mutation authority. Examples:
`github-issue:owner/repo#123`, `github-pr-thread:owner/repo#45:<thread-id>`,
`markdown:/path/plan.md#heading`, `markdown-check:/path/plan.md:42`,
`todo:/path/file.ext:88`, `ci:owner/repo/actions/runs/<id>`, or
`ledger:<portfolio>:<item-id>`. The ledger is the orchestration projection; the
source item remains the acceptance and closure source unless the owner
explicitly migrates it.

For Markdown plans or checklists, enumerate unchecked items with their nearest
heading context and a stable path plus line or anchor. Preserve parent context,
map each actionable item to a ledger workstream, and close it by applying or
proposing a file update, moving residual scope to `deferred`, or recording the
owner decision that leaves it open.

## Loop Semantics

Run orchestration as bounded waves, not as a one-pass checklist:

1. Resolve or initialize the ledger.
2. Snapshot authorized task sources and reconcile them with existing ledger
   workstreams by stable source id.
3. Select the next root-owned and delegated wave.
4. Execute, monitor, integrate, and gate the wave.
5. Update the ledger and any authorized source closeout targets.
6. Rescan due sources, then repeat only while there are `active` items, due next
   checks, authorized `ready-next` actions, or newly surfaced source items.

Each wave must produce at least one ledger state transition, new proof, source
update, owner decision brief, or explicit no-progress/blocker record. Do not
loop silently on the same worker status or source snapshot.

## Runtime Requirements

- Codex App thread tools when visible App workers are requested and available:
  `codex_app.create_thread`, `codex_app.read_thread`,
  `codex_app.send_message_to_thread`, `codex_app.set_thread_title`,
  `codex_app.set_thread_archived`, `codex_app.handoff_thread`,
  `codex_app.fork_thread`, and optionally `codex_app.list_threads` or
  `codex_app.set_thread_pinned`.
- CLI/subagent worker tools when that is the active inspectable surface:
  `multi_agent_v1.spawn_agent`, `multi_agent_v1.wait_agent`,
  `multi_agent_v1.send_input`, `multi_agent_v1.close_agent`, or the CLI
  `/agent` equivalent.
- Codex heartbeat or automation support when the user asks for periodic worker
  monitoring.
- The reusable `$autoreview` skill for closeout review after non-trivial code
  edits and after review-triggered fixes.
- Standalone Git/GitHub companion skills as needed:
  `$github-portfolio-triage`, `$github-triage`, `$github-issues`,
  `$github-ci`, `$github-deep-review`, `$github-review-threads`,
  `$github-releases`, `$git-commit`, and `$yeet`.
- Planning companion skills as needed before implementation scheduling:
  `$plan-feature` for rough new feature intent and existing PRDs that do not
  yet have generated implementation issues.
- Local ledger storage at
  `~/.cache/dotagents/skills/codex-orchestrator/ledgers/`.

If a required Codex tool is not already visible, search the available tool
registry for the operation name, such as `create_thread`, `read_thread`,
`spawn_agent`, or `wait_agent`, before treating the surface as unavailable.
Record the actual callable tool name when it differs from the logical names
above. If a required Codex tool or companion skill remains unavailable, continue
only with the parts that can be done safely and report the exact missing
surface.

## Worker Surface Selection

Resolve owner authorization before delegation. If the owner already specified
worker surface and quota, record that policy and proceed within it. If the
owner requests workers, parallelism, background work, heartbeat monitoring, or
broad orchestration, delegation is authorized only to the extent the requested
surface and quota are clear. If the request is a small single-thread task, keep
the work in the root thread unless parallel work materially improves progress.

If the owner request is broad, worker-oriented, or materially parallelizable
but does not clearly specify worker surface and limits, ask for a worker policy
before creating any delegated worker:

- In Codex App, ask whether to use CLI/subagents, visible Codex App threads,
  both/auto, or no delegation.
- Outside Codex App, ask whether to use CLI/subagents or no delegation.
- Ask for the maximum active CLI/subagents and, when Codex App threads are
  allowed, the maximum active Codex App threads. If both surfaces are allowed,
  also ask whether there is an overall concurrent delegated-worker cap for the
  session.
- Always ask whether progress should be monitored manually in the root thread
  or with a heartbeat. When asking about heartbeat monitoring, propose a
  5-minute interval by default and state that the owner can change it. If a
  heartbeat is requested, also ask for the scope, stop condition, and whether
  it may steer workers or only report status.
- While waiting for the answer, do only root-owned discovery or planning that
  does not create workers, create visible App threads, mutate source state, or
  assume a delegation quota or heartbeat policy.

Use this concise clarification shape when the owner omitted delegation or
monitoring details:

> How should I run orchestration for this session: `cli-subagent`,
> `codex-app-thread`, `auto`, or `none`? What max active count should I use
> for each allowed worker surface? Should I monitor progress manually, or create
> a heartbeat? Default heartbeat is `every-5-minutes`, and you can change it.

Visible Codex App thread creation requires explicit owner intent for visible,
new, separate, or background threads. Do not create user-owned App threads
merely because a subtask exists.

Before assigning workstreams, record the owner-authorized worker policy in the
ledger with `Delegated worker surface` set to
`auto|codex-app-thread|cli-subagent|none`, plus `Max active delegated workers`.
`auto` means choose per workstream from available and owner-authorized delegated
surfaces: in Codex CLI this resolves to `cli-subagent`, while in Codex App it
may choose `codex-app-thread` or `cli-subagent`. `none` disables delegation.
Record `no-delegation` only as the actual per-workstream `Surface` for
root-owned work. When separate caps are supplied, also record
`Max active CLI/subagents`, `Max active Codex App threads`, and any
owner-specified session-wide delegated-worker cap.

Choose the worker surface deliberately:

- In Codex App, prefer visible Codex App worker threads for substantial
  delegated work only when the owner explicitly asks for visible, new,
  separate, or background worker threads, or otherwise explicitly indicates
  they expect to see, inspect, rename, hand off, archive, or continue workers
  from the sidebar.
- In Codex CLI, prefer CLI/subagent workers for bounded parallel work because
  they are inspectable through `/agent`.
- If only one surface is exposed, use that surface only when it can satisfy the
  authorization, scope, and inspection requirements. Otherwise do not delegate.

Record the chosen surface, worker id, title or nickname, repository, scope, and
authorization modes in the ledger. Do not call a hidden subagent a visible
thread.

## Delegation Fast Rules

- Treat `Delegated worker surface: auto` as permission to choose among
  available owner-authorized delegated surfaces, not as a quota to fill.
- Use visible Codex App threads only when the owner explicitly asked for
  visible, new, separate, or background workers.
- Use CLI/subagent workers for inspectable bounded parallel work when visible
  App threads were not requested, or when `Delegated worker surface: auto`
  permits subagents and they are the better fit for the workstream.
- Split workers by independent ownership boundary: repository, package,
  service, path set, or tightly scoped workstream. In multi-repo projects this
  is usually one active worker per affected repo per wave; in a single repo or
  monorepo, use multiple workers only when files, contracts, tests, and
  validation paths are cleanly separated.
- Keep small single-thread tasks, overlapping file work, shared contracts,
  dependency or root config changes, migrations, generated snapshots, broad
  tests, conflict resolution, and last-mile integration in the root thread.
- Before sending overlapping new scope into an existing worker, resync or
  replace that worker instead of assuming its checkout is still current.

## Delivery Mode Execution

For implementation or publication workstreams, resolve delivery mode from
the source item, a linked `Source PRD`, or the owner request. Record it in the
ledger and execute against that delivery mode. For generated implementation issues,
first read the issue body and any linked `Source PRD`; the PRD is the canonical
source for full delivery mode details, while the issue body supplies the copied
feature-level `Delivery mode` label plus issue-level parallelization,
dependencies, blocks, closeout, and overrides. Use those issue-local fields as
the scheduling graph for waves and worker routing. Treat an issue line such as
`Delivery mode: one-feature-branch (feature-level, inherited from Source PRD)`
as a feature-level landing strategy, not as a claim that only this one issue
uses that branch/PR shape.

For PRD-backed issue workflows, read
`references/prd-backed-delivery.md` before scheduling or publishing. Keep
delivery authority, publication authority, and issue mutation authority
separate. When the owner asks to implement a PRD or generated issue, and the
PRD or generated issue explicitly defines branch plus draft PR delivery,
commit, push, and draft PR creation are part of the PRD delivery contract after
gates pass unless the owner restricted the request to local-only, inspect-only,
no-push, or no-PR work. For ad hoc or legacy sources without a linked PRD
delivery contract, `implement` remains local-only and publication requires
explicit owner authorization.

When delegating these stages to a worker, list each authorized capability
explicitly: `commit` for local commits, `push` for the exact branch/refspec, and
`pr` for draft PR creation or update. These are not cumulative shortcuts.
If `project-memory/agents/issue-tracker.md` records
`default_worker_authorization`, treat it as a starting policy default only.
Restrict it to the current owner/session authorization, publication authority,
worker inspectability, dirty-worktree state, and gates before dispatch.

Apply issue-level scheduling constraints before choosing a wave or worker:

- `Parallelization: independent`: eligible for delegation when authorization,
  ownership boundaries, and gates allow it.
- `Parallelization: depends-on <issue>`: queue-ready is not start-ready. Do not
  start or delegate it until the named dependency is completed with
  root-verifiable proof, or until the owner explicitly changes the dependency.
- `Parallelization: blocks <issue>`: the issue may start when otherwise
  eligible, but dependent workstreams stay unassigned until this one completes.
- `Parallelization: root-integrated`: keep implementation in the root thread;
  use workers only for read-only inspection or clearly isolated supporting
  proof when that does not change the integration ownership.

If dependency references are malformed, missing, or cyclical, classify the
workstream as `needs-owner`/`blocked` and do not dispatch until the graph is
corrected.

If a dependency, `Source PRD`, closeout path, or parallelization value is
missing, ambiguous, or contradictory, classify the workstream as `needs-owner`
or `blocked` instead of inventing scheduling semantics.

- `one-feature-branch`: use for one git repo, including monorepos. The root
  orchestrator owns the shared feature branch and usually one draft PR for the
  whole feature. Parallel workers may use isolated helper worktrees, patches,
  handoff, or reviewed worker commits, but the root integrates their output
  into the shared branch and owns the final PR.
- `one-pr-per-repo`: use for true multi-repo work. Create or use one feature
  branch per affected repo, usually the same `feature/<feature-slug>` branch
  name, and publish one draft PR per repo when publication is authorized. Link
  every repo PR from the coordination PRD or issue and require cross-repo
  integration proof before closeout.
- `one-pr-per-issue`: use only when the issue is isolated enough that its
  branch and PR cannot conflict with shared contracts, migrations, lockfiles,
  generated files, broad validation, or other active issue work.
- `direct-commit`: use only when explicitly authorized by the owner or source
  item. Record the authorization, validation, and issue-closing target before
  committing.

Do not let workers invent a different branch or PR strategy. For implementation
or publication workstreams that need branch or PR strategy, generated issues
should include both a copied feature-level `Delivery mode` label and a durable
`Source PRD` pointer. If generated issue metadata omits the copied label,
contradicts the PRD, or contradicts repo reality, stop and classify the
workstream as `needs-owner` until the delivery mode is corrected or explicitly
overridden. For ad hoc or legacy source items, fall back to a durable
`Source PRD` pointer only when the source was not produced by `$plan-feature`.
Inspect-only workstreams, such as PR review or CI diagnosis, do not need a
delivery mode unless the review result is being turned into implementation
or publication work.

## Companion Skill Routing

Use the smallest standalone companion skill for each Git or GitHub workstream:

| Workstream | Companion skill |
| --- | --- |
| Read-only scans across multiple explicit repositories | `$github-portfolio-triage` |
| Current-repository issue, PR, label, milestone, or queue triage | `$github-triage` |
| GitHub issue creation, comments, labels, issue types, closure, or parent/sub-issue relationships | `$github-issues` |
| Evidence-first issue, PR, bug, root-cause, or fix-quality review | `$github-deep-review` |
| GitHub Actions runs, pending checks, or failing PR logs | `$github-ci` |
| PR review threads, comment context, or selected replies | `$github-review-threads` |
| Release readiness, tags, GitHub Releases, notes, assets, or package availability | `$github-releases` |
| Local staging, commit authoring, and push-only flows | `$git-commit` |
| Full local checkout publish flow to branch plus draft PR | `$yeet` |

## Workflow

1. Resolve the portfolio ledger with `references/ledger.md`.
2. Identify the repository set, task sources, current goals, delivery mode
   or `Source PRD` inheritance, issue-level scheduling constraints, delivery
   authority, publication authority, issue mutation authority, suppressed
   items, owner constraints, and portfolio-specific gate overrides. Register
   task sources in the ledger with source ids, source refs, dedupe rules,
   branch or PR expectations, closeout target, mutation authority, and
   integration proof target.
3. Select Git/GitHub companion skills from the routing table. If discovery is
   needed, use `$github-portfolio-triage` for broad or multi-repo queue scans;
   use focused current-repo companions such as `$github-triage`,
   `$github-issues`, `$github-deep-review`, `$github-ci`, or
   `$github-review-threads` only when the task is focused on one repo or PR. If the
   user provided a rough new feature idea, route it through `$plan-feature`
   full-flow mode before implementation scheduling; if the user provided an
   existing PRD without generated implementation issues, route it through
   `$plan-feature` issues-from-existing-prd mode unless the request is
   inspect-only; if the user provided generated issues, a
   checklist, or an implementation plan, decompose that durable source into
   workstreams before scanning for additional queue signals. For broad
   maintainer discovery, include open issues, open PRs, failing or pending CI,
   latest release or package state when relevant, unreleased changelog/TODO
   signals, and owner-suppressed items.
4. Classify work with the canonical vocabulary in `references/ledger.md`:
   `active`, `autonomous`, `needs-owner`, `ready-next`, `blocked`, `deferred`,
   `completed`, `ignored-or-suppressed`, or `released`. Each workstream must
   carry its source id, acceptance criteria, scheduling constraints,
   dependencies, selected gates, proof target, and closeout target.
5. Before delegation, read `references/worker.md` and create one Codex worker
   per independent ownership boundary, such as repository, package, service,
   path set, or tightly scoped workstream, using the selected worker surface,
   recorded or inherited delivery mode, and the current dependency wave. Use
   visible Codex App threads in App-oriented workflows only when explicit owner
   intent for visible/new/separate/background workers is present; otherwise use
   CLI/subagent workers when authorized and inspectable, or stay in the root
   thread.
6. Give each worker explicit authorization modes, scope, gates, expected
   proof, delivery mode, publication authority, dependency state, branch
   expectation, integration mode, and final report shape. Workers must not
   spawn sub-workers, create threads, manage other chats, or edit the ledger.
7. For visible Codex App workers, immediately rename each worker thread to
   `<Project>: <short current task>` and update the title when the material
   assignment changes. Keep titles short enough to scan in the sidebar.
8. Keep the root thread focused on orchestration. Delegate heavy repo-local
   implementation to workers when delegation is authorized; perform root-side
   integration only when it is cross-cutting, blocked on worker outputs, or
   necessary to satisfy final gates.
9. Always ask the owner whether progress should be monitored manually or with a
   recurring heartbeat. When proposing heartbeat monitoring, default to
   5-minute checks and make clear that the owner can choose a different
   interval. Create a recurring heartbeat only when the owner selects it.
   Record the interval, monitored workers or workstreams, reporting
   destination, stop condition, and whether the heartbeat may steer workers or
   only report status. If no heartbeat is requested, monitor progress manually
   from the root thread at natural wave boundaries. Before steering, renaming,
   archiving, interrupting, replacing, or closing a worker, read the worker's
   latest state. Capture status, blockers, validation, risks, and next actions
   in the ledger.
10. Before reusing a worker for a new wave, changing overlapping scope, or
    integrating worker output, apply the lifecycle guidance in
    `references/worker.md`: resync against root-integrated work, choose a
    root-owned integration method, record generated ignored artifacts, and make
    an explicit worker closeout decision.
11. Before marking owner-ready, issue-closed, merge-ready, release-ready, or
    final, apply `references/gates.md`. Treat blocked live proof, deferred
    acceptance criteria, and worker-reported risks as gate inputs, not as notes
    to bury after closure.
12. For non-trivial code edits, require focused tests and `$autoreview`; rerun
   both after any review-triggered code change.
13. Before closing a source item that is only partially satisfied, create or
    link an owner-visible follow-up when mutation is authorized. For GitHub
    issue lifecycle work, use `$github-issues`; for PR replies, use
    `$github-review-threads`. For Markdown or local plans this may be a checkbox
    update, follow-up bullet, or proposed patch. If mutation is not authorized,
    keep the item owner-ready with the proposed update body and do not call it
    complete.
14. Before stopping, execute every `ready-next` action that is within current
    authorization. In PRD-backed workflows where branch plus draft PR delivery
    is authorized by the source contract, commit, push, and draft PR creation
    are authorized `ready-next` actions after gates pass. Reclassify any
    remaining `ready-next` item as `needs-owner`, `blocked`, or `deferred` with
    the missing decision, access, or follow-up.
15. Stop only after reconciling the original task sources against the ledger.
    The ledger must show no `active` worker requiring orchestration, no
    `autonomous` item that can still be delegated, no authorized `ready-next`
    action, and no newly surfaced source item. Remaining work must be
    `completed` with gates satisfied, `needs-owner` with a decision brief,
    `blocked` with minimum missing access/action, `released`, `deferred` with a
    linked or proposed follow-up, or `ignored-or-suppressed` with source key,
    reason, owner, date, and unchanged source fingerprint. Completed workers
    should be moved out of active tracking or explicitly marked as awaiting a
    root-owned closeout action.

## Final Report

Before handing control back to the owner, return a compact owner-facing report:

- overall status: `completed`, `needs-owner`, `blocked`, `deferred`,
  `released`, or mixed with the blocking reason;
- source items reconciled, with source ids/refs and closeout state;
- workers used, integration method per worker, and any worker output left
  unintegrated;
- commits, branches, PRs, issue updates, releases, or draft mutation commands
  produced under current authorization;
- gates and proof: tests, CI, autoreview, live proof, cross-repo proof, or why
  a proof path was unavailable;
- remaining owner decisions, blocked access, deferred follow-ups, and the next
  safe action.

## References

- `references/ledger.md`: named-ledger resolution, ledger template, portfolio
  overrides, and write ownership.
- `references/worker.md`: worker prompt template, authorization modes, no
  subdelegation rule, and final report format.
- `references/prd-backed-delivery.md`: PRD/generated-issue delivery contracts,
  publication authority, and closeout rules.
- `references/gates.md`: universal gate catalog for owner-ready, merge, release,
  CI, autoreview, and cross-repo integration decisions.

## Boundaries

- V1 does not include 1Password, specialized release executors, ledger-parsing
  scripts, or mandatory live GitHub write tests.
- Portfolio triage is read-only. Follow-up mutations require explicit user
  authorization and the matching standalone Git/GitHub skill.
- Do not depend on repo-local plugin bundles, plugin cache artifacts, or
  removed shared helper runtimes for GitHub work.
- The orchestrator owns ledger updates. Worker threads report facts and
  recommendations; they do not edit portfolio ledgers directly.
