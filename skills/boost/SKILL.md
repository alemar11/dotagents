---
name: boost
description: Explicitly orchestrate read-only planning, research, and analysis in the current ChatGPT App task through one visible gpt-5.6-sol orchestrator at medium reasoning and up to five visible gpt-5.6-luna workers at max reasoning. Use only when the user explicitly invokes Boost or selects this skill in the ChatGPT App. Never use Boost to write code, edit files, or implement a solution; always return a textual Markdown report.
---

# Boost

## Non-negotiable scope

Boost is an analysis and planning skill, not a coding or implementation skill.
This is a MUST rule:

- Use Boost for requirements analysis, architecture exploration, repository
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
  template in `references/output-template.md` as the default report shape.
  Save a Markdown report file only when the user separately requests that
  text artifact; never save code through Boost.

## Activation and authorization

- Activate only after an explicit `$boost` invocation, explicit selection of
  Boost in the skill UI, or an equivalent direct instruction such as “execute
  Boost for this task” in the ChatGPT App.
- Treat that explicit invocation as authorization for the current session to
  create one orchestrator task and for that orchestrator to create the worker
  tasks required by the protocol. Do not ask for a second task-creation
  confirmation at either level.
- Limit this authorization to task creation, task-to-task messages, and task
  monitoring for this Boost run. Do not infer permission to modify the
  repository, commit, push, publish, deploy, change accounts, or perform
  unrelated external actions.
- If the ChatGPT App task tools are unavailable, stop without creating a CLI
  task, a generic subagent, or a replacement workflow. Report that Boost
  requires the App task surface.
- Do not activate for an ordinary mention of “boost”, a planning discussion,
  or an implicit match. `agents/openai.yaml` disables implicit invocation.

## Fixed topology

Create and maintain this read-only topology:

```text
current session
└── Boost: <short title>       gpt-5.6-sol / medium / same project / local
    ├── Worker 1: <short title>  gpt-5.6-luna / max / same project / local
    ├── Worker 2: <short title>  gpt-5.6-luna / max / same project / local
    ├── Worker 3: <short title>  gpt-5.6-luna / max / same project / local
    ├── Worker 4: <short title>  gpt-5.6-luna / max / same project / local
    └── Worker 5: <short title>  gpt-5.6-luna / max / same project / local
```

Create only the number of workers justified by the analysis, from zero to
five. Do not create five workers by default. Use fewer workers when the task
is small, sequential, or has overlapping investigation scope.

## Immutable titles

Choose all titles before the corresponding task is created:

- Give the orchestrator the exact title `Boost: <short title>`.
- Give each worker the exact title `Worker N: <short title>`, with `N` assigned
  in creation order from 1 through 5.
- Keep titles concise, specific, and stable for the entire run. Do not include
  progress, status, dates, model settings, or changing worker counts.
- Pass the title in the initial `codex_app__create_thread` call. Do not use
  `codex_app__set_thread_title` later and do not repair a title by renaming the
  task.
- Treat titles as display metadata only. Never use a title as identity, state,
  a branch name, or a recovery key.
- If the App normalizes or returns a different title, report the mismatch and
  preserve the task identity; never silently rename it.

## Parent-session bootstrap

1. Build a complete read-only handoff from the current session before creating
   the orchestrator. Include the objective, accepted decisions, constraints,
   relevant repository or project context, current state, expected Markdown
   report, validation or evidence expectations, and unresolved risks. Do not
   assume the new task can see the active turn's unfinished context.
2. Resolve the exact project used by the current session:
   - Call `codex_app__list_projects` before using a `project` target.
   - Match the current session's saved project by exact path and host when
     those facts are available; do not select by label alone.
   - For a repository-backed session, create the task with that exact
     `projectId` and `environment: { type: "local" }`.
   - For a projectless session, use `target.type: "projectless"` and the same
     projectless directory context when available. Do not substitute another
     saved project.
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
   title: Boost: <short title>
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

If `codex_app__create_thread` returns only a `clientThreadId`, treat setup as
pending. Do not pass that value to tools that require `threadId`, do not create
a duplicate task, and report the pending state until the App exposes the real
task ID.

## Orchestrator protocol

The orchestrator must execute the following protocol from its initial prompt:

1. Reconstruct the current objective from the parent handoff and keep the
   title already fixed as `Boost: <short title>`. Do not create another
   orchestrator or recursively invoke Boost.
2. Apply the non-negotiable scope gate. Classify the requested outcome as
   analysis, research, or planning. If it asks for implementation, define the
   corresponding read-only plan and explicitly record that no implementation
   will be performed.
3. Analyze the work before creating workers. Split it into bounded read-only
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
   title: Worker N: <short title>
   prompt: the complete read-only assignment and the worker protocol below
   ```

   Do not use `multi_agent_v1__spawn_agent`, a CLI process, a worktree, or a
   different project as a substitute for a visible worker task.
5. Record each returned real `threadId`, `hostId`, immutable title, assignment,
   and dependency order in the orchestrator's working context. If a creation
   result is uncertain, reconcile it with the App before retrying; never create
   a duplicate merely because an immediate response was lost.
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
9. Wait for every created worker to become terminal, blocked, or explicitly
   abandoned. Do not end the orchestrator merely because one worker finished.
10. Synthesize only observed evidence and reasoned conclusions. Do not edit
    the project, create code, apply patches, save implementation artifacts, or
    ask a worker to do any of those things. Return a Markdown report using
    `references/output-template.md`.
11. Send the final Markdown report to the parent task when possible and return
    the same report as the orchestrator's final response.

When a worker fails or a task-creation response is uncertain, preserve the
original worker number and title, reconcile the App state, and keep the run
within the five-worker cap. Do not create a replacement with a changing title
or silently restart a task that may already exist.

## Worker protocol

Give every worker a complete read-only assignment rather than expecting it to
infer scope from the title. Include the exact orchestrator `threadId` and
`hostId` when available, the shared project identity, paths to inspect,
questions to answer, evidence requirements, dependencies, and Markdown memo
format.

Require each worker to:

- Inspect only. Never write, edit, delete, rename, generate, or apply code,
  documentation, configuration, test, or other project files.
- Never run commands with repository or external side effects, including
  commits, pushes, installs, migrations, deployments, or account changes.
- Work only in the same local project and never create or use a Git worktree.
- Avoid overlapping investigation that would waste time; ask the
  orchestrator to serialize dependent research.
- Never create child tasks, rename its task, change the orchestrator title, or
  invoke Boost recursively.
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
- the number of workers created and the terminal state of each;
- the analyzed objective and conclusions;
- observed evidence, inspected paths, and research sources;
- the proposed work breakdown or next steps, without implementing them;
- risks, assumptions, unresolved questions, and confidence;
- an explicit statement that Boost made no code or project-file changes.

Do not hide a partial result behind a success summary. Do not imply that task
creation authorization also authorized repository, Git, GitHub, deployment,
account, or destructive operations.

## App tool boundary

Use the Codex App task tools for orchestration: `list_projects`,
`create_thread`, `wait_threads`, `read_thread`, and
`send_message_to_thread` as needed. Use other tools only for read-only
research or inspection. Keep `model` and `thinking` fixed at creation time.
Never switch to worktrees, generic subagents, raw shell task launchers, or a
second orchestration mechanism.
