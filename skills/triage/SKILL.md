---
name: triage
description: Triage GitHub or local markdown issues into typed workflow states and agent-ready queues.
---

# Triage

## Goal

Move existing, messy, or incoming issues through the repo's configured issue
triage workflow.

Use this skill for GitHub issues or local markdown issues that already exist or
come from a tracker queue. For planning a new feature from scratch, use
`$plan-feature` instead.

## Core Model

Triage has two separate dimensions:

- **Type/category**: what kind of work this is.
- **State**: where the issue is in the workflow.

Canonical issue types:

- `bug`: something is broken or regressed.
- `feature`: a new user or system capability, or a product enhancement.
- `task`: maintenance, refactor, docs, follow-up, cleanup, or an implementation
  work item.

Canonical triage states:

- `needs-triage`: maintainer needs to evaluate.
- `needs-info`: waiting on reporter or requester.
- `ready-for-agent`: fully specified and agent-queue-ready; listed
  dependencies still gate when work can start.
- `ready-for-human`: requires human implementation or judgment.
- `wontfix`: will not be actioned.

`needs-info` is not an implementation queue state. When the reporter or
requester answers, move or treat the issue as `needs-triage` again and
re-evaluate it before it can become `ready-for-agent`.

Use `project-memory/agents/triage-labels.md` to map these canonical names to
the actual tracker issue types, labels, or markdown status values.

## Hard Requirements

- Load `project-memory/agents/issue-tracker.md` and
  `project-memory/agents/triage-labels.md` before mutating anything.
- If required project-memory files are missing, load and run
  `$project-memory` before triaging unless the user explicitly asks for a
  one-off best-effort pass.
- Every triaged issue must have exactly one type/category and one workflow
  state.
- In GitHub mode, use native GitHub Issue Type for `bug`, `feature`, or `task`
  whenever the repo's tracker configuration says issue types are available.
- In local markdown mode, record type and state as frontmatter-like lines near
  the top of the issue file.
- Before marking an issue `ready-for-agent`, load and run `$plan-harder` in
  issue-hardening mode and embed or post the resulting agent brief.
- If the issue is underspecified, load and run `$grill-me-with-context` to resolve
  the smallest blocking question set before writing an agent-ready brief.
- Do not run `$plan-harder` or post an agent brief for `needs-info`; preserve
  established facts and ask concrete questions instead.
- Do not implement the issue.
- Do not use orchestration runtime state for ordinary triage classification or
  tracker routing. `$codex-orchestrator` owns dispatch only after an issue is
  already ready for an agent queue.
- Do not close an issue or mark it `wontfix` without explicit user or
  maintainer confirmation.

## Workflow

### 1. Load tracker rules

Read:

- `project-memory/agents/issue-tracker.md`
- `project-memory/agents/triage-labels.md`
- `project-memory/agents/domain.md`
- `CONTEXT.md` or `CONTEXT-MAP.md`, when relevant
- existing issue templates or local tracker docs, when present

If the configured tracker backend is not `github` or `local`, stop and route
the setup through `$project-memory` instead of inventing tracker semantics.

### 2. Select issue or queue

If the user names an issue, fetch that issue and its recent conversation.

If the user asks for a triage pass without naming an issue, list a focused
queue:

- issues missing a type/category,
- issues with no recognized workflow state,
- `needs-triage` issues,
- `needs-info` issues with reporter/requester activity since the last triage
  note, so they can be re-evaluated as `needs-triage`,
- issues that look ready but lack an agent brief.

For GitHub, use `$github-issues` to list or view issues and recent comments.
Request type and relationship fields when useful, but if the installed `gh`
version rejects them, use the configured fallback from `triage-labels.md`.

For local markdown, use the configured local issue layout from
`project-memory/agents/issue-tracker.md` and `references/local-markdown.md`.

### 3. Gather evidence

Read only enough repo evidence to classify and route the issue:

- issue title, body, comments, labels, type, state, and links,
- related PRD or parent issue, when present,
- relevant code, tests, docs, ADRs, and domain context,
- duplicate or superseding issues when clearly discoverable.

Do not copy raw logs into tracker comments. Summarize only the facts needed for
triage and avoid recording secrets or unrelated user/session text.

### 4. Classify type and state

Choose one canonical type and one canonical state.

Use `bug` when the report describes incorrect existing behavior or a
regression. Use `feature` when the issue asks for a new capability or product
enhancement that still needs product framing. Use `task` when the issue is
maintenance, cleanup, docs, refactoring, follow-up work, or an implementation
subtask under an accepted PRD.

Use `ready-for-agent` only when the issue has:

- clear current and desired behavior,
- explicit scope boundaries,
- acceptance criteria,
- validation,
- no unresolved product or technical blocker,
- an embedded or posted `$plan-harder` agent brief.

Dependencies may still be listed. In that case, the issue is queue-ready but
must not be started until its dependencies are complete, and the dependency
graph must stay acyclic.

Use `needs-info` when the next action is a concrete question for the reporter
or requester. Its next transition is back through `needs-triage` after new
activity, not directly to agent execution. Use `ready-for-human` when the work
is real but needs human authority, judgment, access, design, legal, security,
or code-owner input before an agent can execute. Use `wontfix` only after
explicit confirmation.

### 5. Resolve blockers before writing ready states

If the issue cannot be classified confidently, ask one blocking question or
leave a `needs-info` note with the smallest useful question set.

If the issue is almost agent-ready but still under-specified, use
`$grill-me-with-context` to clarify the missing product/domain decisions. Let
`$grill-me-with-context` and `$domain-modeling` own any durable updates to
`CONTEXT.md` or ADRs.

If blocker resolution still depends on the reporter or requester, stop at
`needs-info`. Do not harden the issue with `$plan-harder`, do not post an agent
brief, and do not call it ready for implementation.

If the issue is queue-ready for agent execution, use `$plan-harder` once on
that single issue and embed the result using `references/agent-brief.md`.

### 6. Write changes

Ask for confirmation before mutating the tracker unless the user explicitly
asked to apply, write, publish, or update triage.

For GitHub:

- Use `$github-issues` to set the issue type when GitHub issue types are
  configured and available.
- Use `$github-issues` to apply the mapped state label.
- Remove conflicting old state labels when the mapping file identifies them.
- Add a concise comment for `needs-info`, `ready-for-human`, `wontfix`, or
  `ready-for-agent` handoff notes.
- For `needs-info`, ask specific actionable questions and summarize what is
  already established. Do not close the issue merely because it needs info.
- Close only when the chosen state is `wontfix` and the user confirmed it.

For local markdown:

- Preserve the original issue content.
- Insert or update the `Type:` line.
- Insert or update the `Status:` line.
- Append triage notes, questions, decisions, or the agent brief under the
  headings in `references/local-markdown.md`.
- Preserve orchestrator workspace fields such as affected repos, integration
  gates, and repo PR links when the issue lives under
  `projects/<project>/features/<feature>/issues/`.

### 7. Report result

Return:

- issue identity and tracker backend,
- selected type/category,
- selected state,
- labels/statuses or GitHub issue type applied,
- whether `$grill-me-with-context` or `$plan-harder` was used,
- next action owner,
- any write that was skipped because confirmation was not granted.

## References

- `references/agent-brief.md`: template for `ready-for-agent` handoff notes.
- `references/local-markdown.md`: local markdown issue format and update rules.
