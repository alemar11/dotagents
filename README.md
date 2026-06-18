# dotagents

Reusable Codex skills, project maintainer skills, optional repo-local plugins, and MCP install helpers.

This repository is organized around reusable installable skills:

- **Reusable skills** under `skills/`, which can be linked locally or installed into Codex.

Project-only maintainer workflows live under `.agents/skills/`, optional repo-local plugin discovery lives under `.agents/plugins/`, and global MCP setup helpers live under `mcps/`.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `skills/` | Reusable skills, each with a `SKILL.md` entrypoint and `agents/openai.yaml` metadata. |
| `plugins/` | Optional repo-local Codex plugins, each with `.codex-plugin/plugin.json` and optional bundled skills. |
| `.agents/skills/` | Project-local maintainer skills for working on this repository. |
| `.agents/plugins/marketplace.json` | Local plugin discovery surface for this checkout. |
| `mcps/` | Helpers for installing global Codex MCP server entries not bundled with Codex itself. |
| `skills-link.sh` | Local development helper that links reusable skills into `~/.agents/skills`. |

## Repo-Local Plugins

There are currently no repo-local plugins registered in `.agents/plugins/marketplace.json`.

## Reusable Skills

| Skill | Purpose |
| --- | --- |
| `autoreview` | Run Codex-only structured closeout review before final, commit, PR, or ship. |
| `code-wiki` | Explore a local repository or git URL, then generate an evidence-backed linked HTML code wiki. |
| `crusty` | Direct-only skeptical critique for work decisions, plans, architecture, naming, and tradeoffs. |
| `domain-modeling` | Build and maintain project domain language and durable decisions while work is being clarified. |
| `git-commit` | Handle commit and push-only requests with direct `git` commands and explicit staging. |
| `github-ci` | Inspect GitHub Actions checks and failing PR logs with a focused `ci-inspect` CLI. |
| `github-deep-review` | Review GitHub issues, PRs, and fixes by tracing root cause, provenance, proof, and fix quality. |
| `github-portfolio-triage` | Scan multiple explicit GitHub repositories read-only for queue, CI, release, and next-action summaries. |
| `github-releases` | Check, plan, draft, publish, and validate GitHub Releases, tags, notes, and package availability. |
| `github-review-threads` | Inspect PR review threads and route selected replies with a focused `reviews` CLI. |
| `github-stars` | Manage authenticated-user GitHub stars and star lists with a focused `stars` CLI. |
| `github-triage` | Inspect and triage current-repo GitHub issue and PR queues with direct `gh` commands. |
| `grill-with-docs` | Stress-test repo-backed plans while updating context docs and ADRs. |
| `improve-codebase-architecture` | Find architecture candidates, then pressure-test the selected refactor. |
| `skill-cli-creator` | Build host-aware embedded CLIs that live inside a skill or plugin under `scripts/`. |
| `tanstack` | Review and implement TanStack product and integration patterns through one reusable skill with focused references. |
| `codex-changelog` | Check installed Codex CLI and Codex App versions, then print CLI and app changelog sections. |
| `xcode-changelog` | Resolve active Xcode notes, include latest notes when behind, look up a version, or list Apple Xcode release notes. |
| `plan-harder` | Create higher-rigor implementation plans or harden single issues before coding. |
| `grill-me` | Stress-test plans, decisions, designs, drafts, strategies, workflows, and coding approaches before action. |
| `learn` | Capture durable corrections or preferences and write confirmed learnings only to `AGENTS.md`. |
| `codex-orchestrator` | Coordinate workers with root-owned lifecycle, standalone Git/GitHub companion skills, gates, ledgers, and closure follow-ups. |
| `postgres` | Connect to Postgres databases, run SQL and diagnostics, inspect schemas and migrations, and review query performance. |
| `skill-audit` | Audit installed Codex skills, plugin packages, and bundled plugin skills using repo, memory, session, and portfolio-health evidence. |
| `swift-api-design` | Design or review Swift APIs using curated summaries and a bundled copy of the official Swift API Design Guidelines. |
| `swift-docc` | Write, structure, review, and publish Swift-DocC documentation using curated summaries and a bundled upstream DocC source tree. |
| `yeet` | Publish local work as a branch and draft PR by composing standalone git and GitHub skills. |

### TanStack References

The reusable `tanstack` skill covers TanStack AI, CLI, Config, DB, Devtools, Form, Pacer, Query, Ranger, Router, Start, Store, Table, Virtual, and cross-stack integration from one `$tanstack` invocation surface.

