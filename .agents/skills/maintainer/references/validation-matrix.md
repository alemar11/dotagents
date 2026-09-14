# Validation Matrix

Select every lane touched by the maintenance change. A mixed change uses the
union of its lanes; one successful lane never substitutes for another.

| Change type | Required proof |
| --- | --- |
| Docs or metadata | Parse touched YAML/frontmatter, verify descriptions and repo docs, check links/references, run `git diff --check`. |
| Runtime skill instructions | Statically review affected handoffs, triggers, authority, completion, and reference paths; validate metadata. Use existing behavioral tests only when affected, and a bounded scenario only for uncertainty static review cannot resolve. Do not add prose tests. |
| Composed workflow | Review affected routing, authority, recovery, and closeout contracts. Run existing contract suites when their executable behavior is affected; use bounded disposable-repo scenarios only for uncertainty static checks cannot resolve. Remove fixtures and verify cleanup. |
| Embedded CLI | Run its tests, shipped `--help`, `--version`, `--json doctor`, and one safe fixture/dry-run/read-only operation. |
| Plugin | Apply the required semantic version bump, align embedded CLI version, rebuild deterministically, run plugin tests, reinstall, compare source/cache artifacts, and prove from before/after status that reinstall introduced no checkout changes. |
| Migration or removal | Scan callers/dependencies/install docs, verify replacement discovery, prove retired surfaces are absent, and test the chosen compatibility policy. |
| Codex dependency change | Verify each affected `SKILL.md` and its nearest local `AGENTS.md` when a maintenance contract changes; keep Codex contracts explicit and portable fallbacks generic. |
| Non-trivial implementation | Run native `codex review` on the final scoped diff and resolve or disposition accepted findings before commit/publication. |

## Evidence Rules

- Record the selected lanes before validation.
- Use full source/diff state once. During iteration prefer `git status --short`,
  `git diff --stat`, `git diff --name-only`, focused hunks, fingerprints, and
  failed-gate excerpts.
- Read the complete relevant diff before final review and publication.
- Record commands, artifact paths or refs, fingerprints/versions, results, and
  skipped proof with its blocker.
- A required lane that cannot run is `result=fail` unless the user explicitly accepts a
  narrower delivery result.
- Reuse passing checks across selected lanes. Broaden or repeat validation only
  after a new change, failure, or unresolved risk; prose edits alone do not
  require executable suites, hosted runs, or model experiments.

## Scenario Safety

- Keep fixtures under one disposable root outside the repository.
- Use local-only/dry-run targets and no external writes unless the user
  explicitly authorizes them.
- Snapshot repo status before and after, preserve user-owned dirty state, and
  delete fixtures at completion.
- Scenario token cost is diagnostic, not a gate. Never weaken required proof to
  meet a token target.
