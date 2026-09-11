# dotagents

Reusable agent skills and project maintainer skills.

This repository is organized around reusable installable skills:

- **Reusable skills** under `skills/`, which can be linked locally or installed into Codex.

Project-only maintainer workflows live under `.agents/skills/`. The retained
`.agents/plugins/marketplace.json` registry is empty; the current catalog ships
as skills.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `skills/` | Reusable skills, each with a `SKILL.md` entrypoint and `agents/openai.yaml` metadata. |
| `.agents/skills/` | Project-local maintainer skills for working on this repository. |
| `.agents/plugins/marketplace.json` | Local plugin discovery surface for this checkout. |
| `skills-link.sh` | Local development helper that links reusable skills into `~/.agents/skills`. |

## Reusable Skills

| Skill | Purpose |
| --- | --- |
| `learn` | Maintain durable project knowledge, decisions, localization guidance, and code review rules. |
| `grilling-session` | Refine a topic or handoff through repository-grounded questions with concrete recommended answers. |
| `explore` | Explore evidence, refine the question, and investigate read-only in the current task or session with optional research subagents. |
| `adversarial-review` | Pressure-test a software change with an independent read-only review and evidence-backed findings. |
| `review-pr` | Request or resume a hosted Codex PR review, wait, and report the provider result to the calling task. |
| `spec` | Refine a feature spec and actionable task plan in conversation; publish to GitHub when requested. |
| `implement` | Implement selected local work from a spec, ticket, issue, or direct request, validate it, and commit only when authorized, without orchestration or publication. |
| `deslop` | Explicit-only audit and minimal safe cleanup of low-value code across every major directory. |
| `git-commit` | Create or push explicit regular, fixup, or amend-fixup commits without publishing a PR. |
| `yeet` | Confirm scope and caller-provided resolved issues, commit, push, add automatic issue-closing references, and open or update one pull request. Stack linking and review requests are separate. |
| `github-actions` | Diagnose or explicitly fix failing GitHub Actions checks. |
| `github-status` | Summarize issue and pull-request queues read-only, or inspect one PR's exact-head delivery readiness, merge policy, checks, and automation state. |
| `github-issues` | Manage GitHub issues, attachments, relationships, label/type classification, and taxonomy proposals. |
| `github-projects` | Manage GitHub Projects, fields, items, repository or team links, templates, and lifecycle. |
| `github-releases` | Inspect, plan, publish, and validate releases, tags, notes, assets, and packages. |
| `versioning` | Distinguish versions, tags, and GitHub Releases; suggest SemVer and operate approval-gated release-tag workflows. |
| `github-review-threads` | Inspect review threads, address selected feedback, and explicitly reply or resolve. |
| `github-stacked-pr` | Manage stacked branches and dependent pull requests, including inspection, linking, rebase, sync, navigation, and explicit stack-wide publication or merge. |
| `github-stars` | Manage the authenticated user's GitHub stars and star lists. |
| `crusty` | Skeptical, evidence-backed critique of work decisions and implementations. Use only when explicitly asked for Crusty. |
| `ms-roberts` | Use when medium or long user-authored English prompts contain grammar errors; append corrections and learning tips after the main answer. |
| `socrates` | Offer opt-in exercises about meaningful recent engineering work, or quiz the user when explicitly requested. |
| `okf` | Write, scaffold, inspect, and validate Open Knowledge Format Markdown bundles with the shipped CLI. |
| `skill-cli-creator` | Create or refactor CLIs shipped inside a skill or plugin bundle. |
| `tanstack` | Build, debug, review, or migrate applications using TanStack packages. |
| `postgres` | Inspect Postgres databases, design or run SQL, and manage migrations through the shipped Postgres CLI. |
| `swift-api-design` | Design, rename, or review Swift API surfaces using the bundled official API Design Guidelines. |
| `swift-docc` | Author, review, preview, or publish Swift-DocC symbol documentation, articles, and tutorials. |
| `youtube` | Search YouTube videos and playlists or answer from timestamped transcripts. Use for YouTube links and spoken-content research. |
| `ghostty` | Inspect or arrange Ghostty terminals and edit configuration or keybindings when explicitly requested. |
| `herdr` | Inspect or control Herdr terminal workspaces, panes, and agents when the user explicitly asks to use Herdr. |
| `hopper` | Configure and verify Hopper Disassembler MCP for Codex or Cursor globally or per project. |
| `discourse` | Configure and verify Discourse MCP for Codex or Cursor globally or per project. |
| `xcode-mcp` | Explicitly configure, launch, or diagnose Apple's native headless Xcode MCP server. |
| `xcode-skills` | Explicitly install or update Xcode's embedded skills in a target repository. |
| `xcode-whats-new` | Explicitly read official release notes for the active, latest, or requested stable or beta Xcode. |

