---
name: study
description: Explicitly orchestrate read-only planning, research, and analysis in the current ChatGPT App task through one visible gpt-5.6-sol orchestrator at medium reasoning and at most five visible gpt-5.6-luna workers at max reasoning. Use only when the user explicitly invokes Study or selects this skill in the ChatGPT App. Never allow a Study orchestrator or worker to invoke Study. Treat five workers as an absolute cap, report when a larger request is capped, never write or edit project files, and always return a textual Markdown report.
---

# Study

## Non-negotiable scope

Study is an analysis and planning skill, not a coding or implementation skill.
This is a MUST rule:

- Use Study for requirements analysis, architecture exploration, repository
  investigation, technical research, comparison, risk analysis, test strategy,
  implementation planning, and other read-only discovery.
- Never write, edit, delete, rename, generate, or apply source code or project
  files. Do not produce a patch, commit, push, deployment, or other final
  implementation artifact.
- Never ask a worker to implement, fix, refactor, test by changing the
  project, or edit the result. Workers may inspect and reason only.
- If the current request is phrased as coding or implementation work, convert
  it into a read-only analysis or implementation plan. State the boundary in
  the final report and do not make code changes.
- Return the final result as textual Markdown in the parent session. Use the
  template in `references/output-template.md` as the report shape. Never save
  the report to a file during Study. If the user wants a saved artifact,
  finish the read-only run first and state that a separate non-Study workflow
  with explicit write authorization is required.
- Use only operations proven read-only. Do not use shell redirection, `tee`,
  formatters, package managers, test/build/lint commands that write caches or
  reports, or any command that may generate or update files. Do not mutate
  Git, GitHub issues or pull requests, comments, reviews, labels, releases,
  accounts, or external systems.
- The Codex App task-management operations explicitly authorized in this skill
  are deliberate orchestration effects and the only exception to the rule
  above. “Read-only” always means no project, repository, GitHub, account, or
  unrelated external mutation; it does not prohibit the authorized task
  creation, messaging, monitoring, or post-result archival requests.

## Activation and authorization

- Activate only after an explicit `$study` invocation, explicit selection of
  Study in the skill UI, or an equivalent direct instruction such as “execute
  Study for this task” in the ChatGPT App.
- Treat that explicit invocation as authorization for the current session to
  create one orchestrator task and for that orchestrator to create the worker
  tasks required by the protocol. Do not ask for a second task-creation
  confirmation at either level.
- Limit this authorization to task creation, task-to-task messages, task
  monitoring, and orchestrator-led archival of finished worker tasks for this
  Study run. Archive workers only after their terminal results are captured;
  never archive the orchestrator. Do not infer permission to modify the
  repository, commit, push, publish, deploy, change accounts, or perform
  unrelated external actions.
- If the ChatGPT App task tools are unavailable, stop without creating a CLI
  task, a generic subagent, or a replacement workflow. Report that Study
  requires the App task surface.
- Do not activate for an ordinary mention of “study”, a planning discussion,
  or an implicit match. `agents/openai.yaml` disables implicit invocation.
- Only the parent session may activate Study. After it creates the orchestrator,
  neither that orchestrator nor any worker may invoke Study for any reason,
  including an explicit downstream request. They must decline the recursive
  invocation, continue only within their existing bounded assignment when
  possible, and report the request to the parent. Never create a nested Study
  topology.

## Maximum topology

Create and maintain this read-only topology:

```text
current session
└── Study: [<run-tag>] <short title>       gpt-5.6-sol / medium / same project / local
    ├── Worker 1: [<run-tag>] <short title>  gpt-5.6-luna / max / same project / local
    ├── ...
    └── Worker N: [<run-tag>] <short title>  gpt-5.6-luna / max / same project / local
        where 0 <= N <= 5
```

Five is an absolute, non-bypassable worker cap for the entire Study run:

- For an explicit request of zero workers, plan zero and let the orchestrator
  perform the analysis itself.
- For an explicit request of one through four workers, plan exactly that count.
  Do not reduce or exceed it merely because another count seems more efficient.
- For an explicit request of exactly five workers, plan exactly five.
- If the user requests more than five workers, normalize the request to five
  without asking for confirmation and plan exactly five independently bounded
  assignments. Never create a sixth worker, delegate the overflow through
  child tasks, start a second orchestrator, or substitute another orchestration
  mechanism.
