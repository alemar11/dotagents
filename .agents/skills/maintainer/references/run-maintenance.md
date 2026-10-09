# Routine Maintenance

Use for a bare `$maintainer`, `run`, or maintenance of named packages. Cover the
whole inventory in [task-menu.md](task-menu.md) unless the user narrows it. An
empty plugin marketplace is valid. An `audit`, review, or dry-run performs the
same applicable assessment without repairs or refresh writes.

## Coverage

Assess every row below for the selected inventory. Do not stop after the first
finding or ask the user to select tasks. Load each procedure when reaching its
part of the pass; reuse evidence and skip branches that have no applicable owner.

| Area | Procedure and expected work |
| --- | --- |
| Health and prerequisites | [skill-health.md](skill-health.md): inspect structure, references, discovery, maintenance guidance, required tools/services, and documented fallbacks. |
| Instruction quality and overlap | [instruction-density-review.md](instruction-density-review.md): assess density, duplication, selection overlap, and ownership; apply behavior-preserving improvements. Propose package merges or responsibility changes. |
| Descriptions and metadata | [metadata-sync.md](metadata-sync.md): align descriptions, UI metadata, catalogs, and installation guidance while preserving invocation policy. |
| Managed sources | Run [Swift-DocC refresh](swift-docc-refresh.md), [Swift API Design refresh](swift-api-design-refresh.md), and [OKF spec refresh](okf-spec-refresh.md) for their in-scope owners. Check freshness, refresh stale bundles, and reconcile affected references. In read-only mode, check and report only. |
| Connected workflows | When the pass finds cross-skill contract inconsistencies or supplied runtime evidence exposes a defect, use [workflow-family-hardening.md](workflow-family-hardening.md). Repair concrete defects within established responsibilities; propose unresolved behavioral or structural decisions. Without such evidence, report this branch as not applicable. |

Use [skill-upgrade.md](skill-upgrade.md) for concrete repairs not already owned
by a branch. Routine maintenance authorizes these local corrections and managed
source updates; it does not authorize package restructuring, new tools, global
configuration, skill installation, or publication. Preserve local modifications
and explicit pins; report conflicts rather than overwriting them.

## Completion

Continue independent work when a branch lacks access or a prerequisite. Report
that branch as blocked, not unchanged or complete. Do not invent changes for a
current bundle or a healthy package.

Return coverage for each area as checked, changed, not applicable, or blocked,
with a reason for exclusions and any deferred proposals. This is a closeout
summary, not a persisted task ledger. Use one shared
[release-checklist.md](release-checklist.md) pass for validation and final
`result`/`change_state`; reuse completed checks. Commit and push require their
own request.
