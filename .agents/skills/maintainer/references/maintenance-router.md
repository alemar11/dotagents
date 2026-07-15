# Maintenance Router

Open this reference first. This router runs only after the user explicitly
invokes `$maintainer`, asks to run Maintainer, or an explicitly invoked parent
workflow routes here. Ordinary skill, plugin, metadata, docs, or repository
requests must not auto-select this skill.

## Route Table

| Request type | Match | Playbook |
| --- | --- | --- |
| `maintain` | Bare run, named package upgrade, or explicit metadata alignment | `run-maintenance.md`, `skill-upgrade.md`, or `metadata-sync.md` according to scope |
| `audit` | Skill/repo health, policy compliance, structure, or pre-release validation | `skill-health.md` |
| `instruction-density` | Behavior-preserving compaction review | `instruction-density-review.md` |
| `description-review` | Description compactness, selection value, or metadata wording | `metadata-sync.md`; run instruction-density first when behavior-sensitive |
| `workflow-hardening` | Sessions, logs, tests, live failures, or repeated corrections expose connected drift | `workflow-family-hardening.md` |
| `package-lifecycle` | Merge, rename, move, bundle, replace, or retire a package | `package-lifecycle.md` |
| `codex-deps` | Codex-dependency or portability-boundary audit | `codex-dependency-audit.md` |
| `codex-tool-surface` | Codex subagent or App task lifecycle surface changed | `codex-tool-surface-refresh.md` |
| `refresh` | Explicit Swift-DocC, Swift API Design, or TanStack refresh | Matching refresh playbook named in `SKILL.md` |
| `okf-spec` | Explicit OKF official-spec comparison or refresh | `okf-spec-refresh.md` |

## Routing Rules

1. A bare `run`, `run your tasks`, or maintenance pass resolves to
   `maintain` with `run-maintenance.md`. Inspect local skills and plugins,
   shortlist concrete low-ambiguity drift, apply safe upgrades, sync touched
   docs, audit health, and close out. Do not infer refresh, new-skill creation,
   workflow hardening, package lifecycle work, or a substantial reshape.
2. Named existing packages resolve to targeted `maintain` with
   `skill-upgrade.md`; explicit metadata/docs wording resolves to
   `metadata-sync.md`.
3. Runtime or cross-skill evidence resolves to `workflow-hardening`. Keep all
   evidence gathering read-only until the finding is accepted.
4. Public identity, ownership, or package-removal changes resolve to
   `package-lifecycle`, with `$skill-creator` or `$plugin-creator` first for a
   substantial reshape.
5. Instruction-density review runs before any behavior-sensitive compaction and
   stops for approval before mutation.
6. Health audits resolve to `audit` and remain read-only. A generic maintenance
   run may consume their safe findings through `skill-upgrade.md`.
7. Codex dependency, tool-surface, domain refresh, and OKF routes run only when
   explicitly requested. Targeted `maintain okf` may run the stale check but
   must not refresh the bundled spec without explicit refresh authority.
8. Brand-new skills and plugins start with their creator workflow; Maintainer
   returns only for integration or later maintenance.

## Mixed Requests

Run accepted categories in this order:

1. `instruction-density` and stop for approval before mutation;
2. `workflow-hardening`;
3. `package-lifecycle` with creator-first routing when required;
4. `maintain`;
5. `description-review`;
6. `codex-deps`;
7. `codex-tool-surface`;
8. explicit `refresh` or `okf-spec`;
9. `audit` and common closeout.

## Task Isolation

Run only the routed playbooks. Do not silently expand generic maintenance into
refresh, workflow hardening, package lifecycle, a substantial reshape, or new
package creation. Do not expand metadata-only work into repo-wide audit, and do
not convert a read-only instruction-density or health audit into edits without
the authority defined by its caller.

## Delegation

When runtime policy permits and delegation materially improves the work, use
explorers for independent read-only slices and workers only for disjoint write
ownership. Keep routing, final wording, edit integration, severity synthesis,
and final git verification in the main agent. Creating visible user-owned Codex
App tasks still requires the applicable explicit permission.

## Common Closeout

Load `options.md`, select every applicable lane from `validation-matrix.md`, and
finish with `release-checklist.md`. Branch playbooks add only their unique
evidence; the release checklist owns common reporting and publication authority.
