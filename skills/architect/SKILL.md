---
name: architect
description: "Design features and substantial changes in one repository, from user behavior to responsibilities, interfaces, and a verifiable task plan. Ends at a specification, without implementation."
---

# Architect

Turn the current discussion, supplied references or an existing spec into an
implementable design: observable behavior, ownership and contracts, reasoned
decisions, and the smallest verifiable task plan. Keep the specification in the
current conversation by default. Publish one GitHub issue per spec with all
tasks embedded only when the user explicitly requests publication.

## Scope and execution

Select exactly one implementation repository, defaulting to the current one
when it matches. Resolve an unclear target before drafting. Report other
repository work as out of scope; do not split it into companion specs or add
cross-repository issue references. Planning does not implement, create branches
or PRs, change execution progress, or implicitly start implementation.

Work in the invoking session. When the outcome is clear,
rename this task to `📚 Architect · <outcome>` if supported; failure is a
reported limitation, not a blocker. Do not create or fork a planner task or use
titles as identity. Optional research, alternative designs, and draft review
follow [subagent briefs](references/subagents.md). Adapt the selected brief with
the exact question, relevant paths or source contents, accepted decisions,
scope limits, and expected findings.
Research independent unknowns in parallel; give the reviewer the complete draft
and requirements once available. Keep research evidence distinct from review
findings, assess both, and retain ownership of the spec. When helpers are
unavailable or prohibited, perform the work locally and disclose any lost
review independence.

## Design the outcome before the tasks

Read [specification.md](references/specification.md) for content, identity and
review requirements. Reuse conversation evidence and accepted decisions;
inspect relevant code and repository instructions to resolve remaining facts.
For revisions, first apply [existing-specs.md](references/existing-specs.md).

Start by refining the brief in the current conversation. Invoke the installed
`$grilling-session` skill when material choices need user input;
evidence, prior answers, safe assumptions or delegated decisions may resolve a
choice without another question. A complete brief proceeds directly to design;
an existing design needs only the affected decisions rechecked.
Ordinary answer waits are nonterminal; missing essential evidence blocks only
affected work after unaffected authorized work is completed.

Start with a realistic user journey or caller example and its observable
result. Ground it in the relevant current behavior and accepted constraints.
When the change introduces or alters state, responsibilities, interfaces, or
module boundaries, read [design.md](references/design.md) to settle ownership,
invariants, failure behavior, and consequential alternatives before splitting
the work. Keep depth proportional: a straightforward change can have a short
design and one task. Do not manufacture architecture or competing proposals.

Separate product choices requiring user judgment from facts that source research
can settle and empirical questions requiring an experiment. Planning does not
authorize runnable prototypes or product edits. For an unresolved empirical
question, identify the smallest useful experiment and the decision it gates;
use separately authorized evidence when available and continue unaffected
planning. Do not claim the dependent design is ready without that evidence.

Draft with [spec.md](templates/spec.md): problem, usage, observable behavior,
scope, design and accepted decisions, acceptance criteria and embedded tasks.
Once the design is coherent, use
[task-decomposition.md](references/task-decomposition.md) when creating or changing
tasks: prefer narrow end-to-end outcomes, real prerequisites and checks that
prove behavior. Keep task dependencies separate from worker, branch and PR
topology, which belong to the execution caller.

Review and correct the design and complete task plan before handoff or
publication. Preserve requested outcomes and decisions, cover every criterion
with credible task checks, verify dependency feasibility, and ensure each task
works with the main spec in a fresh session.
Check that realistic usage fits the proposed contracts, state has clear owners,
and the design does not require callers to coordinate hidden implementation
steps. If review disproves a design assumption, revise the affected decision
and its tasks together; do not patch the task list around an incoherent design.
Same-repository issue links are ordinary references; native blocker management
uses `gh` directly on explicit request, outside Architect.

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

For publication, verify the complete GitHub artifact. Reconcile uncertain or
partial publication against its existing identity before retrying; never claim
publication from the conversational draft. Architect publication never creates,
updates or removes GitHub labels and never starts delivery.

Return the refined spec or published link, a concise task summary, material
assumptions, review/publication results and exact remaining blockers or questions.
Do not reproduce published bodies or review logs unless asked. Keep operation
receipts out of specs; artifact completion proves no implementation.
Resume from the current conversation or a published issue and current evidence,
without a planning graph or journal.

## Skill Dependencies

Material clarification requires installed `$grilling-session`. Never install or
substitute this dependency during a run.
