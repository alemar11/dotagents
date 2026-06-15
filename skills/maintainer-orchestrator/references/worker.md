# Worker Reference

Use this reference before creating or messaging Codex worker threads.

## Worker Rules

- Create one worker per repository or tightly scoped workstream.
- Give each worker a single clear objective, repository path or URL, branch
  expectations, and exit condition.
- Workers may inspect, implement, test, and report only within their authorized
  mode.
- Workers must not spawn sub-workers, create new Codex threads, or delegate
  their assignment.
- Workers must not edit orchestrator ledgers. They report status back to the
  orchestrator, which updates the ledger.
- Workers must preserve unrelated local changes and stage only authorized
  paths.

## Authorization Modes

- `inspect`: read-only investigation, triage, diagnosis, or plan.
- `implement`: local code/docs changes plus focused validation, but no push,
  PR, merge, release, or external mutation.
- `push-pr`: commit, push, or draft PR creation when the user explicitly
  authorized publication.
- `ci-rerun-fix`: rerun checks or push targeted fixes for a known PR or branch
  when the user authorized CI follow-up.
- `merge-close`: merge, close, label, comment, or otherwise mutate GitHub state
  only with explicit owner approval.
- `release`: tag, release, publish, or package promotion only with explicit
  owner approval and the release gate satisfied.

## Prompt Template

```text
You are a Codex worker for the <portfolio> portfolio.

Scope:
- Repository: <repo path or owner/repo>
- Workstream: <short name>
- Objective: <one concrete outcome>
- Authorization mode: <inspect|implement|push-pr|ci-rerun-fix|merge-close|release>
- Allowed paths or surfaces: <paths, branches, PRs, issues, or commands>
- Forbidden actions: no subdelegation, no ledger edits, no unrelated cleanup,
  no publish/merge/release unless this mode explicitly permits it.

Context:
- Owner request: <summary>
- Current ledger status: <summary>
- Known blockers or assumptions: <bullets>
- Required gates: <gate names from references/gates.md>
- Required proof: <tests, live proof, CI, autoreview, docs, screenshots>

Execution:
1. Inspect the current state before editing.
2. Preserve unrelated worktree changes.
3. If editing, run focused validation.
4. Run or request autoreview when required by the gate.
5. Stop and report if blocked by access, ambiguous owner intent, unsafe state,
   missing dependency, or a gate that cannot be satisfied.

Final report:
- Status: done|blocked|needs-owner|ready-for-review
- Changes: files or external objects touched
- Validation: commands run and outcomes
- Gate status: pass/fail/not-applicable with evidence
- Risks: residual risks or test gaps
- Next: exact owner or orchestrator action
```

## Heartbeat Checks

When heartbeat monitoring is requested, poll workers at the requested interval
or a conservative default such as five minutes. Ask for status, blocker,
validation, and expected next checkpoint. Do not interrupt a worker with new
scope unless the user changed priority or a gate failed.
