---
name: autoreview
description: Explicitly run a bounded Codex-only closeout review, adding one native Codex review only for high-risk changes, reusing clean evidence, and verifying committed fixes incrementally.
---

# Auto Review

## Scope

AutoReview is an explicitly invoked, read-only closeout review for a coherent
repository change. It may be invoked directly by the user or explicitly by a
composing workflow. It reviews dirty local, branch, or exact-commit targets,
returns structured findings and evidence, and may add one native Codex lens for
high-risk changes.

The supported entrypoint is `scripts/autoreview`. AutoReview does not implement
fixes, mutate the repository, submit or approve pull requests, or own tracker,
CI, merge, deployment, or release actions. Explicit invocation selects this
workflow; it does not by itself require launching the helper. Apply the
freshness contract below first.

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
Codex engine execution. Local mode sends Git status, staged and unstaged diffs,
and every non-ignored untracked text file. Branch and commit modes send the
selected diff and stat. Any `--prompt`, `--prompt-file`, or `--dataset` content
is also sent. Prompt and dataset files must be repo-relative regular UTF-8
files opened component-by-component from a pinned repository descriptor without
absolute paths, parent traversal, or symlinks. Local mode requires two
consecutive input captures to match. AutoReview does not truncate review input:
binary, unreadable, non-UTF-8, oversized, or concurrently changing input fails
before that prompt is sent to Codex and is reported as incomplete.
Under `review_profile=high-risk`, the one native `codex review` sends the same
selected repository target through the Codex engine. `read-only` prohibits
mutation; it does not mean offline. `--no-web-search` disables reviewer web
search, not the Codex engine transfer. The reviewer remains repository-aware
and may inspect readable unchanged repository files.

AutoReview must not ask a separate prose confirmation such as "Do you
explicitly approve sending this patch and review prompt?" The disclosure above
is a runtime description, not an authorization protocol. Use approval UI only
when the host runtime itself requires it. A skill cannot waive that host gate;
if the host denies execution, report the host-level blocker and stop instead of
turning the denial into another manual-consent loop.

## Canonical Closeout Sequence

1. Read [references/review-policy.md](references/review-policy.md), derive
   `review_profile=standard|high-risk`, and finish the coherent candidate HEAD
   before opening a review lineage.
2. Apply `Review Evidence Freshness`. If clean evidence is reusable, return it
   to the caller and skip the helper invocation.
3. Run the focused local tests or proof first.
4. Run `scripts/autoreview` on the correct target mode. For `high-risk`, also
   run the single native Codex review selected by the review policy on the same
   unchanged HEAD.
5. Verify and aggregate findings from both lenses before accepting fixes.
6. Fix only the accepted findings in one coherent batch when possible.
7. Rerun focused tests or proof if code changed.
8. For committed branch work, read
   [references/evidence-chain.md](references/evidence-chain.md), disposition
   every finding, import native findings with `finding_source=codex-review`, and
   use `review_phase=fix-verification` after accepted fixes. Local or
   exact-commit targets without chain evidence rerun a full review.
9. Stop on `terminal-clean`, policy-qualified `verification-clean`,
   `terminal-composite-clean`, or consciously rejected remaining findings.
   Do not run `terminal-full` automatically. Repeated feedback without a
   substantive changed head is `review-no-progress`, not permission for an
   unbounded retry loop.

## Runtime Surface

- The supported runtime entrypoint is `scripts/autoreview` inside this skill.
- AutoReview always runs `gpt-5.6-sol`. It ignores user model and reasoning
  defaults and accepts no alternate model.
- Pass the derived `review_profile` to the helper. It maps
  `review_profile=standard` to `model_reasoning_effort=high` and
  `review_profile=high-risk` to `model_reasoning_effort=xhigh`. No lower,
  `max`, or `ultra` effort is part of this bounded review contract.
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

### In simple words: which problem to fix and how

`[Medium][Edge case]` In two monitored runs, the reviewer returned a result
that said the review failed but did not name any actual problem, so the helper
could not safely use it. The helper never guesses a finding or calls an invalid
result clean. A composing workflow may journal the ordinary invocation and
apply its own bounded recovery policy without giving AutoReview access to the
caller's state store.

The validated JSON result uses canonical option values:

- `review_outcome=pass|fail`
- `priority=0|1|2|3`, rendered to people as `P0` through `P3`
- `finding_category=bug|security|regression|test-gap|maintainability`

`review_explanation`, `review_confidence`, finding prose, and code locations
remain separate data. Human output may explain the result as "patch is correct"
or "patch is incorrect", but callers must branch on `review_outcome`.
Helper-owned `review_input` contains `input_complete` and `omissions`.
Successful review and dry-run results always use `input_complete=true` with an
empty omission list. AutoReview never launches an initial or repair model call
with input already known to be incomplete. Under `--json`, the structured error
uses `input_complete=false` and records each rejected or omitted source, path,
and canonical reason. Callers must not treat an incomplete input error as clean
review evidence.

Each omission uses:

