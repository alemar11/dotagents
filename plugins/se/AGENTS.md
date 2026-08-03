# SE Plugin Maintenance

`plugins/se/` is the repo-local source package for durable project
context, architecture improvement, feature intake, planning, implementation
orchestration, and active-session auditing. Runtime behavior belongs in the
bundled skills and references; this file governs package ownership and
maintenance.

## Ownership map

- `.codex-plugin/plugin.json` owns plugin identity, discovery metadata, bundled
  skill exposure, and version.
- `references/options.md` owns the shared `run_mode` registry.
- `references/clarification-protocol.md` owns the internal question loop and
  the phase-derived lightweight Idea and context-backed Feature profiles.
- `references/workflow-contract.md` owns semantic GitHub metadata and label
  values; G owns GitHub transport and verification.
- `references/codex-dependency-preflight.md` owns the read-only SE-to-G runtime
  availability gate and manual remediation guidance; it never installs or
  enables plugins.
- `references/ready-gate.md` owns the execution-readiness gate consumed by
  `implement`.
- `references/contract-repair.md` owns the portable Feature/Implement repair
  boundary; `scripts/validate-contract-repair` enforces its structural
  invariants without owning repair semantics or Codex effects.
- `skills/idea/` owns Idea capture, including conditional lightweight intake
  clarification, and stops after capture reporting.
- `skills/feature/` owns complete Feature Spec and implementation-issue planning,
  including context-backed clarification, deferred knowledge handoff, and the
  internal codebase-grounded hardening pass for missing issues.
- `skills/implement/` owns Codex App orchestration and delivery verification.
- `skills/audit/` owns read-only monitoring of active sessions using SE skills
  and prioritized feedback, bug, and improvement reporting.
- `skills/learn/` owns durable repository context, ADR routing,
  confirmed capture, Code Review Rules, and explicit `AGENTS.md` compaction.
- `skills/improve-codebase-architecture/` owns evidence-backed architecture
  candidate discovery and pressure-testing before implementation.

## Maintenance contract

- Keep `idea`, `feature`, `implement`, `learn`, `improve-codebase-architecture`,
  and `audit` as separate public bundled skills.
- Keep clarification internal to `idea` and `feature`. The caller phase derives
  its profile; do not expose a fourth clarification skill or add a selectable
  clarification mode.
- Keep issue hardening internal to `feature`: it owns focused repository research,
  issue-level gotcha review, blocker detection, and merging only the final
  stable result into the generated issue. Do not restore a separate public
  hardening skill or caller-result envelope.
- Keep `implement` as a separate public bundled skill; do not merge execution
  orchestration into `feature`.
- Keep Contract Repair as one general route. Feature owns contract semantics;
  Implement owns suspension, task lifecycle, readback, continuation, and
  supersession; the root never edits planning or repository artifacts.
- Keep `run_mode: preview | publish` identical across `idea` and `feature`;
  `implement` retains its own startup-authorization contract.
- Do not reintroduce retired public skill identifiers `project-context` or
  `plan`, or compatibility aliases. The consumer data path `project-context/`
  remains canonical.
- Preserve the Implement Feature App-only execution boundary and its internal
  `implement-feature` protocol/cache identifiers during the move.
- Keep `ready-for-agent` enforcement in `implement`'s preflight; `implement`
  must not apply or repair the label.
- Keep GitHub transport in G; do not add a second provider adapter.
- Keep Project Context as the sole durable knowledge owner. Architecture
  discovery may route accepted decisions to it but must not persist a second
  memory format.
- Do not restore standalone copies or install entries for `learn` or
  `improve-codebase-architecture`.

## Validation

- Validate the manifest with the plugin validator.
- Validate all six bundled skill metadata files with the skill validator.
- Run the focused `feature` and `implement` test suites plus Project Context
  documentation/link checks and repository-wide stale-reference scans.
- Run `git diff --check` before handoff.
