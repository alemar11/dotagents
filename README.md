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

GitStack is the repo-local Git and GitHub workflow plugin. It uses the official GitHub connector for supported remote operations, authenticated `gh` for connector gaps, and direct `git` for local repository work. It bundles:

| Skill | Purpose |
| --- | --- |
| `gitstack:github` | Handle general or mixed GitHub requests through the appropriate focused workflows. |
| `gitstack:git-commit` | Create or push explicit regular, fixup, or amend-fixup commits without publishing a PR. |
| `gitstack:github-repository-triage` | Triage issue and pull request queues across one or more repositories read-only. |
| `gitstack:github-issues` | Manage GitHub issue lifecycle, metadata, relationships, and dry-runs. |
| `gitstack:github-investigation` | Investigate issues, pull requests, and proposed fixes using repository evidence. |
| `gitstack:github-actions` | Diagnose or explicitly fix failing GitHub Actions checks. |
| `gitstack:github-review-threads` | Inspect review threads, address selected feedback, and explicitly reply or resolve. |
| `gitstack:github-releases` | Inspect, plan, publish, and validate releases, tags, notes, assets, and packages. |
| `gitstack:github-stars` | Manage the authenticated user's GitHub stars and star lists. |
| `gitstack:yeet` | Confirm scope, commit, push, and open or update a draft pull request. |

## Reusable Skills

| Skill | Purpose |
| --- | --- |
| `autoreview` | Run bounded structured closeout review, adding one native Codex review only for high-risk changes on the same HEAD. |
| `code-wiki` | Generate an evidence-backed linked HTML wiki for a local repository or git URL. |
| `code-review-rules` | Discover, evaluate, and install evidence-backed Codex Code Review rules in the closest applicable `AGENTS.md`. |
| `crusty` | Direct-only independent advisory critique for decisions, implementations, architecture, naming, and tradeoffs. |
| `okf` | Write, scaffold, inspect, and validate Open Knowledge Format markdown bundles with the shipped OKF CLI. |
| `grill-me-with-context` | Stress-test repo-backed plans and capture or hand off durable decisions. |
| `improve-codebase-architecture` | Find evidence-backed architecture candidates, then pressure-test the selected refactor before implementation. |
| `skill-cli-creator` | Build host-aware embedded CLIs that live inside a skill or plugin under `scripts/`. |
| `tanstack` | Review or build TanStack apps across Query, Router, Start, Form, Table, Virtual, Store, DB, AI, CLI, and integrations. |
| `codex-changelog` | Print installed Codex CLI and Codex App changelogs from GitHub Releases and the OpenAI Codex changelog page. |
| `xcode-changelog` | Resolve active Xcode notes, include latest notes when behind, look up a version, or list Apple Xcode release notes. |
| `plan-harder` | Create higher-rigor implementation plans or harden single issues before coding. |
| `capture-idea` | Manually save one or more discussed proposals as durable Ideas for later feature planning. |
| `plan-feature` | Manually converge feature intent or an existing Spec into a complete applied or proposed planning bundle. |
| `implement-feature` | Coordinate visible Codex workers in the ChatGPT App through reviewed GitHub PR or named local-branch delivery. |
| `grill-me` | Stress-test plans, decisions, drafts, workflows, and coding approaches on explicit request. |
| `learn` | Capture confirmed durable corrections or preferences and write them only to `AGENTS.md`. |
| `project-memory` | Maintain tracker routing, domain language, ADRs, context, and localization memory. |
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

