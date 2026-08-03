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

G is the repo-local Git and GitHub workflow plugin. It uses the official GitHub connector for supported remote operations, authenticated `gh` for connector gaps, and direct `git` for local repository work. It bundles:

| Skill | Purpose |
| --- | --- |
| `g:github` | Handle general or mixed GitHub requests through the appropriate focused workflows. |
| `g:git-commit` | Create or push explicit regular, fixup, or amend-fixup commits without publishing a PR. |
| `g:github-repository-triage` | Triage issue and pull request queues across one or more repositories read-only. |
| `g:github-issues` | Manage GitHub issue lifecycle, metadata, relationships, and dry-runs. |
| `g:github-investigation` | Investigate issues, pull requests, and proposed fixes using repository evidence. |
| `g:github-actions` | Diagnose or explicitly fix failing GitHub Actions checks. |
| `g:github-review-threads` | Inspect review threads, address selected feedback, and explicitly reply or resolve. |
| `g:github-releases` | Inspect, plan, publish, and validate releases, tags, notes, assets, and packages. |
| `g:github-stars` | Manage the authenticated user's GitHub stars and star lists. |
| `g:send` | Confirm scope and resolved issues, commit, push, add automatic issue-closing references, open or update a pull request, and link it to an existing target PR when applicable. Review requests are separate. |
| `g:github-stack` | Manage stacked branches and dependent pull requests through the G stack CLI, including inspection, linking, rebase, sync, navigation, and explicit stack-wide publication or merge. |
| `g:audit` | Monitor active sessions using G skills and return a prioritized read-only report. |

SE is the repo-local project-lifecycle plugin. It keeps durable project knowledge, architecture discovery, Idea capture, Feature convergence, Implement orchestration, and active-session auditing as separate skills. The feature workflow shares one internal clarification protocol and metadata contract, while GitHub transport remains delegated to G:

| Skill | Purpose |
| --- | --- |
| `se:learn` | Maintain durable Project Context, ADRs, localization memory, confirmed corrections, and Code Review Rules. |
| `se:improve-codebase-architecture` | Find evidence-backed architecture candidates, then pressure-test the selected refactor. |
| `se:idea` | Capture durable GitHub Ideas with lightweight clarification when needed. |
| `se:feature` | Clarify material unknowns and converge Feature Specs plus agent-ready implementation issue graphs. |
| `se:implement` | Create one visible Sol/medium root controller and coordinate isolated workers through validation, review, and PR-ready delivery. |
| `se:audit` | Monitor active sessions using SE skills and return a prioritized read-only report. |

## Reusable Skills

| Skill | Purpose |
| --- | --- |
| `codex-cli` | Launch one complete prompt in a separate Codex CLI task with Sol/Terra/Luna selection and model-aware reasoning. |
| `code-wiki` | Generate an evidence-backed linked HTML wiki for a local repository or git URL. |
| `crusty` | Self-contained skeptical critique for decisions, implementations, architecture, naming, and tradeoffs. |
| `okf` | Write, scaffold, inspect, and validate Open Knowledge Format markdown bundles with the shipped OKF CLI. |
| `skill-cli-creator` | Build host-aware embedded CLIs that live inside a skill or plugin under `scripts/`. |
| `tanstack` | Review or build TanStack apps across Query, Router, Start, Form, Table, Virtual, Store, DB, AI, CLI, and integrations. |
| `codex-changelog` | Print installed Codex CLI and Codex App changelogs from GitHub Releases and the OpenAI Codex changelog page. |
| `xcode-changelog` | Resolve active Xcode notes, include latest notes when behind, look up a version, or list Apple Xcode release notes. |
| `focus` | Create a focused new Codex task from a compact handoff of the latest substantive discussion. |
| `study` | Orchestrate read-only planning, research, or analysis through one Sol task and up to five Luna workers; never write code or edit project files. |
| `postgres` | Connect to Postgres, run SQL/diagnostics, inspect schemas/migrations, and review query, PostGIS, or pgvector patterns. |
| `skill-audit` | Audit installed Codex skills and plugins from historical evidence or live App task monitoring with defect annotations. |
| `swift-api-design` | Design or review Swift APIs using local summaries and the bundled official Swift API Design Guidelines. |
| `swift-docc` | Write, structure, review, and publish Swift-DocC docs using local summaries and bundled DocC sources. |

