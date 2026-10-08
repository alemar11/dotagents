---
name: architect
description: "Design features and substantial changes in one repository, from user behavior to responsibilities, interfaces, and a verifiable task plan. Ends at a specification, without implementation."
---

# Architect

Turn the discussion, supplied references or an existing spec into an
implementable design and verifiable task plan. Keep it in the conversation;
publish to GitHub only on explicit request.

## Scope and execution

Use the single-repository scope in
[specification.md](references/specification.md), defaulting to the current
repository when it matches and resolving an unclear target before drafting.
Planning does not implement, create branches or PRs, change execution progress,
or authorize runnable prototypes.

Work in the invoking session. When the outcome is clear,
rename this task to `📚 Architect · <outcome>` if supported; failure is a
reported limitation, not a blocker. Do not create or fork a planner task or use
titles as identity. Use [subagent briefs](references/subagents.md) only when
delegating research, alternatives, or draft review. Retain ownership of the
spec; if helpers are unavailable or prohibited, work locally and disclose lost
review independence.

## Design the outcome before the tasks

Read the specification contract for content, identity and review requirements.
Reuse accepted decisions and evidence; inspect relevant code and repository
instructions for remaining facts. For revisions, first apply
[existing-specs.md](references/existing-specs.md), including its compatibility
rules for separate task issues.

Start by refining the brief in the current conversation. Invoke the installed
`$grilling-session` skill when material choices need user input;
evidence, prior answers, safe assumptions or delegated decisions may resolve a
choice without another question. A complete brief proceeds directly to design;
an existing design needs only the affected decisions rechecked.
Ordinary answer waits are nonterminal; missing essential evidence blocks only
affected work after unaffected authorized work is completed.

Start from realistic usage and its observable result. Read
[design.md](references/design.md) when changing state, responsibilities,
interfaces, or module boundaries. Settle the design before splitting the work;
a straightforward change can have a short design and one task.

Separate user choices, researchable facts, and empirical questions. For missing
empirical evidence, name the smallest experiment and the decision it gates;
use separately authorized evidence and continue unaffected planning.

Draft with [spec.md](templates/spec.md). Use
[task-decomposition.md](references/task-decomposition.md) when creating or
changing tasks; execution topology belongs to the caller.

Review and correct the complete design and task plan against the specification
contract before handoff or publication. If review disproves an assumption,
revise the decision and its tasks together.

## Refine and optionally publish

Read [states.md](references/states.md) for operation selection. Load
[GitHub output](references/github-output.md) only for publication. Refinement
stays in the conversation and performs no durable write. Publish only after an
explicit user request.
Use authenticated `gh` directly for hosted reads and writes, verifying the
intended host and repository before access. Report unavailable CLI access or
authentication for the affected operation. Before every hosted write apply
[hosted-content safety](references/hosted-content-safety.md).
Local-source refinement needs no GitHub access.

Return the refined spec or published link, a concise task summary, material
assumptions, review/publication results and exact remaining blockers or questions.
Do not reproduce published bodies or review logs unless asked. Keep operation
receipts out of specs; artifact completion proves no implementation.
Resume from the current conversation or a published issue and current evidence,
without a planning graph or journal.

## Skill Dependencies

Material clarification requires installed `$grilling-session`. Never install or
substitute this dependency during a run.