- Before worker creation, tell the parent that the request was capped and give
  the original requested count and the cap-limited planned count. Repeat the
  cap event, those counts, and the actual created count in the final report.
- An explicit request for exactly five workers selects five independently
  bounded read-only assignments. If task creation fails or remains unresolved,
  never compensate with a sixth request; report the lower actual count as
  partial.
- If the user does not specify a count, choose zero to five based on the
  analysis; do not create five by default. `original_requested_count` is then
  `unspecified`, `planned_worker_count` is the justified count after applying
  the cap, and `created_worker_count` is the number of real worker thread IDs
  returned.

These count rules have precedence over the general efficiency heuristic. A
creation failure may lower the actual created count, but never changes the
planned count or permits a replacement beyond its reserved slot.
Set `full_capacity_mode=yes` whenever `planned_worker_count=5`, whether the
source was an exact request, a capped request, or an orchestrator-selected
unspecified count. Record that source separately as `full_capacity_source`.

Use these routing terms consistently:

- `parent session`: the task where the user invoked Study; it creates and
  monitors the orchestrator and relays milestones to the user.
- `orchestrator`: the single Sol task created by the parent session; it is the
  immediate supervisor of every worker.
- `worker`: a Luna task created by the orchestrator; it reports only to the
  orchestrator unless the App requires the owning user to answer directly.
- `owning user`: the human authorized to answer approvals or input requests.

## Shared run tag and immutable titles

Choose one visual `run_tag` before the orchestrator is created:

- Format it as a concise lower-kebab value derived from the topic plus a short
  lowercase alphanumeric nonce, for example `auth-7k2`. Keep the complete tag
  under 18 characters.
- Treat brackets as title syntax, not part of the value: `[auth-7k2]`.
- Choose it once in the parent session and pass the exact value in the
  orchestrator handoff and every worker assignment. Never regenerate it.
- Give the orchestrator the exact title
  `Study: [<run-tag>] <short title>`.
- Give each worker the exact title
  `Worker N: [<run-tag>] <short title>`, with `N` assigned in creation order
  from 1 through 5.
- Keep titles concise, specific, and stable for the entire run. Do not include
  progress, status, dates, model settings, or changing worker counts.
- Pass the title in the initial `codex_app__create_thread` call. Do not use
  `codex_app__set_thread_title` later and do not repair a title by renaming the
  task.
- Treat the run tag and titles as display metadata only. Never use either as
  identity, state, a branch name, a correlation key, or a recovery key. Bind
  identity and lineage only to real thread IDs recorded in the ledger.
- If the App normalizes or returns a different title, report the mismatch and
  preserve the task identity; never silently rename it or reconstruct identity
  by searching for the run tag.

## Parent-session bootstrap

1. Build a complete read-only handoff from the current session before creating
   the orchestrator. Include the objective, accepted decisions, constraints,
   relevant repository or project context, current state, expected Markdown
   report, validation or evidence expectations, and unresolved risks. Do not
   assume the new task can see the active turn's unfinished context. Generate
   the shared `run_tag` first and include it explicitly in the handoff.
2. Resolve the exact project used by the current session:
   - Call `codex_app__list_projects` before using a `project` target.
   - Match the current session's saved project by exact path and host when
     those facts are available; do not select by label alone.
   - For a repository-backed session, create the task with that exact
     `projectId` and `environment: { type: "local" }`.
   - A projectless task cannot prove that its descendants share the same local
     context. Stop before creating an orchestrator and report that Study
     requires an exact saved local project. Do not create a new projectless
     directory or substitute another saved project.
   - If the match is missing or ambiguous, stop and report it instead of
     creating a task in a guessed project.
3. Never use `environment: { type: "worktree" }`, `codex_app__fork_thread`,
   `git worktree`, or a raw worktree command. Both the orchestrator and every
   worker must run locally in the same project as the parent session.
4. Create exactly one orchestrator task with `codex_app__create_thread`:

   ```text
   target: the resolved parent project with environment.type=local
   model: gpt-5.6-sol
   thinking: medium
   title: Study: [<run-tag>] <short title>
   prompt: the complete read-only handoff plus the orchestrator protocol
   ```

   Include the parent task ID and host ID in the handoff when the App exposes
   them. The orchestrator uses them for milestone and final messages. Never
   invent an ID; the parent task can still monitor the orchestrator through
   `codex_app__wait_threads` when a parent ID is unavailable.