- `code-wiki` requires `$imagegen` when generating raster overview or conceptual images for a wiki.
- `code-review-rules` requires `$learn` for every approved durable `AGENTS.md` creation or update; it owns discovery and evaluation but never writes the file directly.
- `maintainer` uses `$skill-audit` conditionally when health diagnosis or workflow hardening needs portfolio, prompt-quality, overlap, or session evidence; requires `$skill-creator` or `$plugin-creator` for substantial package reshapes; and requires `$autoreview` for non-trivial implementation closeout.
- `grill-me-with-context` requires `$grill-me` and `$project-memory` so it can run the questioning loop, update project context docs or ADRs through the `domain-memory` slice for direct use, or return a deferred domain-knowledge handoff to a parent workflow.
- `improve-codebase-architecture` requires `$grill-me-with-context` to pressure-test the selected architecture candidate before implementation.
- `capture-idea` requires `$project-memory` for tracker routing and the canonical Idea marker mapping. It uses `$gitstack:github-issues` for exact GitHub preflight reads and applied Idea mutations.
- `plan-feature` requires `$project-memory`, `$grill-me-with-context`, and `$plan-harder` for setup, repo-backed clarification, Feature Spec writing, issue hardening, and deferred knowledge closeout. It uses `$gitstack:github-issues` for exact paginated GitHub Idea and planning-bundle convergence reads in both write modes, plus applied tracker mutations.
- `implement-feature` requires local `python3` for its shipped `scripts/run-state` SQLite coordinator, read-only `scripts/verify-ready` terminal verifier, and `$autoreview` for every delivery; GitStack is required only for GitHub transport. AutoReview owns the review profile and adds one native Codex review only for high-risk changes. The controller task may be bound to a multi-folder local Codex project, but that project's primary-folder Git defaults and attached folders are control-plane and read-only coordination context only. Before state, Implement Feature maps every affected repository bijectively to its own separate repo-specific saved Git project whose reported primary folder and Git common directory match the repository; the multi-folder controller project never satisfies that worker mapping. Remote, broad, duplicate, ambiguous, or missing mappings stop unless the one startup interaction explicitly authorizes creation of the exact missing projects. That interaction also covers visible Codex tasks and their assigned worktrees. Workers own implementation, validation, commits, review candidates, finding acceptance and fixes, tracker proof, and either GitHub PR or named local-branch closeout; canonical `review_owner=worker|root` is persisted through reconciled ChatGPT App task operations and owns AutoReview execution only. The root coordinates every worker allowed by path and dependency serialization without a fixed numeric cap and uses one permanently unversioned per-user database-schema-3 DB at `~/.cache/dotagents/skills/implement-feature/run-state.sqlite3`; CLI, runtime-contract, and named JSON protocol SemVer identities remain separate from that SQLite schema integer. Runs pin their exact runtime artifact, generated operation IDs reconcile Codex task changes, and one stable bootstrap ID gives replayable exactly-once authority effect. The single-row `runtime_metadata` table and SQLite transactions fence no-migration hard cuts without an external lock file, while canonical Feature Spec and head-branch claims prevent duplicate work and different roots may use distinct worktrees in the same repository. It never plans, repairs planning artifacts, switches the main worktree, or merges pull requests.
  Multi-repository runs validate the complete linked Feature Spec Set before
  state, persist only shared `feature_id` membership, and finish with one
  independently verified branch or PR per repository plus one exact HEAD
  vector.

## Project-Local Skills

| Skill | Path | Purpose |
| --- | --- | --- |
| maintainer | `.agents/skills/maintainer/` | Manually audit, maintain, and re-engineer repo skills and plugins through health, lifecycle, validation, metadata, and explicit refresh workflows. |

Project-local skills are repository-specific and are not included in reusable install commands.

## Installation

### Use Repo-Local Plugins

Repo-local plugins are exposed through `.agents/plugins/marketplace.json`; they are not installed by `skills-link.sh`.

Register the `alemar11` marketplace from GitHub, then install GitStack:

```sh
codex plugin marketplace add alemar11/dotagents --ref main
codex plugin add gitstack@alemar11
```

If the `alemar11` marketplace is already registered, install GitStack directly:

```sh
codex plugin add gitstack@alemar11
```

For local development from a dotagents checkout, register the checkout instead
of the GitHub source, then install the same plugin:

```sh
codex plugin marketplace add /path/to/dotagents
codex plugin add gitstack@alemar11
```

During local development, rebuild, test, and reinstall after each versioned
change with the explicit maintenance helper:

```sh
plugins/gitstack/projects/gitstack/scripts/reinstall-local
```

For a Git-backed marketplace checkout, refresh the marketplace before reinstalling:

```sh
codex plugin marketplace upgrade alemar11
codex plugin remove gitstack@alemar11
codex plugin add gitstack@alemar11
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
Use $skill-installer to install skills from alemar11/dotagents --path skills/autoreview skills/code-wiki skills/code-review-rules skills/crusty skills/okf skills/grill-me-with-context skills/improve-codebase-architecture skills/skill-cli-creator skills/tanstack skills/codex-changelog skills/xcode-changelog skills/plan-harder skills/capture-idea skills/plan-feature skills/implement-feature skills/grill-me skills/learn skills/project-memory skills/postgres skills/skill-audit skills/swift-api-design skills/swift-docc
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
  --skill code-review-rules \
  --skill crusty \
  --skill okf \
  --skill grill-me-with-context \
  --skill improve-codebase-architecture \
  --skill skill-cli-creator \
  --skill tanstack \
  --skill codex-changelog \
  --skill xcode-changelog \
  --skill plan-harder \
  --skill capture-idea \
  --skill plan-feature \
  --skill implement-feature \
  --skill grill-me \
  --skill learn \
  --skill project-memory \
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
