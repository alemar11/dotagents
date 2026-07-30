# Repository Guidelines

## Overview

This repository hosts reusable Codex skills, project maintainer skills, optional repo-local plugins, and MCP install helpers. Reusable skills live under `skills/`, optional repo-local plugins live under `plugins/`, project maintainer skills live under `.agents/skills/`, and global MCP install helpers live under `mcps/`. Every reusable or bundled skill is documented by a `SKILL.md` entrypoint, and every plugin must ship `.codex-plugin/plugin.json`. Keep guidance lightweight and focused on building and evolving skills and plugins.
Agent skills follow the specification at `https://agentskills.io/specification`.
Codex skills reference: `https://developers.openai.com/codex/skills/`.

## Repository Context

### Issue tracker

Feature Specs, implementation issues, and Ideas live in GitHub Issues. See
`project-memory/config/issue-tracker.md`.

### Repository scope

This Git repository contains independently planned reusable skills and
repo-local plugins. Root and scoped context files provide any path-specific
routing needed by a workflow.

### Artifact markers, issue types, and workflow states

Canonical planning vocabulary and GitHub label mappings live in
`project-memory/config/triage-labels.md`.

## Creating Skills

- Prefer `$skill-creator` as the canonical scaffold and workflow reference for new skills or substantial skill reshapes; follow its initialization, metadata, validation, and forward-testing guidance before repo-specific cleanup.
- When a new or reshaped skill needs an embedded CLI under `scripts/` or a maintenance project under `projects/<tool>/`, route that CLI design and layout work through `$skill-cli-creator`.
- Create a dedicated directory per skill with a clear, stable name.
- Place reusable skills under `skills/<name>/`; place project maintainer skills under `.agents/skills/<name>/`.
- Add a `SKILL.md` that defines purpose, triggers, and the workflow to follow.
- Add `agents/openai.yaml` with UI metadata for the skill.
- Use the specification at `https://agentskills.io/specification` and `https://developers.openai.com/codex/skills/` when creating new skills.
- Keep `README.md` updated with current reusable and project skill lists, with a one-line description for each.

## Creating Plugins

- Prefer `$plugin-creator` as the canonical scaffold and marketplace-entry workflow reference for new plugins or substantial plugin reshapes; follow it for normalized naming, manifest shape, optional folders, and marketplace generation before repo-specific cleanup.
- When a new or reshaped plugin needs an embedded CLI under `scripts/`, `skills/<skill>/scripts/`, or a maintenance project under `projects/<tool>/`, route that CLI design and layout work through `$skill-cli-creator`.
- Use the specification at `https://developers.openai.com/codex/plugins` when creating new plugins.
- Create a dedicated directory under `plugins/<name>/` with a clear, stable plugin name.
- Add `.codex-plugin/plugin.json` and treat it as the plugin manifest source of truth for bundled metadata, assets, and bundled skill exposure.
- Register each repo-local plugin in `.agents/plugins/marketplace.json` in the same change that adds, removes, or renames the plugin.
- If the plugin bundles skills, place them under `plugins/<name>/skills/<skill>/` and give each bundled skill its own `SKILL.md`; add `agents/openai.yaml` when that bundled skill has UI metadata in this repo.
- Keep shared plugin runtime artifacts under `plugins/<name>/scripts/` and any maintenance-only implementation under `plugins/<name>/projects/<tool>/`.
- Keep `README.md` updated with the current plugin list and one-line descriptions, including bundled-skill summaries when that improves discoverability.

## Repository-Wide Rules

### Documentation and Metadata