- Product references live under `skills/tanstack/references/`: `ai.md`, `cli.md`, `config.md`, `db.md`, `devtools.md`, `form.md`, `integration.md`, `pacer.md`, `query.md`, `ranger.md`, `router.md`, `start.md`, `store.md`, `table.md`, `virtual.md`.
- Router references include `router-routing-structure.md`, `router-navigation-and-search.md`, `router-data-loading-and-ssr.md`, `router-auth-and-failures.md`, and `router-plugin-and-splitting.md`.
- Start references include `start-framework-and-execution.md`, `start-server-functions-and-routes.md`, `start-middlewares-and-server-core.md`, `start-server-components-and-migrations.md`, and `start-deployments.md`.
- CLI references include `cli-scaffolding.md`, `cli-addons-existing-app.md`, `cli-ecosystem-integrations.md`, `cli-custom-addons-dev-watch.md`, and `cli-docs-and-library-metadata.md`.

This repository ships one broad reusable `tanstack` skill rather than separate upstream-style product plugins, narrow focused skills, or bundle aliases such as `tanstack-all`. For TanStack application work, install the reusable TanStack skill instead of copying advice from mixed community sources.

## Skill Dependencies

- `code-wiki` requires `$imagegen` when generating raster overview or conceptual images for a wiki.
- `codex-orchestrator` requires `$autoreview` and the relevant standalone Git/GitHub skills for GitHub-backed triage, CI, review, release, commit, or publish work: `$github-triage`, `$github-portfolio-triage`, `$github-ci`, `$github-deep-review`, `$github-review-threads`, `$github-releases`, `$git-commit`, and `$yeet`.
- `grill-with-docs` requires `$grill-me` and `$domain-modeling` so it can run the questioning loop and update project context docs or ADRs inline.
- `improve-codebase-architecture` requires `$grill-with-docs` to pressure-test the selected architecture candidate before implementation.
- `yeet` requires `$git-commit`; it may route to `$github-triage`, `$github-deep-review`, `$github-ci`, or `$github-review-threads` for focused GitHub follow-up work.

## Project-Local Skills

| Skill | Path | Purpose |
| --- | --- | --- |
| Maintainer | `.agents/skills/Maintainer/` | Maintain and improve one or more skills or plugins in this repository with shared upgrade workflows and skill-specific refresh tasks. |

Project-local skills are repository-specific and are not included in reusable install commands.

## Installation

### Use Repo-Local Plugins

Repo-local plugins are exposed through `.agents/plugins/marketplace.json`; they are not installed by `skills-link.sh`.

No repo-local plugins are currently registered. Use the standalone reusable git and GitHub skills for git authoring, GitHub triage, CI, reviews, releases, and publishing.

### Link Reusable Skills For Local Development

Run this from the repository root to link `skills/` into `~/.agents/skills`:

```sh
./skills-link.sh
```

This helper only links reusable skills. It does not install, mirror, or rewrite plugin marketplace entries.

### Install Reusable Skills With `skill-installer` (Codex-only)

Inside Codex, install all reusable skills with:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/autoreview skills/code-wiki skills/crusty skills/domain-modeling skills/git-commit skills/github-ci skills/github-deep-review skills/github-portfolio-triage skills/github-releases skills/github-review-threads skills/github-stars skills/github-triage skills/grill-with-docs skills/improve-codebase-architecture skills/skill-cli-creator skills/tanstack skills/codex-changelog skills/xcode-changelog skills/plan-harder skills/grill-me skills/learn skills/codex-orchestrator skills/postgres skills/skill-audit skills/swift-api-design skills/swift-docc skills/yeet
```

Install one reusable skill by passing only its path:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/code-wiki
```

Replace `skills/code-wiki` with any path listed in the reusable skills table.

### Install Reusable Skills With `npx skills`

These commands use the [`vercel-labs/skills`](https://github.com/vercel-labs/skills) CLI and target Codex directly.

List the skills available in this repository:

```sh
npx skills add alemar11/dotagents --list
```

Install all reusable skills globally for Codex:

```sh
npx skills add alemar11/dotagents -a codex -g -y \
  --skill autoreview \
  --skill code-wiki \
  --skill crusty \
  --skill domain-modeling \
  --skill git-commit \
  --skill github-ci \
  --skill github-deep-review \
  --skill github-portfolio-triage \
  --skill github-releases \
  --skill github-review-threads \
  --skill github-stars \
  --skill github-triage \
  --skill grill-with-docs \
  --skill improve-codebase-architecture \
  --skill skill-cli-creator \
  --skill tanstack \
  --skill codex-changelog \
  --skill xcode-changelog \
  --skill plan-harder \
  --skill grill-me \
  --skill learn \
  --skill codex-orchestrator \
  --skill postgres \
  --skill skill-audit \
  --skill swift-api-design \
  --skill swift-docc \
  --skill yeet
```

Install one reusable skill globally for Codex:

```sh
npx skills add alemar11/dotagents -a codex -g -y --skill code-wiki
```

Replace `code-wiki` with any skill name from the reusable skills table. Omit `-g` to install into the current project's `.agents/skills/` instead of your global `~/.codex/skills/`.

Restart Codex after installing or updating skills.
