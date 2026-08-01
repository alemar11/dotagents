# Feature Flow Plugin Maintenance

`plugins/feature-flow/` is the repo-local source package for feature intake,
planning, and implementation orchestration. Runtime behavior belongs in the
bundled skills and references; this file governs package ownership and
maintenance.

## Ownership map

- `.codex-plugin/plugin.json` owns plugin identity, discovery metadata, bundled
  skill exposure, and version.
- `references/options.md` owns the shared `run_mode` registry.
- `references/workflow-contract.md` owns semantic GitHub metadata and label
  values; GitStack owns GitHub transport and verification.
- `references/ready-gate.md` owns the execution-readiness gate consumed by
  `implement`.
- `skills/idea/` owns Idea capture and stops after capture reporting.
- `skills/plan/` owns complete Feature Spec and implementation-issue planning.
- `skills/engineering-plan/` owns codebase-grounded implementation planning and
  issue hardening without repository or tracker writes.
- `skills/implement/` owns Codex App orchestration and delivery verification.

## Maintenance contract

- Keep `idea`, `plan`, and `engineering-plan` as separate public bundled skills.
- Keep `engineering-plan` separate from `plan`: Plan owns Feature Spec and issue
  graph convergence; Engineering Plan owns planning-only output and its caller
  result envelope.
- Keep `implement` as a separate public bundled skill; do not merge execution
  orchestration into `plan`.
- Keep `run_mode: preview | publish` identical across `idea` and `plan`;
  `implement` retains its own startup-authorization contract.
- Do not reintroduce retired standalone package names or compatibility aliases.
- Preserve the Implement Feature App-only execution boundary and its internal
  `implement-feature` protocol/cache identifiers during the move.
- Keep `ready-for-agent` enforcement in `implement`'s preflight; `implement`
  must not apply or repair the label.
- Keep GitHub transport in GitStack; do not add a second provider adapter.

## Validation

- Validate the manifest with the plugin validator.
- Validate all four bundled skill metadata files with the skill validator.
- Run the focused `plan` and `implement` test suites and repository-wide
  stale-reference scans.
- Run `git diff --check` before handoff.
