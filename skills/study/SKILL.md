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
  the cap, and `created_worker_count` is the number of stable worker identities
  returned.

These count rules have precedence over the general efficiency heuristic. A
creation failure may lower the actual created count, but never changes the
planned count or permits a replacement beyond its reserved slot.
Set `full_capacity_mode=yes` whenever `planned_worker_count=5`, whether the
source was an exact request, a capped request, or an orchestrator-selected
unspecified count. Record that source separately as `full_capacity_source`.

### Default worker-count heuristic

Apply this heuristic only when `original_requested_count=unspecified`; explicit
worker-count requests and the cap rules above take precedence. Choose the
smallest band that gives every worker a distinct, bounded assignment with its
own evidence and acceptance criteria:

- **1–2 workers:** use for a focused question, one repository or source family,
  or one or two clearly separable investigation surfaces.
- **3 workers:** use as the normal default for a multi-dimensional comparison
  or study, typically splitting local contract, external subject, and
  comparative fit or recommendation.
- **4–5 workers:** use only for a broad investigation with four or five
  genuinely independent tracks, such as separate runtime, architecture,
  maintenance, validation, and UX/security questions. Do not add workers merely
  to reduce latency or duplicate the same source review.

If no meaningful parallel split exists, choose zero and let the orchestrator
perform the analysis. When the evidence is borderline between bands, prefer the
lower band. A plan of five is full-capacity mode and must be justified in the
report; five is a cap, not the default.

Use these routing terms consistently:

- `parent session`: the task where the user invoked Study; it creates and
  monitors the orchestrator and relays milestones to the user.
- `orchestrator`: the single Sol task created by the parent session; it is the
  immediate supervisor of every worker.
- `worker`: a Luna task created by the orchestrator; it reports only to the
  orchestrator unless the App requires the owning user to answer directly.
- `owning user`: the human authorized to answer approvals or input requests.

## Study App task contract

The parent and orchestrator interact with Codex App directly through current
live capabilities for creation, observation, monitoring, messaging, titles,
and archival.
This skill owns Study's outcomes, topology, authorization, lifecycle, and
verification. The model uses the current live Codex capabilities directly.

Resolve the exact saved project and host from authoritative App state before
creating the orchestrator. Every Study task must remain in that same project
and local environment without a worktree. The model calls the live creation
tool once per authorized orchestrator or worker slot, treating the immediate
response only as a receipt. After a real task ID exists, independently read or
list the task and verify its identity, project, host, environment, state,
requested Study settings when exposed, and title as separate metadata.

A rejection, timeout, transport error, client-side setup identifier, or other
uncertain response requires bounded reconciliation through the live App before
any retry. Reuse the exact task when it exists. Retry a reserved slot only when
authoritative evidence proves that no task was created and the slot's recovery
rules permit it; otherwise mark the slot unresolved and stop later creation.
Never correlate or reconstruct identity from a title, prompt preview, or timing.

## Shared run tag and requested titles

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
- Request the canonical title during creation when the current live
  capabilities support that outcome. Do not treat the creation receipt or a
  title embedded in the prompt as visible-title evidence.
- After a stable task identity exists, independently observe the task. If
  the observed title exactly matches the requested title, record
  `title-verified` and keep the creation-time result. If the title is missing,
  unavailable, or different, apply the requested title at most once when title
  mutation is available. Independently observe the task again and record
  the creation receipt, any fallback receipt, observed title, evidence source,
  and `title-unverified` or `title-drift` warning before continuing. If
  creation-time title initialization is unavailable, use this fallback when
  available.
- Never rename a task again to repair drift. Title setup and title readback are
  best-effort metadata: once the real task ID, project, environment, state,
  and requested Study profile are independently verified, continue creating
  or monitoring tasks with the warning attached. Require an exact title only
  when the user explicitly requests one; otherwise a title warning is not a
  setup failure.
- Treat the run tag and titles as display metadata only. Never use either as
  identity, state, a branch name, a correlation key, or a recovery key. Bind
  identity and lineage only to stable task identities recorded in the ledger.
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
   - Resolve the current session's authoritative saved project before creating
     the orchestrator. Match by exact path and host; do not select by label
     alone.
   - Require the orchestrator and every worker to use that exact saved project
     directly in its local environment.
   - A standalone task outside the saved project cannot prove that its
     descendants share the same local context. Stop before creation and report
     that Study requires an exact saved local project; do not substitute
     another destination.
   - If the match is missing or ambiguous, stop and report it instead of
     creating a task in a guessed project.
3. Never use an isolated checkout, a task fork, a Git worktree, or a raw
   worktree command. Both the orchestrator and every worker must run locally in
   the same authoritative project and host as the parent session.