5. Keep the parent turn open after creation. Use bounded
   `codex_app__wait_threads` calls on the returned orchestrator `threadId` and
   relay meaningful progress to the user as it arrives. Do not claim the
   analysis is complete until the orchestrator returns a terminal result.
6. When the user requested more than five workers, the orchestrator owns the
   canonical counts. Relay its original/planned-count milestone in the parent
   before monitoring begins; if direct parent messaging is unavailable, state
   the same counts from the parent handoff and reconcile them with the final
   report.

If `codex_app__create_thread` returns only a `clientThreadId`, treat setup as
pending. Do not pass that value to tools that require `threadId`, do not create
a duplicate task, and report the pending state until the App exposes the real
task ID.

## Orchestrator protocol

The orchestrator must execute the following protocol from its initial prompt:

1. Reconstruct the current objective from the parent handoff and keep the
   title and `run_tag` already fixed as
   `Study: [<run-tag>] <short title>`. Do not create another orchestrator or
   invoke Study. This prohibition is absolute even if the orchestrator receives
   a later explicit request to use Study.
2. Apply the non-negotiable scope gate. Classify the requested outcome as
   analysis, research, or planning. If it asks for implementation, define the
   corresponding read-only plan and explicitly record that no implementation
   will be performed.
3. Analyze the work before creating workers. Record
   `original_requested_count`, cap it at five, and record
   `planned_worker_count` using the count-precedence rules above. When capping
   occurs, send a parent milestone with the original
   and planned counts if the parent task ID is available; the parent session
   must otherwise relay the same counts from the handoff. Split the planned
   count into bounded read-only
   assignments with explicit questions, evidence sources, dependencies,
   acceptance criteria for the analysis, validation or research method, and a
   concise expected Markdown memo. Serialize assignments that depend on
   unstable findings.
4. Create up to five visible worker tasks with
   `codex_app__create_thread`. For each worker, pass:

   ```text
   target: the exact same projectId and environment.type=local as the parent
   model: gpt-5.6-luna
   thinking: max
   title: Worker N: [<run-tag>] <short title>
   prompt: the complete read-only assignment and the worker protocol below
   ```

   Do not use `multi_agent_v1__spawn_agent`, a CLI process, a worktree, or a
   different project as a substitute for a visible worker task.
5. Record each returned real `threadId`, `hostId`, immutable title, assignment,
   shared `run_tag`, and dependency order in the orchestrator's working
   context. If a creation result is uncertain, reconcile it with the App before
   retrying; never create a duplicate merely because an immediate response was
   lost.
6. Monitor all created workers with bounded `codex_app__wait_threads` calls,
   using returned cursors to avoid replaying the same progress. Use
   `codex_app__read_thread` for the exact status or final evidence needed for a
   decision. Do not busy-poll.
7. Use `codex_app__send_message_to_thread` for concise worker questions,
   evidence requests, dependency handoffs, blocker handling, and parent
   milestones. Keep routine research collaboration between each worker and
   this orchestrator; do not make the parent session relay every worker
   message.
8. Keep the parent informed at meaningful milestones when its real task ID is
   available: analysis scope fixed, workers created, material blocker, first
   terminal result, and final synthesis. If no parent ID is available, rely on
   the parent's `wait_threads` monitoring and include all milestones in the
   orchestrator's final result.
9. Wait for every created worker to become `completed`, `failed`, or explicitly
   `abandoned`. A `needs-attention` worker is nonterminal: notify the parent and
   pause until the owning user resolves the request or explicitly directs
   abandonment. Do not end merely because one worker finished.
10. Capture terminal evidence for every worker: its final memo when available,
    otherwise its final structured state, reason, error, and last message.
    After all workers are terminal or explicitly abandoned, request archival
    of every worker with `codex_app__set_thread_archived`. Keep the orchestrator
    unarchived so it remains as the single visible Study summary task. Record
    the archival call receipt and any bounded post-call verification
    separately; never hide an archival failure or request archival before
    terminal evidence has been captured.
11. Synthesize only observed evidence and reasoned conclusions. Do not edit
    the project, create code, apply patches, save implementation artifacts, or
    ask a worker to do any of those things. Return a Markdown report using
    `references/output-template.md`.