- Keep README.md skill descriptions, list, and install prompts in sync with `agents/openai.yaml` and any skill adds/removes/renames.
- Keep README.md plugin descriptions and list in sync with `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, and any plugin adds/removes/renames.
- Keep a `Skill Dependencies` section in `README.md` only when one or more skills explicitly require loading other skills at runtime; list each such skill and the required companion skills, update the section when those requirements change, and remove or omit the section entirely when no such requirements exist.
- Keep `AGENTS.md` focused on repository structure, ownership boundaries, implementation notes, maintenance routing, portability notes, and durable learnings; keep invocation behavior, trigger rules, workflows, outputs, and other user-facing runtime contracts in the relevant `SKILL.md` and reference docs.
- Keep `AGENTS.md` lean: record only repo-specific rules or durable learnings that are hard to infer from the tree, and prefer linking or routing to `SKILL.md`, reference docs, or local package manifests instead of duplicating detailed doctrine, migration history, or exhaustive anti-regression lists.
- When new durable rules are discovered while creating or updating skills, add them to this AGENTS.md under the appropriate skill section.
- Use a repository-wide section only when a rule applies across packages; otherwise place it in the dedicated section for the owning skill or plugin.
- In `references/` folders, keep `.md` filenames lowercase except for `README.md` and `AGENTS.md`.
- If `brand_color` isn’t provided, pick a random hex color not already used by other skills in this repo and set it in `agents/openai.yaml`.

### Runtime Contract Design

- Keep behavior-affecting option contracts canonical across this repository: use `snake_case` field names and lower-kebab assigned values. Natural-language phrases may explain an option but must not be its value; resolve prose directly to canonical values and emit and persist only canonical values. Runtime skills must reject noncanonical fields and values instead of accepting aliases, mapping retired syntax, or providing compatibility migrations unless their dedicated section defines an exception. Keep an option value separate from associated prose, data, or references. Factual booleans and externally owned syntax are exempt. (Codex learning)
- Build skill content through progressive disclosure: keep selection-critical metadata plus core routing and load-bearing workflow-order, safety/mutation, and output contracts in `SKILL.md`; give each behavior-affecting contract or field registry one canonical owner; move branch-specific detail behind directly linked references with explicit read conditions whose predicates are decidable from already-loaded content or the target artifact; and cross-reference instead of repeating canonical field lists or detailed prose. (Codex learning)

### Testing and Validation

- Measure compaction against always-loaded metadata and representative invoked paths (`SKILL.md` plus every reference required by that path), not total repository lines or text moved between files on the same path. Preserve trigger, workflow-order, safety, mutation, and output semantics with focused contract tests, and forward-test representative paths when static checks cannot prove equivalence. (Codex learning)
- Keep skill and plugin tests meaningful: validate executable behavior or
  structural invariants by parsing representative artifacts, fixtures, state,
  graphs, schemas, or command results. Do not treat the presence of explanatory
  prose in `SKILL.md`, references, AGENTS.md, or scenario Markdown as behavioral
  proof. Exact-text assertions are allowed only when the literal text is itself
  a machine-consumed or externally required contract, such as a field name,
  marker, command syntax, manifest value, or template delimiter; make that
  reason evident in the test. A prose scenario is documentation unless a test
  harness executes its inputs and verifies its outcomes. For model-directed
  workflows, pair deterministic artifact validators with representative
  forward runs, and never claim runtime behavior from documentation-presence
  checks alone. (Codex learning)

### Runtime and Maintenance Boundaries

- Runtime skills must stay unaware of `.agents/skills/maintainer`: do not reference it, its runbooks, or maintainer-routing instructions from runtime `SKILL.md` files or runtime usage references. Keep that routing only in repo-level maintainer docs such as this `AGENTS.md`.
- Runtime skills may surface runtime learnings or durable guidance candidates, but they must not perform self-upgrade, metadata-sync, reference-refresh, or other repo-maintenance workflows from their own runtime instructions.
- Keep skill-maintenance and repo-maintenance workflows owned by `.agents/skills/maintainer` in repo-level maintainer docs, but invoke `$maintainer` only when the user selects it explicitly; ordinary change requests follow this `AGENTS.md` and the targeted package directly.

### Cache Ownership

- Scope per-user cache files under `~/.cache/dotagents/` by owner: reusable skills use `~/.cache/dotagents/skills/<skill-name>/...`, plugin-shared caches use `~/.cache/dotagents/plugins/<plugin-name>/...`, and plugin-bundled skill caches use `~/.cache/dotagents/plugins/<plugin-name>/skills/<skill-name>/...`. (Codex learning)

### Repository Tooling

- Keep `skills-link.sh` as the canonical local install helper for this repo's reusable skills: it links `skills/` into `~/.agents/skills` only and must not install, mirror, or rewrite plugin marketplace entries. (Codex learning)

### Git Commits

- If changes affect multiple skills or plugins, split them into separate, meaningful commits.

## Package-Specific Rules

### Codex Dependency Classification

- Keep the repo-level source of truth for skill portability in this `AGENTS.md`: record which skills are Codex-dependent vs portable when that boundary matters for maintenance or runtime behavior.
- Codex-dependent skills must explicitly name the Codex runtime tools, artifacts, or filesystem contracts they require in `SKILL.md`; skills intended to stay portable may mention Codex-only helpers only as optional accelerators with a generic fallback.
- In this section, `portable` means "not dependent on Codex-only runtime features"; it does not necessarily mean the skill is repository-agnostic or broadly reusable unchanged.
- Current Codex-dependent skills are `autoreview`, `codex-changelog`, `code-review-rules`, `code-wiki`, `focus-task`, `learn`, `maintainer`, `implement-feature`, `pi-delegate`, and `skill-audit`.
- Treat `skill-audit` as Codex-dependent because its live branch requires Codex App task discovery, authoritative task reads, and bounded task waits; historical audits also use Codex memory and session evidence.
- Treat `autoreview` as Codex-dependent because its runtime contract shells through local `git` and Codex CLI `exec` with structured output flags (`--output-schema`, `--output-last-message`) and read-only review execution.
- Treat `code-wiki` as Codex-dependent because its runtime contract requires Codex subagents for parallel repo study when available, `$imagegen` for selected raster wiki visuals, and `~/.cache/dotagents/skills/code-wiki/` as its disposable clone/analysis cache.
- Treat `focus-task` as Codex-dependent because it requires the Codex App project-listing, task-creation, and task-title tools to create a compact-context continuation task without forking the caller's complete history.
- Treat `code-review-rules` as Codex-dependent because its historical evidence branch may inspect Codex session, memory, or task evidence scoped to the current repository; it composes with `$learn` for every approved durable `AGENTS.md` write.
- Treat `implement-feature` as Codex-dependent and runtime-dependent on `python3` because it runs only in the ChatGPT App in Codex mode: implementation requires `scripts/run-state`, read-only local closeout through `scripts/verify-ready`, explicitly authorized visible Codex tasks, ChatGPT-created worktrees, execution-ready Feature Spec bundles, `$autoreview`, and GitStack workflows. The ChatGPT App owns command execution and approval; GitStack owns Git and GitHub behavior. It has no planning, root/background implementation, raw Git worktree machinery, or merge authority.
- Treat `pi-delegate` as Codex-dependent and runtime-dependent on `python3` plus the local `pi` executable because Codex remains the controller, launches a trusted Pi subprocess in the current project, and independently verifies its findings or changes. Keep it manual-only and pin every delegated run to `zai-coding-cn/glm-5.2`.
- Treat `.agents/skills/maintainer` as Codex-dependent because health diagnosis and workflow-family hardening conditionally use `$skill-audit` plus Codex memory/session evidence for portfolio, prompt-quality, overlap, or runtime invocation claims, substantial reshapes require `$skill-creator` or `$plugin-creator`, and non-trivial implementation closeout requires `$autoreview`.
- Treat `crusty` as Codex-aware but portable because direct-only invocation policy and optional subagents are Codex-aware, while its advisory critique and implementation-evaluation workflows can run sequentially with generic web/search fallback.
- Treat `plan-harder` as Codex-aware but portable because Codex-only helpers such as `request_user_input` or subagents are optional and have a non-Codex fallback path.
- Treat `grill-me` as Codex-aware but portable because structured question helpers such as `request_user_input` are optional; its fallback is plain one-question-at-a-time dialogue.
- Treat `grill-me-with-context` as portable and skill-composed because it requires `$grill-me` and `$project-memory`, both portable, and otherwise relies on local repo/docs inspection.
- Treat `improve-codebase-architecture` as Codex-aware but portable because optional subagents can speed read-only repo exploration, while sequential source inspection plus `$grill-me-with-context` is the fallback path.
- Treat `project-memory` as Codex-aware but portable because optional session-history bootstrap is isolated in `skills/project-memory/references/session-history.md`, while its core setup and internal domain-modeling flow fall back to repository evidence plus optional localization evidence.
- Treat `capture-idea` as Codex-aware but portable because `request_user_input` is an optional multi-Idea selection accelerator with a plain-language fallback, while its core local capture contract uses Project Memory routing and its GitHub apply path composes with GitStack.
- Treat `plan-feature` as portable and skill-composed because its core and local-tracker workflows require `$project-memory`, `$grill-me-with-context`, and `$plan-harder`; its GitHub tracker backend additionally requires `$gitstack:github-issues`.
- Treat `skill-cli-creator` as Codex-aware but portable because it may route to Codex scaffold helpers when available, but its embedded-CLI design workflow can continue with an equivalent manually created skill or plugin host.
- Treat GitStack as Codex-dependent because its bundled workflows require the official GitHub connector. Its shared CLI fallback remains runtime-dependent on Python 3.11+, local `git`, and authenticated `gh`.
- Treat `okf` as portable runtime-dependent because it requires `python3` for its shipped `scripts/okf` CLI, uses optional `PyYAML` when available for exact YAML parsing, and otherwise relies on local markdown/spec assets without Codex-only runtime tools.
- Treat `tanstack` as portable because it is guidance-only, relies on local repo/package inspection plus current TanStack-owned docs when exact APIs matter, and does not require Codex-only runtime tools.
- Treat `xcode-changelog` as portable and runtime-dependent on macOS plus network access: it requires `python3`, `xcodebuild`, `xcode-select`, `plutil`, and outbound access to Apple’s documentation endpoints.
- When a skill becomes Codex-dependent or stops being Codex-dependent, update this section in the same change as the skill docs.
- Keep this list updated whenever a skill is added, removed, renamed, or its portability boundary changes.

### Delegated Model Registry

- Keep this registry of skills that explicitly select a delegated model: `autoreview` -> `gpt-5.6-sol` (`high` standard, `xhigh` high-risk); `implement-feature` -> `gpt-5.6-sol` (`medium` routine, `high` complex, `xhigh` risky/cross-system); `pi-delegate` -> `zai-coding-cn/glm-5.2` (user-selected Pi thinking level, `medium` default). Exclude delegations that inherit the parent or host default or are provider-managed. (Codex learning)
- Whenever a skill adds, removes, or changes an explicit delegated model or reasoning-effort policy, update this registry in the same change; use it as the audit list when a pinned model generation is upgraded or retired. (Codex learning)

### Repo-local Plugins

- Keep repo-local plugin registration centralized in `.agents/plugins/marketplace.json`; do not add a plugin without wiring it there in the same rollout.
- Treat `.codex-plugin/plugin.json` as the plugin-local source of truth for plugin name, version, assets, and bundled-skill exposure.
- Plugin manifests must keep asset and bundled-skill paths repo-relative and valid from the plugin root; update them together with any plugin layout move. (Codex learning)
- Bundled plugin skills must follow the same runtime/maintenance split as reusable skills under `skills/`: runtime guidance stays in their `SKILL.md`, while repo-maintenance routing stays in repo-level maintainer docs. (Codex learning)
- Keep plugin-bundled skills discoverable under `plugins/<plugin>/skills/` and keep any plugin-owned shared runtime surfaces under `plugins/<plugin>/scripts/`.
- When a plugin grows a maintenance-only implementation tree, keep it under `plugins/<plugin>/projects/<tool>/` and document rebuild/runtime rules there with a local `AGENTS.md`.

### Plugin Lifecycle and Versioning

- Treat `.agents/plugins/marketplace.json` as the repo discovery surface for local plugins: Codex can discover a plugin from the workspace marketplace file and resolve each plugin `source.path` relative to the repo root.
- Treat `~/.codex/plugins/cache/<developer>/<plugin>/<version>/` as the installed plugin cache: once a local plugin is installed, Codex may copy the plugin there and refresh that cached copy from the workspace source when the plugin changes. (Codex learning)
- Keep plugin install and update assumptions cache-aware: if a plugin manifest, bundled skill, runtime script, asset, or other shipped plugin file changes, assume Codex may compare or load the cached copy rather than reading only from the workspace path. (Codex learning)
- Any committed change under `plugins/<plugin>/` must update that plugin's `.codex-plugin/plugin.json` `version` in the same rollout.
- When a plugin ships an embedded CLI with its own version metadata, keep that CLI version aligned with the owning plugin's `.codex-plugin/plugin.json` `version` unless the plugin documents a deliberate independent release policy. (Codex learning)
- Use semantic versioning for plugin version bumps: major for breaking plugin contract changes such as removing or renaming the plugin, removing or renaming bundled skills, incompatible CLI or config changes, or other behavior that can break existing users.
- Use a minor version bump for backward-compatible feature additions or meaningful capability expansion under `plugins/<plugin>/`, such as adding a bundled skill, adding a new runtime command or workflow, or expanding the plugin's install surface without breaking existing behavior.
- Use a patch version bump for backward-compatible fixes and maintenance updates under `plugins/<plugin>/`, including bug fixes, packaging fixes, icon or metadata corrections, prompt or docs adjustments, rebuilds that preserve behavior, and other hotfix-style changes.

### Postgres Skill

- Keep Postgres runtime and operator guidance in `skills/postgres/SKILL.md` and `skills/postgres/references/*`, not in this repo-level file.
- Postgres is exempt from the repository-wide hard-cut requirement for behavior-affecting option fields and values; its own runtime contract governs compatibility behavior.

### OKF Skill

- Keep OKF runtime guidance in `skills/okf/SKILL.md`, `skills/okf/references/*`, and the shipped `skills/okf/scripts/okf` CLI.
- Keep official OKF spec refresh mechanics in `.agents/skills/maintainer`, using `.agents/skills/maintainer/references/okf-spec-runbook.md` as the canonical procedure.
- Runtime OKF docs must not reference `.agents/skills/maintainer`, maintainer scripts, or maintainer-only routing.

### Swift-DocC Skill

- Keep Swift-DocC bundled-asset refresh and reference integrity checks in `.agents/skills/maintainer`, and use `.agents/skills/maintainer/references/swift-docc-runbook.md` as the canonical procedure.
- Keep runtime Swift-DocC docs and fast-path reference design in `skills/swift-docc/`; keep maintainer-only refresh routing here. (Codex learning)

### Swift API Design Skill

- Keep Swift API Design bundled-asset refresh and reference integrity checks in `.agents/skills/maintainer`, and use `.agents/skills/maintainer/references/swift-api-design-runbook.md` as the canonical procedure.
- Keep runtime Swift API Design docs and bundled-source usage details in `skills/swift-api-design/`; keep maintainer-only refresh routing here.
- Refresh `swift-api-design` from `swiftlang/swift-org-website/documentation/api-design-guidelines/index.md` until the live Swift.org page demonstrably migrates to a different substantive source. (Codex learning)

### Plan Harder Skill

- Keep `plan-harder` as the single reusable home for higher-rigor planning support in this repo; do not reintroduce a separate lightweight clarification skill unless that package boundary is intentionally restored. (Codex learning)
- Keep `plan-harder` runtime workflow, clarification behavior, and output details in `skills/plan-harder/SKILL.md` and its references, not in this `AGENTS.md`.
- Keep `plan-harder` output-only: its standalone surface returns chat output and
  its issue-hardening caller surface returns a structured result to the
  invoking workflow. It must not create `plans/`, write Markdown plan files, or
  edit repo files as part of its own runtime workflow.

### Pi Delegate Skill

- Keep `pi-delegate` manual-only with `policy.allow_implicit_invocation: false`.
- Allow explicitly delegated bounded research, investigation, analysis, review, implementation, and mixed tasks; do not reject advisory work merely because Codex could perform it directly. Preserve the user's mutation boundary in the worker brief, independently verify material findings or changes, and inspect the working tree after read-only runs because Pi is not sandboxed.
- Keep `zai-coding-cn/glm-5.2` fixed in its shipped launcher; never fall back to another provider or model when preflight fails.
- Let the user select any canonical Pi thinking level and default to `medium` when omitted; do not infer a different level from task complexity.
- Codex remains the controller: Pi may edit files and run local project commands, but Codex must inspect the complete diff and independently validate the result before closeout.
- Run Pi in the caller's current project or worktree with explicit project trust through `--approve`, so project-local Pi resources and skills can load. Use it only in trusted projects; do not change into the skill root or treat Pi project trust as a sandbox.
- Allow concurrent Pi sessions and require the controller to monitor each sanitized progress stream by stable run ID, resolved session ID, name, and project root through terminal state before integrating the combined diff.
- Bound every Pi run with the launcher timeout and terminate the complete Pi process tree on timeout or controller cancellation; preserve explicit `completed`, `failed`, `timeout`, and `aborted` terminal evidence.
- Use task-file transport for multiline, skill-invoking, quoted, or shell-sensitive Pi prompts so literal skill names and syntax reach the launcher unchanged.

### Grill and Project Memory Composition

- Keep `grill-me` as the generic stateless pressure-testing loop; repo-backed documentation capture belongs in `grill-me-with-context`.
- Keep `grill-me-with-context` as the thin composition layer over `grill-me` and `$project-memory domain-memory`, not a duplicate questioning or domain-capture loop.
- Keep `improve-codebase-architecture` as architecture discovery and candidate selection first; it should hand the selected candidate to `grill-me-with-context` before implementation rather than duplicating the documentation loop.
- Use `project-memory/` as the visible root for durable project memory owned by these runtime skills: `project-memory/config/` for repo-specific agent operating config and `project-memory/adr/` for durable decision records. Use root `CONTEXT.md` as the single context entry point and route optional scoped `CONTEXT.md` files from its `Scoped Contexts` table.

### Project Memory Skill

- Keep `project-memory` as the normal public lifecycle surface for creating or refreshing `AGENTS.md` pointers plus `project-memory/config/issue-tracker.md`, `project-memory/config/triage-labels.md`, root and optional scoped `CONTEXT.md`, optional `TRANSLATION.md`, and ADR routing or content in Git repositories.
- Use exactly one `project-memory/` directory per Git repository root. Internal monorepo scopes use scoped `CONTEXT.md` files and optional subdirectories under the root `project-memory/adr/`; they must not create nested `project-memory/` directories. Non-Git roots never own Project Memory.
- For context discovery, treat the current Git repository as the default selected root. Explicit user scope or a validated linked Feature Spec Set authorizes the selected repository identities, but the composed caller must supply candidate local Git roots separately and verify each root against one authorized identity. Project Memory never fabricates paths from Spec refs or infers scope from the ChatGPT App primary project, saved-project list, common parent, or path proximity. Read each verified root `CONTEXT.md` when present, then follow every non-overlapping `Scoped Contexts` row matched by affected paths. Reject extra or unmatched roots and inspect matched paths without context directly rather than creating dangling pointers. (Codex learning)
- For implementation closeout that carries accepted durable decisions, require the implementor to invoke `$project-memory domain-memory`; Project Memory must run its internal domain-modeling workflow, reconcile the carried delta against behavior that actually landed, update only the named durable surfaces, and verify the documentation diff. `$plan-feature` assigns this work but must not perform it during planning. (Codex learning)
- Keep `skills/project-memory/references/options.md` limited to the genuine controls `memory_slice`, `domain_operation`, `write_mode`, and `capture_mode`. Derive execution context from repository evidence, treat a knowledge handoff as input data, and report capture outcome as result state rather than selectable configuration. (Codex learning)
- Keep issue-tracker setup limited to the durable `tracker_backend` values `github` and `local`. Delivery target, branch, PR shape, publication mode, issue-mutation authority, repository-set topology, and runtime orchestration policy are not Project Memory configuration. (Codex learning)
- Always use `AGENTS.md` for short project-memory pointers when an agent-instruction file is needed; keep domain context, tracker detail, planning history, and accepted decisions in `CONTEXT.md`, `project-memory/config/*`, or ADRs.
- Keep Project Memory as the sole reusable owner of the canonical artifact marker `idea`, issue types (`bug`, `feature`, `task`), workflow states (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), and their explicit mapping transports through `skills/project-memory/references/triage-labels.md`. Marker rows use `label` or `local-header`; type rows use `native-type`, `label`, `body-field`, or `local-header`; state rows use `label` or `local-header`, subject to backend compatibility. Keep each repository's `project-memory/config/triage-labels.md` as the concrete tracker mapping source consumed by Capture Idea, Plan Feature, and other workflows; consumers must reject missing or unsupported transports rather than infer them or define a parallel registry.
- Keep `TRANSLATION.md` optional and evidence-backed: create it only when localization support or durable translation rules are clear from repo evidence or explicit user confirmation, and add an `AGENTS.md` localization pointer only when the file exists or is confirmed.
- Do not add schema versions to `project-memory` generated Markdown files or templates unless a concrete parser or migration workflow requires versioning.
- Keep behavior-affecting setup files human-first but table-first: use typed configuration tables for tracker backend, artifact markers, issue types, and workflow states, and leave prose for rationale and conventions.
- Keep setup conservative: it configures locations and mappings for fresh projects, and only bootstraps domain memory for existing projects when the evidence is accepted, load-bearing, and not merely tentative session discussion.
- Keep first-time-user setup ambiguity prompts canonical in `skills/project-memory/references/setup-questions.md`: normally ask no questions, show concrete conflicting evidence when one is necessary, use project language rather than Project Memory internals, and translate answers to canonical configuration internally.
- During authorized Project Memory domain bootstrap, always create or update root `CONTEXT.md` at every selected Git root. Keep evidence-poor roots minimal with explicit unknowns; use verified monorepo scopes for stable routing, and require stronger accepted evidence before adding richer vocabulary, rules, boundaries, or scoped context files.
- Resolve `write_mode=propose` for review-only or no-mutation work and `write_mode=apply` only with scoped write authority. Do not persist that run choice in project configuration.

### Capture Idea Skill

- Keep `capture-idea` as the manual-only public surface for preserving tentative proposals before Feature Spec planning; ordinary brainstorming, issue creation, planning, and implementation requests must not auto-select it.
- Keep `skills/capture-idea/references/options.md` limited to the run-scoped `write_mode` control. Consume tracker backend, tracker owner, artifact-marker mapping, candidate decisions, queue intent, paths, and refs as execution facts or data.
- Keep one durable Idea per independently plannable proposal and exactly one tracker-owning repository per Idea. GitHub Ideas use the configured `idea` label with native Issue Type unset; local Ideas use `planning/ideas/<idea-slug>.md` with `artifact_marker: idea`, no `issue_type`, and optional explicit `needs-triage` only at capture.
- Keep Capture Idea separate from Feature Spec drafting and domain memory. `$plan-feature` owns durable Idea-source consumption and lifecycle reconciliation; Project Memory owns the marker and state registry; GitStack owns GitHub mutation mechanics.

### Plan Feature Skill

- Keep `plan-feature` as the single public convergent planning surface: every successful run produces or completes one implementation-eligible Feature Spec with a nonempty hardened issue graph for a single repository or monorepo, or one linked repo-owned Spec and graph per affected repository for a multi-repository feature. No additional top-level Spec exists. Never return a standalone Spec without its required issue graph as a successful terminal result; keep dense Feature Spec writing and issue splitting guidance in the internal `references/` phase files.
- Keep `skills/plan-feature/references/options.md` as the owner of the sole default-path control, `write_mode`. Consume `tracker_backend` as a validated Project Memory fact, derive the affected repository set and source route from explicit intake evidence, and do not add repository topology as a run option or durable config. (Codex learning)
- Keep tracker location and code delivery separate: Project Memory owns only `tracker_backend`; Plan Feature renders `delivery_type` as stable non-option data in every implementation-eligible Feature Spec and issue. Support GitHub tracker plus `github-pr`, local tracker plus `local-branch`, and local tracker plus `github-pr`; never infer PR delivery merely from GitHub repository identity. (Codex learning)
- Treat explicitly selected durable `source_idea_refs` as planning input only when no durable `source_spec_ref` exists at intake. Reject proposed Idea refs. On the existing-source route, derive `bound_source_idea_refs` only from exact `- Source Idea:` lines in the complete Spec set; if explicit refs are also supplied, require exact set equality and reject additional, missing, different, or unbound refs. Use bound refs only for continuation validation and lifecycle reconciliation after complete-bundle convergence, never to redraft the Spec. Allow backlog discovery only from an explicit Idea-discovery request, keep it read-only until the user selects refs, and never scan Ideas during an ordinary planning run. Preserve Idea bodies, transform their canonical sections as tentative planning evidence, render refs only in each relevant Feature Spec `## Source`, and keep refs plus coverage maps out of generated issue Execution Contracts.
- Reconcile coverage for every consumed Idea independently only after the complete requested planning result is durable and verified. Load the complete outcome history plus prior coverage Specs, require monotonic cumulative covered and remaining scope, and persist one canonical append-only outcome per successful result. A terminal wait for one requester answer may use `needs-info`; partial coverage returns the Idea to `needs-triage`; full coverage closes the GitHub Idea or marks the local Idea consumed. An Idea tracks planning completion, so later PR merge does not own its closure. Proposal and other non-durable previews report intended coverage separately; partially published runs do not write outcomes or close source Ideas.
- Keep `plan-feature` manual-only in Codex metadata with `policy.allow_implicit_invocation: false`; ordinary feature, planning, Feature Spec, issue splitting, implementation, or triage requests must not auto-select it. (Codex learning)
- Keep Feature Spec vocabulary and the single convergent pipeline as a hard runtime cut with no read aliases for retired planning names, fields, values, paths, or authority values. Active planning state and hosted or local issue bodies must already use the canonical Feature Spec contract before the runtime consumes them; do not switch runtimes until a stale-vocabulary scan is clean. (Codex learning)
- `write_mode=apply` publishes through the configured tracker; `write_mode=propose` performs no writes and returns proposed bodies, paths, metadata, and publication order. Never publish incomplete Feature Specs or mark partial work agent-ready; uniquely marked non-executable staging issues are permitted only for hosted roles inside the recoverable multi-repository publication transaction. (Codex learning)
- In monorepo and multi-repository planning, carry the accepted product slug, every exact selected Git root, each matched scoped context file, and the authoritative feature slug through `plan-feature` and its internal phases. Multi-repository planning additionally generates or preserves one lowercase UUID `feature_id` shared by all linked Specs. Prefer explicit or path-derived slugs over title-derived slugs. (Codex learning)
- Keep the `plan-feature` Feature Spec phase focused on producing or publishing new Feature Spec artifacts from clarified requirements, or validating a supplied durable source against the existing-source policy; do not let it split implementation issues.
- On the existing-source route, protect stable fields directly: required outcome and Non-Goals, canonical source, repositories, allowed paths, branch, dependencies, acceptance text/count/order, safety, and material validation budgets and terminal outcome. Preserve executor-owned checkbox markers and compatible mutable execution content, including recommended implementation approach or internal design, safer rewrites, additional or equivalent tests, compatible clarifications, and progress, status, or evidence. A material stable-field change blocks and requires a separately authorized planning repair; marker-only or compatible mutable changes do not. Materially constrained validation must state an explicit prose failure policy before `ready-for-agent`. (Codex learning)
- For recoverable publication across hosted and local roles, persist reconstructable typed transaction facts and compare stable fields directly while preserving mutable execution content. Do not use tracker-text, template, body, result, packet, or message hashes. Resume only a recognized transaction, create or finalize only its exact missing targets and relationships, and treat every other appeared or materially changed target as a race. (Codex learning)
- Keep the `plan-feature` issue phase focused on converging Feature Specs into vertical implementation issues. Enumerate complete durable state before synthesis, seed the candidate graph with contract-equivalent issues as fixed IDs/slices, synthesize only uncovered scope, create only missing issues, repair only missing mapped tracker metadata or parent/sub-issue attachment, return a verified no-op for a complete bundle, and stop on stale, conflicting, duplicate, or extra artifacts. Never renumber or regenerate a retained issue. Re-read the owning Spec, Project Memory mappings, and complete issue/metadata/relationship state immediately before proposal, no-op, or the first mutation and prove exact absence before every create. For a local contract-equivalent active file, a supported metadata repair may add only missing canonical header lines and must leave the rest byte-identical; never repair `done/` lifecycle state. Dependency data and source-body sibling or cross-Spec relationships must already match. After graph and scope stabilization it must run `$plan-harder` one or more times per missing issue, rerun it after material pre-publication repairs, and persist only the final stable brief plus one provenance line without duplicating top-level sections.
- Keep Plan Feature delivery-neutral: it produces the same complete planning contract for GitHub and local Markdown trackers, does not require a GitHub remote, and never selects the executor's publication or terminal transport. Feature Spec and issue acceptance criteria are separate stable contracts and need not be textually identical; require a transient complete Spec-to-issue coverage map before publication. (Codex learning)
- In GitHub tracker mode, hosted issues are authoritative and body files are transient outside the repository. In local mode, durable artifacts live under `planning/features/<feature-slug>/`; proposal output is returned without creating a mirror or durable file.
- Generated implementation issues are the durable execution graph by default; do not create a separate hosted issue, local file, Feature Spec section, or inline scheduling artifact. If a user asks for a summary, return it as a non-authoritative view derived from the current issue bodies. (Codex learning)
- Give each implementation issue one canonical `## Execution Contract` containing its source ref, feature slug, affected repositories, allowed paths, per-Spec target branch, and `dependency_ids`. Keep one branch shared only inside each Feature Spec and require exactly one Spec owner for every implementation-bundle `(repository, target_branch_name)` pair. Keep goal, requirements, acceptance, and validation authoritative in their normal sections; do not repeat option, delivery, or handoff projections. (Codex learning)
- Treat Plan Feature `allowed_paths` as the smallest complete and reasonably predictable execution envelope, not the shortest guessed file list: prefer stable directory or subsystem prefixes, include foreseeable feature-owned implementation, integration, validation, test, fixture, configuration, generated-contract input, and technical-documentation paths, and never under-scope merely to manufacture disjoint scheduling. Keep genuine single-file boundaries and local tracker active/done paths exact, exclude unrelated pre-existing failures, and require evidence before authorizing a repository-wide wildcard. Keep the canonical machine-readable rule table in `skills/plan-feature/references/spec-phase.md`. (Codex learning)
- Keep execution-time scope repair as a narrow internal `source_route=existing-source` branch, never a new Plan Feature option or top-level route. A separately invoked Plan Feature task may only expand `allowed_paths` monotonically for one durable Spec and implementation issue, must reread and revalidate the complete bundle, publish Spec then issue then append-only audit with fail-safe recovery, and return the exact portable repair result. It must never consume or emit worker/task/worktree/claim/generation identity. (Codex learning)
- In GitHub issue-tracker mode, keep the Feature Spec issue as the parent issue and attach generated implementation issues as sub-issues while preserving its durable ref only in each child's canonical `## Execution Contract` `source_spec_ref` row.
- In GitHub issue-tracker mode, title Feature Spec issues as `Feature Spec: <Feature Name>` and implementation issues as `<feature-slug>: <NN> <vertical outcome>`.
- Keep generated issue type/state in the owning tracker surface: consume the explicit Project Memory transport and exact value, using `native-type`, `label`, or `body-field` for GitHub types, `label` for GitHub workflow state, and `local-header` locally. Reject missing or incompatible transports. Revalidate native-type availability and exact values before publication, and create and verify only exact missing configured labels before dependent applied mutations; proposal mode reports label-creation intent only. Local applied issues use the two canonical header lines; proposal bodies carry no applied metadata while reporting the intended mapping separately. Never issue a native type mutation when types are disabled. (Codex learning)
- Feature Spec bodies should not carry workflow status fields such as `Status: Draft`; readiness and lifecycle state belong in tracker metadata, labels, or generated implementation issues.
- Local markdown implementation issue headings should use the same convention as GitHub implementation issue titles: `<feature-slug>: <NN> <vertical outcome>`.
- In GitHub issue-tracker mode, Feature Spec issues use the mapped `feature` transport and generated implementation sub-issues use the mapped `task` transport; use native Issue Types only when available, otherwise honor the configured fallback label or body convention.
- In multi-repository planning, every linked repo-owned Spec carries the same lowercase UUID `feature_id` and the exact same normalized `Feature Spec Set` table. The set has one globally qualified row per affected repository, including self, in deterministic repository order with a non-empty responsibility; no additional top-level Spec, coordination repository, saved-project inference, or incomplete set is valid.
- Keep every applied multi-repository source and dependency ref globally unambiguous: use `owner/repository#<number>` or a canonical hosted URL for GitHub and `<feature-id>--<repository-key>/planning/features/<feature-slug>/SPEC.md` for local Markdown. A linked member's lower-kebab `repository_key` is stable, unique inside the frozen set, at most 48 characters, and persisted in Planning Identity; the shared UUID makes the local qualifier globally unique. Propagate the same identity through every `Feature Spec Set`, Feature Dependency, and issue `source_spec_ref`; proposed refs use `proposed-spec:<feature-id>/<repository-key>` and never become executable. (Codex learning)
- Generated implementation issues may be `ready-for-agent` while listing unfinished dependencies; that means the issue is specified enough for the queue, but consumers must wait for dependencies to complete before starting it. Dependencies must be explicit, acyclic, and must not create retain cycles that lock the queue.
- Cross-Feature-Spec dependencies contain only the upstream durable ref and reason. Peer workers may start before upstream completion, but final dependent or combined proof binds the exact prerequisite delivery evidence and waits for merge only when the durable dependency contract explicitly requires merged input. Intra-Spec issues contain only forward `dependency_ids`; derive reverse edges instead of persisting `blocked_issue_ids` or a parallelization enum. (Codex learning)
- Generated issues include tracker-specific lifecycle prose without choosing delivery: GitHub issues update checkboxes and use a supported tracker transition selected by the executor, while local Markdown issues move to `issues/done/` after substantive proof. Local issue scope must include the tracker-owning Git repository plus the exact active and done paths, then rerun invalidated gates. If those paths do not resolve inside an affected Git repository, withhold the issue as non-executable. Do not persist a completion-method option. (Codex learning)
- The `plan-feature` issue phase owns any issue tracker or local markdown writes
  it performs; `$plan-harder` remains output-only and must not write plan files
  or issue files.
- Generated implementation issues should include one standard plan-hardening provenance line under `## Implementation Plan` for the final stable `$plan-harder` pass; merge that final result into the appropriate issue sections instead of pasting it wholesale.
- Never persist `knowledge_delta` or `## Domain Knowledge Handoff` in a Feature Spec. Carry accepted durable decisions as run/phase data and persist repository-owned target shards only on final closeout issues, then require `$project-memory domain-memory` after integrated behavior is proven. Every target surface must be contained by its owner issue's sole Git repository and allowed paths. A cross-repository decision names one canonical `<feature-id>--<repository-key>/<repo-relative-path>` target whose prefix resolves to the declared owning Feature Spec Set member; peer repositories may carry only repo-local context changes and backlinks that copy that exact target, never duplicate canonical records. On the existing-source route, reject explicit knowledge data outside the authorized repository/path scope instead of widening it. In a multi-repository bundle, each combined boundary belongs to an existing linked Spec whose Feature Dependencies identify the exact peer inputs; never create a dedicated integration Spec, issue subtree, branch, or worker. Keep issue dependencies intra-Spec. (Codex learning)
- Both `plan-feature` phases should read each selected repository's `project-memory/config/issue-tracker.md`, tracker mappings, and applicable context before deciding where its Feature Spec or issues belong.

### Maintainer Skill

- Keep `maintainer` manual-only in Codex metadata with `policy.allow_implicit_invocation: false`; ordinary skill, plugin, metadata, docs, or repository change requests must not auto-select it. Use it only when the user invokes `$maintainer`, asks to run Maintainer, or an explicitly invoked parent workflow routes there. (Codex learning)
- The `.agents/skills/maintainer` skill is the explicit maintainer for auditing health and improving existing skills and plugins in this repository through shared upgrade tasks and skill-specific refresh workflows.
- `maintainer` is the only maintainer skill that should orchestrate upgrades, metadata sync, reference refresh, and other repository maintenance for existing skills and plugins in this repository.
- Keep `maintainer` self-contained: workflow markdown guidance must live under `.agents/skills/maintainer/references/`.
- Keep the dependency direction one-way: runtime skills must not depend on, reference, or route users to `.agents/skills/maintainer`; only repo-level maintainer docs may define explicit `$maintainer` routes.
- When `$maintainer` is explicitly invoked to update skill or plugin metadata/docs across the repo, route through its playbooks and keep README/openai metadata text aligned. Without explicit invocation, apply the same repository invariants directly without loading the maintainer workflow.
- Keep instruction-density reviews proposal-first: identify lower-instruction equivalents, then wait for explicit approval before compaction refactors.
- For brand-new skill creation, use `$skill-creator` first. Use `$maintainer` afterward for repo integration or follow-up maintenance only when the user explicitly invokes it or an explicitly invoked parent workflow routes there; otherwise apply the repository integration rules directly. (Codex learning)
- Keep Codex-dependency audits and TanStack Intent coverage refresh as explicit maintainer-owned maintenance tracks; do not spread those maintenance workflows into runtime skills. (Codex learning)
- Keep TanStack skills coverage alignment against `tanstack-skills/tanstack-skills/plugins` as an explicit maintainer-owned maintenance track; map upstream product plugins into the single reusable `skills/tanstack/` skill and verify product guidance against TanStack-owned docs. (Codex learning)
- During Codex dependency audits, require Codex-dependent skills to name their required Codex tools or runtime contracts precisely, and require portable skills to keep Codex-only helpers optional with a generic fallback.
- During an explicit `$maintainer` run, use `$skill-audit` read-only and conditionally for deeper health diagnosis or workflow-family hardening when portfolio, prompt-quality, overlap, or runtime evidence is required; let `$maintainer` own approved contract changes and regression coverage. Without explicit invocation, apply approved fixes and regression coverage directly to the targeted packages.
- Route substantial skill/plugin merges, removals, public invocation changes, and standalone-to-plugin moves through `$skill-creator` or `$plugin-creator` first. Return to `$maintainer` for lifecycle cleanup, metadata, validation, and release checks only when it was explicitly invoked or an explicitly invoked parent workflow routed there; otherwise apply those repository invariants directly.
- Select maintainer validation by change type. Plugin and CLI maintenance must verify shipped artifacts and installed/cache state; composed-workflow changes require focused contract tests and bounded scenario proof when risk justifies it.

### Codex Changelog Skill

- Keep `codex-changelog` as a Codex-dependent reusable skill under `skills/codex-changelog/`; release-source selection and output formatting belong in its own `SKILL.md` and references, not in this `AGENTS.md`.

### Code Wiki Skill

- Keep `code-wiki` as a Codex-dependent reusable skill under `skills/code-wiki/`; runtime repo-study workflow, HTML contract, and image rules belong in `skills/code-wiki/SKILL.md` and its references, not in this `AGENTS.md`.
- Keep `code-wiki` final wiki outputs outside `.cache`; default git clones and temporary analysis artifacts belong under `~/.cache/dotagents/skills/code-wiki/`, while user-requested self-contained source storage belongs under `<wiki-root>/.cache/sources/` with an ignore-all `.gitignore`. (Codex learning)

### Skill CLI Creator Skill

- Route embedded-CLI design and layout work through `$skill-cli-creator`; keep detailed host, execution, and configuration doctrine in `skills/skill-cli-creator/SKILL.md` and its references.
- Repo-level embedded-CLI invariants are: shipped artifacts live under `scripts/`, maintenance-only implementations live under `projects/<tool>/`, and ownership stays aligned when a CLI is skill-owned, plugin-shared, or owned by one bundled plugin skill. (Codex learning)
- Use direct `scripts/<tool>` implementations for simple single-file CLIs; reserve `projects/<tool>/` for real multi-file, compiled, generated, dependency-managed, or build-backed CLI implementations. (Codex learning)
- Multi-OS compiled CLIs keep the stable executable surface at `scripts/<tool>` and place platform binaries under `scripts/bin/<tool>-<os>-<arch>`; use `projects/<tool>/scripts/` for build/install helpers when needed. (Codex learning)
- Persist embedded-CLI config in owner-aligned `config.toml` files under `<project-root>/.skills/...` or `<project-root>/.plugins/...`, and treat those directories as config-only. (Codex learning)
- Require the shipped artifact to expose `--version` with one semver source of truth, and if `projects/<tool>/` exists require `projects/<tool>/AGENTS.md` plus a scoped `projects/<tool>/.gitignore` when generated state exists. (Codex learning)
- Keep embedded-CLI docs artifact-first: examples must run `<artifact-path> ...`, `<resolved-tool> ...`, or an absolute installed artifact path unless the host explicitly documents a wrapper, alias, or `PATH` contract for bare `<tool> ...`. (Codex learning)

### GitStack Plugin

- Keep GitStack as the sole repo-owned package for local Git and GitHub runtime workflows; do not maintain duplicate standalone `git-commit`, `github-*`, or `submit` packages.
- Keep GitStack runtime self-contained: it must not locate, import, or execute another skill for authorization or state. Composing workflows may validate their own lifecycle state before invoking GitStack, while GitStack owns its exact operation start journal, provider transport, one-use markers, and reconciliation evidence. (Codex learning)
- Keep bundled skills provider-primitive and workflow-agnostic: caller-specific planning, orchestration, project-memory, queue-state, issue-body, and label-taxonomy policy belongs in the composing skill.
- Prefer the official GitHub connector for supported remote operations, authenticated `gh` for connector gaps or same-target fallback, and direct `git` for local repository state and mutation.
- Keep the plugin-shared runtime artifact at `plugins/gitstack/scripts/gitstack`, its maintenance source at `plugins/gitstack/projects/gitstack/`, and its plugin and CLI semantic versions aligned.
- Keep GitHub issue lifecycle mechanics in `$gitstack:github-issues`, review-thread mechanics in `$gitstack:github-review-threads`, and stars/list mechanics in `$gitstack:github-stars`.
- Keep GitStack's shared invocation registry limited to caller inputs. Derived provider states and review judgments belong to their owning result contracts. Omit mutation mode for pure reads; use it only to choose apply versus preview for a write-shaped GitHub operation.
- Keep `$gitstack:github-repository-triage` read-only and responsible for detailed single-repository queue grouping plus comparative scans of multiple explicit repositories. Route evidence-backed issue disposition to `$gitstack:github-investigation` and all issue lifecycle mutations to `$gitstack:github-issues`.
- Keep `$gitstack:submit` as publish orchestration over `$gitstack:git-commit` and focused GitStack GitHub workflows rather than duplicating their behavior.

### Implement Feature Skill

- Keep `implement-feature` as the single ChatGPT App, Codex-mode-only reusable orchestration entrypoint under `skills/implement-feature/`; do not add a terminal-session orchestration sibling or alternate worker surface.
- Keep availability and listing requests on the tracker-only `discovery-only` route before startup references are loaded. Discovery reports candidates with execution eligibility explicitly unverified and never creates run state, claims, tasks, worktrees, or tracker changes; only an explicit start, implement, or resume directive enters execution preflight. (Codex learning)
- Keep `skills/implement-feature/references/options.md` limited to `visible_app_task_permission`, GitHub-conditional `scope_repair_task_permission`, and conditional `missing_project_action`. An explicit `$implement-feature` execution request resolves worker-task permission as `granted` without another confirmation unless the user explicitly denies it; keep scope-repair and missing-project authority in the existing startup interaction. The project field exists only when a required repository is not already a saved Git project and uses canonical values `create-projects` and `stop`. Every other behavior is a fixed invariant, execution-bundle datum, or derived runtime observation. (Codex learning)
- Keep `implement-feature` manual-only in Codex metadata with `policy.allow_implicit_invocation: false`; ordinary implementation, planning, triage, GitHub, commit, PR, or multi-repo requests must not auto-select it. (Codex learning)
- The root coordinates visible Codex task scheduling, its unfinished run, Feature Spec claims, crash-safe task-operation reconciliation, coarse status, and read-only final verification; one worker per implementation-eligible Feature Spec owns implementation through delivery-ready evidence end to end. Record the current controller task's exact local saved Git-project binding as `controller_project_id`; that fixed task binding, not the mutable UI primary selection, is control-plane identity and never expands feature scope or grants root implementation. While runnable workers remain nonterminal, root keeps the current turn open with bounded task waits. An unexpected interruption resumes manually in the same root task; never create a replacement root or persist a synthetic lifecycle. Root never edits or judges tracker criteria. Multi-repository workers receive exact peer task and checkout identities, communicate directly, and assign combined proof to existing workers; no dedicated integration worker exists. Each worker stays isolated to its own worktree, starts and cleans up its own component, and supplies exact pre/post HEAD plus endpoint evidence to the peer that owns combined proof. Cross-worktree access is forbidden. Monorepos normally integrate inside one worker/worktree. (Codex learning)
- Keep `skills/implement-feature/scripts/run-state` as the sole stateful helper. Version its CLI, runtime contract, and named JSON protocols independently with SemVer; keep the SQLite database schema as a separate monotonically increasing integer. The current runtime line is CLI `4.2.0`, runtime contract `5.0.0`, CLI-envelope and run-manifest protocols `3.0.0`, Feature Spec Set input and scope-repair observation protocols `1.0.0`, app-operation observation `2.1.0`, the remaining named JSON protocols `2.0.0`, and database schema `4`. Protocol payloads must carry exact `schema` and `schema_version` fields, reject aliases and unknown keys, and take a major protocol bump for incompatible key, type, or enum changes. Keep `scripts/verify-ready` read-only and outside run-state persistence. (Codex learning)
- All controllers for one user share the permanently unversioned `~/.cache/dotagents/skills/implement-feature/run-state.sqlite3`; the single-row application-owned `runtime_metadata` table is the sole database-schema and cutover-fence source of truth. Never use `PRAGMA user_version`, an external lock file, migrations, data-copy upgrades, importers, compatibility state files, or versioned DB filenames. Every run pins the exact runtime contract, CLI version, and shipped artifact SHA-256, and only that exact runtime may mutate it. Any future database-schema or SQLite-shape change is a breaking hard cut and requires explicit user consent before implementation. (Codex learning)
- For a consented schema cut, set `runtime_metadata.target_schema_version` transactionally while the old schema remains usable, reject new starts, and let existing owners drain only through retained executables that exactly match every distinct persisted runtime pin; fail closed if any executable is unavailable or unprovable. Schema `1` predates runtime pins, so active schema-1 owners must drain before schema `4`; schemas `2` and `3` may contain owners pinned to different runtime/CLI identities, and every exact executable is required behind the schema-4 fence. A drained recognized database may be recreated directly. After zero owners, use one exclusive SQLite transaction to recheck zero, drop every application table/index/trigger, recreate the complete fresh schema and singleton metadata row, and commit without carrying any row forward. SQLite rollback must restore the complete old schema on failure. Older runtimes must fail closed on newer schemas; unknown, unversioned, corrupt, and same-number-invalid databases must also fail closed without reset. Keep the executable cutover procedure in `skills/implement-feature/references/run-state.md`. (Codex learning)
- Treat every Codex task mutation as one generated logical `operation_id`. For bootstrap authority, derive and propagate one stable `bootstrap_id`, require worker-side deduplication, and replay only the same reconciled bootstrap identity after authoritative readback; this guarantees an exactly-once effect, not exactly-once delivery. Scope revision similarly preserves one repair ID, derived revision ID, and target contract generation across replay. Persist canonical `review_owner=worker|root` atomically on the bootstrap operation and permit at most one reconciled worker-to-root `set-review-owner` reroute, never a reversal or duplicate logical owner effect. Each authorized launch carries a monotonic `launch_count`; reject observations from stale generations, and allow protected non-bootstrap replay only after authoritative failed readback proves no effect, except deduplicated scope revision may replay after authoritative unknown or failed readback. Keep observation templates as descriptors and observation builders as pure, strict, no-overwrite artifact writers; only the corresponding finish or ready command may mutate run state. (Codex learning)
- Keep state limited to runs, normalized per-run repository-to-project bindings, assignments, validated linked `feature_id` membership, canonical Feature Spec claims, delivery type, contract generation, opaque scope repair identity/readback, normal Git head/base facts, and typed Codex task-operation reconciliation facts; PR/provider refs exist only for GitHub delivery. Each affected repository maps to one distinct local saved Git project, assignments inherit that mapping, and a saved project may not stand in for multiple repositories in one run. Validate complete ephemeral linked member bodies before state, then persist only the validator-produced UUID membership: do not persist raw Spec/issue bodies, requested or allowed paths, normalized Feature Spec Set tables, responsibility or criterion text, checklists, issue phases, validation attempts, process/port state, worker technical/domain state, generic request/result payloads, or text hashes. Reject stale same-number DB structure exactly. (Codex learning)
- Keep tracker and delivery independent: Project Memory owns only `tracker_backend`; Plan Feature renders stable `delivery_type`; Implement Feature validates source refs from tracker transport and terminal evidence from delivery transport. Support GitHub+PR, local+local branch, and local+PR, including local Markdown/local branch in a GitHub-identified repository. (Codex learning)
- Preserve the core runtime boundaries: one startup authorization interaction, exact one-to-one local saved Git-project preflight for every affected repository before state, explicit and separate authority for any missing-project creation, path- and dependency-safe scheduling without a fixed numeric worker cap, per-assignment Spec/head-branch claims, crash-safe Codex task changes, evidence-only root follow-ups, worker-owned repair, review execution owned only by the persisted canonical `review_owner=worker|root`, and declarative durable-drift blocking. On one implementation-time path miss, retain the same worker/task/worktree/bootstrap and claim, delegate only the portable monotonic scope mutation to a separate Plan Feature task, recompute whole-envelope overlap without file claims, and let root deliver generation `N+1`; a second miss requires full replanning. Automate this only for GitHub-backed planning until local artifact propagation has an explicit safe transport. Remote, non-Git, broad parent, duplicate, or ambiguous saved projects never substitute for an exact affected-repository project. Keep executable detail only in `skills/implement-feature/SKILL.md` and its references. (Codex learning)
- Terminal results are PR-ready-for-merge-but-not-merged or local-branch-ready; merge and post-merge work remain outside this skill.

### Learn Skill

- Keep `learn` as the repo-facing persistence surface for durable `AGENTS.md` updates in this repository; broader memory-system files are outside this repo's editable scope.
- When durable learnings are added through `learn`, place them in the most appropriate existing section when possible, otherwise create a fitting section; use `## Codex Learnings` only as a fallback, and suffix each inserted bullet with ` (Codex learning)`.
- When the user says a rule is a "hard rule" or otherwise uses durable language and the correct persistence target is unclear, ask where to save it and recommend an `AGENTS.md` target by default. (Codex learning)

### Code Review Rules Skill

- Keep `code-review-rules` manual-only and proposal-first: it may inspect repository and bounded Codex historical evidence, but previous sessions are candidate evidence rather than authority and it must not auto-select itself for ordinary reviews or `AGENTS.md` maintenance.
- Keep `$learn` as the sole writer and confirmation owner for Code Review Rule changes. `code-review-rules` owns discovery, scoping, evidence filtering, the violation/safe/unrelated/ordinary-bug evaluation matrix, and exact proposal rendering; it passes the unchanged target and wording to `$learn`, which shows them, pauses once for approval, and performs the approved write without a duplicate confirmation.
- Do not bootstrap generic or empty review guidance by default. Create a missing `AGENTS.md` only for at least one approved evidence-backed rule, and prefer the closest applicable nested file over broad root rules.

### Skill Audit Skill

- Keep `skill-audit` as the single audit surface for installed Codex surfaces: standalone skills, plugin packages, and bundled plugin skills.
- Keep `skill-audit` implementation centered on local discovery surfaces first, with shared or cached installations used as verification surfaces rather than editable sources. (Codex learning)
- Keep portfolio-level duplicate, unused, prompt-budget, and root-summary analysis inside `skill-audit` rather than a separate cleanup skill; `scripts/portfolio-health` is audit evidence, not an automatic deletion workflow.
- When auditing a bundled plugin skill, require `skill-audit` to inspect both the bundled skill contract and the owning plugin package, including `.codex-plugin/plugin.json` when available. (Codex learning)
- Treat Codex plugin cache copies under `~/.codex/plugins/cache/...` as verification only; do not route fixes or edits to cache paths. (Codex learning)
- When a named target path lives under `~/.codex/plugins/cache/...`, require `skill-audit` to resolve plugin identity first, then use visible workspace plugin discovery surfaces such as `.agents/plugins/marketplace.json` and the owning `.codex-plugin/plugin.json` to confirm the editable source when possible; if no workspace mapping is visible, report that the editable source was not confirmed. (Codex learning)
- When plugin-package issues are actually bundled-skill issues, prefer recommending the narrowest owning surface: bundled plugin skill, plugin package, repo docs, or `Maintainer`.
- Keep live `skill-audit` monitoring observational: bind findings to the exact runtime contract and authoritative App task evidence, never steer monitored tasks, and treat unavailable current evidence as a monitor limitation rather than inferred progress or a defect. (Codex learning)
- Keep the `skill-audit` workflow as one documented DAG rather than an execution engine: `SKILL.md` owns canonical order, target-kind references are overlays, historical and live evidence have separate owners, and optional portfolio or writing lenses never reorder the core flow. Its shipped `portfolio-health` and `session-evidence` v1 CLIs are independent leaf helpers with hard-cut interfaces and a shared `{ok, version, command, data}` JSON envelope. (Codex learning)
