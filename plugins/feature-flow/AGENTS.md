# Feature Flow Plugin Maintenance

`plugins/feature-flow/` is the repo-local source package for feature intake,
planning, and implementation orchestration. Runtime behavior belongs in the
bundled skills and references; this file governs package ownership and
maintenance.

## Ownership map

- `.codex-plugin/plugin.json` owns plugin identity, discovery metadata, bundled
  skill exposure, and version.
- `references/options.md` owns the shared `run_mode` registry.
- `references/clarification-protocol.md` owns the internal question loop and
  the phase-derived lightweight Idea and context-backed Plan profiles.
- `references/workflow-contract.md` owns semantic GitHub metadata and label
  values; GitStack owns GitHub transport and verification.
- `references/ready-gate.md` owns the execution-readiness gate consumed by
  `implement`.
- `skills/idea/` owns Idea capture, including conditional lightweight intake
  clarification, and stops after capture reporting.
- `skills/plan/` owns complete Feature Spec and implementation-issue planning,
  including context-backed clarification, deferred knowledge handoff, and the
  internal codebase-grounded hardening pass for missing issues.
- `skills/implement/` owns Codex App orchestration and delivery verification.

## Maintenance contract

- Keep `idea`, `plan`, and `implement` as separate public bundled skills.
- Keep clarification internal to `idea` and `plan`. The caller phase derives
  its profile; do not expose a fourth clarification skill or add a selectable
  clarification mode.
- Keep issue hardening internal to `plan`: it owns focused repository research,
  issue-level gotcha review, blocker detection, and merging only the final
  stable result into the generated issue. Do not restore a separate public
  hardening skill or caller-result envelope.
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
- Validate all three bundled skill metadata files with the skill validator.
- Run the focused `plan` and `implement` test suites and repository-wide
  stale-reference scans.
- Run `git diff --check` before handoff.
