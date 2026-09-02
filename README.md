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

SE is the repository's software-delivery workflow plugin. It turns ideas into
Feature plans, delivers them through reviewed pull requests, maintains project
knowledge, and audits active work:

| Skill | Purpose |
| --- | --- |
| `se:learn` | Maintain durable project knowledge, decisions, localization guidance, and code review rules. |
| `se:idea` | Save a concrete proposal for later Feature planning, or preview it locally. |
| `se:feature` | Turn related requests into clear Features and Macro Tasks, then delegate minimal optional issue labels and type without writing code. |
| `se:implement` | Deliver planned Features with lightweight graph orchestration, reusable workers, and standalone or stacked pull requests. |
| `se:audit` | Observe active SE work and report workflow problems or improvement opportunities without making changes. |

Xcode is the repository's Apple developer-tools plugin. It preserves the
official stable and beta release-note resolver and adds safe launch guidance
for Apple's native headless MCP server:

| Skill | Purpose |
| --- | --- |
| `xcode:whats-new` | Resolve release notes for the active Xcode plus the latest stable and beta versions, or for one requested version. |
| `xcode:mcp` | Safely launch and verify the Xcode-provided headless MCP server on attended Macs, unattended hosts, or explicitly isolated CI machines. |

## Reusable Skills

| Skill | Purpose |
| --- | --- |
| `codex-cli` | Launch one complete prompt in a separate Codex CLI task with Sol/Terra/Luna selection and model-aware reasoning. |
| `code-wiki` | Generate an evidence-backed linked HTML wiki for a local repository or git URL. |
| `crusty` | Self-contained skeptical critique for decisions, implementations, architecture, naming, and tradeoffs. |
| `eli5` | Turn a topic, code path, design tradeoff, or incident into a picture-first HTML explainer with large visuals and very few words. |
| `g` | Route requested Git and GitHub work through one reusable skill using direct `git`, authenticated `gh`, its shipped CLI, and the complete `projects/g` source tree. |
| `ms-roberts` | Silently track substantive grammar issues in medium or complex English prompts and return an American-English correction report on request or session close. |
| `okf` | Write, scaffold, inspect, and validate Open Knowledge Format markdown bundles with the shipped OKF CLI. |
| `skill-cli-creator` | Build host-aware embedded CLIs that live inside a skill or plugin under `scripts/`. |
| `tanstack` | Review or build apps with TanStack libraries across data, routing, UI, content, tooling, and integrations. |
| `focus` | Create a focused new Codex task from a compact handoff of the latest substantive discussion. |
| `study` | Orchestrate read-only planning, research, or analysis through one Sol task and up to five Luna workers; never write code or edit project files. |
| `postgres` | Connect to Postgres, run SQL/diagnostics, inspect schemas/migrations, and apply version-aware SQL, PostGIS, pgvector, pg_cron, or pg_durable patterns. |
| `plugins-reload` | Explicitly refresh the repo-local SE and Xcode plugin caches after source changes. |
| `skill-audit` | Audit installed Codex skills and plugins from historical evidence or live App task monitoring with defect annotations. |
| `swift-api-design` | Design or review Swift APIs using local summaries and the bundled official Swift API Design Guidelines. |
| `swift-docc` | Write, structure, review, and publish Swift-DocC docs using local summaries and bundled DocC sources. |
| `youtube` | Search YouTube videos and playlists, retrieve timestamped transcripts, and search spoken content across playlists. |

### TanStack References

The reusable `tanstack` skill covers TanStack AI, Charts, CLI, Config, DB, Devtools, Form, Highlight, Hotkeys, Markdown, Pacer, Query, Ranger, Router, Start, Store, Table, Virtual, and cross-stack integration from one `$tanstack` invocation surface.

- Product references live under `skills/tanstack/references/`: `ai.md`, `charts.md`, `cli.md`, `config.md`, `db.md`, `devtools.md`, `form.md`, `highlight.md`, `hotkeys.md`, `integration.md`, `markdown.md`, `pacer.md`, `query.md`, `ranger.md`, `router.md`, `start.md`, `store.md`, `table.md`, `virtual.md`.
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
- The G-dependent SE skills run a read-only skill preflight before their first required `$g` handoff and fail closed when G is unavailable. Feature publication requires G's GitHub Issues workflow and may use its GitHub Tagger workflow; no SE skill installs G automatically.
- `se:idea` traverses a graph-first in-memory capture workflow and publishes to GitHub by default; an explicitly requested preview stays entirely local. Its durable output is the hosted issue, not project memory, and its optional idea-source handoff remains transient.
- `se:learn` runs in the invoking task and performs only authorized local-repository context changes; it has no external dependency preflight, task profile, GitHub transport, publication, or worker delegation contract.
- `se:implement` accepts only caller-supplied published parent Feature issues
  and treats each parent as the semantic contract. It places one
  visible graph orchestrator in the single involved project or a selected
  coordination project. The orchestrator follows a small transient execution
  graph, reuses repository-bound worker worktrees for serial Features, and adds
  lanes only when it chooses concurrent work. Same-repository dependencies use
  stacked branches and pull requests;
  cross-repository dependencies affect scheduling only. Its host-local SQLite
  registry atomically protects an immutable repository set and stores only
  repository ownership, while Features, workers, Git, pull requests, review,
  and CI remain externally owned. Each stable exact-head pull request must be
  ready rather than draft and have terminal clean hosted review plus required
  validation and CI. Implement never merges, deploys, or releases.
