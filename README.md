# dotagents

Reusable Codex skills, repo-local plugins, project maintainer skills, and MCP install helpers.

This repository is organized around two installable surfaces:

- **Reusable skills** under `skills/`, which can be linked locally or installed into Codex.
- **Repo-local plugins** under `plugins/`, which bundle related skills and shared runtime artifacts.

Project-only maintainer workflows live under `.agents/skills/`, and global MCP setup helpers live under `mcps/`.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `skills/` | Reusable skills, each with a `SKILL.md` entrypoint and `agents/openai.yaml` metadata. |
| `plugins/` | Repo-local Codex plugins, each with `.codex-plugin/plugin.json` and optional bundled skills. |
| `.agents/skills/` | Project-local maintainer skills for working on this repository. |
| `.agents/plugins/marketplace.json` | Local plugin discovery surface for this checkout. |
| `mcps/` | Helpers for installing global Codex MCP server entries not bundled with Codex itself. |
| `skills-link.sh` | Local development helper that links reusable skills into `~/.agents/skills`. |

## Repo-Local Plugins

Install repo-local plugins from this checkout through `.agents/plugins/marketplace.json`.

| Plugin | Path | Purpose |
| --- | --- | --- |
| GitStack | `plugins/gitstack/` | Bundles git commit authoring, git/gh-first GitHub workflows, maintainer triage, focused CI/review helpers, release checks, and publish orchestration. |

### GitStack Skills

`git-commit`, `github`, `github-triage`, `github-reviews`, `github-ci`, `github-releases`, `yeet`.

`plugins/gitstack/` expects both `git` and GitHub CLI `gh` on `PATH` before GitHub-backed commands run:

```sh
command -v git && git --version
command -v gh && gh --version
```

Use `plugins/gitstack/skills/github/references/core/installation.md` for cross-platform install guidance.

For linked git + GitHub workflows, install the GitStack plugin instead of looking for separate standalone `git-commit`, `github`, or `yeet` skills.

## Reusable Skills

| Skill | Purpose |
| --- | --- |
| `autoreview` | Run Codex-only structured closeout review for local changes, branch diffs, or commits. |
| `chrome-devtools` | Debug and automate live Chrome pages with Chrome DevTools MCP, the Homebrew CLI, and a hybrid session runner. |
| `code-wiki` | Explore a local repository or git URL, then generate an evidence-backed linked HTML code wiki. |
| `skill-cli-creator` | Build host-aware embedded CLIs that live inside a skill or plugin under `scripts/`. |
| `tanstack` | Review and implement TanStack product and integration patterns through one reusable skill with focused references. |
| `codex-changelog` | Check installed Codex CLI and Codex App versions, then print CLI and app changelog sections. |
| `xcode-changelog` | Resolve active Xcode notes, include latest notes when behind, look up a version, or list Apple Xcode release notes. |
| `plan-harder` | Create a higher-rigor implementation plan with focused clarification, a gotcha pass, and a saved `plans/<topic>-plan.md`. |
| `grill-me` | Stress-test plans, decisions, designs, drafts, strategies, workflows, and coding approaches before action. |
| `learn` | Capture durable corrections or preferences and write confirmed learnings only to `AGENTS.md`. |
| `postgres` | Connect to Postgres databases, run SQL and diagnostics, inspect schemas and migrations, and review query performance. |
| `skill-audit` | Audit installed Codex skills, plugin packages, and bundled plugin skills using evidence from repos, memory, sessions, and current context. |
| `swift-api-design` | Design or review Swift APIs using curated summaries and a bundled copy of the official Swift API Design Guidelines. |
| `swift-docc` | Write, structure, review, and publish Swift-DocC documentation using curated summaries and a bundled upstream DocC source tree. |

### TanStack References

The reusable `tanstack` skill covers TanStack AI, CLI, Config, DB, Devtools, Form, Pacer, Query, Ranger, Router, Start, Store, Table, Virtual, and cross-stack integration from one `$tanstack` invocation surface.

- Product references live under `skills/tanstack/references/`: `ai.md`, `cli.md`, `config.md`, `db.md`, `devtools.md`, `form.md`, `integration.md`, `pacer.md`, `query.md`, `ranger.md`, `router.md`, `start.md`, `store.md`, `table.md`, `virtual.md`.
- Router references include `router-routing-structure.md`, `router-navigation-and-search.md`, `router-data-loading-and-ssr.md`, `router-auth-and-failures.md`, and `router-plugin-and-splitting.md`.
- Start references include `start-framework-and-execution.md`, `start-server-functions-and-routes.md`, `start-middlewares-and-server-core.md`, `start-server-components-and-migrations.md`, and `start-deployments.md`.
- CLI references include `cli-scaffolding.md`, `cli-addons-existing-app.md`, `cli-ecosystem-integrations.md`, `cli-custom-addons-dev-watch.md`, and `cli-docs-and-library-metadata.md`.

This repository ships one broad reusable `tanstack` skill rather than separate upstream-style product plugins, narrow focused skills, or bundle aliases such as `tanstack-all`. For TanStack application work, install the reusable TanStack skill instead of copying advice from mixed community sources.

## Skill Dependencies

- `code-wiki` requires `$imagegen` when generating raster overview or conceptual images for a wiki.

## Project-Local Skills

| Skill | Path | Purpose |
| --- | --- | --- |
| Maintainer | `.agents/skills/Maintainer/` | Maintain and improve one or more skills or plugins in this repository with shared upgrade workflows and skill-specific refresh tasks. |

Project-local skills are repository-specific and are not included in reusable install commands.

## Installation

### Use Repo-Local Plugins

Repo-local plugins are exposed through `.agents/plugins/marketplace.json`; they are not installed by `skills-link.sh`.

- Use GitStack for linked git + GitHub workflows.

### Link Reusable Skills For Local Development

Run this from the repository root to link `skills/` into `~/.agents/skills`:

```sh
./skills-link.sh
```

This helper only links reusable skills. It does not install, mirror, or rewrite plugin marketplace entries.

### Install Reusable Skills With `skill-installer` (Codex-only)

Inside Codex, install all reusable skills with:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/autoreview skills/chrome-devtools skills/code-wiki skills/skill-cli-creator skills/tanstack skills/codex-changelog skills/xcode-changelog skills/plan-harder skills/grill-me skills/learn skills/postgres skills/skill-audit skills/swift-api-design skills/swift-docc
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
  --skill chrome-devtools \
  --skill code-wiki \
  --skill skill-cli-creator \
  --skill tanstack \
  --skill codex-changelog \
  --skill xcode-changelog \
  --skill plan-harder \
  --skill grill-me \
  --skill learn \
  --skill postgres \
  --skill skill-audit \
  --skill swift-api-design \
  --skill swift-docc
```

Install one reusable skill globally for Codex:

```sh
npx skills add alemar11/dotagents -a codex -g -y --skill code-wiki
```

Replace `code-wiki` with any skill name from the reusable skills table. Omit `-g` to install into the current project's `.agents/skills/` instead of your global `~/.codex/skills/`.

Restart Codex after installing or updating skills.
