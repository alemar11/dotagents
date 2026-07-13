---
name: plan-harder
description: Create higher-rigor implementation plans or harden a single issue into an agent-ready brief before coding.
---

# Plan Harder

## Goal

Produce a deeper implementation plan than a normal planning pass. Slow down,
reduce ambiguity, surface hidden risks, and leave behind a concrete plan that
is ready for careful execution.

Only create the plan. Do not implement the work.

Plan Harder resolves one `planning_mode`:

- `planning_mode=full-plan`: create a phased implementation plan for a feature,
  migration, refactor, or other multi-step change.
- `planning_mode=issue-hardening`: make one vertical slice or issue agent-ready
  by adding the missing execution detail an implementation agent needs.

It also resolves one `output_surface`:

- `output_surface=standalone`: return the plan or hardened issue brief to the
  user in chat.
- `output_surface=caller`: when another skill explicitly invokes Plan Harder
  with `planning_mode=issue-hardening`, return the structured result to that
  workflow so it can merge or persist the brief. Do not emit standalone
  closeout text on this surface. `planning_mode=full-plan` requires
  `output_surface=standalone`.

Load `references/options.md` before resolving either field. Normalize legacy
or natural-language input once and use only canonical field/value assignments
in current handoffs and results.

Default to the smallest valid route:

- If the input is one issue, one slice, or one task from another planning
  skill, use `planning_mode=issue-hardening`.
- If the user can reasonably accept recommended assumptions, offer a compact
  defaults-based clarification path instead of a long question loop.
- Escalate to `planning_mode=full-plan` only when the work genuinely needs
  phases or cross-cutting sequencing.

## Planning-Only Contract

- Do not implement the work.
- Do not open PRs, mutate GitHub state, publish artifacts, or silently continue
  into coding after the plan.
- Do not write Markdown files under `plans/`.
- Do not create or update repo files as part of this skill. Return the plan or
  hardened issue brief to the user or calling workflow so that owner can decide
  where to persist it.
- If the broader request includes later implementation, issue creation, or
  orchestration, finish the plan first and make the handoff explicit instead of
  blending phases together.

## Trigger Rules

- Use when the user explicitly invokes `plan-harder` or asks for a harder,
  deeper, or more stress-tested plan.
- Use `planning_mode=issue-hardening` when the user asks to harden, solidify,
  make agent-ready, or de-risk a single issue or vertical slice before
  implementation.
- Use `planning_mode=issue-hardening` when another skill invokes `plan-harder` on one
  issue as a pre-implementation rigor pass.
- Use for ambiguous, high-risk, or multi-phase work only when the user has
  explicitly asked for planning, plan hardening, or a pre-implementation rigor
  pass.
- Do not auto-select this skill merely because an implementation request is
  complex, risky, or underspecified. Keep ordinary execution planning inside
  the implementation workflow unless the user or a calling planning skill
  explicitly requests Plan Harder.
- Do not use for straightforward planning work that does not need an extra
  review pass.

## Output Surface

- With `output_surface=standalone`, return the plan or issue-hardening brief in
  chat.
- Never save to `plans/`, create `plans/`, or write a Markdown plan file.
- If the user asks to save the plan, explain that this skill only plans harder
  and returns the result; a separate workflow can persist it afterward.
- When the plan is meant to feed later implementation or GitHub issue creation,
  end with issue-sized work slices and a clear handoff note.
- When hardening an existing issue, end with a clear implementation handoff for
  exactly that issue and name any remaining blocker that prevents assignment.

For routine issue-hardening runs, prefer a compact brief that reaches
`## Implementation Plan` quickly instead of repeating generic planning doctrine.

With `output_surface=caller`:

- require the caller to set `planning_mode=issue-hardening` and provide one
  bounded work item plus the minimum relevant context;
- return the structured caller template from `references/templates.md`, with
  `result_status=ready` or `result_status=blocked`;
- include every unresolved blocker in `blockers`; never infer `ready` when that
  list is non-empty;
- resolve unknowns from the supplied context and focused repo evidence when
  possible; otherwise return them in `blockers` for the caller to clarify
  instead of starting a separate user-facing question loop;
- do not add a user-facing summary, a claim that no files were written, or a
  standalone implementation handoff after the structured result;
- do not persist anything. The caller owns any later issue, tracker, or file
  write.

## Workflow

### 1. Choose the Mode

- Use `planning_mode=full-plan` for a feature, migration, refactor, or plan that
  still needs phases or multiple tasks.
- Use `planning_mode=issue-hardening` for one existing issue, one vertical
  slice, or one work item produced by a PRD or issue-splitting skill.
- If another skill calls Plan Harder with an issue body, treat that as
  `planning_mode=issue-hardening` with `output_surface=caller`.
  `planning_mode=full-plan` uses `output_surface=standalone`.