12. Send the final Markdown report to the parent task when possible and return
    the same report as the orchestrator's final response.

When a worker fails or a task-creation response is uncertain, preserve the
original worker number and title, reconcile the App state, and keep the run
within the five-worker cap. Do not create a replacement with a changing title
or silently restart a task that may already exist.

## Monitoring and recovery state machine

Track each planned worker slot separately from any task it creates. Slot states
are `not-started`, `pending-setup`, `created`, `creation-failed`, and
`unresolved-setup`:

- Reserve the slot before calling `create_thread`; never renumber, free, or
  reuse it during the run.
- A definitive creation error proving no task exists sets `creation-failed`.
  Continue with later planned slots but never retry that slot.
- A timeout, transport error, or response with neither ID and uncertain server
  state sets `pending-setup`, stops later creation, and follows the same bounded
  reconciliation as a returned `clientThreadId`.
- A returned `clientThreadId` stays in its own ledger field and must never be
  passed to thread-ID tools or counted in `created_worker_count`. Use up to
  three bounded `list_threads` snapshots and correlate only through an explicit
  matching client-ID field, never title or preview.
- If reconciliation fails, set `unresolved-setup`; leave every later planned
  slot `not-started` with reason `creation halted after uncertain slot`, and
  report a partial run. Never create replacements.
- A real `threadId` sets `created`. Before turn telemetry appears, track the
  task workflow state as `created-awaiting-turn`; bounded empty snapshots do not
  imply failure or justify replacement.

Track every real task in exactly one workflow state:

- `created-awaiting-turn`: a real ID exists but no turn status is observable.
- `active`: the latest turn is in progress.
- `completed`: the latest turn completed without error and the task is idle.
- `needs-attention`: structured App telemetry reports a nonempty actionable
  `activeFlags` value such as `waitingOnUserInput`, or `wait_threads` returns an
  explicit needs-attention wake. Preserve the raw flag or wake reason. Never
  infer this state from prose alone. Notify the parent session; the owning user
  must answer through the App surface.
- `monitoring-unavailable`: neither wait nor read telemetry can establish the
  current task state. Preserve the last known state and raw tool errors, notify
  the parent session, and pause. This is infrastructure observability, never a
  user-action `needs-attention` state.
- `failed`: the latest turn ended with an error. Record the raw error and
  preserve the task identity.
- `abandoned`: recovery is proven unavailable, or the owning user explicitly
  abandons a `needs-attention` task. Record the exact reason.

Maintain separate `wait_cursor` and `read_page_cursor` values per real task.
Only a `wait_threads` cursor is reused as `afterCursor`; only a `read_thread`
page cursor is reused for pagination. An incoming parent message may interrupt
a wait without invalidating the last confirmed wait cursor; resume from that
cursor. Deduplicate evidence by returned revision and message or event ID, not
by prose. On a wait error, use `read_thread`; if monitoring remains unavailable,
mark `monitoring-unavailable` and notify the parent. Never turn missing
telemetry into a success claim. Resume only when either telemetry surface
recovers; if recovery is proven impossible, the owning user may explicitly
direct abandonment.

Track archival separately from slot and task state. Request archival only for
`completed`, `failed`, or explicitly `abandoned` workers after terminal
evidence is captured. For a failed or abandoned worker, structured final state,
reason, error, and last telemetry substitute for a missing memo. Record the
`set_thread_archived` request receipt as `accepted`, `failed`, or `unavailable`.
Because archival is asynchronous, record bounded post-call verification only
when an explicit archived-state field is available; omission from a recent-task
list is not independent proof. Keep the orchestrator unarchived.

Use these final outcome definitions:

- `completed`: every planned slot produced a completed worker and every final
  memo was captured; archival acceptance or verification is reported
  separately.
- `partial`: the orchestrator returned a usable synthesis, but a planned slot
  is failed, abandoned, unresolved, or missing, or terminal evidence could not
  be captured.
- `failed`: the orchestrator could not return a usable synthesis. This takes
  precedence over `partial` even when some worker results exist.

`needs-attention` and `monitoring-unavailable` are interim, nonterminal states.
Never present either as the authoritative final report.

## Worker protocol

