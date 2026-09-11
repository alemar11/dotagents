---
name: explore
description: "Run an explicitly requested read-only exploration in the current task or session with optional bounded delegation."
---

# Explore

## Scope and execution

Activate only for explicit `$explore`, Explore UI selection, or an equivalent
instruction to execute this workflow, never an ordinary mention or implicit
planning match. Follow this sequence in the invoking task or session: context
preparation, direct exploration, Grilling Session, remaining investigation,
then a conversational report. Retain its working directory
and context; no replacement controller, visible task, fork, transfer brief,
saved-project lookup or surface classification is needed.

Explore and its workers inspect and reason only. Use operations proven read-only:
no project files, patches, generated artifacts, caches, reports, lockfiles, Git
state, hosted records, accounts or external systems may be mutated. Explicit
invocation authorizes bounded native subagents, not implementation or external
writes. Workers cannot invoke Explore, create controllers or delegate further;
decline recursive requests, continue valid assigned work and report them to the
controller.

Return findings here without saving a file. If the user requests a saved report
or switches to implementation, finish Explore and perform that separately
authorized work through its owning workflow. Read
[states.md](references/states.md) before interpreting interview, worker or outcome
state. No workers are created before Grilling Session finishes.

## Context preparation

Before initial exploration, compose `$learn` in a strictly read-only context
inspection using `memory_slice=domain-memory`,
`domain_operation=periodic-review`, and `capture_mode=defer-to-caller`.
Require it to read the applicable `AGENTS.md` chain, root `CONTEXT.md`, matched
first-class subproject context, and only topic files or ADRs relevant to the
subject. Reuse current evidence already gathered in this conversation. Do not
request setup, repair, compaction, or capture.

Explore owns this dependency. If Learn is unavailable, report that blocker
before exploration or worker creation. If no repository context exists,
continue from the supplied conversation and sources, recording that no
established project knowledge was found. Keep findings in the current
conversation for exploration and the subsequent interview; Grilling Session
does not call Learn again.

## Required sequence

1. Complete the context preparation above, then explore the subject directly
   using the request, conversation, and available project knowledge.
   Read the relevant source, tests, documentation, and supplied external
   evidence. Establish how the current system works, plausible explanations
   or approaches, and the unknowns that affect the user's goal. Reuse evidence
   already inspected; do not restart research merely because Explore was invoked.
   Keep this pass bounded to what makes the next decisions informed, rather
   than exhaustively researching every branch. If the subject or access cannot
   be established, ask only the clarification needed to begin.
2. Briefly share the useful findings, separating observations from hypotheses,
   and compose `$grilling-session` using that evidence and the conversation.
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
6. Collect helper results, resolve evidence gaps where possible, and synthesize
   the answer. Report limitations in evidence or independence.
7. Read [references/output-template.md](references/output-template.md) and
   return the report here.

## Output contract

Use the [output template](references/output-template.md) to distinguish
observations, inferences, missing evidence and assumptions, with scope, sources,
results, worker evidence, risks, confidence and the next action. Do not report
controller-transfer or App setup telemetry.

In every case, report `Changes made: None`.

## Skill Dependencies

Explore requires the installed `$learn` skill for read-only context
preparation and `$grilling-session` for decision refinement. It never
installs or refreshes these dependencies during a run.