4. Create exactly one orchestrator once. Require the resolved local project,
   `gpt-5.6-sol` at medium reasoning, the canonical Study title when supported,
   and the complete read-only handoff plus orchestrator protocol.

   The Sol/medium profile is mandatory Study policy. Treat the explicit
   `$study` invocation as authorization for it; never inherit the calling
   task's profile. After a stable task identity is available, independently
   verify `Study: [<run-tag>] <short title>`. If creation did not set that exact
   title, apply the verified title fallback at most once and verify it again.
   Do not create workers until the orchestrator's real task ID, project,
   environment, state, and requested model/reasoning are verified. A missing or
   different title becomes `title-unverified` or `title-drift` telemetry and
   does not block worker creation unless the user explicitly required the
   exact title.
   The creation request proves only the requested settings. Compare active
   model and reasoning telemetry independently when the App exposes it; if it
   differs, report `settings-drift` and stop before creating workers. If it is
   unavailable, record that limitation and never claim applied Sol settings
   from the prompt or creation request alone.

   Include the stable parent task and host identities in the handoff when they
   are observable. The orchestrator uses them for milestone and final messages.
   Never invent an identity; the parent can still monitor the orchestrator when
   direct parent messaging is unavailable.
5. If structural identity, project/environment, state, or requested settings
   cannot be verified for the orchestrator, stop before creating workers and
   report the exact setup failure. A title warning alone does not stop Study;
   preserve the real task ID and continue without creating a replacement.
6. Keep the parent turn open after creation. Monitor the exact orchestrator
   with bounded waits and relay meaningful progress to the user as it arrives.
   Do not claim the analysis is complete until the orchestrator returns a
   terminal result.
7. When the user requested more than five workers, the orchestrator owns the
   canonical counts. Relay its original/planned-count milestone in the parent
   before monitoring begins; if direct parent messaging is unavailable, state
   the same counts from the parent handoff and reconcile them with the final
   report.

If creation returns only a provisional setup identity, treat setup as pending.
Do not use it as a stable task identity, do not create a duplicate task, and
report the pending state until the real task can be observed.

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
4. Create up to five visible worker tasks. For each reserved slot, create once
   in the same authoritative local project and host as the parent, using
   `gpt-5.6-luna` at max reasoning, the canonical worker title when supported,
   and the complete read-only assignment plus worker protocol.

   The Luna/max profile is mandatory Study policy and must not be inherited
   from the orchestrator. After each stable task identity is available,
   independently verify `Worker N: [<run-tag>] <short title>`. If creation did
   not set that exact title, apply the verified title fallback at most once
   and verify it again
   before recording `title-unverified` or `title-drift` telemetry. Do not use
   the prompt as title evidence. Compare active model and reasoning telemetry
   when exposed; record `settings-drift` for any mismatch and do not create a
   replacement. A title warning does not prevent the worker from starting.

   Do not use a generic subagent mechanism, CLI process, worktree, or different
   project as a substitute for a visible worker task.
5. Record each stable task identity, host identity, initialized title,
   assignment, shared `run_tag`, and dependency order in the orchestrator's working
   context. If a creation result is uncertain, reconcile it with the App before
   retrying; never create a duplicate merely because an immediate response was
   lost.
6. Monitor all created workers with bounded waits that resume from the latest
   observed progress and independently inspect exact status or final evidence
   when needed for a decision. Do not busy-poll.
7. Send concise worker questions, evidence requests, dependency handoffs,
   blocker handling, and parent milestones directly between the relevant
   tasks. Keep routine research collaboration between each worker and this
   orchestrator; do not make the parent session relay every worker message.
8. Keep the parent informed at meaningful milestones when its real task ID is
   available: analysis scope fixed, workers created, material blocker, first
   terminal result, and final synthesis. If no parent ID is available, rely on
   the parent's monitoring and include all milestones in the
   orchestrator's final result.
9. Wait for every created worker to become `completed`, `failed`, or explicitly
   `abandoned`. A `needs-attention` worker is nonterminal: notify the parent and
   pause until the owning user resolves the request or explicitly directs
   abandonment. Do not end merely because one worker finished.
10. Capture terminal evidence for every worker: its final memo when available,
    otherwise its final structured state, reason, error, and last message.
    After all workers are terminal or explicitly abandoned, request archival
    of every worker through the live task lifecycle. Keep the orchestrator
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
are `not-started`, `pending-setup`, `created`, `creation-failed`,
`settings-drift`, and `unresolved-setup`:

- Reserve the slot before creating a task; never renumber, free, or
  reuse it during the run.
- A definitive creation error proving no task exists sets `creation-failed`.
  Continue with later planned slots but never retry that slot.
- A timeout, transport error, or response with neither ID and uncertain server
  state sets `pending-setup`, stops later creation, and follows the same bounded
  reconciliation as any other provisional setup result.
