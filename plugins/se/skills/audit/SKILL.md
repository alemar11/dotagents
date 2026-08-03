---
name: audit
description: "Monitor active Codex App tasks across all available projects and hosts that use SE-owned skills, collecting observable feedback, confirmed bugs, and improvements into a prioritized read-only report. Use only after an explicit $se:audit invocation; do not use for historical or static audits."
---

# SE Session Audit

## Scope

Use this skill only after an explicit `$se:audit` invocation. Monitor current
Codex App tasks that show direct evidence of using a skill owned by the SE
plugin, regardless of project or host. Include sessions that also hand off to
G, but do not count a G handoff alone as SE use.

Keep the audit read-only. Return the report in the current audit task; do not
write a report file unless the user separately authorizes that destination.

## Workflow

1. Inspect the current Codex App tool declarations before calling them. Pass
   only fields and enum values exposed by the current runtime.
2. Establish the project inventory with `codex_app__list_projects` when that
   operation is exposed, then discover recent tasks with
   `codex_app__list_threads` across the available hosts. Reconcile project and
   host identities where the responses expose them. Select every returned task
   that is currently active and can be attributed to an SE skill. If the
   runtime cannot establish complete active task coverage, mark the report
   `coverage=partial` and do not claim that all sessions were observed.
3. Exclude the current audit task, other audit/monitor tasks, inactive tasks,
   unrelated chats, and tasks that only expose the skill catalog.
4. Confirm SE use from task-visible evidence such as an explicit `$se:<skill>`
   invocation, a linked `plugins/se/skills/<skill>/SKILL.md`, or an SE-owned
   skill action mapped to the current plugin manifest. Do not infer use from
   titles, descriptions, project paths, or cache state.
5. Read each selected task with `codex_app__read_thread`, recording its real
   `thread_id`, `host_id` when exposed, project/repository when exposed,
   status, used SE skills, and the evidence frontier. If the read fails,
   times out, or is truncated across the relevant turns, report the evidence
   gap instead of inferring behavior.
6. When `codex_app__wait_threads` is available, wait in bounded batches of at
   most eight tasks. Re-read a task after a material transition, a cursor or
   evidence gap, and before the final judgment. Continue until every selected
   task reaches a terminal state or the user stops the audit. Without bounded
   waits, use bounded authoritative reads and report the reduced coverage.
7. Compare observed behavior with the exact active SE skill contract. Separate
   selection, workflow order, authority/mutation safety, handoff/routing,
   evidence quality, recovery, and instruction-cost findings.

## Findings and priorities

Keep these categories separate:

- **Feedback**: explicit user/agent feedback, observed strengths, or friction.
- **Bug**: a concrete contradiction with the active SE contract, confirmed by a
  fresh authoritative task read. Do not classify model behavior, App
  availability, repository state, user input, or G's failure as an SE bug
  unless SE owns the missing guardrail.
- **Improvement**: an actionable proposal that is not yet a confirmed contract
  violation.

Assign stable bug IDs in first-seen order (`LIVE-001`, `LIVE-002`, ...). Track
  `provisional`, `confirmed`, `resolved`, or `withdrawn` status and keep one
  entry per root cause. Assign priorities as follows:

- `P0`: data loss, security, unauthorized mutation, or complete audit failure.
- `P1`: workflow blocker or repeated materially incorrect behavior.
- `P2`: meaningful degradation or recurring operator friction.
- `P3`: documentation, clarity, cost, or polish improvement.

## Final report

Return a compact Markdown report with this order:

1. **Monitored tasks** — task ID, host, project/repository, terminal status,
   and confirmed SE skills.
2. **Performance snapshot** — compliant behavior, useful feedback, and
   coverage/evidence gaps.
3. **Feedback** — strengths and friction with task-visible evidence.
4. **Bug registry** — ID, status, priority, affected skill, impact, evidence,
   owning surface, and smallest remediation.
5. **Improvements** — proposal, expected value, risk, and priority.
6. **Priority order** — the highest-value next actions, ranked.
7. **Terminal assessment** — assess each used SE skill separately and
   distinguish target defects from external runtime or repository conditions.

## Mutation boundary

Do not call task creation, messaging, title, pin, archive, handoff, Goal, Git,
GitHub, or repository-write tools from this skill. If the user requests a fix,
finish the audit and switch to the owning implementation workflow explicitly.
