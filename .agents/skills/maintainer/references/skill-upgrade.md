# Skill Upgrade Playbook

Use this playbook as the targeted-maintenance mode of the unified `maintain
skills` task when a user asks to upgrade, modernize, tighten, or improve one
or more existing skills or plugins.

## Purpose
- Improve one or more existing skills or plugins with meaningful, scoped documentation or metadata updates.
- Preserve each target's intent while making triggers, workflow, guardrails, or supporting docs easier to use and maintain.
- Avoid silently expanding a targeted upgrade into repo-wide refresh work.

## Task Boundary
- `upgrade` is for one or more existing target skills or plugins.
- Default scope per target skill:
  - the skill's `SKILL.md`
  - the skill's `agents/openai.yaml`
  - the skill's `references/*.md`
  - directly coupled mentions in `README.md` or `AGENTS.md` when wording or durable repo guidance changes
- Default scope per target plugin:
  - `.codex-plugin/plugin.json`
  - bundled `skills/*`, shared `scripts/*`, `projects/*`, and `assets/*` when directly coupled to the requested change
  - `.agents/plugins/marketplace.json`
  - directly coupled mentions in `README.md` or `AGENTS.md`
- Do not refresh domain best-practices content unless the user explicitly asks for `refresh`.
- If the requested change merges/removes public packages, changes public invocation, redistributes major responsibilities, moves standalone skills into a plugin, or breaks a handoff schema, stop this playbook and route through `$skill-creator` or `$plugin-creator` first. Resume with `package-lifecycle.md` for integration and cleanup.

## Workflow
1. Identify the target skill, plugin, or mixed target set and inspect each current package:
   - for skills: `SKILL.md`, `agents/openai.yaml`, any referenced `references/*.md`, and `scripts/*`
   - for plugins: `.codex-plugin/plugin.json`, bundled `skills/*`, shared `scripts/*`, `projects/*`, and `assets/*` as needed
   - related mentions in `README.md`, `AGENTS.md`, and `.agents/plugins/marketplace.json` when a plugin is involved
2. Define the concrete upgrade goals for each target before editing:
   - trigger clarity
   - workflow structure
   - guardrail precision
   - Codex dependency labeling or portability-boundary clarity when relevant
   - description compactness, selection value, and alignment across metadata surfaces
   - metadata/doc sync
   - moving dense guidance into `references/` when that improves maintainability
3. Apply minimal, meaningful edits that preserve each target's current intent.
4. Run a focused sync pass using `references/metadata-sync.md` for the touched skills, plugins, and any directly coupled docs.
5. Run a focused health pass using `references/skill-health.md`:
   - required files still exist
   - referenced scripts/docs exist
   - no contradictory instructions were introduced
   - `references/` markdown naming still follows repo policy
6. Select the applicable lanes from `references/validation-matrix.md`, finish
   with `references/release-checklist.md`, and report canonical `result` and
   `change_state` values.

## Quality Gates
- Each upgraded target has a concrete rationale; avoid cosmetic rewrites with no practical gain.
- Touched docs stay aligned across `SKILL.md`, `agents/openai.yaml`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, and `README.md` when those files are in scope.
- Touched descriptions stay concise and preserve trigger family without duplicating detailed workflow or guardrail text.
- `AGENTS.md` changes happen only when the upgrade introduces durable repository guidance.
- If a touched skill is Codex-dependent, its required Codex tools/runtime contracts are named plainly; if it is portable, Codex-only helpers remain optional.
- Return `result=pass` and `change_state=no-change` when no meaningful
  improvement is needed after inspection.

## Branch Report Additions

Add the target packages, concrete upgrade goals, and target-by-target rationale
to the common final report owned by `references/release-checklist.md`.