- A provisional setup identity stays separate from stable task identity and
  must not count as a created worker. Use up to three bounded authoritative
  snapshots and correlate only through explicit identity evidence, never title,
  prompt preview, or timing.
- A real task whose title cannot be initialized or independently verified keeps
  the `created` slot state. Record `title-unverified` or `title-drift` beside
  the real ID and evidence, do not retry or create a replacement, and continue
  the worker flow. Only an explicit exact-title request may turn that warning
  into a setup failure.
- A real task whose observed model or reasoning differs from the requested
  creation settings sets `settings-drift`. Preserve its real ID and evidence,
  do not retry or create a replacement, and report the run as partial unless
  the orchestrator itself failed settings verification before any worker was
  created.
- If reconciliation fails, set `unresolved-setup`; leave every later planned
  slot `not-started` with reason `creation halted after uncertain slot`, and
  report a partial run. Never create replacements.
- A stable task identity sets `created`. Before turn telemetry appears, track the
  task workflow state as `created-awaiting-turn`; bounded empty snapshots do not
  imply failure or justify replacement.

Track every real task in exactly one workflow state:

- `created-awaiting-turn`: a real ID exists but no turn status is observable.
- `active`: the latest turn is in progress.
- `completed`: the latest turn completed without error and the task is idle.
- `needs-attention`: structured task telemetry reports an explicit actionable
  request. Preserve the observed reason and never infer this state from prose
  alone. Notify the parent session; the owning user must answer through the App.
- `monitoring-unavailable`: neither wait nor read telemetry can establish the
  current task state. Preserve the last known state and raw tool errors, notify
  the parent session, and pause. This is infrastructure observability, never a
  user-action `needs-attention` state.
- `failed`: the latest turn ended with an error. Record the raw error and
  preserve the task identity.
- `abandoned`: recovery is proven unavailable, or the owning user explicitly
  abandons a `needs-attention` task. Record the exact reason.

Maintain separate progress and inspection positions per real task according to
the live capabilities that produced them; never interchange them. An incoming
parent message may interrupt a wait without invalidating the last confirmed
progress position. Deduplicate evidence by stable revisions or event identity,
not by prose. If one monitoring path fails, independently inspect the exact
task; if monitoring remains unavailable, mark `monitoring-unavailable` and
notify the parent. Never turn missing telemetry into a success claim. Resume
only when authoritative observation recovers; if recovery is proven impossible,
the owning user may explicitly direct abandonment.

Track archival separately from slot and task state. Request archival only for
`completed`, `failed`, or explicitly `abandoned` workers after terminal
evidence is captured. For a failed or abandoned worker, structured final state,
reason, error, and last telemetry substitute for a missing memo. Record the
archival request receipt as `accepted`, `failed`, or `unavailable`.
Because archival is asynchronous, record bounded post-request verification only
when authoritative archival state is observable; omission from a recent-task
view is not independent proof. Keep the orchestrator unarchived.

Use these final outcome definitions:

- `completed`: every planned slot produced a completed worker and every final
  memo was captured; archival acceptance or verification is reported
  separately.
- `partial`: the orchestrator returned a usable synthesis, but a planned slot
  is failed, abandoned, settings-drift, unresolved, or missing, or terminal
  evidence could not be captured. Title warnings alone do not make the run
  partial.
- `failed`: the orchestrator could not return a usable synthesis. This takes
  precedence over `partial` even when some worker results exist.

`needs-attention` and `monitoring-unavailable` are interim, nonterminal states.
Never present either as the authoritative final report.

## Worker protocol

Give every worker a complete read-only assignment rather than expecting it to
infer scope from the title. Include the exact orchestrator and host identities
when available, the shared `run_tag`, shared project identity, paths
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
  completion messages directly to the orchestrator when its stable identity is
  available. Do not
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
- a ledger for every planned slot, including provisional and stable task
  identities, creation receipt or error, slot state, and unstarted-slot reason;
- task telemetry provenance: host, project, environment, requested model and
  reasoning, title source, separate monitoring positions, observed attention
  reason, error, and terminal-evidence identity;
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

## Codex interaction boundary

Use the current live Codex capabilities directly for the authorized Study task
topology and use other capabilities only for read-only research or inspection.
Never switch to isolated checkouts, generic subagents, raw shell task launchers,
or a second orchestration mechanism. Keep the Sol/medium orchestrator and
Luna/max worker profiles fixed as semantic Study policy.

Before mutation, establish that the live runtime can create and independently
observe the requested topology, monitor exact tasks, exchange required
messages, and request post-result worker archival. Do not serialize or mirror
the live interface. If structural identity, project, local execution, state,
settings, monitoring, or cleanup cannot be established, stop or use the
specific recovery behavior above. Title initialization and archival are
best-effort metadata and lifecycle capabilities: report their absence or
failure without replacing a structurally verified task or hiding a valid
analysis result.
