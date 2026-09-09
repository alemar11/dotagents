---
name: spec
description: "Create or revise feature specs and task plans on explicit request; save to GitHub and offer delivery authorization."
---

# Feature Specification

Produce one repository-scoped spec and an ordered, verifiable task plan from the
current discussion, supplied references, or an existing spec. When requested work
spans repositories, produce one linked spec per implementation repository.
The requested result is verified GitHub issues, or complete in-conversation
previews when no writes were requested. Planning does not implement code, create
branches or PRs, change execution progress, or start Delivery implicitly.

## Current session

Work in the invoking session with its configured model and reasoning. Once the
outcome is clear, update the current task title to `📚 Plan Feature · <outcome>`
when supported. Invocation authorizes this title update; do not create or fork
a planner task. If renaming is unavailable or fails, continue planning and
briefly report the limitation. Titles do not establish spec or repository identity.

Follow the shared [execution scope](../../references/execution-scope.md).
For independent repository research or a bounded draft review, optional helpers
may reduce elapsed time or improve evidence. Use the corresponding role in
[subagents.md](../../references/subagents.md); read that role before delegation.
Keep ownership of the complete spec here and work serially when helpers are
unavailable or prohibited.

## Draft and review

Read [specification.md](references/specification.md) for the saved content and
identity contract. Inspect relevant code and repository instructions, preserving
source attribution, caller scope, and accepted decisions. For revisions,
read [existing-specs.md](references/existing-specs.md) before changing the draft.

Compose [Grilling Session](../grilling-session/SKILL.md) in this session only for
material unresolved decisions. Preserve prior answers and use safe labeled
assumptions or delegated choices; a complete brief needs no fresh interview.
Ordinary answer waits are not terminal blockers.

Use [spec.md](templates/spec.md) to draft the complete artifact, including its
embedded task sections. Read [task-decomposition.md](references/task-decomposition.md)
when deriving or changing tasks. Keep the smallest useful task plan.
Describe prerequisites by the evidence and
activity they gate. Spec uses ordinary links and never manages native GitHub
blockers; explicit blocker requests belong to `g:github-issues`, outside Spec.
A usable PR candidate may enable dependent work before its issue closes.

For linked repository specs, define shared contracts and each repository's
PR-readiness evidence under [specification.md](references/specification.md#shared-contracts-across-repositories).

Review the complete draft against the specification contract before saving:
requested outcomes and accepted decisions are preserved, every acceptance
criterion has task coverage and credible verification, dependencies are real
and feasible, and each task is understandable with the main spec in a fresh
session. Acceptance checks describe feature behavior and prerequisite evidence;
worker, branch and PR topology choices belong to Delivery. Revisions preserve
identities and executor-owned progress.
Correct findings across the whole artifact. A complete brief needs no additional
interview or pre-save approval. Ask only about material choices that existing
evidence, accepted decisions, or safe assumptions cannot resolve. If essential
evidence is unavailable, report the affected scope and missing input after
completing unaffected authorized work. Resume from the saved content and current
evidence; do not maintain a planning workflow graph or execution journal.

## Save and report

Invocation authorizes saving one GitHub issue per spec, subject to caller
constraints. Draft, preview, or no-write requests return the complete issue body
in the conversation without files or hosted writes. GitHub is the only saved-spec
destination; do not write local spec files or exports. A local-file-only request
is outside this skill's save capability and does not authorize GitHub publication.
Read [states.md](references/states.md) and [GitHub output](references/github-output.md).

Before hosted source reads or saves, apply the shared
[G dependency preflight](../../references/codex-dependency-preflight.md).
Before every hosted write, apply
[hosted-content-safety.md](../../references/hosted-content-safety.md).
A preview using only supplied or local source material needs no G access.

Verify the complete saved representation. Reconcile uncertain effects against
the same artifact before retrying, retaining identities from partial saves.
Never substitute a local file or preview after a failed save. After a
verified authoritative save, follow [delivery authorization](references/delivery-authorization.md)
to ask whether to enable pickup, reuse established authority and verify any
requested marker change. Publishing alone never enables automatic delivery.
Perform an explicitly requested downstream handoff only after verified save and
any requested marker change; reconcile its result before claiming completion.

Return the saved reference or complete preview, a concise task summary,
material assumptions, review and save results, observed delivery authorization,
and any exact remaining blocker or unanswered authorization question.
Keep the final report concise; do not reproduce saved issue bodies or internal
review logs unless requested. Previews still include the complete proposed bodies.
Keep operation receipts out of the saved spec. Planning completion proves the
artifact exists, not that its feature has been implemented.

## Skill Dependencies

Material clarification composes bundled `se:grilling-session`, using its current
context-first refinement contract. Hosted reads and saves require the installed
`g@alemar11` issue workflow. Spec never installs or substitutes dependencies.
