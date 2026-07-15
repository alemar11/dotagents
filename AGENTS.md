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
- Keep behavior-affecting option contracts canonical across this repository: use `snake_case` field names and lower-kebab assigned values. Natural-language phrases may explain an option but must not be its value; resolve prose directly to canonical values and emit and persist only canonical values. Outside `skills/postgres/`, runtime skills must reject noncanonical fields and values instead of accepting aliases, mapping retired syntax, or providing compatibility migrations. Keep an option value separate from associated prose, data, or references. Factual booleans and externally owned syntax are exempt. (Codex learning)
- Build skill content through progressive disclosure: keep selection-critical metadata plus core routing and load-bearing workflow-order, safety/mutation, and output contracts in `SKILL.md`; give each behavior-affecting contract or field registry one canonical owner; move branch-specific detail behind directly linked references with explicit read conditions whose predicates are decidable from already-loaded content or the target artifact; and cross-reference instead of repeating canonical field lists or detailed prose. (Codex learning)
- Measure compaction against always-loaded metadata and representative invoked paths (`SKILL.md` plus every reference required by that path), not total repository lines or text moved between files on the same path. Preserve trigger, workflow-order, safety, mutation, and output semantics with focused contract tests, and forward-test representative paths when static checks cannot prove equivalence. (Codex learning)
- In `references/` folders, keep `.md` filenames lowercase except for `README.md` and `AGENTS.md`.
- If `brand_color` isn’t provided, pick a random hex color not already used by other skills in this repo and set it in `agents/openai.yaml`.
- Plugin manifests must keep asset and bundled-skill paths repo-relative and valid from the plugin root; update them together with any plugin layout move. (Codex learning)
- Bundled plugin skills must follow the same runtime/maintenance split as reusable skills under `skills/`: runtime guidance stays in their `SKILL.md`, while repo-maintenance routing stays in repo-level maintainer docs. (Codex learning)
- Runtime skills must stay unaware of `.agents/skills/maintainer`: do not reference it, its runbooks, or maintainer-routing instructions from runtime `SKILL.md` files or runtime usage references. Keep that routing only in repo-level maintainer docs such as this `AGENTS.md`.
- Runtime skills may surface runtime learnings or durable guidance candidates, but they must not perform self-upgrade, metadata-sync, reference-refresh, or other repo-maintenance workflows from their own runtime instructions.
- Keep skill-maintenance and repo-maintenance workflows owned by `.agents/skills/maintainer` in repo-level maintainer docs, but invoke `$maintainer` only when the user selects it explicitly; ordinary change requests follow this `AGENTS.md` and the targeted package directly.
- Keep the repo-level source of truth for skill portability in this `AGENTS.md`: record which skills are Codex-dependent vs portable when that boundary matters for maintenance or runtime behavior.
- Codex-dependent skills must explicitly name the Codex runtime tools, artifacts, or filesystem contracts they require in `SKILL.md`; skills intended to stay portable may mention Codex-only helpers only as optional accelerators with a generic fallback.
- Scope per-user cache files under `~/.cache/dotagents/` by owner: reusable skills use `~/.cache/dotagents/skills/<skill-name>/...`, plugin-shared caches use `~/.cache/dotagents/plugins/<plugin-name>/...`, and plugin-bundled skill caches use `~/.cache/dotagents/plugins/<plugin-name>/skills/<skill-name>/...`. (Codex learning)

