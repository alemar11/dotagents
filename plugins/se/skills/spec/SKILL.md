---
name: spec
description: "Create or revise feature specs and task plans in one repository; save to GitHub and offer delivery authorization."
---

# Feature Specification

Turn the current discussion, supplied references or an existing spec into a
complete user-visible outcome and the smallest verifiable task plan. Save one
GitHub issue per spec with all tasks embedded, or return complete conversational
previews for draft/no-write requests.

## Scope and execution

Select exactly one implementation repository, defaulting to the current one
when it matches. Resolve an unclear target before drafting. Report other
repository work as out of scope; do not split it into companion specs or add
cross-repository issue references. Planning does not implement, create branches
or PRs, change execution progress, or implicitly start Delivery.

Follow [execution scope](../../references/execution-scope.md) in the invoking
session with its configured model and reasoning. When the outcome is clear,
rename this task to `📚 Plan Feature · <outcome>` if supported; failure is a
reported limitation, not a blocker. Do not create or fork a planner task or use
titles as identity. Optional research or draft-review helpers use the appropriate
[shared role](../../references/subagents.md); read it before delegation. Retain
spec ownership and proceed serially when helpers are unavailable or prohibited.

## Define the outcome and tasks

Read [specification.md](references/specification.md) for content, identity and
review requirements. Reuse conversation evidence and accepted decisions;
inspect relevant code and repository instructions to resolve remaining facts.
For revisions, first apply [existing-specs.md](references/existing-specs.md).

Compose [Grilling Session](../grilling-session/SKILL.md) only for material choices
that evidence, prior answers, safe labeled assumptions or delegated decisions
cannot resolve. A complete brief needs no new interview or pre-save approval.
Ordinary answer waits are nonterminal; missing essential evidence blocks only
affected work after unaffected authorized work is completed.

Draft with [spec.md](templates/spec.md): problem, observable behavior, scope,
accepted decisions, acceptance criteria and embedded tasks. Use
[task-decomposition.md](references/task-decomposition.md) when creating or changing
tasks: prefer narrow end-to-end outcomes, real prerequisites and checks that
prove behavior. Keep task dependencies separate from worker, branch and PR
topology, which belong to Delivery.

Review and correct the whole artifact before saving. Preserve requested outcomes
and decisions, cover every criterion with credible task checks, verify dependency
feasibility, and ensure each task works with the main spec in a fresh session.
Same-repository issue links are ordinary references; native blocker management
belongs to G on explicit request, outside Spec.

## Save and hand off

Read [states.md](references/states.md) and [GitHub output](references/github-output.md)
for operation selection, publication and readback. Invocation authorizes the
scoped save unless restricted. GitHub is the only saved destination: previews
remain in conversation, and local-file-only requests authorize no hosted save.
Before hosted reads apply [G preflight](../../references/codex-dependency-preflight.md);
before every hosted write apply [hosted-content safety](../../references/hosted-content-safety.md).
Local-source previews need no G access.

Verify the complete saved artifact. Reconcile uncertain or partial saves against
its existing identity before retrying; never substitute files or previews for a
failed save. After verified save, follow
[delivery authorization](references/delivery-authorization.md) for the pickup
decision, marker verification and any explicitly requested downstream handoff.
Publication alone neither authorizes nor starts delivery.

Return saved links or complete previews, a concise task summary, material
assumptions, review/save results, observed pickup authorization and exact remaining
blockers or questions. Do not reproduce saved bodies or review logs unless asked.
Keep operation receipts out of specs; artifact completion proves no implementation.
Resume from saved content and current evidence, without a planning graph or journal.

## Skill Dependencies

Material clarification uses bundled `se:grilling-session`. Hosted reads and saves
require installed `g@alemar11`. Never install or substitute dependencies.