- `se:audit` runs only after explicit invocation and observes a frozen cohort of
  active SE sessions until terminal state or user stop. Complete coverage
  requires exhausting every authoritative continuation and host/project
  partition; capped or untraversable inventories are reported as partial. It
  keeps all evidence transient, treats missing visibility as indeterminate
  rather than a violation, and never contacts tasks or mutates repositories and
  GitHub.
- Multi-repository runs additionally validate the complete linked Feature Plan Set and finish with one independently verified GitHub PR per implementation-eligible Feature plus one exact HEAD vector.

## Project-Local Skills

| Skill | Path | Purpose |
| --- | --- | --- |
| maintainer | `.agents/skills/maintainer/` | Manually audit, maintain, and re-engineer repo skills and plugins through health, lifecycle, validation, metadata, and explicit refresh workflows. |

Project-local skills are repository-specific and are not included in reusable install commands.

## Installation

### Use Repo-Local Plugins

Repo-local plugins are exposed through `.agents/plugins/marketplace.json`; they are not installed by `skills-link.sh`.
SE's hosted workflows require the reusable `g` skill. Install or link
`skills/g` using the reusable-skill instructions below before using those
workflows; SE does not install it automatically.

Register the `alemar11` marketplace from GitHub, then install the required plugins:

```sh
codex plugin marketplace add alemar11/dotagents --ref main
codex plugin add se@alemar11
codex plugin add xcode@alemar11
```

If the `alemar11` marketplace is already registered, install the plugins directly:

```sh
codex plugin add se@alemar11
codex plugin add xcode@alemar11
```

For local development from a dotagents checkout, register the checkout instead
of the GitHub source, then install the same plugin:

```sh
codex plugin marketplace add /path/to/dotagents
codex plugin add se@alemar11
codex plugin add xcode@alemar11
```

During local development, validate each changed plugin and reinstall it from
the repository source:

```sh
codex plugin add se@alemar11 --json
codex plugin add xcode@alemar11 --json
```

For a Git-backed marketplace checkout, refresh the marketplace before reinstalling:

```sh
codex plugin marketplace upgrade alemar11
codex plugin remove se@alemar11
codex plugin add se@alemar11
codex plugin remove xcode@alemar11
codex plugin add xcode@alemar11
```

When migrating from the retired Feature Flow plugin identity, remove the old
installation before installing SE:

```sh
codex plugin remove feature-flow@alemar11
codex plugin add se@alemar11
```

Restart Codex or open a fresh task after installation so the bundled skills and
connectors are discovered. Do not edit installed cache copies under
`~/.codex/plugins/cache/`.

### Link Reusable Skills For Local Development

Run this from the repository root to link `skills/` into `~/.agents/skills`:

```sh
./skills-link.sh
```

This helper only links reusable skills. It does not install, mirror, or rewrite plugin marketplace entries.

### Install Reusable Skills With `skill-installer` (Codex-only)

Inside Codex, install all reusable skills with:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/codex-cli skills/code-wiki skills/crusty skills/eli5 skills/g skills/ms-roberts skills/okf skills/skill-cli-creator skills/tanstack skills/focus skills/study skills/postgres skills/plugins-reload skills/skill-audit skills/swift-api-design skills/swift-docc skills/youtube
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
  --skill eli5 \
  --skill g \
  --skill ms-roberts \
  --skill okf \
  --skill skill-cli-creator \
  --skill tanstack \
  --skill focus \
  --skill study \
  --skill postgres \
  --skill plugins-reload \
  --skill skill-audit \
  --skill swift-api-design \
  --skill swift-docc \
  --skill youtube
```

Install one reusable skill globally for Codex:

```sh
npx skills add alemar11/dotagents -a codex -g -y --skill code-wiki
```

Replace `code-wiki` with any skill name from the reusable skills table. Omit `-g` to install into the current project's `.agents/skills/` instead of your global `~/.codex/skills/`.

Restart Codex after installing or updating skills.