### Codex Dependency Classification
- In this section, `portable` means "not dependent on Codex-only runtime features"; it does not necessarily mean the skill is repository-agnostic or broadly reusable unchanged.
- Current Codex-dependent skills are `autoreview`, `codex-changelog`, `code-wiki`, `learn`, `maintainer`, `codex-orchestrator`, and `skill-audit`.
- Treat `autoreview` as Codex-dependent because its runtime contract shells through local `git` and Codex CLI `exec` with structured output flags (`--output-schema`, `--output-last-message`) and read-only review execution.
- Treat `code-wiki` as Codex-dependent because its runtime contract requires Codex subagents for parallel repo study when available, `$imagegen` for selected raster wiki visuals, and `~/.cache/dotagents/skills/code-wiki/` as its disposable clone/analysis cache.
- Treat `codex-orchestrator` as Codex-dependent because its runtime contract requires Codex CLI subagent tools, Codex App task tools for explicitly permitted visible workers, Codex Goal mode when available with a ledger fallback when unavailable, Codex GitHub code review requests for the default authorized merge-ready pull-request closeout path (with an exact authorized-user-scoped skip option), ledger-driven progress monitoring, scheduled ledger checks when authorized and runtime-supported, `~/.cache/dotagents/skills/codex-orchestrator/ledgers/`, `$autoreview`, `$plan-feature` for feature planning or existing Feature Spec issue generation before implementation scheduling, and GitStack bundled skills for Git and GitHub workflows.
- Treat `.agents/skills/maintainer` as Codex-dependent because workflow-family hardening uses `$skill-audit` plus Codex memory/session evidence for portfolio or runtime invocation claims, substantial reshapes require `$skill-creator` or `$plugin-creator`, and non-trivial implementation closeout requires `$autoreview`.
- Treat `crusty` as Codex-aware but portable because direct-only invocation policy and optional subagents are Codex-aware, while its core challenge workflow can run sequentially with generic web/search fallback.
- Treat `plan-harder` as Codex-aware but portable because Codex-only helpers such as `request_user_input` or subagents are optional and have a non-Codex fallback path.
- Treat `grill-me` as Codex-aware but portable because structured question helpers such as `request_user_input` are optional; its fallback is plain one-question-at-a-time dialogue.
- Treat `grill-me-with-context` as portable and skill-composed because it requires `$grill-me` and `$project-memory`, both portable, and otherwise relies on local repo/docs inspection.
- Treat `improve-codebase-architecture` as Codex-aware but portable because optional subagents can speed read-only repo exploration, while sequential source inspection plus `$grill-me-with-context` is the fallback path.
- Treat `project-memory` as Codex-aware but portable because optional session-history bootstrap is isolated in `skills/project-memory/references/session-history.md`, while its core setup and internal domain-modeling flow fall back to repo/workspace evidence plus optional localization evidence.
- Treat `plan-feature` as portable and skill-composed because its core and local-tracker workflows require `$project-memory`, `$grill-me-with-context`, and `$plan-harder`; its GitHub tracker backend additionally requires `$gitstack:github-issues`.
- Treat `triage` as portable and skill-composed because its core and local-tracker workflows rely on project-memory mappings, `$grill-me-with-context`, and `$plan-harder`; its GitHub tracker backend additionally requires `$gitstack:github-issues`.
- Treat `skill-cli-creator` as Codex-aware but portable because it may route to Codex scaffold helpers when available, but its embedded-CLI design workflow can continue with an equivalent manually created skill or plugin host.
- Treat GitStack as Codex-dependent because its bundled workflows require the official GitHub connector. Its shared CLI fallback remains runtime-dependent on Python 3.11+, local `git`, and authenticated `gh`.
- Treat `okf` as portable runtime-dependent because it requires `python3` for its shipped `scripts/okf` CLI, uses optional `PyYAML` when available for exact YAML parsing, and otherwise relies on local markdown/spec assets without Codex-only runtime tools.
- Treat `tanstack` as portable because it is guidance-only, relies on local repo/package inspection plus current TanStack-owned docs when exact APIs matter, and does not require Codex-only runtime tools.
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

### OKF skill
- Keep OKF runtime guidance in `skills/okf/SKILL.md`, `skills/okf/references/*`, and the shipped `skills/okf/scripts/okf` CLI.
- Keep official OKF spec refresh mechanics in `.agents/skills/maintainer`, using `.agents/skills/maintainer/references/okf-spec-runbook.md` as the canonical procedure.
- Runtime OKF docs must not reference `.agents/skills/maintainer`, maintainer scripts, or maintainer-only routing.

### Swift-DocC skill
- Keep Swift-DocC bundled-asset refresh and reference integrity checks in `.agents/skills/maintainer`, and use `.agents/skills/maintainer/references/swift-docc-runbook.md` as the canonical procedure.
- Keep runtime Swift-DocC docs and fast-path reference design in `skills/swift-docc/`; keep maintainer-only refresh routing here. (Codex learning)

