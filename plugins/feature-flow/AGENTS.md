# Feature Flow Plugin Maintenance

`plugins/feature-flow/` is the repo-local source package for feature intake and
planning. Runtime behavior belongs in the bundled skills and references; this
file governs package ownership and maintenance.

## Ownership map

- `.codex-plugin/plugin.json` owns plugin identity, discovery metadata, bundled
  skill exposure, and version.
- `references/options.md` owns the shared `run_mode` registry.
- `references/workflow-contract.md` owns semantic GitHub metadata and label
  values; GitStack owns GitHub transport and verification.
- `skills/idea/` owns Idea capture and stops after capture reporting.
- `skills/plan/` owns complete Feature Spec and implementation-issue planning.

## Maintenance contract

- Keep `idea` and `plan` as separate public bundled skills.
- Keep `run_mode: preview | publish` identical across both skills.
- Do not reintroduce retired standalone package names or compatibility aliases.
- Keep `implement-feature` outside this plugin and do not add readiness
  enforcement here.
- Keep GitHub transport in GitStack; do not add a second provider adapter.

## Validation

- Validate the manifest with the plugin validator.
- Validate both bundled skill metadata with the skill validator.
- Run the focused `plan` tests and repository-wide stale-reference scans.
- Run `git diff --check` before handoff.
