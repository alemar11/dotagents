---
name: autoreview
description: Run Codex-only structured closeout review by sending the selected change bundle to a separate read-only Codex execution, reusing verified clean evidence for an unchanged target, and verifying committed review fixes incrementally before final, commit, PR, or ship.
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
- a later commit, push, or finalization turn when verified clean review evidence
  still covers the unchanged effective patch

Selecting this skill starts the review workflow; it does not by itself require
launching the helper. Apply the freshness contract below first.

## Review Evidence Freshness

Before launching `scripts/autoreview`, find the latest completed Auto Review for
the intended target in the current task, imported task or session evidence, or a
trusted caller handoff. Reuse it without another helper invocation only when:

- the result is clean, or every remaining finding was consciously rejected;
- the repository and effective patch content and scope are unchanged; and
- the prior command, result, and reviewed target are verifiable.

Staging an unchanged patch, committing exactly that patch, pushing its commit,
or moving from implementation finalization to commit finalization does not
invalidate clean review evidence. A local review may cover the resulting commit
when its full patch is identical. A branch or PR review is reusable only when no
additional commit or changed path expands the reviewed scope.

Run Auto Review again when changed content or paths alter the effective patch,
formatting or generated refreshes alter it, an accepted finding fix changes it,
the branch/base/commit scope expands, the previous result or target cannot be
verified, or the user explicitly asks to review again. A commit, push, PR, ship,
or final-response boundary alone is not a rerun reason.

## Codex Data Transfer

Running the helper sends the selected review bundle to a separate ephemeral
Codex engine execution. This transfer is intrinsic read-only runtime behavior,
not a separate permission boundary. Local mode sends Git status, staged and
unstaged diffs, and every non-ignored untracked file. For untracked files, a NUL
byte replaces the contents with an omission marker; all other bytes are decoded
as text with replacement characters. Branch and commit modes send the selected
diff and stat. Any `--prompt`, `--prompt-file`, or `--dataset` content is also
sent.

After the user explicitly invokes Auto Review or authorizes a calling workflow
that includes it, run without a separate authorization question, acknowledgement
flag, or user-controlled option. A calling workflow with one initial
authorization must disclose this transfer there and treat that single grant as
covering later Auto Review reruns required by a changed target. `read-only`
prohibits mutation; it does not mean offline. `--no-web-search` disables reviewer
web search, not the Codex engine transfer.

## Canonical Closeout Sequence

1. Apply `Review Evidence Freshness`. If clean evidence is reusable, return it
   to the caller and skip the helper invocation.
2. Run the focused local tests or proof first.
3. Run `scripts/autoreview` on the correct target mode.
4. Verify each finding in the real code before accepting it.
5. Fix only the accepted findings.
6. Rerun focused tests or proof if code changed.
7. For committed branch work, read
   [references/evidence-chain.md](references/evidence-chain.md), disposition
   every finding, and use `review_phase=fix-verification` after accepted fixes.
   Local or exact-commit targets without chain evidence rerun a full review.
8. After fixes to the first full review are delta-clean, run the one allowed
   `terminal-full`. Resolve findings from that pass through further progressing
   fix verifications; do not run a third full review in the same lineage.
9. Stop on `terminal-clean`, `terminal-composite-clean`, or consciously rejected
   remaining findings. Repeated feedback without a substantive changed head is
   `review-no-progress`, not permission for an unbounded retry loop.

## Runtime Surface

- The supported runtime entrypoint is `scripts/autoreview` inside this skill.
- If your current working directory is the skill root, run
  `scripts/autoreview --help`.
- If invoking from another repo, resolve the installed skill root first and run
  `<autoreview-skill-root>/scripts/autoreview ...`.
- This skill is Codex-dependent. The helper requires local `git`, the Codex CLI
  `exec` command, structured output flags, a writable `CODEX_HOME` state
  surface, Codex engine network access, and read-only review execution.