### 2. Research First

- Inspect the codebase, architecture, existing patterns, and nearby tests.
- Identify dependencies, edge cases, rollout concerns, and likely failure
  modes before drafting the plan.
- With `planning_mode=issue-hardening`, inspect only the files, tests, docs, and
  contracts needed to make that issue executable; do not expand into a full
  feature plan.

### 3. Clarify High-Risk Unknowns

- With `output_surface=standalone`, ask focused clarifying questions before
  drafting when ambiguity could materially change the work. With
  `output_surface=caller`, return unresolved material questions in `blockers`
  so the caller can apply its own clarification workflow.
- Ask only the minimum question batch needed to eliminate wrong plan branches.
- Prefer `request_user_input` when available.
- Respect the runtime limit of 1-3 questions per `request_user_input` call;
  if more clarification is needed, ask only the highest-signal next batch.
- If `request_user_input` is unavailable, ask the same focused questions in
  plain chat with concise numbered options and a recommended default.
- Prefer short numbered questions over paragraphs.
- Offer multiple-choice options when practical.
- Suggest reasonable defaults when appropriate.
- Include a fast-path reply such as `defaults` when the recommended choices are
  acceptable, and proceed on those defaults when the broader request already
  implies them clearly enough.
- Include a low-friction "not sure - use default" option when that meaningfully
  reduces back-and-forth.
- Do not ask questions that a quick, low-risk discovery read can answer from
  the repo, config, or nearby docs.
- Prioritize questions about:
  - scope and non-goals
  - success criteria
  - compatibility constraints
  - rollout/rollback expectations
  - validation expectations
- Use this underspecification checklist when deciding whether clarification is
  required before the plan is final:
  - the objective is unclear
  - "done" is unclear
  - scope boundaries are unclear
  - constraints are unclear
  - the target environment is unclear
  - safety or reversibility is unclear

### 4. Fetch Official Docs When Needed

- If the plan depends on external libraries, frameworks, APIs, or tools whose
  current behavior matters, fetch the relevant official documentation before
  finalizing tasks.
- Use the runtime's best official-doc path for the current environment rather
  than relying on memory when the detail is likely to drift.

### 5. Draft the Output

Use `references/templates.md` for the exact standalone shapes and the caller
surface result envelope.

With `planning_mode=full-plan`, create a phased plan with:

- a short overview
- prerequisites
- logical sprints or phases
- atomic tasks with clear boundaries
- validation per task
- testing strategy
- risk and rollback notes

Each task should be:

- small enough to commit independently when practical
- specific about files or areas touched when known
- explicit about dependencies on earlier tasks
- testable or otherwise verifiable
- concrete about what "done" means

With `planning_mode=issue-hardening`, create a compact issue brief with:

- issue goal and non-goals,
- assumptions and resolved interpretation,
- implementation approach,
- likely files or areas to inspect,
- dependencies or blockers,
- acceptance criteria,
- validation commands or checks,
- risks and rollback notes,
- handoff instructions for the implementation agent.

Keep the brief small enough to paste into an issue body or issue comment.

### 6. Run a Gotcha Pass

- Re-read the plan or issue brief and look for:
  - missing steps
  - missing dependencies
  - vague acceptance criteria
  - unsafe ordering
  - rollout or rollback gaps
  - missing validation
- If real gaps remain, ask the minimum follow-up questions needed and update
  the plan or issue brief before returning it.

### 7. Review Before Returning

- Review the plan or issue brief for:
  - missing dependencies
  - ordering failures
  - unhandled edge cases
  - vague or untestable tasks
- If the active runtime policy permits delegation and an independent pass adds
  value, you may ask a subagent to perform this review. Tell the reviewer not
  to ask questions and to return only actionable feedback.
- Otherwise, perform the same review locally before returning.
- Incorporate useful review feedback before finishing.

## Output Expectations

- With `output_surface=standalone`, return the final plan or hardened issue brief
  directly in chat, explicitly say that no repo files or `plans/` Markdown were
  created, summarize the riskiest assumptions and remaining questions, and
  include the handoff boundary for later implementation or publication.
- With `output_surface=caller`, return only the structured issue-hardening result
  envelope. The caller owns user-facing closeout, persistence, and any
  implementation or publication handoff.
- Do not implement the plan.

## Example Requests

- "Plan harder for this auth migration before we touch any code."
- "Give me a deeper, stress-tested implementation plan for this feature."
- "Harden this issue before I give it to an agent."
- "Make this vertical slice agent-ready without creating a separate plan file."

## References

- `references/options.md`: canonical option fields, values, and compatibility
  normalization.
- `references/templates.md`: full-plan and issue-hardening output templates.
