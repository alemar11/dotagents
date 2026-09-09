---
name: explore
description: "Run an explicitly requested read-only exploration in the current task or session with optional bounded delegation."
---

# Explore

Follow the shared [execution scope](../../references/execution-scope.md) for
standalone and composed invocation.

## Purpose and boundary

Explore the relevant evidence first, refine the exploration scope through
`se:grilling-session`, then investigate remaining questions and return a
Markdown exploration report in the current conversation.

Explore is not an implementation workflow:

- Never write, edit, delete, rename, generate, or apply project files.
- Never produce a patch, commit, push, deployment, publication, or other
  implementation artifact.
- If the user switches to implementation, end Explore with its findings and
  continue through the authorized implementation workflow. Do not reinterpret
  that request as analysis only.
- Delegate inspection and reasoning only. Never ask a worker to implement,
  fix, refactor, or change tests.
- Use only operations proven read-only. Do not run commands that may update
  caches, reports, lockfiles, generated files, Git state, hosted records,
  accounts, or external systems.
- Return the report in the active Explore controller. Do not save it to a file.
  If the user explicitly requests a saved report, finish Explore and perform
  that scoped file write separately.

The explicit invocation authorizes native subagent delegation under the policy
below. It grants no project, repository, GitHub, account, or unrelated external
mutation authority.

## Activation and recursion guard

- Activate only after an explicit `$se:explore` invocation, explicit Explore UI
  selection, or an equivalent direct instruction to execute Explore.
- Do not activate for an ordinary mention of “explore” or an implicit planning
  match. `agents/openai.yaml` disables implicit invocation.
- The invoking task or session remains the Explore controller. Worker subagents
  never invoke Explore, create controllers, or delegate further work.
- If a downstream prompt requests recursive Explore, decline that part, continue
  the existing bounded assignment when possible, and report the request to the
  controller.

## Current-session execution

Run the entire Explore in the invoking task or session on both App and CLI.
Never create a visible task, fork the session, or transfer Explore to another
controller. Retain the current model, reasoning settings, working directory,
and conversation context; no saved-project lookup or surface classification
is required.

Use the user's request and existing conversation directly. Do not construct a
curated handoff or a separate transfer brief before beginning. Grilling Session
refines the objective, scope, constraints, evidence expectations, and unresolved
questions in place. Its result remains conversational context, not a file or
an input for another controller. Prepare bounded assignments only if workers
are subsequently selected.

Read [references/states.md](references/states.md) before interpreting Grilling
Session, capacity, worker, or outcome state. Initial exploration is direct
controller work; worker planning begins only after Grilling Session.

## Required sequence

1. Explore the subject directly using the request and existing conversation.
   Read the relevant source, tests, documentation, and supplied external
   evidence. Establish how the current system works, plausible explanations
   or approaches, and the unknowns that affect the user's goal. Reuse evidence
   already inspected; do not restart research merely because Explore was invoked.
   Keep this pass bounded to what makes the next decisions informed, rather
   than exhaustively researching every branch. If the subject or access cannot
   be established, ask only the clarification needed to begin.
2. Briefly share the useful findings, separating observations from hypotheses,
   and compose `$se:grilling-session` using that evidence and the conversation.
   Focus its questions on unresolved intent, scope, constraints, and tradeoffs.
   Do not ask the user for facts the exploration already established or invent
   ambiguity to prolong the interview. Exploration findings are provisional
   until checked against the user's intent.
3. Ask one question per turn until Grilling Session returns `refined`, the user
   stops with `user-stopped`, or the interview is `blocked`. Create no workers
   while the interview is awaiting an answer. A blocked interview fails Explore
   before worker creation.
4. Use the confirmed scope, or best-supported interpretation after the user
   stops, to guide the investigation. Preserve unconfirmed items and apply the
   read-only scope gate again.
5. Read [references/orchestration.md](references/orchestration.md), determine
   the useful subagent count and assignments, and investigate the remaining
   questions. Reuse the initial exploration; revisit findings only when answers
   or new evidence change their assumptions. If the existing evidence is
   sufficient, synthesize directly without another research pass.
6. Reconcile worker setup, monitor every created worker to a terminal or
   explicitly abandoned state, capture available evidence, and synthesize the
   result. Never replace a failed or unresolved reserved slot.
7. Read [references/output-template.md](references/output-template.md) and
   return the report here.

## Worker-count policy

Five is an absolute cap across the entire Explore run:

- An explicit request for zero through five workers sets
  `planned_worker_count` to exactly that count.
- A request above five is capped to five without another confirmation. Record
  the original and normalized counts, tell the user before worker creation,
  and report the cap in the result.
- An unspecified count is chosen only after Grilling Session, using the smallest
  useful number from zero through five. Do not default to five.
- Setup failure may lower `created_worker_count`, but it never changes the
  planned count, frees a reserved slot, or authorizes a replacement.

Set `worker_transport` from the planned count:

- `none` when `planned_worker_count=0`;
- `subagent` for a positive plan.

If native subagent transport is unavailable, retain the planned slots, record
their failures, and continue
with a partial controller synthesis when useful. Never fall back to visible
tasks, external processes, or another transport.

## Output contract

The report must distinguish direct observations, inferences, unavailable
evidence, and assumptions. Include the agreed scope, inspected paths and
sources, worker plan and ledger when applicable, results, risks, confidence,
and the smallest useful next action. Do not reconstruct a controller handoff
or report App task placement, title, or setup telemetry.

In every case, report `Changes made: None`.