### Swift API Design skill
- Keep Swift API Design bundled-asset refresh and reference integrity checks in `.agents/skills/maintainer`, and use `.agents/skills/maintainer/references/swift-api-design-runbook.md` as the canonical procedure.
- Keep runtime Swift API Design docs and bundled-source usage details in `skills/swift-api-design/`; keep maintainer-only refresh routing here.
- Refresh `swift-api-design` from `swiftlang/swift-org-website/documentation/api-design-guidelines/index.md` until the live Swift.org page demonstrably migrates to a different substantive source. (Codex learning)

### Plan Harder skill
- Keep `plan-harder` as the single reusable home for higher-rigor planning support in this repo; do not reintroduce a separate lightweight clarification skill unless that package boundary is intentionally restored. (Codex learning)
- Keep `plan-harder` runtime workflow, clarification behavior, and output details in `skills/plan-harder/SKILL.md` and its references, not in this `AGENTS.md`.
- Keep `plan-harder` output-only: its standalone surface returns chat output and
  its issue-hardening caller surface returns a structured result to the
  invoking workflow. It must not create `plans/`, write Markdown plan files, or
  edit repo files as part of its own runtime workflow.

### Grill and Project Memory composition
- Keep `grill-me` as the generic stateless pressure-testing loop; repo-backed documentation capture belongs in `grill-me-with-context`.
- Keep `grill-me-with-context` as the thin composition layer over `grill-me` and `$project-memory domain-memory`, not a duplicate questioning or domain-capture loop.
- Keep `improve-codebase-architecture` as architecture discovery and candidate selection first; it should hand the selected candidate to `grill-me-with-context` before implementation rather than duplicating the documentation loop.
- Use `project-memory/` as the visible root for durable project memory owned by these runtime skills: `project-memory/config/` for repo-specific agent operating config and `project-memory/adr/` for durable decision records. Keep `CONTEXT.md` and optional `CONTEXT-MAP.md` at the project root for fast discovery.