### TanStack References

The reusable `tanstack` skill covers TanStack AI, Charts, CLI, Config, DB, Devtools, Form, Highlight, Hotkeys, Markdown, Pacer, Query, Ranger, Router, Start, Store, Table, Virtual, and cross-stack integration from one `$tanstack` invocation surface.

- Product references live under `skills/tanstack/references/`: `ai.md`, `charts.md`, `cli.md`, `config.md`, `db.md`, `devtools.md`, `form.md`, `highlight.md`, `hotkeys.md`, `integration.md`, `markdown.md`, `pacer.md`, `query.md`, `ranger.md`, `router.md`, `start.md`, `store.md`, `table.md`, `virtual.md`.
- Router references include `router-routing-structure.md`, `router-navigation-and-search.md`, `router-data-loading-and-ssr.md`, `router-auth-and-failures.md`, and `router-plugin-and-splitting.md`.
- Start references include `start-framework-and-execution.md`, `start-server-functions-and-routes.md`, `start-middlewares-and-server-core.md`, `start-server-components-and-migrations.md`, and `start-deployments.md`.
- CLI references include `cli-scaffolding.md`, `cli-addons-existing-app.md`, `cli-ecosystem-integrations.md`, `cli-custom-addons-dev-watch.md`, and `cli-docs-and-library-metadata.md`.

This repository ships one broad reusable `tanstack` skill rather than separate upstream-style product plugins, narrow focused skills, or bundle aliases such as `tanstack-all`. For TanStack application work, install the reusable TanStack skill instead of copying advice from mixed community sources.

## Skill Dependencies

- `explore` explores relevant evidence in the current task or session before
  Grilling Session, then investigates remaining questions using the existing
  conversation. The entire investigation is strictly read-only.
  It never creates visible tasks or prepares a controller transfer handoff.
  Independent evidence work may use subagents with focused research briefs,
  subject to user constraints and host capacity. Workers cannot invoke Explore
  or delegate further. Research helpers prescribe no model or reasoning level.
- Install `explore` with its `grilling-session` and `learn` dependencies.
  Explore invokes Learn for a read-only Project Context pass before exploration,
  then invokes Grilling Session with the gathered evidence. The current task or session asks the user one
  question with a recommended answer per turn and
  cannot plan workers until the scope is confirmed or the user stops
  grilling.
- Install `spec` with its `grilling-session` and `github-issues` dependencies.
  Install `review-pr` with its `github-review-threads` dependency. These
  dependencies must be reachable in the current session; the invoking skills
  never install or substitute them automatically.
- `review-pr` obtains one hosted Codex review result for a PR. Use
  `$github-review-threads` for inspect, reply, resolve, and other provider
  review operations. Use `$adversarial-review` for local independent change
  review; use `$crusty` only when explicitly asked for Crusty.
- `maintainer` uses its local health and validation workflows for diagnosis; it requires `$skill-creator` or `$plugin-creator` for substantial public reshapes and native `codex review` for non-trivial implementation closeout.
- Spec uses installed `$grilling-session` for material clarification and
  `$github-issues` for hosted reads and publication when saving to GitHub.
- `learn` runs in the invoking task and performs only authorized local-repository context changes; it has no external dependency preflight, task profile, GitHub transport, publication, or worker delegation contract.
- `grilling-session` is read-only and explicit or parent-composed. It uses supplied
  context and relevant evidence without requiring Learn or a repository, returns
  a transient refined handoff, and
  never creates tasks or captures durable knowledge automatically.