- Run `scripts/autoreview --json doctor` before delegating review to a worker
  with an uncertain permission profile. If it returns
  `recovery=reroute-to-capable-root`, reroute the review instead of copying
  credentials or repeatedly retrying the worker.
- The doctor verifies `CODEX_HOME` and temporary-directory writability with
  file create/delete probes when those directories exist; permission bits alone
  are not capability proof. A missing `CODEX_HOME` is reported as unverified
  without creating configuration directories, then `codex exec` provides the
  authoritative success or structured failure.

## Structured Result Contract

The validated JSON result uses canonical option values:

- `review_outcome=pass|fail`
- `priority=0|1|2|3`, rendered to people as `P0` through `P3`
- `finding_category=bug|security|regression|test-gap|maintainability`

`review_explanation`, `review_confidence`, finding prose, and code locations
remain separate data. Human output may explain the result as "patch is correct"
or "patch is incorrect", but callers must branch on `review_outcome`.

For committed branch fix loops, the evidence-chain contract additionally uses
`review_phase=full|fix-verification|disposition|terminal-full` and terminal state
`fix-required|verification-clean|terminal-clean|terminal-composite-clean`.
Read [references/evidence-chain.md](references/evidence-chain.md) before using
those values or their strict finding-intake file.

## Closeout Entry Modes

- When fresh review is needed for dirty local work: `scripts/autoreview --mode local`
- When fresh review is needed for a PR, merge, or branch handoff: `scripts/autoreview --mode branch --base origin/main`
- When fresh review is needed for one exact commit: `scripts/autoreview --mode commit --commit HEAD`

## Workflow

1. Apply `Review Evidence Freshness`; skip the helper when clean evidence still
   covers the unchanged effective patch.
2. Format first if formatting can move line numbers. Formatting that changes the
   patch invalidates earlier evidence.
3. Pick the target:
   - Dirty local work: `scripts/autoreview --mode local`
   - Branch or PR work: `scripts/autoreview --mode branch --base origin/main`
   - Already committed work: `scripts/autoreview --mode commit --commit HEAD`
   - If `--base` is omitted for branch review, the helper tries optional
     `gh pr view` base detection and then falls back to the default base.
4. Treat review output as advisory. Verify every finding by reading the real
   code path and adjacent files before changing code.
5. Reject unrealistic edge cases, speculative risks, broad rewrites, and fixes
   that over-complicate the codebase.
6. Prefer small fixes at the right ownership boundary. Do not refactor unless it
   clearly addresses the accepted bug class.
7. If a review-triggered fix changes a committed branch, rerun focused tests
   and follow [references/evidence-chain.md](references/evidence-chain.md).
   Fix verification examines only accepted findings and regressions on changed
   delta lines. A base, merge-base, repository, or path-set expansion starts a
   new full-review lineage.
8. Stop once terminal evidence has no accepted/actionable findings. Do
   not rerun it only for a later lifecycle boundary or nicer closeout wording.

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
- `--review-phase`, `--prior-evidence`, `--finding-file`, and
  `--evidence-output`: create or continue the committed-branch evidence chain
  documented in `references/evidence-chain.md`.
- `--heartbeat-seconds`: change the long-running Codex review heartbeat
  interval. The default is 60 seconds.
- `--no-web-search`: omit Codex web search for the review run.

The helper prints `autoreview clean: no accepted/actionable findings reported`
when Codex returns a valid clean report. It exits nonzero when accepted findings
remain, when the structured report is invalid, or when the review target cannot
be resolved.
Long Codex reviews emit `review still running: codex elapsed=<seconds>s
pid=<pid>` to stderr while the review subprocess is still active.

Under `--json`, environment failures preserve the human `error` and add stable
`error_code` plus `recovery` fields. `codex-home-unwritable` and
`codex-network-unavailable` require `reroute-to-capable-root`; generic
`codex-engine-failed` requires inspection before rerouting.

## Final Report

Include:

- the review command used, or the prior command and result reused;
- when reusing evidence, proof that the effective patch and scope are unchanged;
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
