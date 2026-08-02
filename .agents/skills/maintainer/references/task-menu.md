# Maintainer Task Menu

Use this file when the user asks what the `$maintainer` skill can do or when a
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
   - Finish with skill-health and release-style reporting when the scope is
     broader than metadata-only alignment.
2. `harden workflow family`
   - Use representative sessions, logs, tests, or live failures to repair a
     connected skill/plugin workflow.
   - Confirm ownership, authority, handoffs, sources of truth, validation, and
     closeout before changing contracts.
   - Require regression coverage for accepted behavior defects.
3. `migrate or retire package`
   - Merge, rename, move, bundle, replace, or retire existing skills/plugins.
   - Use `$skill-creator` or `$plugin-creator` first for substantial reshapes,
     then return here for repo integration, stale-surface cleanup, validation,
     versioning, install/cache checks, and release reporting.
4. `audit skill health`
   - Run a read-only health audit across the repo or the touched packages,
     covering structural and policy integrity, metadata and discovery,
     entrypoint size, reference routing, representative invoked-path cost, and
     applicable validation evidence.
   - Treat prompt size as diagnostic and invoke `$skill-audit` only when health
     signals require deeper prompt-quality, overlap, or runtime evidence.
5. `review instruction density`
   - Inspect one or more existing skills or plugins and identify where the same
     runtime behavior can be achieved with fewer instructions.
   - Classify each proposal as `safe trim`, `move to reference`,
     `behavior-risk`, or `leave as-is`.
   - Return a read-only proposal first; do not refactor, edit, or commit
     compaction changes until the user explicitly approves that refactor.
6. `review skill descriptions`
   - Inspect `SKILL.md` frontmatter descriptions, `agents/openai.yaml` short
     descriptions, and README one-liners for length, clarity, selection value,
     and alignment.
   - Prefer compact descriptions that identify purpose and trigger family; keep
     detailed trigger rules and workflow contracts in `SKILL.md` sections or
     references.
   - Return proposed wording first when behavior or invocation boundaries could
     change; apply safe metadata trims directly during approved maintenance
     passes.
7. `audit codex dependencies`
   - Verify which skills are Codex-dependent versus portable, keep the repo
     inventory current, and ensure Codex-specific tools or filesystem contracts
     are named precisely.
8. `refresh swift-docc references`
   - Check the bundled Swift-DocC manifest, refresh the local
     `DocCDocumentation.docc` asset tree when stale, and validate or tighten the
     local `references/*.md` fast paths.
9. `refresh swift-api-design references`
   - Check the bundled Swift API Design manifest, refresh the local guideline
     source file when stale, and validate the local `references/*.md` routing
     layer.
10. `refresh tanstack intent coverage`
   - Review the current TanStack Intent registry and relevant TanStack package
     skill pages for `skills/tanstack/`.
   - Update local skill metadata, `$tanstack` routing, `references/*.md` fast
     paths, and related docs only when newly shipped first-party Intent coverage
     materially changes the right guidance.
   - Use the current TanStack skill layout: `$tanstack` is the primary
     entrypoint, with dense product and domain slices living under `references/`
     instead of separate narrow skill directories.
   - Keep this task explicit; do not fold it into generic repo-wide maintenance.
11. `refresh tanstack skills coverage`
   - Compare local `skills/tanstack/` product-level references against the
     upstream `tanstack-skills/tanstack-skills` plugin tree.
   - Ignore upstream bundle aliases such as `tanstack-all`, `tanstack-core`,
     `tanstack-data`, and `tanstack-ui` unless the local reusable-skill packaging
     model intentionally changes.
   - Verify product-specific API and best-practice details against
     TanStack-owned docs before updating local runtime guidance.
   - Keep this task explicit; do not fold it into generic repo-wide maintenance.
12. `refresh codex tool surface`
   - Inspect the currently exposed Codex subagent and Codex App task tools,
     including spawn, wait, send/resume/close, create-thread,
     read/rename/archive/handoff, and related lifecycle operations.
   - Compare App changes against `plugins/se/skills/implement/` and keep the
     runtime path limited to visible App tasks and App-managed worktrees.
   - Keep this task explicit; do not fold it into generic repo-wide maintenance.
13. `refresh okf spec`
   - Check `skills/okf/assets/manifest.json` and the bundled official spec copy
     against `GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md`.
   - Refresh `skills/okf/assets/spec.md` and the manifest when stale.
   - Validate the OKF runtime skill shape, reference links, CLI executable, and
     tests.
   - Keep this task explicit; do not fold it into generic repo-wide maintenance.
