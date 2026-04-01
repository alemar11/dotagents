# Skills

This directory contains reusable skills and project maintainer skills—task-specific packages of instructions, resources, and optional scripts that help agents follow workflows reliably.

## Skills
- `git-commit/` — Create a well-formed git commit with rationale, explicit staging, and monorepo-safe scope.
- `ask-questions-if-underspecified/` — Clarify requirements before implementing when a request is underspecified or the user asks for clarification.
- `codex-changelog/` — Check the installed Codex CLI and Codex App versions, then print CLI notes from `openai/codex/releases` and app notes from the OpenAI Codex changelog page.
- `plan-hard/` — Create a higher-rigor implementation plan with deeper clarification, a gotcha pass, and a saved `plans/<topic>-plan.md` output.
- `github/` (`GitHub`) — Triage repo-scoped GitHub work, handle issue lifecycle and PR metadata, and route specialist workflows.
- `github-reviews/` (`GitHub Reviews`) — Inspect unresolved PR review feedback, draft or post replies, and submit reviews with thread-aware context.
- `github-ci/` (`GitHub CI`) — Inspect PR checks and GitHub Actions failures while keeping PR-check triage separate from generic run inspection.
- `github-releases/` (`GitHub Releases`) — Plan and create GitHub releases and tags with explicit target resolution and notes strategy.
- `github-publish/` (`GitHub Publish`) — Inspect current-branch publish context, open or reuse pull requests, and manage PR lifecycle state once the branch is already ready or pushed.
- `yeet/` (`Yeet`) — Orchestrate full publish from a local checkout by choosing branch strategy, using `git-commit` for commit discipline, pushing, and handing off to `github-publish` for PR opening or reuse.
- `learn/` — Capture durable corrections or preferences and write confirmed learnings only to `AGENTS.md` when the user sets lasting guidance.
- `postgres/` — Connect to Postgres databases, design schemas and indexes, review SQL/query performance, and use common PostGIS or pgvector patterns.
- `skill-audit/` — Audit installed or user-specified Codex skills using repo evidence, memory, and current context to plan updates, merges, or disables.
- `swift-api-design/` — Design or review Swift APIs using curated local summaries and a bundled upstream copy of the official Swift API Design Guidelines.
- `swift-docc/` — Write, structure, review, and publish Swift-DocC documentation using curated local summaries and a bundled upstream DocC source tree.

## Skill Dependencies
- `github/` requires `github-reviews/`, `github-ci/`, `github-releases/`, `github-publish/`, and `yeet/` for specialist GitHub workflows. The supported install path is the full GitHub suite.
- `yeet/` requires `git-commit/` and `github-publish/` as companion skills for commit discipline and post-push PR handling.

## Project Skills
- `.agents/skills/skills-maintainer/` — Maintain and improve one or more skills in this repository with shared upgrade workflows and skill-specific refresh tasks.
Project skills are repository-local and are not included in the reusable install examples below.

## Codex

### Install With skill-installer (Codex-only)
These prompts are for use inside Codex only.
Copy/paste one of these prompts:

- `Use $skill-installer to install skills from alemar11/skills --path git-commit ask-questions-if-underspecified codex-changelog plan-hard github github-reviews github-ci github-releases github-publish yeet learn postgres skill-audit swift-api-design swift-docc`
- `Use $skill-installer to install skills from alemar11/skills --path git-commit github github-reviews github-ci github-releases github-publish yeet`
- `Use $skill-installer to install skills from alemar11/skills --path github-reviews`
- `Use $skill-installer to install skills from alemar11/skills --path github-ci`
- `Use $skill-installer to install skills from alemar11/skills --path github-releases`
- `Use $skill-installer to install skills from alemar11/skills --path github-publish`
- `Use $skill-installer to install skills from alemar11/skills --path git-commit github-publish yeet`
- `Use $skill-installer to install skills from alemar11/skills --path git-commit`
- `Use $skill-installer to install skills from alemar11/skills --path ask-questions-if-underspecified`
- `Use $skill-installer to install skills from alemar11/skills --path codex-changelog`
- `Use $skill-installer to install skills from alemar11/skills --path plan-hard`
- `Use $skill-installer to install skills from alemar11/skills --path learn`
- `Use $skill-installer to install skills from alemar11/skills --path postgres`
- `Use $skill-installer to install skills from alemar11/skills --path skill-audit`
- `Use $skill-installer to install skills from alemar11/skills --path swift-api-design`
- `Use $skill-installer to install skills from alemar11/skills --path swift-docc`

### Install With `npx skills` (Vercel Skills CLI)
These commands use the [`vercel-labs/skills`](https://github.com/vercel-labs/skills) CLI and target Codex directly.

List the skills available in this repository:

```sh
npx skills add alemar11/skills --list
```

Install all reusable skills globally for Codex:

```sh
npx skills add alemar11/skills -a codex -g -y \
  --skill git-commit \
  --skill ask-questions-if-underspecified \
  --skill codex-changelog \
  --skill plan-hard \
  --skill github \
  --skill github-reviews \
  --skill github-ci \
  --skill github-releases \
  --skill github-publish \
  --skill yeet \
  --skill learn \
  --skill postgres \
  --skill skill-audit \
  --skill swift-api-design \
  --skill swift-docc
```

Install the full GitHub suite globally for Codex:

```sh
npx skills add alemar11/skills -a codex -g -y \
  --skill git-commit \
  --skill github \
  --skill github-reviews \
  --skill github-ci \
  --skill github-releases \
  --skill github-publish \
  --skill yeet
```

Breaking change: standalone `github` no longer covers review, CI, release/tag,
PR publish/lifecycle, or full publish-from-worktree workflows. Install
`github-reviews`, `github-ci`, `github-releases`, `github-publish`, and
`yeet` alongside `github`, plus `git-commit` because `yeet` depends on it, for
the supported GitHub suite layout.

Install an individual skill globally for Codex:

```sh
npx skills add alemar11/skills -a codex -g -y --skill github-reviews
```

```sh
npx skills add alemar11/skills -a codex -g -y --skill github-ci
```

```sh
npx skills add alemar11/skills -a codex -g -y --skill github-releases
```

```sh
npx skills add alemar11/skills -a codex -g -y --skill github-publish
```

```sh
npx skills add alemar11/skills -a codex -g -y --skill git-commit --skill github-publish --skill yeet
```

```sh
npx skills add alemar11/skills -a codex -g -y --skill swift-api-design
```

```sh
npx skills add alemar11/skills -a codex -g -y --skill swift-docc
```

```sh
npx skills add alemar11/skills -a codex -g -y --skill plan-hard
```

Omit `-g` to install into the current project's `.agents/skills/` instead of your global `~/.codex/skills/`.
For GitHub workflows, the supported install path is the full GitHub suite, not standalone `github`.
The repository-local `skills-maintainer` skill is intentionally excluded from these commands.

Restart Codex to pick up new skills.
