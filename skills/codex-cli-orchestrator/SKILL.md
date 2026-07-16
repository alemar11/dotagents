---
name: codex-cli-orchestrator
description: Explicitly coordinate tmux-hosted Codex CLI Feature Spec sessions with root-owned delivery.
---

# Codex CLI Orchestrator

## Purpose And Invocation

Use this Codex-dependent skill only when the owner explicitly invokes
`$codex-cli-orchestrator` or asks to run Codex CLI Orchestrator. The current
interactive Codex CLI session is always the root controller. tmux hosts
persistent Feature Spec workers; tmux is not the controller or communication
protocol.

The CLI runtime requires `python3`, local `git`, `ps`, `tmux`, and Codex CLI.

This skill requires the sibling `codex-orchestrator` installation for the
canonical shared source, ledger, delivery, gate, and closeout contracts. Load
only that package's shared references. Never invoke its App entrypoint and
never use visible App task creation, task ids, task Goals, or App steering.

## Non-Negotiable Invariants

- Resolve the shared active-root claim before creating a run, worktree, or
  worker through the sibling App package's `scripts/orchestrator-claim`
  artifact. App and CLI runs use the same claim namespace and may not overlap.
- Keep at most three nonterminal Feature Spec sessions. One Feature Spec owns
  one slot across all of its repositories and internal subagents.
- Create one tmux-hosted `codex exec` session per Feature Spec, not per issue or
  repository. The root derives scheduling from dependencies, isolation, risk,
  and live capacity.
- Workers may inspect, edit, validate, and report. The root alone owns
  integration, commits, pushes, pull requests, review polling, issue closeout,
  merge decisions, and final delivery.
- A worker may use bounded internal background subagents when useful. It must
  not launch another independent `codex exec`, run `$autoreview`, or create a
  sibling worker.
- Communication is artifact-based. Read `events.jsonl`, `final.json`,
  `exit_code`, `stderr.log`, `codex_session_id`, and `status.json`; never scrape
  panes or use `tmux send-keys`.
- Git worktrees are CLI-only and must be unique per Feature Spec and
  repository. The shipped helper creates and removes them. Workers never
  commit because linked-worktree metadata may be outside their sandbox.
- Preserve owner changes. Cleanup refuses running sessions and dirty
  worktrees; it never deletes branches.
- Delivery and external mutation still require the exact shared permission and
  gate contracts. CLI invocation grants no commit, publication, merge,
  release, or deployment authority.

## Shared Core

Before dispatch, load these canonical sibling references from
`../codex-orchestrator/references/`:

- `core/options.md` for common authority and delivery values;
- `ledger.md` for active-root claims and lifecycle state;
- `spec-backed-delivery.md` for Feature Spec delivery;
- `stacked-feature-specs.md` for an explicit upstream-merge-ready-head edge;
- `gates.md` and `codex-review-closeout.md` before owner-ready closeout;
- `runtime-efficiency.md` after the first wave.

Do not load the sibling App `SKILL.md`, `worker.md`, `options.md`, or
`multi-repo-workspace.md`. If the sibling package or a required shared reference is missing, stop before
mutation and report the installation dependency.

Normal CLI runtime may execute the sibling
`../codex-orchestrator/scripts/orchestrator-claim` shared-core artifact. This is
not invocation of the App orchestrator entrypoint. `scripts/codex-session run
create` acquires the claim before creating run state; run cleanup releases it
only after every Spec is terminal and cleaned.

## Post-Conclusion Merge Authorization

Do not load `../codex-orchestrator/references/core/merge-authorization.md`
before or during CLAIM, registration, preparation, dispatch, worker execution,
integration, or delivery gating. Load it only after the selected delivery target
is complete and the owner separately requests merge. If it is missing then,
stop the optional merge step without changing the completed delivery target.

## Controller Loop

1. **CLAIM** — resolve the shared options and ledger, canonicalize repository
   realpaths, and acquire the common active-root claim through the shared helper
   before creating run state.
2. **REGISTER** — record Feature Specs, workstreams, repositories,
   dependencies, acceptance criteria, delivery targets, and authority.
3. **PREPARE** — create a run manifest and call `scripts/codex-session --json
   run create`, then prepare each ready Spec's isolated repository worktrees.
4. **DISPATCH** — start up to three ready Spec sessions. Supply one bounded
   prompt and the shipped `assets/worker-output-schema.json` per Spec.
5. **MONITOR** — poll helper status and structured artifacts. Resume only by
   the recorded Codex session UUID. Do not interact with panes.
6. **INTEGRATE** — after a worker exits, inspect its current diff and evidence.
   The root runs validation, `$autoreview`, Git integration, and authorized
   delivery from the affected worktrees.
7. **RECONCILE** — update the shared ledger, dispatch newly unblocked Specs,
   and clean only terminal, integrated or intentionally abandoned worktrees.

Continue until all registered sources reach their selected target or a real
authority, dependency, access, tool, gate, or safety blocker stops progress.

## Worker Contract

Load `references/worker.md` before writing a prompt and
`references/runtime.md` before running the helper. Every worker receives the
exact Feature Spec, repository/worktree map, allowed paths and actions,
acceptance criteria, validation commands, delivery target for context, and the
instruction that delivery remains root-owned.

The worker final result must identify changed files, validation evidence,
remaining risks, internal subagent topology, generated artifacts, and the
recommended root integration action. A report is evidence, never closeout.

## Embedded CLI

Normal runtime uses the shipped artifact at `scripts/codex-session`:

```text
scripts/codex-session --version
scripts/codex-session --json doctor
scripts/codex-session --json run create --manifest <file>
scripts/codex-session --json spec prepare --run-id <id> --spec-id <id>
scripts/codex-session --json spec start --run-id <id> --spec-id <id>
scripts/codex-session --json spec status --run-id <id> --spec-id <id>
scripts/codex-session --json spec resume --run-id <id> --spec-id <id>
```

Run manifests and process evidence live under
`~/.cache/dotagents/skills/codex-cli-orchestrator/runs/<run-id>/`. Source
worktrees never live in that cache; use the manifest's validated
workspace-owned `worktree_root`.

## CLI Maintenance

`scripts/codex-session` is the only supported runtime artifact. It is a
standard-library Python script with one `__version__` semver source of truth;
there is no maintenance project or generated runtime binary. Change it in
place, then re-run `--help`, `--version`, `--json doctor`, the focused tests,
and a safe fixture rehearsal. Use major versions for breaking command or JSON
contracts, minor versions for backward-compatible commands, and patches for
fixes.

## References

- `references/options.md`: CLI manifest and state vocabulary.
- `references/worker.md`: bounded worker prompt, actions, and report.
- `references/runtime.md`: tmux, Codex session, worktree, artifact, and recovery
  behavior.
