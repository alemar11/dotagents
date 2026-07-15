# OpenAI Skill Metadata Reference

Use this file when maintaining `agents/openai.yaml` metadata for an existing
skill or for a skill that has already been scaffolded. For brand-new skills,
start with `$skill-creator`; this reference only covers the metadata shape and
repo-local sync checks that happen after a skill boundary exists.

## Skill Metadata (`agents/openai.yaml`)

Optional UI metadata for a skill. `SKILL.md` remains the required entrypoint for triggers and workflow. Metadata lives in `agents/openai.yaml` for every skill that exposes UI fields.

## Minimal Interface
```yaml
interface:
  display_name: "My Skill"
  short_description: "One line shown in the UI."
  icon_small: "assets/icon-32.png"
  icon_large: "assets/icon-128.png"
  brand_color: "#123456"
  default_prompt: "You are a helpful specialist for this skill."
```

Notes:
- Icons must be relative paths under the skill's `assets/` directory.
- Keep `short_description` concise and user-facing; use `SKILL.md` for trigger wording.

## Metadata Maintenance Checklist

When adding or changing skill metadata:
1. Confirm `SKILL.md` frontmatter has the canonical `name` and `description`.
2. Add or update `agents/openai.yaml` with the interface fields above.
3. Keep `display_name`, `short_description`, and `default_prompt` aligned with
   the skill's trigger intent without copying long workflow text into UI
   metadata.
4. Keep icon paths relative to the skill root and verify referenced assets
   exist.
5. Update repo-level `README.md` and installer guidance when a skill is added,
   removed, renamed, or materially repositioned.
6. Update `AGENTS.md` only when the change adds durable repository guidance.
7. Run `references/metadata-sync.md` and a focused check from
   `references/skill-health.md`.

For project maintainer skills, place the skill under `.agents/skills/` instead of `skills/`.

## Where To Check For Updates
- Skill specification: `https://agentskills.io/specification`
- Codex skills docs: `https://developers.openai.com/codex/skills/`
- Codex repo changes: search for `openai.yaml` or `interface` in recent commits/PRs.
