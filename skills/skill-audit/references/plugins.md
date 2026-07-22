# Plugin Audits

Use this workflow for plugin package audits.

Treat the plugin package as a first-class install surface. Audit the package
itself, not just its bundled skills.

## Resolution

- Start from visible plugin discovery surfaces:
  - `.agents/plugins/marketplace.json`
  - `plugins/<name>/`
- If the user names a specific plugin, resolve that plugin first.
- In default full-scope mode, prioritize only the plugins relevant to the
  current workflow instead of auditing every local plugin mechanically.

## What To Inspect

- `.codex-plugin/plugin.json`
- `.agents/plugins/marketplace.json`
- bundled `skills/*`
- shared `scripts/*`
- `projects/*` when present
- assets and directly coupled docs as needed
- cache copies under `~/.codex/plugins/cache/...` only as a verification
  surface

## What To Evaluate

- current role in the repo or workflow
- whether the plugin package is still the right install surface
- whether `.codex-plugin/plugin.json` is current and coherent
- whether `.agents/plugins/marketplace.json` matches the plugin package
- whether the bundled skill set is coherent, overlapping, or missing an obvious
  owner boundary
- whether bundled skill descriptions or contracts need
  `references/writing-style-review.md` for trigger clarity, prompt load,
  information hierarchy, or pruning issues
- whether shared `scripts/*` and `projects/*` still follow the documented
  runtime versus maintenance split
- whether assets and repo-relative paths are valid from the plugin root
- whether versioning and cache-awareness rules are reflected in the package
- whether gaps belong in the plugin package, a bundled skill, repo docs, or an
  owner-specific maintenance workflow

## Historical Evidence Hints

Use `references/historical-evidence.md` without changing its order. Useful
target-specific keys include plugin name, manifest and marketplace paths,
runtime scripts, exact `cwd`, repository basename, and specific failure text.
Use `git log -- <plugin-dir>` for cheap package history.

## Cache Branch

When cache evidence is relevant, load `references/cache-resolution.md`. That
reference owns cache-to-editable-source resolution and the no-mutation rule.

## Ownership Guidance

- Put findings on `plugin-package` when the issue is in the package manifest,
  marketplace registration, bundled-skill boundaries, runtime package layout,
  assets, or version/cache behavior.
- Put findings on `bundled-plugin-skill` when the issue is isolated to one
  bundled skill contract.
- Put findings on `docs` when the package is fine but the repo guidance is the
  real source of drift.
