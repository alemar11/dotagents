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
| `g:github-tagger` | Classify one issue against existing metadata or explicitly analyze a repository and its issues to propose minimal new labels and organization issue types without mutation. |
| `g:github-issues` | Manage GitHub issue lifecycle, metadata, relationships, and dry-runs. |
| `g:github-investigation` | Investigate issues, pull requests, and proposed fixes using repository evidence. |
| `g:github-actions` | Diagnose or explicitly fix failing GitHub Actions checks. |
| `g:github-delivery-status` | Inspect exact-head pull-request delivery readiness, merge policy, rulesets, checks, queue, and automation state without mutating GitHub. |
| `g:github-review-threads` | Inspect review threads, address selected feedback, and explicitly reply or resolve. |
| `g:github-releases` | Inspect, plan, publish, and validate releases, tags, notes, assets, and packages. |
| `g:github-stars` | Manage the authenticated user's GitHub stars and star lists. |
| `g:send` | Confirm scope and caller-provided resolved issues, commit, push, add automatic issue-closing references, and open or update one pull request. Stack linking and review requests are separate. |
| `g:github-stack` | Manage stacked branches and dependent pull requests through the G stack CLI, including inspection, linking, rebase, sync, navigation, and explicit stack-wide publication or merge. |
| `g:audit` | Monitor active sessions using G skills and return a prioritized read-only report. |

SE is the repository's software-delivery workflow plugin. It turns ideas into
Feature plans, delivers them through reviewed pull requests, maintains project
knowledge, and audits active work:

| Skill | Purpose |
| --- | --- |
| `se:learn` | Maintain durable project knowledge, decisions, localization guidance, and code review rules. |
| `se:idea` | Save a concrete proposal for later Feature planning, or preview it locally. |
| `se:feature` | Turn related requests into clear Features and Macro Tasks, then delegate minimal optional issue labels and type without writing code. |
| `se:implement` | Deliver planned Features through reviewed pull requests and verify their final delivery state. |
| `se:audit` | Observe active SE work and report workflow problems or improvement opportunities without making changes. |

## Reusable Skills

| Skill | Purpose |
| --- | --- |
| `codex-cli` | Launch one complete prompt in a separate Codex CLI task with Sol/Terra/Luna selection and model-aware reasoning. |
| `code-wiki` | Generate an evidence-backed linked HTML wiki for a local repository or git URL. |
| `crusty` | Self-contained skeptical critique for decisions, implementations, architecture, naming, and tradeoffs. |
| `ms-roberts` | Track substantive grammar issues in medium or complex English prompts and return a Markdown report with American English corrections, explanations, and tips. |
| `okf` | Write, scaffold, inspect, and validate Open Knowledge Format markdown bundles with the shipped OKF CLI. |
| `skill-cli-creator` | Build host-aware embedded CLIs that live inside a skill or plugin under `scripts/`. |
| `tanstack` | Review or build TanStack apps across Query, Router, Start, Form, Table, Charts, Virtual, Store, DB, AI, CLI, and integrations. |
| `codex-changelog` | Print installed Codex CLI and Codex App changelogs from GitHub Releases and the OpenAI Codex changelog page. |
| `xcode-changelog` | Resolve active Xcode notes, include latest notes when behind, look up a version, or list Apple Xcode release notes. |
| `focus` | Create a focused new Codex task from a compact handoff of the latest substantive discussion. |
| `study` | Orchestrate read-only planning, research, or analysis through one Sol task and up to five Luna workers; never write code or edit project files. |
| `postgres` | Connect to Postgres, run SQL/diagnostics, inspect schemas/migrations, and apply version-aware SQL, PostGIS, or pgvector patterns. |
| `skill-audit` | Audit installed Codex skills and plugins from historical evidence or live App task monitoring with defect annotations. |
| `swift-api-design` | Design or review Swift APIs using local summaries and the bundled official Swift API Design Guidelines. |
| `swift-docc` | Write, structure, review, and publish Swift-DocC docs using local summaries and bundled DocC sources. |

### TanStack References

The reusable `tanstack` skill covers TanStack AI, Charts, CLI, Config, DB, Devtools, Form, Pacer, Query, Ranger, Router, Start, Store, Table, Virtual, and cross-stack integration from one `$tanstack` invocation surface.

