# GitHub portfolio triage workflow

Use this workflow for report-only queue discovery across explicit repository
sets.

## Scope

- Accept explicit `owner/repo` lists, a repo-file, or repositories from an
  active maintainer-orchestrator ledger.
- Do not infer all repositories under an owner or organization by default.
- Do not include archived, forked, suppressed, or retired repositories unless
  the user explicitly asks.
- Do not mutate GitHub state during the scan.

## Report

Start with the `ghflow portfolio scan` summary, then expand only the repos or
items that need a maintainer-ready explanation.

For each surfaced item, include:

- full canonical URL;
- `What`: one sentence;
- `Fit/Risk`: good, mixed, or poor, with one reason;
- `Proof`: CI, repro, source evidence, live proof, or missing proof;
- `Blocker`: none, missing access, failing check, stale branch, unclear
  direction, conflict, or similar;
- `Next`: exact maintainer action.

Use these sections:

- `Autonomous candidates`
- `Needs owner`
- `Defer/close/supersede`
- `Portfolio blockers`
- `Ready next`

When the user asks for follow-up action after a report, route to the focused
GitStack skill: `github-ci`, `github-reviews`, `github-releases`, `yeet`, or
the umbrella `github` skill.
