# G Session Audit

## Scope

Use this workflow only when the user explicitly asks `$g` to audit live G
usage. Monitor current Codex App tasks that show direct evidence of using the
standalone G skill, regardless of project or host. Do not treat skill
installation, catalog visibility, a repository path, or a linked copy as
runtime use.

Keep the audit read-only. Return the report in the current audit task; do not
write a report file unless the user separately authorizes that destination.
Load [../../states.md](../../states.md) before assigning coverage,
finding kind, bug status, or priority.

## Workflow

1. Inspect the current Codex App capability declarations before using them and
   supply only inputs exposed by the current runtime.
2. Establish the visible project inventory when available, then discover
   recent tasks across available hosts. Reconcile project and host identities
   where the responses expose them. Select every returned task
   that is currently active and can be attributed to a G skill. If the runtime
   cannot establish complete active task coverage, mark the report
   `coverage=partial` and do not claim that all sessions were observed.
3. Exclude the current audit task, other audit/monitor tasks, inactive tasks,
   unrelated chats, and tasks that only expose the skill catalog.
4. Confirm G use from task-visible evidence such as an explicit `$g`
   invocation, a linked `skills/g/SKILL.md`, a loaded workflow reference, or a
   call to the skill-owned shipped CLI. Do not infer use from titles,
   descriptions, project paths, or cache state.
5. Read each selected task authoritatively, recording its real
   `thread_id`, `host_id` when exposed, project/repository when exposed,
   status, used G workflows, and the evidence frontier. If the read fails,
   times out, or is truncated across the relevant turns, report the evidence
   gap instead of inferring behavior.
6. When bounded multi-task waiting is available, wait in batches of at most
   eight tasks. Re-read a task after a material transition, a cursor or
   evidence gap, and before the final judgment. Continue until every selected
   task reaches a terminal state or the user stops the audit. Without bounded
   waits, use bounded authoritative reads and report the reduced coverage.
7. Compare observed behavior with the exact active G skill contract. Separate
   selection, workflow order, authority/mutation safety, tool routing,
   evidence quality, recovery, and instruction-cost findings.

## Findings and priorities

Classify every item with the canonical finding-kind meanings in
`../../states.md` and keep those report categories separate. Do not treat
model behavior, App availability, repository state, user input, or another
package's failure as a G bug unless G owns the missing guardrail.

Assign stable bug IDs in first-seen order (`LIVE-001`, `LIVE-002`, ...). Apply
the status transitions and priorities from `../../states.md`, and keep one
entry per root cause.

## Final report

Return a compact Markdown report with this order:

1. **Monitored tasks** — task ID, host, project/repository, terminal status,
   and confirmed G workflows.
2. **Performance snapshot** — compliant behavior, useful feedback, and
   coverage/evidence gaps.
3. **Feedback** — strengths and friction with task-visible evidence.
4. **Bug registry** — ID, status, priority, affected skill, impact, evidence,
   owning surface, and smallest remediation.
5. **Improvements** — proposal, expected value, risk, and priority.
6. **Priority order** — the highest-value next actions, ranked.
7. **Terminal assessment** — assess each used G workflow separately and
   distinguish target defects from external runtime or repository conditions.

## Mutation boundary

Do not create or contact tasks, change task metadata or lifecycle, modify Git
or GitHub state, or write repository files from this workflow. If the user
requests a fix, finish the audit and switch to the owning implementation
workflow explicitly.

## References

- `../../states.md`: coverage, finding, annotation, and priority states.
