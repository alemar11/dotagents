---
name: spec
description: "Refine feature specs and task plans in one repository, keeping the result in conversation by default and optionally publishing it to GitHub."
---

# Feature Specification

Turn the current discussion, supplied references or an existing spec into a
complete user-visible outcome and the smallest verifiable task plan. Refine the
spec in the current conversation by default. Publish one GitHub issue per spec
with all tasks embedded only when the user explicitly requests publication.

## Scope and execution

Select exactly one implementation repository, defaulting to the current one
when it matches. Resolve an unclear target before drafting. Report other
repository work as out of scope; do not split it into companion specs or add
cross-repository issue references. Planning does not implement, create branches
or PRs, change execution progress, or implicitly start implementation.

Work in the invoking session. When the outcome is clear,
rename this task to `📚 Plan Feature · <outcome>` if supported; failure is a
reported limitation, not a blocker. Do not create or fork a planner task or use
titles as identity. Optional research and draft review follow
[subagent briefs](references/subagents.md). Adapt the selected brief with the exact question, relevant paths or
source contents, accepted decisions, scope limits, and expected findings.
Research independent unknowns in parallel; give the reviewer the complete draft
and requirements once available. Keep research evidence distinct from review
findings, assess both, and retain ownership of the spec. When helpers are
unavailable or prohibited, perform the work locally and disclose any lost
review independence.

## Define the outcome and tasks

Read [specification.md](references/specification.md) for content, identity and
review requirements. Reuse conversation evidence and accepted decisions;
inspect relevant code and repository instructions to resolve remaining facts.
For revisions, first apply [existing-specs.md](references/existing-specs.md).

Start by refining the brief in the current conversation. Invoke the installed
`$grilling-session` skill when material choices need user input;
evidence, prior answers, safe assumptions or delegated decisions may resolve a
choice without another question. A complete brief proceeds directly to review.
Ordinary answer waits are nonterminal; missing essential evidence blocks only
affected work after unaffected authorized work is completed.

Draft with [spec.md](templates/spec.md): problem, observable behavior, scope,
accepted decisions, acceptance criteria and embedded tasks. Use
[task-decomposition.md](references/task-decomposition.md) when creating or changing
tasks: prefer narrow end-to-end outcomes, real prerequisites and checks that
prove behavior. Keep task dependencies separate from worker, branch and PR
topology, which belong to the execution caller.

Review and correct the whole artifact before refining or publishing. Preserve
requested outcomes and decisions, cover every criterion with credible task checks, verify dependency
feasibility, and ensure each task works with the main spec in a fresh session.
Same-repository issue links are ordinary references; native blocker management
belongs to `$github-issues` on explicit request, outside Spec.

## Refine and optionally publish

Read [states.md](references/states.md) and [GitHub output](references/github-output.md)
for operation selection and optional publication. Refinement stays in the
conversation and performs no durable write. Publish only after an explicit user
request.
Before hosted reads or writes, verify that `$github-issues` is installed and
reachable by canonical name in the current session. A directory or unrelated
connector alone does not establish availability. Report the missing dependency
before the affected operation; never substitute direct provider calls. Before
every hosted write apply [hosted-content safety](references/hosted-content-safety.md).
Local-source refinement
needs no GitHub skill access.

For publication, verify the complete GitHub artifact. Reconcile uncertain or
partial publication against its existing identity before retrying; never claim
publication from the conversational draft. Spec publication never creates,
updates or removes GitHub labels and never starts delivery.

Return the refined spec or published link, a concise task summary, material
assumptions, review/publication results and exact remaining blockers or questions.
Do not reproduce published bodies or review logs unless asked. Keep operation
receipts out of specs; artifact completion proves no implementation.
Resume from the current conversation or a published issue and current evidence,
without a planning graph or journal.

## Skill Dependencies

Material clarification requires installed `$grilling-session`. Hosted reads and
publication require installed `$github-issues`. Never install or substitute
dependencies during a run.
