# Maintainer Task Menu

Use this file when the user asks what the `Maintainer` skill can do or when a
maintenance request needs to be routed to a concrete task.

## Tasks

1. `maintain skills`
   - Inspect one or more skills or plugins, ensure there is no meaningful drift,
     and compare or update local `SKILL.md`, `agents/openai.yaml`,
     `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`,
     `README.md`, and `AGENTS.md` as needed.
   - With no named targets, default scope is all local skills and repo-local
     plugins in this repository.
   - With named targets, keep the pass targeted to those skills or plugins.
   - With explicit metadata/docs wording, stay in metadata-only alignment mode.
   - Include `SKILL.md` frontmatter descriptions, `agents/openai.yaml` short
     descriptions, and README one-liners in metadata drift and prompt-budget
     checks.
   - Finish with audit and release-style reporting when the scope is broader
     than metadata-only alignment.
2. `audit consistency`
   - Run structure, rules, and reference checks across the repo or the touched
     skills.
3. `review instruction density`
   - Inspect one or more existing skills or plugins and identify where the same
     runtime behavior can be achieved with fewer instructions.
   - Classify each proposal as `safe trim`, `move to reference`,
     `behavior-risk`, or `leave as-is`.
   - Return a read-only proposal first; do not refactor, edit, or commit
     compaction changes until the user explicitly approves that refactor.
4. `review skill descriptions`
   - Inspect `SKILL.md` frontmatter descriptions, `agents/openai.yaml` short
     descriptions, and README one-liners for length, clarity, selection value,
     and alignment.
   - Prefer compact descriptions that identify purpose and trigger family; keep
     detailed trigger rules and workflow contracts in `SKILL.md` sections or
     references.
   - Return proposed wording first when behavior or invocation boundaries could
     change; apply safe metadata trims directly during approved maintenance
     passes.
5. `audit codex dependencies`
   - Verify which skills are Codex-dependent versus portable, keep the repo
     inventory current, and ensure Codex-specific tools or filesystem contracts
     are named precisely.
6. `refresh swift-docc references`
   - Check the bundled Swift-DocC manifest, refresh the local
     `DocCDocumentation.docc` asset tree when stale, and validate or tighten the
     local `references/*.md` fast paths.
7. `refresh swift-api-design references`
   - Check the bundled Swift API Design manifest, refresh the local guideline
     source file when stale, and validate the local `references/*.md` routing
     layer.
8. `refresh tanstack intent coverage`
   - Review the current TanStack Intent registry and relevant TanStack package
     skill pages for `skills/tanstack/`.
   - Update local skill metadata, `$tanstack` routing, `references/*.md` fast
     paths, and related docs only when newly shipped first-party Intent coverage
     materially changes the right guidance.
   - Use the current TanStack skill layout: `$tanstack` is the primary
     entrypoint, with dense product and domain slices living under `references/`
     instead of separate narrow skill directories.
   - Keep this task explicit; do not fold it into generic repo-wide maintenance.
9. `refresh tanstack skills coverage`
   - Compare local `skills/tanstack/` product-level references against the
     upstream `tanstack-skills/tanstack-skills` plugin tree.
   - Ignore upstream bundle aliases such as `tanstack-all`, `tanstack-core`,
     `tanstack-data`, and `tanstack-ui` unless the local reusable-skill packaging
     model intentionally changes.
   - Verify product-specific API and best-practice details against
     TanStack-owned docs before updating local runtime guidance.
   - Keep this task explicit; do not fold it into generic repo-wide maintenance.
10. `refresh codex tool surface`
   - Inspect the currently exposed Codex subagent and Codex App thread tools,
     including spawn, wait, send/resume/close, create-thread,
     read/rename/archive/handoff, and related lifecycle operations.
   - Compare the discovered surface against `skills/codex-orchestrator/`
     runtime requirements, worker-surface rules, and prompt templates.
   - Update `codex-orchestrator` only when the actual tool names, visibility
     behavior, lifecycle capabilities, or authorization boundaries have
     materially changed.
   - Keep this task explicit; do not fold it into generic repo-wide maintenance.
11. `refresh okf spec`
   - Check `skills/okf/assets/manifest.json` and the bundled official spec copy
     against `GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md`.
   - Refresh `skills/okf/assets/spec.md` and the manifest when stale.
   - Validate the OKF runtime skill shape, reference links, CLI executable, and
     tests.
   - Keep this task explicit; do not fold it into generic repo-wide maintenance.