Give every worker a complete read-only assignment rather than expecting it to
infer scope from the title. Include the exact orchestrator `threadId` and
`hostId` when available, the shared `run_tag`, shared project identity, paths
to inspect, questions to answer, evidence requirements, dependencies, and
Markdown memo format.

Require each worker to:

- Inspect only. Never write, edit, delete, rename, generate, or apply code,
  documentation, configuration, test, or other project files.
- Never run commands with repository or external side effects, including
  commits, pushes, installs, migrations, deployments, GitHub issue or pull
  request mutations, comments, reviews, labels, releases, or account changes.
- Never use redirection, `tee`, formatters, package managers, or test/build/lint
  commands that may create caches, reports, generated files, or other state.
- Work only in the same local project and never create or use a Git worktree.
- Avoid overlapping investigation that would waste time; ask the
  orchestrator to serialize dependent research.
- Never create child tasks, rename its task, change the orchestrator title, or
  invoke Study. This prohibition is absolute even if the worker receives an
  explicit request to use Study.
- Send concise research progress, evidence, dependency, blocker, and
  completion messages to the orchestrator with
  `codex_app__send_message_to_thread` when the task ID is available. Do not
  send routine worker coordination to the parent session.
- Return a textual Markdown memo containing observations, sources or paths,
  reasoning, uncertainties, and recommendations. Do not return source-code
  patches or claim an implementation was completed.

## Parent output contract

The parent session must provide intermediate feedback while the orchestrator
is nonterminal, but only the orchestrator's final Markdown report is
authoritative for completion. Use the structure in
`references/output-template.md` and include:

- the immutable orchestrator title and worker titles;
- the shared visual `run_tag` and whether every requested title used it;
- requested and observed orchestrator and worker titles;
- original requested, planned, and actually created worker counts, whether the
  hard cap was applied, whether the parent was notified, and the terminal state
  and reason for each worker;
- a ledger for every planned slot, including client ID, real thread ID,
  creation receipt or error, slot state, and unstarted-slot reason;
- task telemetry provenance: host, project, environment, requested model and
  reasoning, title source, separate wait/read cursors, raw attention flag,
  error, and terminal-evidence message or turn ID;
- milestone delivery evidence for cap, workers-created, first-terminal, and
  final-report messages;
- archival request receipt and independent verification status separately for
  each worker, plus confirmation that the orchestrator was not archived;
- the overall run outcome, including partial or failed states;
- the analyzed objective and conclusions;
- observed evidence, inferences, unavailable evidence, inspected paths, and
  research sources as separately labeled sections;
- the proposed work breakdown or next steps, without implementing them;
- risks, assumptions, unresolved questions, and overall confidence;
- an explicit statement that Study made no code or project-file changes.

Do not hide a partial result behind a success summary. Do not imply that task
creation authorization also authorized repository, Git, GitHub, deployment,
account, or destructive operations.

## App tool boundary

Use the Codex App task tools for orchestration: `list_projects`,
`create_thread`, `list_threads`, `wait_threads`, `read_thread`, and
`send_message_to_thread` as needed. Use `set_thread_archived` only for the
post-result worker archival phase. Use other tools only for read-only research
or inspection. Keep `model` and `thinking` fixed at creation time. Never switch
to worktrees, generic subagents, raw shell task launchers, or a second
orchestration mechanism.

The authorized App task-management calls above are the only exceptions to the
no-side-effect rule. Apply this availability matrix before and during a run:

- `list_projects` and `create_thread` are required before any topology exists;
  if either is unavailable, stop without creating tasks.
- `wait_threads` is required for normal monitoring. If unavailable after task
  creation, use bounded `read_thread` snapshots; if both are unavailable,
  report `monitoring-unavailable` and pause.
- `read_thread` is the required fallback for wait errors and exact final memo
  capture. If unavailable only after a clean wait completion, use the final
  message returned by `wait_threads` and report the missing independent read.
- `send_message_to_thread` is optional when the parent task ID is unavailable
  or monitoring already exposes milestones; report that direct messaging was
  not exercised.
- `list_threads` is optional except for explicit client-ID reconciliation. A
  missing tool makes the reserved slot `unresolved-setup` as described above.
- `set_thread_archived` is post-result cleanup. Its absence or failure is an
  archive-request error, not a reason to hide an otherwise valid analysis
  result. A successful receipt proves acceptance only unless another surface
  exposes an explicit archived-state field.
