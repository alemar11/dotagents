---
name: explore
description: "Run an explicitly requested read-only exploration in the current task or session with optional bounded delegation."
---

# Explore

## Scope and execution

Activate only for explicit `$explore`, Explore UI selection, or an equivalent
instruction to execute this workflow, never an ordinary mention or implicit
planning match. Prepare context and explore directly in the invoking task or
session. Use Grilling Session only for unresolved user decisions, then complete
any remaining investigation and report here. Retain its working directory
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
state. Create workers only once scope is settled or the user has stopped the
interview with enough direction to continue.

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
2. Assess whether a material decision about intent, scope, constraints, or
   tradeoffs still needs the user. When the request and existing conversation
   settle those decisions, mark the interview `not-needed` and continue to
   investigation or synthesis. Missing factual evidence is research work, not
   a reason to request confirmation of an already clear task.
   Otherwise, briefly share useful findings, separating observations from
   hypotheses, and compose `$grilling-session` with the evidence and unresolved
   decisions. Do not invent ambiguity or ask for facts available in the sources.
3. When an interview is needed, ask one question per turn until it returns
   `refined`, the user
   stops with `user-stopped`, or the interview is `blocked`. Create no workers
   while the interview is awaiting an answer. A blocked interview fails Explore
   before worker creation.
4. Use the established scope, or best-supported interpretation after the user
   stops, to guide the investigation. Preserve unconfirmed items and apply the
   read-only scope gate again. A skipped interview requires no final user
   confirmation; it does not remove unresolved evidence from the report.
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

Ground material claims in the primary source that owns them: current code and
tests for repository behavior, official documentation for external contracts,
and authoritative records for current state. Place citations beside the claims
they support. Mark inferences and disclose unavailable primary evidence rather
than treating a secondary summary or helper conclusion as verified fact.

Use the [output template](references/output-template.md) to distinguish
observations, inferences, missing evidence and assumptions, with scope, sources,
results, worker evidence, risks, confidence and the next action. Do not report
controller-transfer or App setup telemetry.

In every case, report `Changes made: None`.

## Skill Dependencies

Explore requires the installed `$learn` skill for read-only context
preparation. `$grilling-session` is required only when user decisions need
refinement; its absence does not block the `not-needed` path. Explore never
installs or refreshes these dependencies during a run.
