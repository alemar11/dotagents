# Repository Guidelines

## Overview
This repository hosts reusable Codex skills, project maintainer skills, optional repo-local plugins, and MCP install helpers. Reusable skills live under `skills/`, optional repo-local plugins live under `plugins/`, project maintainer skills live under `.agents/skills/`, and global MCP install helpers live under `mcps/`. Every reusable or bundled skill is documented by a `SKILL.md` entrypoint, and every plugin must ship `.codex-plugin/plugin.json`. Keep guidance lightweight and focused on building and evolving skills and plugins.
Agent skills follow the specification at `https://agentskills.io/specification`.
Codex skills reference: `https://developers.openai.com/codex/skills/`.

## How to Create a Skill
- Prefer `$skill-creator` as the canonical scaffold and workflow reference for new skills or substantial skill reshapes; follow its initialization, metadata, validation, and forward-testing guidance before repo-specific cleanup.
- When a new or reshaped skill needs an embedded CLI under `scripts/` or a maintenance project under `projects/<tool>/`, route that CLI design and layout work through `$skill-cli-creator`.
- Create a dedicated directory per skill with a clear, stable name.
- Place reusable skills under `skills/<name>/`; place project maintainer skills under `.agents/skills/<name>/`.
- Add a `SKILL.md` that defines purpose, triggers, and the workflow to follow.
- Add `agents/openai.yaml` with UI metadata for the skill.
- Use the specification at `https://agentskills.io/specification` and `https://developers.openai.com/codex/skills/` when creating new skills.
- Keep `README.md` updated with current reusable and project skill lists, with a one-line description for each.

## How to Create a Plugin
- Prefer `$plugin-creator` as the canonical scaffold and marketplace-entry workflow reference for new plugins or substantial plugin reshapes; follow it for normalized naming, manifest shape, optional folders, and marketplace generation before repo-specific cleanup.
- When a new or reshaped plugin needs an embedded CLI under `scripts/`, `skills/<skill>/scripts/`, or a maintenance project under `projects/<tool>/`, route that CLI design and layout work through `$skill-cli-creator`.
- Use the specification at `https://developers.openai.com/codex/plugins` when creating new plugins.
- Create a dedicated directory under `plugins/<name>/` with a clear, stable plugin name.
- Add `.codex-plugin/plugin.json` and treat it as the plugin manifest source of truth for bundled metadata, assets, and bundled skill exposure.
- Register each repo-local plugin in `.agents/plugins/marketplace.json` in the same change that adds, removes, or renames the plugin.
- If the plugin bundles skills, place them under `plugins/<name>/skills/<skill>/` and give each bundled skill its own `SKILL.md`; add `agents/openai.yaml` when that bundled skill has UI metadata in this repo.
- Keep shared plugin runtime artifacts under `plugins/<name>/scripts/` and any maintenance-only implementation under `plugins/<name>/projects/<tool>/`.
- Keep `README.md` updated with the current plugin list and one-line descriptions, including bundled-skill summaries when that improves discoverability.

## Git Commits
- If changes affect multiple skills or plugins, split them into separate, meaningful commits.

