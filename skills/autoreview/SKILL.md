---
name: autoreview
description: Run Codex-only structured closeout review before final, commit, PR, or ship.
---

# Auto Review

Run the shipped Codex-only review helper as a closeout check. This is code
review, not GitHub PR review submission or approval routing.

## Trigger Cues

Use this skill when the user asks for or clearly implies:

- `autoreview`
- `review this before final`
- `review before commit`
- `review before PR`
- `review before ship`
- `review again after fixes`
- a final closeout check after non-trivial code edits where an independent
  bug-finding pass is likely to change the outcome

Do not use this skill for:

- answer-only turns with no file edits
- exploratory analysis or planning unless the user explicitly asks for review
- docs-only edits that do not alter runtime behavior, generated commands,
  install instructions, security posture, or public contracts
- tiny mechanical fixes such as typo corrections, formatting-only changes,
  comment-only edits, or metadata-only sync
- ordinary final responses after focused tests or proof already cover the
  changed behavior

## Canonical Closeout Sequence

1. Run the focused local tests or proof first.
2. Run `scripts/autoreview` on the correct target mode.
3. Verify each finding in the real code before accepting it.
4. Fix only the accepted findings.
5. Rerun focused tests or proof if code changed.
6. Rerun the same `scripts/autoreview` mode, verifying previously accepted
   findings before treating newly surfaced broad concerns as actionable.
7. Stop once the helper is clean or the remaining findings were consciously
   rejected with a reason.

## Runtime Surface

- The supported runtime entrypoint is `scripts/autoreview` inside this skill.
- If your current working directory is the skill root, run
  `scripts/autoreview --help`.
- If invoking from another repo, resolve the installed skill root first and run
  `<autoreview-skill-root>/scripts/autoreview ...`.
- This skill is Codex-dependent. The helper requires local `git`, the Codex CLI
  `exec` command, structured output flags, and read-only review execution.

## Closeout Entry Modes

- Before final or before commit on a dirty worktree: `scripts/autoreview --mode local`
- Before PR, merge, or branch handoff: `scripts/autoreview --mode branch --base origin/main`
- After a commit exists or when reviewing one exact commit: `scripts/autoreview --mode commit --commit HEAD`

## Workflow

1. Format first if formatting can move line numbers.
2. Pick the target:
   - Dirty local work: `scripts/autoreview --mode local`
   - Branch or PR work: `scripts/autoreview --mode branch --base origin/main`
   - Already committed work: `scripts/autoreview --mode commit --commit HEAD`
   - If `--base` is omitted for branch review, the helper tries optional
     `gh pr view` base detection and then falls back to the default base.
3. Treat review output as advisory. Verify every finding by reading the real
   code path and adjacent files before changing code.
4. Reject unrealistic edge cases, speculative risks, broad rewrites, and fixes
   that over-complicate the codebase.
5. Prefer small fixes at the right ownership boundary. Do not refactor unless it
   clearly addresses the accepted bug class.
6. If a review-triggered fix changes code, rerun focused tests and rerun
   `scripts/autoreview` on the updated target. First verify that the accepted
   findings from the previous pass are resolved; treat unrelated new findings
   as advisory unless they expose a concrete regression in the changed scope.
7. Stop once the helper exits cleanly with no accepted/actionable findings. Do
   not run an extra review only to get nicer closeout wording.

## Helper Commands

```bash
scripts/autoreview --mode local
scripts/autoreview --mode branch --base origin/main
scripts/autoreview --mode commit --commit HEAD
scripts/autoreview --json doctor
```

Useful options:

- `--prompt` or `--prompt-file`: add review context.
- `--dataset`: attach a small evidence file to the review prompt.
- `--base`: set the branch review base explicitly. If omitted, branch mode
  tries `gh pr view --json baseRefName --jq .baseRefName` when `gh` is
  available, then falls back to the default base.
- `--model`: pass an explicit Codex model.
- `--dry-run`: build the target bundle and prompt without calling Codex.
- `--json-output`: write the validated structured report to a file.
- `--heartbeat-seconds`: change the long-running Codex review heartbeat
  interval. The default is 60 seconds.
- `--no-web-search`: omit Codex web search for the review run.

The helper prints `autoreview clean: no accepted/actionable findings reported`
when Codex returns a valid clean report. It exits nonzero when accepted findings
remain, when the structured report is invalid, or when the review target cannot
be resolved.
Long Codex reviews emit `review still running: codex elapsed=<seconds>s
pid=<pid>` to stderr while the review subprocess is still active.

## Final Report

Include:

- the review command used;
- tests or proof run after any accepted finding was fixed;
- findings accepted or rejected, with a brief reason;
- the clean result from the final helper run, or why a remaining finding was
  consciously rejected.

Do not push just to review. Push only when the user requested push, ship, or PR
updates.

## CLI Maintenance

- Keep normal runtime execution on `scripts/autoreview`.
- Keep the helper Python standard-library only unless a concrete reliability
  issue justifies more.
- Keep `scripts/autoreview --version` as the semver source of truth.
- Re-verify helper changes with `scripts/autoreview --help`,
  `scripts/autoreview --version`, `scripts/autoreview --json doctor`, and a
  dry-run fixture before relying on the runtime surface.