### TanStack References

The reusable `tanstack` skill covers TanStack AI, CLI, Config, DB, Devtools, Form, Pacer, Query, Ranger, Router, Start, Store, Table, Virtual, and cross-stack integration from one `$tanstack` invocation surface.

- Product references live under `skills/tanstack/references/`: `ai.md`, `cli.md`, `config.md`, `db.md`, `devtools.md`, `form.md`, `integration.md`, `pacer.md`, `query.md`, `ranger.md`, `router.md`, `start.md`, `store.md`, `table.md`, `virtual.md`.
- Router references include `router-routing-structure.md`, `router-navigation-and-search.md`, `router-data-loading-and-ssr.md`, `router-auth-and-failures.md`, and `router-plugin-and-splitting.md`.
- Start references include `start-framework-and-execution.md`, `start-server-functions-and-routes.md`, `start-middlewares-and-server-core.md`, `start-server-components-and-migrations.md`, and `start-deployments.md`.
- CLI references include `cli-scaffolding.md`, `cli-addons-existing-app.md`, `cli-ecosystem-integrations.md`, `cli-custom-addons-dev-watch.md`, and `cli-docs-and-library-metadata.md`.

This repository ships one broad reusable `tanstack` skill rather than separate upstream-style product plugins, narrow focused skills, or bundle aliases such as `tanstack-all`. For TanStack application work, install the reusable TanStack skill instead of copying advice from mixed community sources.

## Skill Dependencies

- `study` requires an exact saved local project and the ChatGPT App task tools,
  keeps its orchestrator and workers there without worktrees, and is strictly
  read-only: it returns a Markdown analysis instead of writing code. Five is
  an absolute worker cap; larger requests are capped and reported automatically.
  One shared visual run tag links the orchestrator and worker titles while real
  thread IDs remain the only identity and recovery keys.
  After capturing terminal results, it requests archival of completed, failed,
  or explicitly abandoned workers, then leaves the orchestrator open as the
  single visible summary task. Neither the
  orchestrator nor a worker may ever invoke Study or create a nested Study run.
  Study passes Sol/medium and Luna/max explicitly at creation. It inspects the
  live creation declaration for title support, uses creation-time titles when
  available, and otherwise applies the verified fallback after a real task ID
  is returned.
  When no worker count is specified, Study normally chooses 1–2 workers for a
  focused investigation, 3 for a multi-dimensional comparison, and 4–5 only
  for broad investigations with genuinely independent tracks; five is a cap,
  not the default.