### Project Memory skill
- Keep `project-memory` as the normal public lifecycle surface for creating or refreshing `AGENTS.md` pointers plus `project-memory/config/issue-tracker.md`, `project-memory/config/project-layout.md`, `project-memory/config/triage-labels.md`, `project-memory/config/domain.md`, root or context-specific `CONTEXT.md`, optional `TRANSLATION.md`, and ADR routing or content in code repos, monorepos, and orchestrator workspaces.
- For implementation closeout that carries accepted durable decisions, require the implementor to invoke `$project-memory domain-memory`; Project Memory must run its internal domain-modeling workflow, reconcile the carried delta against behavior that actually landed, update only the named durable surfaces, and verify the documentation diff. `$plan-feature` assigns this work but must not perform it during planning. (Codex learning)
- `project-memory` must always use `AGENTS.md` for setup pointers and project-memory routing when an agent-instruction file is needed.
- Keep `project-memory` pointer-first for `AGENTS.md`: agent operating rules and short project-memory links stay there, while domain context, tracker detail, planning history, and accepted decisions move to `CONTEXT.md`, `project-memory/config/*`, or ADRs after confirmation.
- Keep `project-memory` issue-tracker setup limited to the durable `tracker_backend` values `github` and `local`; workspace, repo, path, and cross-repo linking details belong in conventions, Feature Specs, generated issues, or prose, not as extra backend enum values.
- Keep `project-memory/config/triage-labels.md` responsible for both issue type/category mapping (`bug`, `feature`, `task`) and workflow state mapping (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`).
- For already-used projects, `project-memory` may seed `CONTEXT.md` and `project-memory/adr/` from strong repo evidence and recent same-repo session history, using its internal domain-modeling workflow for context and ADR content.
- Keep `TRANSLATION.md` optional and evidence-backed: create it only when localization support or durable translation rules are clear from repo evidence or explicit user confirmation, and add an `AGENTS.md` localization pointer only when the file exists or is confirmed.
- Keep `CONTEXT.md` to `TRANSLATION.md` links optional: add a one-line pointer only when localization affects audience, domain terms, product naming, or user-facing copy, and never create broken pointers.
- Do not add schema versions to `project-memory` generated Markdown files or templates unless a concrete parser or migration workflow requires versioning.
- Keep orchestration runtime policy out of project-memory setup files. `$codex-orchestrator` invocation authorizes background Codex subagents for the root and its spawned Codex threads; visible App tasks require `visible_app_task_permission=granted-by-authorized-user`. That grant selects mandatory one-visible-thread-per-Feature-Spec execution, with count derived from eligible Specs; the orchestrator still derives recursive subagent topology, parallelism, and sequencing. Do not store durable dispatch flags, worker-count preferences, visible-task limits, authorization ceilings, scheduled check timing, publication policy, or issue mutation policy as project-memory config.
- Persist repository topology only in `project-memory/config/project-layout.md` with canonical `repository_layout` values `single-repository`, `monorepo`, and `multi-repository-workspace`. Do not store source-root inventories, worktree paths, Codex App worker policy, thread limits, current-run dispatch state, or publication and issue-mutation authority in project-layout config.
- Keep behavior-affecting project-memory setup files human-first but table-first: use typed configuration tables for keys that control tracker backend, delivery target, issue types, triage states, or closeout, and leave prose for rationale and conventions.
- Keep setup conservative: it configures locations and mappings for fresh projects, and only bootstraps domain memory for existing projects when the evidence is accepted, load-bearing, and not merely tentative session discussion.
- In orchestrator workspace mode, keep setup config-only: configure `AGENTS.md`, `project-memory/config/*`, root `CONTEXT.md`, and ADR layout, but do not create `orchestration/<project>/` or `features/<feature>/` folders until `$plan-feature` writes a real feature. Config-only means "no project or feature artifacts during setup," not "only `project-memory/config/*`."
- Orchestrator workspace memory coordinates cross-repo planning only; child repos keep their own `AGENTS.md`, `CONTEXT.md`, optional `TRANSLATION.md`, `project-memory`, validation, branches, commits, and PRs.
- Fresh setup may apply to non-empty starter repos when only tracker, triage, and domain-memory routing is needed; existing-project bootstrap is for seeding or reconciling accepted domain memory from strong evidence.
- For temp, rehearsal, dry-run, or other non-mutating setup runs, do not let a GitHub remote force GitHub issue mutation; use local markdown or return draft GitHub commands instead.

### Plan Feature skill
- Keep `plan-feature` as the single public planning surface for full feature planning, spec-only drafting, and existing Feature Spec issue generation; keep dense Feature Spec writing and issue splitting guidance in its internal `references/` phase files.
- Keep `skills/plan-feature/references/options.md` as the owner of Plan Feature's concrete option registry and apply the repository-wide canonical option contract there. (Codex learning)
- Keep `plan-feature` manual-only in Codex metadata with `policy.allow_implicit_invocation: false`; ordinary feature, planning, Feature Spec, issue splitting, implementation, or triage requests must not auto-select it. (Codex learning)
- Keep Feature Spec vocabulary as a hard runtime cut with no read aliases for retired planning names, fields, modes, paths, or authority values. Active orchestrator ledgers and hosted or local issue bodies must already use the canonical Feature Spec contract before the runtime consumes them; do not switch runtimes until a stale-vocabulary scan is clean. (Codex learning)
- `plan-feature` may run its Feature Spec phase and issue phase only after setup exists and no blocking gates remain; when `effective_target=configured-tracker`, treat `tracker_backend` as the planning-artifact write authority: `github` publishes Feature Spec/issues to GitHub and `local` writes local Markdown files. Other effective-target values are non-mutating. (Codex learning)
- In monorepo or multi-context planning, carry the accepted product slug, workspace path, context file, and authoritative feature slug through `plan-feature` and its internal phases; prefer explicit or path-derived slugs over title-derived slugs. (Codex learning)
- Keep the `plan-feature` Feature Spec phase focused on producing or publishing Feature Spec artifacts from clarified requirements; do not let it split implementation issues.
- Keep the `plan-feature` issue phase focused on splitting Feature Specs into vertical implementation issues; it must run `$plan-harder` once per issue and use the returned brief to enrich the issue body before returning or publishing that issue, without duplicating top-level sections.
- Feature Specs must include a `Change Delivery Target` section using canonical lower-kebab values. Default to `pull-request-ready-for-merge-but-not-merged`; commit-only, push-without-PR, and draft-PR targets require explicit authorization. For multi-repository PR delivery, every involved repo uses the same branch name and opens its own PR. (Codex learning)
- In GitHub tracker backend mode, hosted issues are authoritative; do not persist repo-local `planning/tmp/` or `project-memory/features/` mirrors just to feed `gh --body-file`. Use temporary files outside the repo and remove them unless `effective_target=configured-tracker`, `local_mirror=requested`, and a safe repo-relative `local_mirror_path` are all resolved. (Codex learning)
- Keep repo-local planning artifacts under one container and one feature subtree: durable local Feature Specs live under `planning/features/<feature>/SPEC.md`, durable local implementation issues live under `planning/features/<feature>/issues/`, and temporary dry-run, rehearsal, transport, fingerprint, and comparison artifacts live under `planning/tmp/<feature>/` and must be safe to delete. Multi-repo workspace parent coordination uses the same feature-centric shape under `orchestration/<project>/features/<feature>/`. (Codex learning)
- Generated implementation issues are the durable execution graph by default; do not create a separate hosted issue, local file, Feature Spec section, or inline scheduling artifact. If a user asks for a summary, return it as a non-authoritative view derived from the current issue bodies. (Codex learning)
- Generated implementation issues inherit the complete delivery target tuple from their `source_spec_ref`; issue bodies copy the effective `change_delivery_target`, `change_delivery_permission`, and `repository_layout`, then record parallelization, dependency ids, closeout, and only issue-level delivery exceptions so orchestrator workers do not invent branch or PR strategy. (Codex learning)
- In GitHub issue-tracker mode, keep the Feature Spec issue as the parent issue and attach generated implementation issues as sub-issues while preserving `source_spec_ref: #<number>` in each child issue body.
- In GitHub issue-tracker mode, title Feature Spec issues as `Feature Spec: <Feature Name>` and implementation issues as `<feature-slug>: <NN> <vertical outcome>`.
- Feature Spec bodies should not carry workflow status fields such as `Status: Draft`; readiness and lifecycle state belong in tracker metadata, labels, or generated implementation issues.
- Local markdown implementation issue headings should use the same convention as GitHub implementation issue titles: `<feature-slug>: <NN> <vertical outcome>`.
- In GitHub issue-tracker mode, Feature Spec issues use the mapped `feature` issue type and generated implementation sub-issues use the mapped `task` issue type when GitHub issue types are available.
- In GitHub-backed multi-repo planning, related partial Feature Specs and implementation issues across repos must link to each other by URL or issue number; do not require a coordination repo or project label as durable setup configuration.
- Generated implementation issues may be `ready-for-agent` while listing unfinished dependencies; that means the issue is specified enough for the queue, but consumers must wait for dependencies to complete before starting it. Dependencies must be explicit, acyclic, and must not create retain cycles that lock the queue.
- Generated implementation issues must include a `## Completion` section: GitHub issues close through a closing keyword on the relevant PR by default, with final-commit closure allowed only as an explicitly authorized exception, while local markdown issues are moved into the configured `issues/done/` folder after validation rather than being deleted or marked with a `done` status. Create `issues/done/` on demand when moving the first completed issue. In orchestrator workspace mode, moving to `done` requires cross-repo integration proof.
- Keep final-commit GitHub issue closure separate from branch-publication permission: Plan Feature must resolve `issue_update_permission=direct-issue-updates-explicitly-authorized` from independently scoped evidence before emitting `issue_completion_method=final-commit-closing-keyword`; `changes-pushed-to-target-branch-without-pull-request` alone never grants issue closure. (Codex learning)
- For local Markdown issues with `change_delivery_target: local-commit-created-without-pushing`, treat the commit as delivery proof, then move the issue to `issues/done/`; hosted final-commit closure is not a local issue lifecycle signal.
- The `plan-feature` issue phase owns any issue tracker or local markdown writes
  it performs; `$plan-harder` remains output-only and must not write plan files
  or issue files.
- Generated implementation issues should include a standard plan-hardening provenance line under `## Implementation Plan` so one `$plan-harder` pass per issue is auditable; the rest of the `$plan-harder` output should be merged into the appropriate issue sections instead of pasted wholesale.
- Orchestrator implementation issues must include integration gates by name or link; repo PR placeholders may be `ready-for-agent` inputs before implementation, but completion requires real repo PR links or equivalent integration proof. (Codex learning)
- Orchestrator reports and ledgers must record worker evidence when delegation is used or attempted: `visible_app_task_permission`, `actual_execution_location`, worker/session id or failure evidence, nested subagent topology, fallback reason, and parallel/sequential/root-owned execution. With visible permission granted, also record the one-to-one Feature Spec ref/title to visible-thread mapping, thread-owned review polling, drift corrections, and the absence of root implementation/review fallback; otherwise worker surface and count remain orchestrator-derived. Recursive subagent topology, parallelism, and sequencing are never user-configured limits. (Codex learning)
- In local orchestrator mode, the `plan-feature` Feature Spec phase owns the Feature Spec and accepted project/repo/gate support files, while the issue phase owns issue files and never refreshes `PROJECT.md`, `repos/*.md`, or `integration-gates.md`; requested support-file changes must finish in the Feature Spec phase before the issue-phase handoff.
- Both `plan-feature` phases should read `project-memory/config/issue-tracker.md`, `project-memory/config/project-layout.md`, and related project memory before deciding where Feature Specs or issues belong.
- Keep `plan-feature` lean profiles internal and evidence-driven: they may narrow discovery and repeated output for clear `spec-only` runs or small runs from an existing Feature Spec, but must not skip `$plan-harder`, verticality, graph, publication, or domain-closeout gates. Record exact phase-token deltas only for run-scoped uncontaminated counter intervals; label interleaved deltas as intervals or report `unavailable` without estimation. (Codex learning)

### Triage skill
- Keep `triage` focused on existing incoming GitHub or local markdown issues; new feature planning should still go through `plan-feature`.
- In GitHub mode, use GitHub Issue Type for work kind (`Bug`, `Feature`, `Task` by default) and labels for workflow state.
- In local markdown mode, persist `issue_type`, `workflow_state`, and
  `source_spec_ref`; reject noncanonical issue metadata instead of reading or
  rewriting aliases.
- Treat `needs-info` as a human/reporter waiting state, not an implementation queue state: reporter activity returns the issue to `needs-triage` for re-evaluation before it can become `ready-for-agent`.
- In local markdown mode, completed issues move to the configured `issues/done/` path instead of adding a new completed status; create the `done/` directory on demand when completing the first issue.
- Before marking an existing issue `ready-for-agent`, `triage` must harden that single issue through `$plan-harder` and preserve the resulting agent brief in the tracker.

### Maintainer skill
- Keep `maintainer` manual-only in Codex metadata with `policy.allow_implicit_invocation: false`; ordinary skill, plugin, metadata, docs, or repository change requests must not auto-select it. Use it only when the user invokes `$maintainer`, asks to run Maintainer, or an explicitly invoked parent workflow routes there. (Codex learning)
- The `.agents/skills/maintainer` skill is the explicit maintainer for improving existing skills and plugins in this repository through shared upgrade tasks and skill-specific refresh workflows.
- `maintainer` is the only maintainer skill that should orchestrate upgrades, metadata sync, reference refresh, and other repository maintenance for existing skills and plugins in this repository.
- Keep `maintainer` self-contained: workflow markdown guidance must live under `.agents/skills/maintainer/references/`.
- Keep the dependency direction one-way: runtime skills must not depend on, reference, or route users to `.agents/skills/maintainer`; only repo-level maintainer docs may define explicit `$maintainer` routes.
- When `$maintainer` is explicitly invoked to update skill or plugin metadata/docs across the repo, route through its playbooks and keep README/openai metadata text aligned. Without explicit invocation, apply the same repository invariants directly without loading the maintainer workflow.
- Keep instruction-density reviews proposal-first: identify lower-instruction equivalents, then wait for explicit approval before compaction refactors.
- For brand-new skill creation, use `$skill-creator` first. Use `$maintainer` afterward for repo integration or follow-up maintenance only when the user explicitly invokes it or an explicitly invoked parent workflow routes there; otherwise apply the repository integration rules directly. (Codex learning)
- Keep Codex-dependency audits and TanStack Intent coverage refresh as explicit maintainer-owned maintenance tracks; do not spread those maintenance workflows into runtime skills. (Codex learning)
- Keep TanStack skills coverage alignment against `tanstack-skills/tanstack-skills/plugins` as an explicit maintainer-owned maintenance track; map upstream product plugins into the single reusable `skills/tanstack/` skill and verify product guidance against TanStack-owned docs. (Codex learning)
- During Codex dependency audits, require Codex-dependent skills to name their required Codex tools or runtime contracts precisely, and require portable skills to keep Codex-only helpers optional with a generic fallback.
- During an explicit `$maintainer` run, route representative runtime failures and cross-skill ownership defects through its workflow-family hardening playbook; keep `$skill-audit` read-only and let `$maintainer` own approved contract changes and regression coverage. Without explicit invocation, apply approved fixes and regression coverage directly to the targeted packages.
- Route substantial skill/plugin merges, removals, public invocation changes, and standalone-to-plugin moves through `$skill-creator` or `$plugin-creator` first. Return to `$maintainer` for lifecycle cleanup, metadata, validation, and release checks only when it was explicitly invoked or an explicitly invoked parent workflow routed there; otherwise apply those repository invariants directly.
- Select maintainer validation by change type. Plugin and CLI maintenance must verify shipped artifacts and installed/cache state; composed-workflow changes require focused contract tests and bounded scenario proof when risk justifies it.

### Codex Changelog skill
- Keep `codex-changelog` as a Codex-dependent reusable skill under `skills/codex-changelog/`; release-source selection and output formatting belong in its own `SKILL.md` and references, not in this `AGENTS.md`.

### Code Wiki skill
- Keep `code-wiki` as a Codex-dependent reusable skill under `skills/code-wiki/`; runtime repo-study workflow, HTML contract, and image rules belong in `skills/code-wiki/SKILL.md` and its references, not in this `AGENTS.md`.
- Keep `code-wiki` final wiki outputs outside `.cache`; default git clones and temporary analysis artifacts belong under `~/.cache/dotagents/skills/code-wiki/`, while user-requested self-contained source storage belongs under `<wiki-root>/.cache/sources/` with an ignore-all `.gitignore`. (Codex learning)

### Skill CLI Creator skill
- Route embedded-CLI design and layout work through `$skill-cli-creator`; keep detailed host, execution, and configuration doctrine in `skills/skill-cli-creator/SKILL.md` and its references.
- Repo-level embedded-CLI invariants are: shipped artifacts live under `scripts/`, maintenance-only implementations live under `projects/<tool>/`, and ownership stays aligned when a CLI is skill-owned, plugin-shared, or owned by one bundled plugin skill. (Codex learning)
- Use direct `scripts/<tool>` implementations for simple single-file CLIs; reserve `projects/<tool>/` for real multi-file, compiled, generated, dependency-managed, or build-backed CLI implementations. (Codex learning)
- Multi-OS compiled CLIs keep the stable executable surface at `scripts/<tool>` and place platform binaries under `scripts/bin/<tool>-<os>-<arch>`; use `projects/<tool>/scripts/` for build/install helpers when needed. (Codex learning)
- Persist embedded-CLI config in owner-aligned `config.toml` files under `<project-root>/.skills/...` or `<project-root>/.plugins/...`, and treat those directories as config-only. (Codex learning)
- Require the shipped artifact to expose `--version` with one semver source of truth, and if `projects/<tool>/` exists require `projects/<tool>/AGENTS.md` plus a scoped `projects/<tool>/.gitignore` when generated state exists. (Codex learning)
- Keep embedded-CLI docs artifact-first: examples must run `<artifact-path> ...`, `<resolved-tool> ...`, or an absolute installed artifact path unless the host explicitly documents a wrapper, alias, or `PATH` contract for bare `<tool> ...`. (Codex learning)

### GitStack plugin
- Keep GitStack as the sole repo-owned package for local Git and GitHub runtime workflows; do not maintain duplicate standalone `git-commit`, `github-*`, or `yeet` packages.
- Keep bundled skills provider-primitive and workflow-agnostic: caller-specific planning, orchestration, project-memory, queue-state, issue-body, and label-taxonomy policy belongs in the composing skill.
- Prefer the official GitHub connector for supported remote operations, authenticated `gh` for connector gaps or same-target fallback, and direct `git` for local repository state and mutation.
- Keep the plugin-shared runtime artifact at `plugins/gitstack/scripts/gitstack`, its maintenance source at `plugins/gitstack/projects/gitstack/`, and its plugin and CLI semantic versions aligned.
- Keep GitHub issue lifecycle mechanics in `$gitstack:github-issues`, review-thread mechanics in `$gitstack:github-review-threads`, and stars/list mechanics in `$gitstack:github-stars`.
- Keep `$gitstack:yeet` as publish orchestration over `$gitstack:git-commit` and focused GitStack GitHub workflows rather than duplicating their behavior.

### Codex Orchestrator skill
- Keep `codex-orchestrator` as a standalone reusable skill under `skills/codex-orchestrator/`, using namespaced GitStack bundled skills for queue, issue lifecycle, CI, review, release, commit, and publish workflows.
- Keep `skills/codex-orchestrator/references/options.md` as the owner of Codex Orchestrator's concrete option registry; ledgers, prompts, handoffs, recovery packets, and reports must use those canonical values. (Codex learning)
- Keep `codex-orchestrator` manual-only in Codex metadata with `policy.allow_implicit_invocation: false`; ordinary implementation, planning, triage, GitHub, commit, PR, or multi-repo requests must not auto-select it. (Codex learning)
- Treat one active `codex-orchestrator` root as the owner for a project or portfolio source graph. Parallel implementation should run as scoped workers under that root, not as multiple independent orchestrator roots in the same repo or overlapping source graph.
- Keep runtime orchestration, worker, gate, active-root, target-repo `AGENTS.md`, and ledger details in `skills/codex-orchestrator/SKILL.md` and its references; keep this file limited to dependency and ownership boundaries.
- Keep worker authorization surface-based: invocation authorizes background Codex subagents for the root and its spawned Codex threads, while visible Codex App tasks require explicit owner consent. Once granted, consent selects mandatory one-visible-thread-per-Feature-Spec mode: each thread owns its Spec through merge-ready PR closeout, including Codex-review polling and fixes, while the root only schedules, monitors, steers drift, and reconciles evidence and must never take implementation or review back. Each thread chooses its internal subagent topology; the root derives serial/parallel scheduling from dependencies and capacity. Do not expose delegation toggles, numeric worker caps, or a separate visibility selector. (Codex learning)
- Require every orchestrator-created visible Codex thread to establish or resume its own assignment-scoped Goal before work begins. The root supplies the objective and terminal delivery target, verifies thread-reported Goal evidence, and records an exact objective fallback only when that thread runtime exposes no Goal tool; this is automatic runtime behavior, not a user option, and does not apply to internal background subagents. (Codex learning)
- Keep merge root-owned and unavailable by default: `pull-request-ready-for-merge-but-not-merged` does not imply merge, and only an explicit owner instruction may select `granted-for-named-pull-request` plus either `ask-authorized-user-after-checks` or `merge-automatically-after-checks`. (Codex learning)
- For `pull-request-ready-for-merge-but-not-merged`, keep a newly published PR draft through required exact-head Codex review, feedback disposition, fix validation, and current CI; mark it ready only after that head has a verified terminal review with no unresolved actionable feedback, or an exact owner-scoped review skip plus all remaining gates pass. (Codex learning)
- Keep final GitHub parent Feature Spec lifecycle closeout root-owned, but assign the pre-merge PR-body closer to the owning visible Feature Spec thread when mandatory thread mode is active. The closer may be added to the default-branch whole-Spec PR only after its default-required Codex review or exact owner-scoped review skip and all other Feature Spec closeout gates pass; non-default-base PRs retain a linked later closeout vehicle. After `armed`, the root owns any authorized merge watch and post-merge issue-closure verification, or establishes the durable owner/event-driven-automation handoff. (Codex learning)
- Persist portfolio ledgers under `~/.cache/dotagents/skills/codex-orchestrator/ledgers/`, with one ledger per named portfolio by default.
- When an owner intentionally splits orchestration across separate roots, require explicit non-overlapping repo/source boundaries or an explicit takeover/handoff decision.
- Keep recovery packets compact, derived, and freshness-validated against every recorded repo and source checkpoint before reuse; the authoritative ledger and source items still own decisions. Use delta evidence after the first snapshot and record exact per-phase token usage only for root-scoped uncontaminated counter intervals. (Codex learning)


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
