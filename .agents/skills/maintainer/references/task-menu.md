# Maintainer Task Menu

Use this file when the user asks what the `$maintainer` skill can do or when a
maintenance request needs to be routed to a concrete task. This is a capability
reference, not a menu the user must choose from. Routine maintenance covers all
applicable tasks through [run-maintenance.md](run-maintenance.md); arguments
narrow scope. Each task lists its scope, mutation boundary, and owning playbook.

Default package inventory for unnamed repo-wide work:

- reusable skills under `skills/*`
- project-local skills under `.agents/skills/*`
- optional Codex plugins under `plugins/*` when present and registered in
  `.agents/plugins/marketplace.json` (an empty marketplace is valid; missing
  plugins are not drift)
- coupled maintenance projects under repo-root `projects/*` and skill-local
  `skills/*/projects/*` when those packages are in scope

## Tasks

1. `maintain skills`
   - **Purpose:** Complete routine maintenance pass, or explicitly requested
     renames, moves, merges, replacements, and removals of existing packages.
   - **Scope:** Named skills/plugins, or all packages in the inventory above when
     unnamed. Include coupled `README.md` / `AGENTS.md` and, when present,
     marketplace or plugin manifests.
   - **Mutation:** A generic run applies only safe, low-ambiguity fixes. Package
     restructuring or removal requires an explicit request; substantial reshapes
     use the creator workflow first. Source refreshes and evidenced workflow repairs
     are included; new packages are not.
   - **Playbooks:** `run-maintenance.md` (whole inventory or named packages),
     `skill-upgrade.md` (concrete repairs or specifically requested changes),
     `metadata-sync.md` (metadata/docs-only wording).
2. `harden workflow family`
   - **Purpose:** Repair a connected multi-skill or skill/plugin workflow after
     runtime or cross-skill evidence shows ownership, authority, handoff,
     validation, or closeout defects.
   - **Scope:** The smallest connected package set that owns the failure.
   - **Mutation:** Inspect evidence first; routine maintenance may repair concrete
     defects within established responsibilities. Propose structural decisions.
     Select proof through the validation matrix; direct reviews stay read-only.
   - **Playbook:** `workflow-family-hardening.md`. Conditional on evidence during
     routine maintenance, or selected directly.
3. `audit skill health`
   - **Purpose:** Read-only structural, discovery, instruction, reference-path,
     and validation health check.
   - **Scope:** Named packages or the full inventory above. Empty plugin sets
     are healthy when marketplace and docs agree.
   - **Mutation:** None. Findings are evidence, not edit authority.
   - **Playbook:** `skill-health.md`.
4. `review instruction density`
   - **Purpose:** Find behavior-preserving compaction: fewer or better-routed
     instructions for the same runtime guarantees.
   - **Scope:** Entrypoint, disclosed references, and metadata that duplicate
     runtime rules. Optional plugin manifests only when they create confusion.
   - **Mutation:** Review-only requests produce proposals; routine maintenance,
     explicit refactoring, or audit-and-fix authorize behavior-preserving edits.
   - **Playbook:** `instruction-density-review.md`.
5. `review skill descriptions`
   - **Purpose:** Tighten discovery wording across `SKILL.md` frontmatter,
     `agents/openai.yaml`, and README one-liners.
   - **Scope:** Purpose and trigger family only; keep workflow contracts in the
     skill body or references.
   - **Mutation:** Propose first when invocation boundaries could change; apply
     safe metadata trims during approved maintenance.
   - **Playbooks:** `metadata-sync.md`; run `instruction-density-review.md`
     first when the wording change is behavior-sensitive.
6. `refresh swift-docc references`
   - **Purpose:** Refresh bundled Swift-DocC assets and local fast-path
     references when the upstream DocC tree is stale.
   - **Scope:** `skills/swift-docc/` assets, manifest, and `references/*.md`.
   - **Mutation:** Refresh stale sources during routine maintenance or a direct
     refresh request; audit and review remain read-only.
   - **Playbooks:** `swift-docc-refresh.md`, `swift-docc-runbook.md`.
7. `refresh swift-api-design references`
   - **Purpose:** Refresh bundled Swift API Design guideline source and local
     routing references when stale.
   - **Scope:** `skills/swift-api-design/` guideline asset, manifest, and
     `references/*.md`.
   - **Mutation:** Refresh stale sources during routine maintenance or a direct
     refresh request; audit and review remain read-only.
   - **Playbooks:** `swift-api-design-refresh.md`, `swift-api-design-runbook.md`.
8. `refresh okf spec`
   - **Purpose:** Refresh the bundled Open Knowledge Format official spec copy
     and manifest when upstream `SPEC.md` is newer.
   - **Scope:** `skills/okf/assets/`, related references, CLI, and tests.
   - **Mutation:** Refresh stale sources during routine maintenance, including
     targeted `maintain okf`, or a direct refresh request; reviews stay read-only.
   - **Playbooks:** `okf-spec-refresh.md`, `okf-spec-runbook.md`.