- `code-wiki` requires `$imagegen` when generating raster overview or conceptual images for a wiki.
- `maintainer` uses `$skill-audit` conditionally when health diagnosis or workflow hardening needs portfolio, prompt-quality, overlap, or session evidence; requires `$skill-creator` or `$plugin-creator` for substantial package reshapes; and requires native `codex review` for non-trivial implementation closeout.
- `se:improve-codebase-architecture` prepares a Project Context handoff after its internal pressure-test and invokes `$se:learn` only when accepted durable knowledge, named targets, evidence, and explicit scoped capture authority are present.
- `se:idea` loads the plugin workflow contract and uses `$g:github-issues` for exact GitHub preflight reads and Idea mutations.
- `se:feature` uses the plugin's internal clarification protocol for context-backed questions and `$se:learn` for context or ADR routing plus implementation-closeout handoff. Feature owns Feature Spec writing and internal issue hardening, loads the plugin workflow contract for feature metadata, and uses `$g:github-issues` for exact paginated GitHub Idea and Feature-bundle convergence reads in both run modes plus published tracker mutations.
- `se:implement` keeps discovery GitHub-only and side-effect free. Explicit execution first creates or resumes one visible `gpt-5.6-sol`/`medium` root controller in the invoking session's exact local project; the parent relays coarse milestones and the final root report. The root then reads the SE workflow contract, requires `ready-for-agent` on every final implementation issue before claims or workers, preflights exact saved Git projects, creates isolated visible workers, and ends with independently verified reviewed GitHub PRs without merging. The normal six-stage flow and exception routing live in `plugins/se/skills/implement/SKILL.md`; detailed state and recovery contracts remain in its references.
- The G-dependent SE skills run a read-only Codex plugin preflight before their first `$g:github-issues` handoff and fail closed when G is unavailable; they never install G automatically.
- Multi-repository runs additionally validate the complete linked Feature Spec Set and finish with one independently verified GitHub PR per repository plus one exact HEAD vector.

## Project-Local Skills

| Skill | Path | Purpose |
| --- | --- | --- |
| maintainer | `.agents/skills/maintainer/` | Manually audit, maintain, and re-engineer repo skills and plugins through health, lifecycle, validation, metadata, and explicit refresh workflows. |

Project-local skills are repository-specific and are not included in reusable install commands.

## Installation

### Use Repo-Local Plugins

Repo-local plugins are exposed through `.agents/plugins/marketplace.json`; they are not installed by `skills-link.sh`.

Register the `alemar11` marketplace from GitHub, then install the required plugins:

```sh
codex plugin marketplace add alemar11/dotagents --ref main
codex plugin add g@alemar11
codex plugin add se@alemar11
```

If the `alemar11` marketplace is already registered, install G directly:

```sh
codex plugin add g@alemar11
codex plugin add se@alemar11
```

For local development from a dotagents checkout, register the checkout instead
of the GitHub source, then install the same plugin:

```sh
codex plugin marketplace add /path/to/dotagents
codex plugin add g@alemar11
codex plugin add se@alemar11
```

During local development, validate the changed plugin and reinstall each
versioned plugin from the repository source. G has a dedicated helper;
SE is reinstalled directly:

```sh
plugins/g/projects/g/scripts/reinstall-local
codex plugin add se@alemar11 --json
```

For a Git-backed marketplace checkout, refresh the marketplace before reinstalling:

```sh
codex plugin marketplace upgrade alemar11
codex plugin remove g@alemar11
codex plugin add g@alemar11
codex plugin remove se@alemar11
codex plugin add se@alemar11
```

When migrating from the retired Feature Flow plugin identity, remove the old
installation before installing SE:

```sh
codex plugin remove feature-flow@alemar11
codex plugin add se@alemar11
```

Restart Codex or open a fresh task after installation so the bundled skills and GitHub connector are discovered. Do not edit installed cache copies under `~/.codex/plugins/cache/`.

### Link Reusable Skills For Local Development

Run this from the repository root to link `skills/` into `~/.agents/skills`:

```sh
./skills-link.sh
```

This helper only links reusable skills. It does not install, mirror, or rewrite plugin marketplace entries.

### Install Reusable Skills With `skill-installer` (Codex-only)

Inside Codex, install all reusable skills with:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/codex-cli skills/code-wiki skills/crusty skills/okf skills/skill-cli-creator skills/tanstack skills/codex-changelog skills/xcode-changelog skills/focus skills/study skills/postgres skills/skill-audit skills/swift-api-design skills/swift-docc
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
  --skill codex-cli \
  --skill code-wiki \
  --skill crusty \
  --skill okf \
  --skill skill-cli-creator \
  --skill tanstack \
  --skill codex-changelog \
  --skill xcode-changelog \
  --skill focus \
  --skill study \
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