- Product references live under `skills/tanstack/references/`: `ai.md`, `charts.md`, `cli.md`, `config.md`, `db.md`, `devtools.md`, `form.md`, `integration.md`, `pacer.md`, `query.md`, `ranger.md`, `router.md`, `start.md`, `store.md`, `table.md`, `virtual.md`.
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
- The G-dependent SE skills run a read-only Codex plugin preflight before their first required G handoff and fail closed when G is unavailable; Feature publication requires both `$g:github-issues` and `$g:github-tagger`, while no SE skill installs G automatically.
- `se:idea` traverses a graph-first in-memory capture workflow and publishes to GitHub by default; an explicitly requested preview stays entirely local. Its durable output is the hosted issue, not project memory, and its optional idea-source handoff remains transient.
- `se:learn` runs in the invoking task and performs only authorized local-repository context changes; it has no external dependency preflight, task profile, GitHub transport, publication, or worker delegation contract.
- `se:implement` accepts only complete authoritative GitHub Feature Plan Sets with verified sibling Feature and same-parent Macro Task projections and stable Feature acceptance IDs, then returns a verified standalone or stacked PR topology per Feature. GitHub interaction is mandatory end to end; it has no local-only or preview execution mode. A Sol/medium orchestrator verifies the set registry, Feature-level dependencies, and parent/child Macro Task registries; interprets each textual Feature and macro context; derives technical execution units separately from delivery topology; and creates isolated Feature Workers. Each Worker may use bounded delegated support for code analysis, execution-unit assistance, validation, or critique when delegation and capacity are observed; unavailable or unknown delegation falls back to serial parent execution and never blocks the required Worker. Same-repository Feature dependencies are mandatory stack intent, while cross-repository dependencies remain scheduling-only and standalone. A stacked child may start from its parent's verified `candidate-published` exact HEAD before that parent is delivery-ready. After publication, the Feature Worker becomes inactive but resumable and releases its path claim; the orchestrator centrally monitors hosted review, CI, delivery status, and stack drift, and resumes that same Worker only for an actionable fix, evidence repair, or rebase after reacquiring the path envelope. Workers own implementation semantics, validation, and local Feature/Macro Task evidence bound to the exact candidate HEAD; the orchestrator aggregates plan evidence without rewriting the plan. Each PR closes only its parent Feature plus every associated local Macro Task, regardless of internal technical realization. Product-level contradictions are surfaced to the user rather than causing an automatic Feature-planning relaunch. Final provider readiness is supplied by `g:github-delivery-status`, whose `ready` and `ready-with-manual-action` dispositions do not grant Implement merge, auto-merge, bypass, or queue authority. Idea, Feature, and Implement apply one shared portable-content gate immediately before each hosted write; G owns transport and readback rather than semantic cleanup. Parent drift invalidates descendant evidence for bottom-to-top worker reconciliation. Every SE skill exposes a compact state glossary, and Implement distinguishes the persisted pair `delivery-pending @ candidate-published` from workflow nodes and external provider dispositions. Its SQLite WAL ledger prevents concurrent orchestrators on the same Feature Plan Set, stores durable checkpoints and idempotent side effects only, and enforces the documented state registry; schema changes still use explicit drop-and-recreate rather than migrations.
- `se:audit` runs only after explicit invocation and observes a frozen cohort of active SE sessions until terminal state or user stop. It keeps all evidence transient, treats missing visibility as indeterminate rather than a violation, and never contacts tasks or mutates repositories and GitHub.
- Multi-repository runs additionally validate the complete linked Feature Plan Set and finish with one independently verified GitHub PR per implementation-eligible Feature plus one exact HEAD vector.

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
versioned plugins from the repository source. G has a dedicated helper; SE is
reinstalled directly:

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
Use $skill-installer to install skills from alemar11/dotagents --path skills/codex-cli skills/code-wiki skills/crusty skills/ms-roberts skills/okf skills/skill-cli-creator skills/tanstack skills/codex-changelog skills/xcode-changelog skills/focus skills/study skills/postgres skills/skill-audit skills/swift-api-design skills/swift-docc
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
  --skill ms-roberts \
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
