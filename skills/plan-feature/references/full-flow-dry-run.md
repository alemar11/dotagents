# Full-Flow Dry-Run Fixture

Use this fixture to forward-test the planning pipeline without writing local
artifacts or mutating a hosted tracker.

## User Request

```text
Use $plan-feature to plan a feature named "account settings export". This is a
dry run: do not write files and do not mutate GitHub. Return draft publish
commands instead.
```

## Setup Snapshot

```text
tracker_mode: github
effective_target: draft-publish-commands
local_artifact_writes: disallowed
external_tracker_mutation: disallowed
feature_slug: account-settings-export
delivery_mode: one-feature-branch
source_prd_ref: draft-prd:account-settings-export
prd_body_fingerprint: sha256:7f4a9c21d003
```

## Expected Pipeline

1. `$plan-feature` reviews project memory and resolves run authorization.
2. `$grill-me-with-context` resolves only blockers that affect the PRD or issue
   split.
3. The PRD phase returns the PRD body, a draft PRD publish command,
   `source_prd_ref=draft-prd:account-settings-export`, and
   `prd_body_fingerprint=sha256:7f4a9c21d003`.
4. The issue phase returns hardened issue bodies plus draft issue publish commands.
   Draft issue bodies may contain `Source PRD: draft-prd:account-settings-export`
   only because no hosted PRD number exists yet.
5. `$codex-orchestrator` may inspect the resulting issue graph in dry-run mode
   but must not dispatch implementation workers, commit, push, create PRs, or
   close issues from the draft PRD ref.

## Expected Draft Publish Plan

- Publish the PRD first and capture the created issue number as `PRD_NUMBER`.
- Confirm the draft issue commands carry the same PRD body fingerprint as the
  draft PRD command.
- Replace every issue body line
  `Source PRD: draft-prd:account-settings-export` with
  `Source PRD: #$PRD_NUMBER` before creating hosted implementation issues.
- Attach each generated implementation issue to the PRD parent when the tracker
  supports parent/sub-issues.
- Keep `ready-for-agent` labels lowercase through the tracker mapping.
- Return exact commands without executing them.

## Failure Conditions

- A repo-local `.scratch/` PRD or issue file is created.
- A GitHub issue is created, edited, labeled, typed, closed, or attached.
- An implementation worker receives `commit`, `push`, or `pr` authorization
  from project memory, plan-feature output, tracker defaults, or the draft PRD
  ref alone.
- Draft PRDs, generated issues, and draft publish commands include worker
  authorization fields or worker capability modes.
- Generated issues use a prose `Source PRD` such as the PRD title when a stable
  draft ref is available.