- `spec` targets one repository per invocation, with no cross-repository issue
  references or companion specs. It saves coherent specs with stable task identities, recommended
  order, real prerequisites, and completion checks. GitHub is the only saved destination;
  no-write previews stay in the conversation and require no GitHub skill access when using
  only supplied or local sources. GitHub is the sole saved-spec authority.

- Engineering skills retain the same delegation policy standalone and composed. Implement
  implements and validates, then commits only with user or composed-assignment
  authority; independent review is a separate caller-owned gate, with no
  reviewer delegation inside Implement.
- `review-pr` reuses a completed current-target review, resumes a pending
  request, or requests and waits when needed. It returns the provider result to
  the calling task, standalone or composed, with no subagents, repairs, CI or
  acceptance decisions. Explicit inspect-only scope remains read-only.


## Project-Local Skills

| Skill | Path | Purpose |
| --- | --- | --- |
| maintainer | `.agents/skills/maintainer/` | Manually audit, maintain, and re-engineer repo skills and plugins through health, lifecycle, validation, metadata, and explicit refresh workflows. |

Project-local skills are repository-specific and are not included in reusable install commands.

## Installation

### Link Reusable Skills For Local Development

Run this from the repository root to link `skills/` into `~/.agents/skills`:

```sh
./skills-link.sh
```

This helper only links reusable skills. It does not install, mirror, or rewrite plugin marketplace entries.

### Install Reusable Skills With `skill-installer` (Codex-only)

Inside Codex, install all reusable skills with:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/git-commit skills/yeet skills/github-actions skills/github-status skills/github-issues skills/github-projects skills/github-releases skills/versioning skills/github-review-threads skills/github-stacked-pr skills/github-stars skills/crusty skills/ms-roberts skills/socrates skills/okf skills/skill-cli-creator skills/tanstack skills/postgres skills/swift-api-design skills/swift-docc skills/youtube skills/hopper skills/discourse skills/xcode-mcp skills/xcode-skills skills/xcode-whats-new skills/ghostty skills/herdr skills/learn skills/grilling-session skills/explore skills/adversarial-review skills/review-pr skills/spec skills/implement skills/deslop
```

Install one reusable skill by passing only its path:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/crusty
```

Replace `skills/crusty` with any path listed in the reusable skills table.

### Install Reusable Skills With `npx skills`

These commands use the [`vercel-labs/skills`](https://github.com/vercel-labs/skills) CLI and target Codex directly.

List the skills available in this repository:

```sh
npx skills add alemar11/dotagents --list
```

Install all reusable skills globally for Codex:

```sh
npx skills add alemar11/dotagents -a codex -g -y \
  --skill git-commit \
  --skill yeet \
  --skill github-actions \
  --skill github-status \
  --skill github-issues \
  --skill github-projects \
  --skill github-releases \
  --skill versioning \
  --skill github-review-threads \
  --skill github-stacked-pr \
  --skill github-stars \
  --skill crusty \
  --skill ms-roberts \
  --skill socrates \
  --skill okf \
  --skill skill-cli-creator \
  --skill tanstack \
  --skill postgres \
  --skill swift-api-design \
  --skill swift-docc \
  --skill youtube \
  --skill hopper \
  --skill discourse \
  --skill xcode-mcp \
  --skill xcode-skills \
  --skill xcode-whats-new \
  --skill ghostty \
  --skill herdr \
  --skill learn \
  --skill grilling-session \
  --skill explore \
  --skill adversarial-review \
  --skill review-pr \
  --skill spec \
  --skill implement \
  --skill deslop
```

Install one reusable skill globally for Codex:

```sh
npx skills add alemar11/dotagents -a codex -g -y --skill crusty
```

Replace `crusty` with any skill name from the reusable skills table. Omit `-g` to install into the current project's `.agents/skills/` instead of your global `~/.codex/skills/`.

Restart Codex after installing or updating skills.
