# Metadata Sync Playbook

Use this playbook as the metadata-only mode of the unified `maintain skills`
task to keep one or more targeted skills' `SKILL.md`, `agents/openai.yaml`,
plugin manifests, and repo-level docs aligned.

## Task Boundary (Sync Only)
- `sync` aligns metadata and docs only.
- Do not run structure/policy compliance checks here (those belong to `audit`).
- Do not run bundled-reference refresh workflows here (those belong to their specific `refresh` tasks).

## Canonical Source Order
When fields drift, resolve in this order:
1. `SKILL.md` frontmatter (`name`, `description`) is canonical for skill identity/purpose.
2. `agents/openai.yaml` should stay semantically aligned for UI text (`display_name`, `short_description`, `default_prompt`).
3. `README.md` one-liners should mirror the same user-facing purpose as metadata.

Use `references/skill_openai_metadata.md` only for the expected UI field shape
and metadata-editing checks. Do not use it as a replacement for `$skill-creator`
when a brand-new skill scaffold is needed.

## What to Align
- Skill identity and purpose (`name`, `description`, display labels)
- Trigger intent in `SKILL.md` vs UI-facing `short_description`
- Description compactness and selection value across `SKILL.md` frontmatter, `agents/openai.yaml` short descriptions, and README one-liners
- README skill list and one-line descriptions
- Any install prompts or usage snippets that list skill names
- Plugin names, descriptions, marketplace entries, and usage snippets when plugins are in scope

## Workflow
1. Enumerate skill manifests:
   - `find . -type f -name 'SKILL.md' -not -path '*/.git/*' -not -path '*/.cache/*' | sort`
   - `find . -type f -path '*/agents/openai.yaml' -not -path '*/.git/*' -not -path '*/.cache/*' | sort`
2. For each targeted skill, compare:
   - `SKILL.md` frontmatter `name` and `description`
   - `agents/openai.yaml` interface fields (`display_name`, `short_description`, `default_prompt`)
   - README entry wording for that skill
   - description length and duplication against trigger rules, workflow details, and guardrails already present in the skill body
3. Update mismatches with minimal wording drift.
4. Reconcile README lists so added, removed, or renamed skills are reflected.
5. Confirm descriptions remain one-line and user-facing in README/openai metadata.

## Parallel Subagent Pattern
- Use internal subagents when the active runtime policy permits and independent inspection materially improves speed or quality. Ask only when runtime policy requires it or for visible user-owned Codex App threads.
- After manifest enumeration, spawn multiple explorer subagents for independent inspection slices:
  - one for `SKILL.md` frontmatter and trigger wording
  - one for `agents/openai.yaml` display text and prompt alignment
  - one for `README.md` entries and install-prompt references
- Integrate findings and apply wording updates in one local pass so the final language stays coherent.
- Do not split overlapping edits in the same paragraph or list across multiple worker subagents.

## Quality Gates
- Every listed skill has both `SKILL.md` and `agents/openai.yaml`.
- No stale skill names remain in README/install prompts.
- Description changes preserve original intent while improving consistency.
- Descriptions are compact enough for prompt-budget inventory and do not carry detailed workflow contracts that belong in the skill body.
- `result=pass`: no metadata/doc drift remains.
- `result=fail`: unresolved drift in any of `SKILL.md`, `agents/openai.yaml`,
  or README mapping.
