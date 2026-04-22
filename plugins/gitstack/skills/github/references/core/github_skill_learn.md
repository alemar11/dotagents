# GitHub Skill Learn

Use this reference when repeated runtime GitHub work uncovers a pattern that
may deserve promotion into a durable `ghflow` command improvement, routing rule,
or reference update.

## Improve an existing `ghflow` command when

- The repeated workflow already overlaps a current `ghflow` noun/verb.
- The gap is about CLI flag drift, repo resolution, retries, output shape, or
  another natural extension of the current command.
- Extending the command keeps its interface focused instead of turning it into
  a generic catch-all wrapper.
- The new behavior can be explained briefly in `--help` and validated with the
  same shipped-artifact checks already used by this skill.

## Propose a new runtime command when

- The same repository-scoped GitHub workflow is repeated across multiple
  sessions.
- The workflow is generic to GitHub repositories rather than tied to one repo's
  labels, branch naming, or org policy.
- A `ghflow` command would materially improve speed, safety, or reuse compared
  with replaying raw `gh` commands by hand.
- No existing command is a clean fit without blurring its responsibility.
- The command can expose a small, explicit interface and use the shared
  repo-resolution and JSON-envelope conventions when they apply.

## Promote to `SKILL.md` or runtime references when

- The learning changes command routing, the fast pick, or another runtime
  decision point.
- Users need the correction before they choose between raw `gh` and a `ghflow`
  command.
- The workflow should become part of the standard runtime path for future runs.

## Keep as maintainer-only guidance when

- The lesson is about repo upkeep, metadata sync, executable bits, release
  hygiene, or docs validation.
- The behavior is useful for maintaining this skill package but not for solving
  runtime GitHub tasks.
- The change belongs in maintainer docs or tests, not the runtime skill
  surface.

## Keep out entirely when

- The pattern is repo-specific, org-specific, preview-only, or too unstable to
  canonize yet.
- The wrapper would add little value beyond a single obvious `gh` command.
- The lesson is better kept in session memory until it proves durable.

## Packaging rules

- Prefer improving an existing `ghflow` command before adding a new one.
- Keep commands repository-scoped; do not expand this runtime skill toward
  organization-level mutations.
- Favor explicit flags, predictable output, and one clear job per command.
- When cross-repo or non-project use is valid, support `--repo` and
  `--allow-non-project` consistently with the rest of the skill.
- Document every promoted command in the owning domain's `script-summary.md`
  and keep the root `references/script-summary.md` index aligned.
- Update the owning skill's `SKILL.md` only when the promoted learning changes
  the runtime decision flow or the preferred fast path.

## Current promoted learnings

- Release creation should stay `git`/`gh`-first; prefer explicit `gh release`
  and `gh api repos/.../releases/generate-notes` flows over rebuilding thin
  wrappers in `ghflow`.
- `gh pr edit` may require `read:project`; when the change is only
  title/body/base, prefer a narrow `gh api -X PATCH repos/.../pulls/...`
  fallback instead of growing a dedicated wrapper surface.
- Generic Actions triage is not always PR-based; keep that split in the `ci`
  domain and reserve `gh pr checks` for PR-associated runs.
- Repo resolution from git remotes must strip the trailing `.git`, and shared
  repo normalization should live in the project implementation rather than
  diverging per command.
- `ghflow` should stay limited to shared higher-level helpers such as publish
  context, review-thread routing, and authenticated-user stars or star lists.
- New runtime-command proposals should first answer: can an existing `ghflow`
  command absorb this cleanly, or is a new focused command the better reusable
  match?