## Rules
- Keep README.md skill descriptions, list, and install prompts in sync with `agents/openai.yaml` and any skill adds/removes/renames.
- Keep README.md plugin descriptions and list in sync with `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, and any plugin adds/removes/renames.
- Keep a `Skill Dependencies` section in `README.md` only when one or more skills explicitly require loading other skills at runtime; list each such skill and the required companion skills, update the section when those requirements change, and remove or omit the section entirely when no such requirements exist.
- Keep `AGENTS.md` focused on repository structure, ownership boundaries, implementation notes, maintenance routing, portability notes, and durable learnings; keep invocation behavior, trigger rules, workflows, outputs, and other user-facing runtime contracts in the relevant `SKILL.md` and reference docs.
- Keep `AGENTS.md` lean: record only repo-specific rules or durable learnings that are hard to infer from the tree, and prefer linking or routing to `SKILL.md`, reference docs, or local package manifests instead of duplicating detailed doctrine, migration history, or exhaustive anti-regression lists.
- When new durable rules are discovered while creating or updating skills, add them to this AGENTS.md under the appropriate skill section.
- Use this section only as a fallback when no more appropriate section exists in AGENTS.md.
- In `references/` folders, keep `.md` filenames lowercase except for `README.md` and `AGENTS.md`.
- If `brand_color` isn’t provided, pick a random hex color not already used by other skills in this repo and set it in `agents/openai.yaml`.
- Plugin manifests must keep asset and bundled-skill paths repo-relative and valid from the plugin root; update them together with any plugin layout move. (Codex learning)
- Bundled plugin skills must follow the same runtime/maintenance split as reusable skills under `skills/`: runtime guidance stays in their `SKILL.md`, while repo-maintenance routing stays in repo-level maintainer docs. (Codex learning)
- Runtime skills must stay unaware of `.agents/skills/Maintainer`: do not reference it, its runbooks, or maintainer-routing instructions from runtime `SKILL.md` files or runtime usage references. Keep that routing only in repo-level maintainer docs such as this `AGENTS.md`.
- Runtime skills may surface runtime learnings or durable guidance candidates, but they must not perform self-upgrade, metadata-sync, reference-refresh, or other repo-maintenance workflows from their own runtime instructions.
- Route skill-maintenance and repo-maintenance work through `.agents/skills/Maintainer` from repo-level maintainer docs, not from runtime `SKILL.md` files.
- Keep the repo-level source of truth for skill portability in this `AGENTS.md`: record which skills are Codex-dependent vs portable when that boundary matters for maintenance or runtime behavior.
- Codex-dependent skills must explicitly name the Codex runtime tools, artifacts, or filesystem contracts they require in `SKILL.md`; skills intended to stay portable may mention Codex-only helpers only as optional accelerators with a generic fallback.
- Scope per-user cache files under `~/.cache/dotagents/` by owner: reusable skills use `~/.cache/dotagents/skills/<skill-name>/...`, plugin-shared caches use `~/.cache/dotagents/plugins/<plugin-name>/...`, and plugin-bundled skill caches use `~/.cache/dotagents/plugins/<plugin-name>/skills/<skill-name>/...`. (Codex learning)

### Codex Dependency Classification
- In this section, `portable` means "not dependent on Codex-only runtime features"; it does not necessarily mean the skill is repository-agnostic or broadly reusable unchanged.
- Current Codex-dependent skills are `autoreview`, `codex-changelog`, `code-wiki`, `learn`, `codex-orchestrator`, and `skill-audit`.
- Treat `autoreview` as Codex-dependent because its runtime contract shells through local `git` and Codex CLI `exec` with structured output flags (`--output-schema`, `--output-last-message`) and read-only review execution.
- Treat `code-wiki` as Codex-dependent because its runtime contract requires Codex subagents for parallel repo study when available, `$imagegen` for selected raster wiki visuals, and `~/.cache/dotagents/skills/code-wiki/` as its disposable clone/analysis cache.
- Treat `codex-orchestrator` as Codex-dependent because its runtime contract requires Codex thread tools, heartbeat automation, `~/.cache/dotagents/skills/codex-orchestrator/ledgers/`, `$autoreview`, and standalone Git/GitHub companion skills including `$github-portfolio-triage`, `$github-triage`, `$github-ci`, `$github-deep-review`, `$github-review-threads`, `$github-releases`, `$git-commit`, and `$yeet`.
- Treat `crusty` as Codex-aware but portable because direct-only invocation policy and optional subagents are Codex-aware, while its core challenge workflow can run sequentially with generic web/search fallback.
- Treat `plan-harder` as Codex-aware but portable because Codex-only helpers such as `request_user_input` or subagents are optional and have a non-Codex fallback path.
- Treat `grill-me` as Codex-aware but portable because structured question helpers such as `request_user_input` are optional; its fallback is plain one-question-at-a-time dialogue.
- Treat `domain-modeling` as portable because it uses local repo evidence and project memory such as `CONTEXT.md`, `CONTEXT-MAP.md`, and `project-memory/adr/`, with no Codex-only runtime tools required.
- Treat `grill-me-with-context` as portable and skill-composed because it requires `$grill-me` and `$domain-modeling`, both portable, and otherwise relies on local repo/docs inspection.
- Treat `improve-codebase-architecture` as Codex-aware but portable because optional subagents can speed read-only repo exploration, while sequential source inspection plus `$grill-me-with-context` is the fallback path.
- Treat `setup-project-memory` as Codex-aware but portable because optional session-history bootstrap is isolated in `skills/setup-project-memory/references/session-history.md`, while its core setup flow falls back to repo/workspace evidence plus `$domain-modeling`.
- Treat `to-prd` as portable because it uses local repo or workspace evidence, project memory, and configured issue-tracker instructions to produce or publish PRDs without Codex-only runtime tools.
- Treat `to-issues` as portable and skill-composed because it requires `$plan-harder` for each generated issue and otherwise relies on local project memory plus configured issue-tracker instructions.
- Treat `plan-feature` as portable and skill-composed because it requires `$setup-project-memory`, `$grill-me-with-context`, `$to-prd`, and `$to-issues` while relying on project-memory routing rather than Codex-only runtime tools.
- Treat `triage` as portable and skill-composed because it relies on project-memory issue-tracker mappings, can load `$setup-project-memory` when setup is missing, uses `$grill-me-with-context` for underspecified repo-backed issue intent, and requires `$plan-harder` before marking an issue `ready-for-agent`.
- Treat `skill-cli-creator` as Codex-aware but portable because it may route to Codex scaffold helpers when available, but its embedded-CLI design workflow can continue with an equivalent manually created skill or plugin host.
- Treat `git-commit`, `github-deep-review`, `github-triage`, `github-releases`, and `yeet` as portable scriptless skills because they rely on direct local `git` and GitHub CLI `gh` workflows rather than Codex-only runtime features.
- Treat `github-ci`, `github-review-threads`, `github-portfolio-triage`, and `github-stars` as portable runtime-dependent skills because they require `python3`, local `git` or `gh` as documented by each skill, and their own shipped `scripts/<tool>` artifacts under the owning standalone skill.
- Treat `tanstack` as portable because it is guidance-only, relies on local repo/package inspection plus current TanStack-owned docs when exact APIs matter, and does not require Codex-only runtime tools.
- Treat `.agents/skills/Maintainer` as a portable project-local maintainer skill because it relies on this repository layout and local shell/docs workflows, while any subagent usage remains optional.
- Treat `xcode-changelog` as portable and runtime-dependent on macOS plus network access: it requires `python3`, `xcodebuild`, `xcode-select`, `plutil`, and outbound access to Apple’s documentation endpoints.
- When a skill becomes Codex-dependent or stops being Codex-dependent, update this section in the same change as the skill docs.
- Keep this list updated whenever a skill is added, removed, renamed, or its portability boundary changes.

### Repo-local Plugins
- Keep repo-local plugin registration centralized in `.agents/plugins/marketplace.json`; do not add a plugin without wiring it there in the same rollout.
- Treat `.codex-plugin/plugin.json` as the plugin-local source of truth for plugin name, version, assets, and bundled-skill exposure.
- Keep plugin-bundled skills discoverable under `plugins/<plugin>/skills/` and keep any plugin-owned shared runtime surfaces under `plugins/<plugin>/scripts/`.
- When a plugin grows a maintenance-only implementation tree, keep it under `plugins/<plugin>/projects/<tool>/` and document rebuild/runtime rules there with a local `AGENTS.md`.
- Keep `skills-link.sh` as the canonical local install helper for this repo's reusable skills: it links `skills/` into `~/.agents/skills` only and must not install, mirror, or rewrite plugin marketplace entries. (Codex learning)

### Plugin Lifecycle and Versioning
- Treat `.agents/plugins/marketplace.json` as the repo discovery surface for local plugins: Codex can discover a plugin from the workspace marketplace file and resolve each plugin `source.path` relative to the repo root.
- Treat `~/.codex/plugins/cache/<developer>/<plugin>/<version>/` as the installed plugin cache: once a local plugin is installed, Codex may copy the plugin there and refresh that cached copy from the workspace source when the plugin changes. (Codex learning)
- Keep plugin install and update assumptions cache-aware: if a plugin manifest, bundled skill, runtime script, asset, or other shipped plugin file changes, assume Codex may compare or load the cached copy rather than reading only from the workspace path. (Codex learning)
- Any committed change under `plugins/<plugin>/` must update that plugin's `.codex-plugin/plugin.json` `version` in the same rollout.
- When a plugin ships an embedded CLI with its own version metadata, keep that CLI version aligned with the owning plugin's `.codex-plugin/plugin.json` `version` unless the plugin documents a deliberate independent release policy. (Codex learning)
- Use semantic versioning for plugin version bumps: major for breaking plugin contract changes such as removing or renaming the plugin, removing or renaming bundled skills, incompatible CLI or config changes, or other behavior that can break existing users.
- Use a minor version bump for backward-compatible feature additions or meaningful capability expansion under `plugins/<plugin>/`, such as adding a bundled skill, adding a new runtime command or workflow, or expanding the plugin's install surface without breaking existing behavior.
- Use a patch version bump for backward-compatible fixes and maintenance updates under `plugins/<plugin>/`, including bug fixes, packaging fixes, icon or metadata corrections, prompt or docs adjustments, rebuilds that preserve behavior, and other hotfix-style changes.

### Postgres skill
- Keep Postgres runtime and operator guidance in `skills/postgres/SKILL.md` and `skills/postgres/references/*`, not in this repo-level file.

### Swift-DocC skill
- Keep Swift-DocC bundled-asset refresh and reference integrity checks in `.agents/skills/Maintainer`, and use `.agents/skills/Maintainer/references/swift-docc-runbook.md` as the canonical procedure.
- Keep runtime Swift-DocC docs and fast-path reference design in `skills/swift-docc/`; keep maintainer-only refresh routing here. (Codex learning)

### Swift API Design skill
- Keep Swift API Design bundled-asset refresh and reference integrity checks in `.agents/skills/Maintainer`, and use `.agents/skills/Maintainer/references/swift-api-design-runbook.md` as the canonical procedure.
- Keep runtime Swift API Design docs and bundled-source usage details in `skills/swift-api-design/`; keep maintainer-only refresh routing here.
- Refresh `swift-api-design` from `swiftlang/swift-org-website/documentation/api-design-guidelines/index.md` until the live Swift.org page demonstrably migrates to a different substantive source. (Codex learning)

### Plan Harder skill
- Keep `plan-harder` as the single reusable home for higher-rigor planning support in this repo; do not reintroduce a separate lightweight clarification skill unless that package boundary is intentionally restored. (Codex learning)
- Keep `plan-harder` runtime workflow, clarification behavior, and output details in `skills/plan-harder/SKILL.md` and its references, not in this `AGENTS.md`.
- Keep `plan-harder` chat-output-only: it must not create `plans/`, write Markdown plan files, or edit repo files as part of its own runtime workflow.

### Grill and Domain Modeling skills
- Keep `grill-me` as the generic stateless pressure-testing loop; repo-backed documentation capture belongs in `grill-me-with-context`.
- Keep `domain-modeling` focused on runtime project-language and decision capture in `CONTEXT.md`, relevant docs, and ADRs under `project-memory/adr/`; do not use it for repo-maintenance metadata sync.
- Keep `grill-me-with-context` as the thin composition layer over `grill-me` and `domain-modeling`, not a duplicate questioning loop.
- Keep `improve-codebase-architecture` as architecture discovery and candidate selection first; it should hand the selected candidate to `grill-me-with-context` before implementation rather than duplicating the documentation loop.
- Use `project-memory/` as the visible root for durable project memory owned by these runtime skills: `project-memory/agents/` for repo-specific agent operating config and `project-memory/adr/` for durable decision records. Keep `CONTEXT.md` and optional `CONTEXT-MAP.md` at the project root for fast discovery.

### Setup Project Memory skill
- Keep `setup-project-memory` as the reusable setup surface for creating or refreshing `AGENTS.md` pointers plus `project-memory/agents/issue-tracker.md`, `project-memory/agents/triage-labels.md`, and `project-memory/agents/domain.md` in code repos, monorepos, and orchestrator workspaces.
- `setup-project-memory` must always use `AGENTS.md` for setup pointers and project-memory routing when an agent-instruction file is needed.
- Keep `setup-project-memory` issue-tracker setup limited to GitHub, local markdown, orchestrator-local, GitHub-coordination, or custom only; do not add additional hosted-tracker-specific templates to the project-memory flow.
- Keep `project-memory/agents/triage-labels.md` responsible for both issue type/category mapping (`bug`, `feature`, `task`) and workflow state mapping (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`).
- For already-used projects, `setup-project-memory` may seed `CONTEXT.md` and `project-memory/adr/` from strong repo evidence and recent same-repo session history, using `$domain-modeling` for the context and ADR shape.
- Keep setup conservative: it configures locations and mappings for fresh projects, and only bootstraps domain memory for existing projects when the evidence is accepted, load-bearing, and not merely tentative session discussion.
- In orchestrator workspace mode, keep setup config-only: configure `AGENTS.md`, `project-memory/agents/*`, root `CONTEXT.md`, and ADR layout, but do not create `projects/<project>/` or `features/<feature>/` folders until `$plan-feature`, `$to-prd`, or `$to-issues` writes a real feature.
- Orchestrator workspace memory coordinates cross-repo planning only; child repos keep their own `AGENTS.md`, `CONTEXT.md`, `project-memory`, validation, branches, commits, and PRs.

### PRD and issue-splitting skills
- Keep `plan-feature` as the thin wrapper over `setup-project-memory`, `grill-me-with-context`, `to-prd`, and `to-issues`; do not let it duplicate grilling, PRD drafting, vertical slicing, or issue-hardening logic.
- `plan-feature` may pass explicit write authorization to `to-prd` and `to-issues` only after setup exists and no gates remain.
- Keep `to-prd` focused on producing or publishing PRD artifacts from clarified requirements; do not let it split implementation issues.
- Keep `to-issues` focused on splitting PRDs into vertical implementation issues; it must run `$plan-harder` once per issue and embed the returned brief before returning or publishing that issue.
- In GitHub issue-tracker mode, keep the PRD issue as the parent issue and attach generated implementation issues as sub-issues while preserving `Source PRD: #<number>` in each child issue body.
- In GitHub issue-tracker mode, title PRD issues as `PRD: <Feature Name>` and implementation issues as `<feature-slug>: <NN> <vertical outcome>`.
- In GitHub issue-tracker mode, PRD issues use the mapped `feature` issue type and generated implementation sub-issues use the mapped `task` issue type when GitHub issue types are available.
- In orchestrator GitHub coordination mode, apply a GitHub label named exactly `<project-slug>` to the PRD parent issue and every generated vertical feature issue in the coordination repo.
- Generated implementation issues must include a `## Completion` section: GitHub issues close through a closing keyword on the implementation PR or final commit, while local markdown issues are moved into the configured `issues/done/` folder after validation rather than being deleted or marked with a `done` status. In orchestrator workspace mode, moving to `done` requires cross-repo integration proof.
- `to-issues` owns any issue tracker or local markdown writes it performs; `$plan-harder` remains chat-output-only and must not write plan files or issue files.
- Both skills should read `project-memory/agents/issue-tracker.md` and related project memory before deciding where PRDs or issues belong.

### Triage skill
- Keep `triage` focused on existing incoming GitHub or local markdown issues; new feature planning should still go through `plan-feature`.
- In GitHub mode, use GitHub Issue Type for work kind (`Bug`, `Feature`, `Task` by default) and labels for workflow state.
- In local markdown mode, use `Type:` for work kind and `Status:` for workflow state.
- Treat `needs-info` as a human/reporter waiting state, not an implementation queue state: reporter activity returns the issue to `needs-triage` for re-evaluation before it can become `ready-for-agent`.
- In local markdown mode, completed issues move to the configured `issues/done/` path instead of adding a new completed status.
- Before marking an existing issue `ready-for-agent`, `triage` must harden that single issue through `$plan-harder` and preserve the resulting agent brief in the tracker.

### Maintainer skill
- The `.agents/skills/Maintainer` skill is the default maintainer for improving existing skills and plugins in this repository through shared upgrade tasks and skill-specific refresh workflows.
- `Maintainer` is the only maintainer skill that should orchestrate upgrades, metadata sync, reference refresh, and other repository maintenance for existing skills and plugins in this repository.
- Keep `Maintainer` self-contained: workflow markdown guidance must live under `.agents/skills/Maintainer/references/`.
- Keep the dependency direction one-way: runtime skills must not depend on, reference, or route users to `.agents/skills/Maintainer`; only repo-level maintainer docs may route work to `Maintainer`.
- When updating skill or plugin metadata/docs across the repo, route through the `Maintainer` playbooks and keep README/openai metadata text aligned.
- For brand-new skill creation, use `$skill-creator` first; use `Maintainer` afterward only for repo integration or follow-up maintenance. (Codex learning)
- Keep Codex-dependency audits and TanStack Intent coverage refresh as explicit maintainer-owned maintenance tracks; do not spread those maintenance workflows into runtime skills. (Codex learning)
- Keep TanStack skills coverage alignment against `tanstack-skills/tanstack-skills/plugins` as an explicit maintainer-owned maintenance track; map upstream product plugins into the single reusable `skills/tanstack/` skill and verify product guidance against TanStack-owned docs. (Codex learning)
- During Codex dependency audits, require Codex-dependent skills to name their required Codex tools or runtime contracts precisely, and require portable skills to keep Codex-only helpers optional with a generic fallback.

### Codex Changelog skill
- Keep `codex-changelog` as a Codex-dependent reusable skill under `skills/codex-changelog/`; release-source selection and output formatting belong in its own `SKILL.md` and references, not in this `AGENTS.md`.

### Code Wiki skill
- Keep `code-wiki` as a Codex-dependent reusable skill under `skills/code-wiki/`; runtime repo-study workflow, HTML contract, and image rules belong in `skills/code-wiki/SKILL.md` and its references, not in this `AGENTS.md`.
- Keep `code-wiki` final wiki outputs outside `.cache`; default git clones and temporary analysis artifacts belong under `~/.cache/dotagents/skills/code-wiki/`, while user-requested self-contained source storage belongs under `<wiki-root>/.cache/sources/` with an ignore-all `.gitignore`. (Codex learning)

### Skill CLI Creator skill
- Route embedded-CLI design and layout work through `$skill-cli-creator`; keep detailed host, execution, and migration doctrine in `skills/skill-cli-creator/SKILL.md` and its references.
- Repo-level embedded-CLI invariants are: shipped artifacts live under `scripts/`, maintenance-only implementations live under `projects/<tool>/`, and ownership stays aligned when a CLI is skill-owned, plugin-shared, or owned by one bundled plugin skill. (Codex learning)
- Use direct `scripts/<tool>` implementations for simple single-file CLIs; reserve `projects/<tool>/` for real multi-file, compiled, generated, dependency-managed, or build-backed CLI implementations. (Codex learning)
- Multi-OS compiled CLIs keep the stable executable surface at `scripts/<tool>` and place platform binaries under `scripts/bin/<tool>-<os>-<arch>`; use `projects/<tool>/scripts/` for build/install helpers when needed. (Codex learning)
- Persist embedded-CLI config in owner-aligned `config.toml` files under `<project-root>/.skills/...` or `<project-root>/.plugins/...`, and treat those directories as config-only. (Codex learning)
- Require the shipped artifact to expose `--version` with one semver source of truth, and if `projects/<tool>/` exists require `projects/<tool>/AGENTS.md` plus a scoped `projects/<tool>/.gitignore` when generated state exists. (Codex learning)
- Keep embedded-CLI docs artifact-first: examples must run `<artifact-path> ...`, `<resolved-tool> ...`, or an absolute installed artifact path unless the host explicitly documents a wrapper, alias, or `PATH` contract for bare `<tool> ...`. (Codex learning)

### Standalone Git and GitHub skills
- Keep reusable git and GitHub runtime workflows under standalone `skills/*` as the preferred reusable install surface for `git-commit`, `github-deep-review`, `github-triage`, `github-releases`, `github-ci`, `github-review-threads`, `github-portfolio-triage`, `github-stars`, and `yeet`.
- Keep standalone skills independent from repo-local plugin files, plugin shared scripts, and installed plugin cache copies; standalone runtime docs and code must use direct `git`, direct `gh`, or their own `scripts/<tool>` artifacts.
- Keep `git-commit`, `github-deep-review`, `github-triage`, `github-releases`, and `yeet` scriptless unless a concrete repeated workflow needs a real shipped script.
- Keep `yeet` as a convenience orchestration skill that composes standalone `git-commit` and focused `github-*` skills rather than owning duplicate helper code.
- Keep stars and star-list workflows in standalone `github-stars`, not in repository triage.

### Codex Orchestrator skill
- Keep `codex-orchestrator` as a standalone reusable skill under `skills/codex-orchestrator/`, using standalone Git/GitHub companion skills for queue, CI, review, release, commit, and publish workflows.
- Keep runtime orchestration, worker, gate, and ledger details in `skills/codex-orchestrator/SKILL.md` and its references; keep this file limited to dependency and ownership boundaries.
- Persist portfolio ledgers under `~/.cache/dotagents/skills/codex-orchestrator/ledgers/`, with one ledger per named portfolio by default.

### GitHub Deep Review skill
- Keep `github-deep-review` focused on evidence-first GitHub issue, PR, root-cause, provenance, and fix-quality review; keep PR review-thread reply routing in `github-review-threads`.
- Do not reintroduce a broad umbrella `github` skill unless repeated runtime evidence shows ambiguous GitHub work needs a dedicated model-visible router again.

### Git Commit skill
- Keep the standalone reusable `git-commit` skill under `skills/git-commit/` scriptless and focused on selective staging, commit authoring, and push-only flows with direct `git`.

### Yeet skill
- Keep the standalone reusable `yeet` skill under `skills/yeet/` scriptless unless a future repeated publish workflow proves a shipped script is necessary.
- Keep `yeet` focused on publish orchestration from a local checkout rather than duplicating commit-authoring or generic GitHub skill ownership. (Codex learning)

### Learn skill
- Keep `learn` as the repo-facing persistence surface for durable `AGENTS.md` updates in this repository; broader memory-system files are outside this repo's editable scope.
- When durable learnings are added through `learn`, place them in the most appropriate existing section when possible, otherwise create a fitting section; use `## Codex Learnings` only as a fallback, and suffix each inserted bullet with ` (Codex learning)`.
- When the user says a rule is a "hard rule" or otherwise uses durable language and the correct persistence target is unclear, ask where to save it and recommend an `AGENTS.md` target by default. (Codex learning)

### Skill Audit skill
- Keep `skill-audit` as the single audit surface for installed Codex surfaces: standalone skills, plugin packages, and bundled plugin skills.
- Keep `skill-audit` implementation centered on local discovery surfaces first, with shared or cached installations used as verification surfaces rather than editable sources. (Codex learning)
- Keep portfolio-level duplicate, unused, prompt-budget, and root-summary analysis inside `skill-audit` rather than a separate cleanup skill; `scripts/portfolio-health` is audit evidence, not an automatic deletion workflow.
- When auditing a bundled plugin skill, require `skill-audit` to inspect both the bundled skill contract and the owning plugin package, including `.codex-plugin/plugin.json` when available. (Codex learning)
- Treat Codex plugin cache copies under `~/.codex/plugins/cache/...` as verification only; do not route fixes or edits to cache paths. (Codex learning)
- When a named target path lives under `~/.codex/plugins/cache/...`, require `skill-audit` to resolve plugin identity first, then use visible workspace plugin discovery surfaces such as `.agents/plugins/marketplace.json` and the owning `.codex-plugin/plugin.json` to confirm the editable source when possible; if no workspace mapping is visible, report that the editable source was not confirmed. (Codex learning)
- When plugin-package issues are actually bundled-skill issues, prefer recommending the narrowest owning surface: bundled plugin skill, plugin package, repo docs, or `Maintainer`.