- `source=branch-diff|commit-diff|dataset|fix-delta|prompt-file|review-prompt|staged-diff|unstaged-diff|untracked-file`
- `reason=binary|changed-during-read|non-utf8|size-limit|symlink|unreadable|unsafe-path`
- `path=<repo-relative-or-rejected-path>|null`; aggregate prompt omissions use
  `null`

For committed branch fix loops, the evidence-chain contract additionally uses
`review_phase=full|fix-verification|disposition|terminal-full` and terminal state
`fix-required|verification-clean|terminal-clean|terminal-composite-clean`.
Read [references/review-policy.md](references/review-policy.md) and
[references/evidence-chain.md](references/evidence-chain.md) before using those
values or their strict finding-intake file.

## Closeout Entry Modes

- When fresh review is needed for dirty local work: `scripts/autoreview --review-profile <derived-profile> --mode local`
- When fresh review is needed for a PR, merge, or branch handoff: `scripts/autoreview --review-profile <derived-profile> --mode branch --base origin/main`
- When fresh review is needed for one exact commit: `scripts/autoreview --review-profile <derived-profile> --mode commit --commit HEAD`

## Workflow

1. Apply `Review Evidence Freshness`; skip the helper when clean evidence still
   covers the unchanged effective patch.
2. Format first if formatting can move line numbers. Formatting that changes the
   patch invalidates earlier evidence.
3. Pick the target:
   - Dirty local work: `scripts/autoreview --review-profile <derived-profile> --mode local`
   - Branch or PR work: `scripts/autoreview --review-profile <derived-profile> --mode branch --base origin/main`
   - Already committed work: `scripts/autoreview --review-profile <derived-profile> --mode commit --commit HEAD`
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
8. Stop once the review policy accepts the clean evidence and no
   accepted/actionable findings remain. Do
   not rerun it only for a later lifecycle boundary or nicer closeout wording.

## Helper Commands

```bash
scripts/autoreview --review-profile standard --mode local
scripts/autoreview --review-profile standard --mode branch --base origin/main
scripts/autoreview --review-profile standard --mode commit --commit HEAD
scripts/autoreview --review-profile high-risk --mode branch --base origin/main
scripts/autoreview --json doctor
scripts/autoreview --json findings template --finding-source codex-review --output /tmp/autoreview-finding-draft.json
scripts/autoreview --json findings prepare --input /tmp/autoreview-finding-draft.json --output /tmp/autoreview-findings.json
```

Useful options:

- `--prompt`: add inline review context.
- `--prompt-file`: add review context from a repo-relative, non-symlink UTF-8
  regular file.
- `--dataset`: attach a repo-relative, non-symlink UTF-8 regular evidence file
  to the review prompt.
- `--base`: set the branch review base explicitly. If omitted, branch mode
  tries `gh pr view --json baseRefName --jq .baseRefName` when `gh` is
  available, then falls back to the default base.
- `--review-profile`: pass AutoReview's derived `standard|high-risk` result.
  The helper selects Sol with `high|xhigh` reasoning from that result; this is
  not a user preference or a free-form model control.
- `--dry-run`: build the target bundle and prompt without calling Codex.
- `--json-output`: write the validated structured report to a file.
- `--review-phase`, `--prior-evidence`, `--finding-file`, and
  `--evidence-output`: create or continue the committed-branch evidence chain
  documented in `references/evidence-chain.md`.
- Composing workflows call the ordinary AutoReview surface. They may journal
  the exact invocation and result externally, but AutoReview never reads or
  mutates another skill's state, claim, controller, or cache.
- `findings template|prepare`: emit a strict draft without caller-generated ids,
  then validate authoritative fields and generate canonical ids locally. These
  operations never call Codex or consume review budget.
- `--heartbeat-seconds`: change the long-running Codex review heartbeat
  interval. The default is 60 seconds.
- `--no-web-search`: omit Codex web search for the review run.

The helper prints `autoreview clean: no accepted/actionable findings reported`
when Codex returns a valid clean report. It exits nonzero when accepted findings
remain, when review input is incomplete, when the structured report is invalid,
or when the review target cannot be resolved. The aggregate review prompt is
bounded at 512,000 UTF-8 bytes and fails rather than truncating when that limit
is exceeded.
Long Codex reviews emit `review still running: codex elapsed=<seconds>s
pid=<pid>` to stderr while the review subprocess is still active.

Under `--json`, environment failures preserve the human `error` and add stable
`error_code` plus `recovery` fields. `codex-home-unwritable` and
`codex-network-unavailable` require `reroute-to-capable-root`; generic
`codex-engine-failed` requires inspection before rerouting.

## Final Report

Include:

- the derived `review_profile` and the evidence-backed risk boundary;
- the fixed `gpt-5.6-sol` model and derived `high|xhigh` reasoning effort;
- the review command used, or the prior command and result reused;
- for `high-risk`, the one native Codex review selector and confirmation that
  it inspected the same candidate HEAD;
- when reusing evidence, proof that the effective patch and scope are unchanged;
- tests or proof run after any accepted finding was fixed;
- findings accepted or rejected, with a brief reason;
- confirmation that `review_input.input_complete=true` and no input was
  omitted;
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
