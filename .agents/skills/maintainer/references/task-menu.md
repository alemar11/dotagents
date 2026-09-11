# Maintainer Task Menu

Use this file when the user asks what the `$maintainer` skill can do or when a
maintenance request needs to be routed to a concrete task. Each task lists its
scope, mutation boundary, and owning playbook.

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
   - **Purpose:** Conservative health and upgrade pass for existing packages.
   - **Scope:** Named skills/plugins, or all packages in the inventory above when
     unnamed. Include coupled `README.md` / `AGENTS.md` and, when present,
     marketplace or plugin manifests.
   - **Mutation:** Safe, low-ambiguity fixes only. Report strategic or
     behavior-sensitive candidates; do not invent refresh, lifecycle, hardening,
     or new-package work.
   - **Playbooks:** `run-maintenance.md` (unnamed/bare), `skill-upgrade.md`
     (named packages), `metadata-sync.md` (metadata/docs-only wording).
2. `harden workflow family`
   - **Purpose:** Repair a connected multi-skill or skill/plugin workflow after
     runtime or cross-skill evidence shows ownership, authority, handoff,
     validation, or closeout defects.
   - **Scope:** The smallest connected package set that owns the failure.
   - **Mutation:** Read-only evidence first; edit only after the finding is
     accepted. Require regression coverage for accepted behavior defects.
   - **Playbook:** `workflow-family-hardening.md`. Explicit only.
3. `migrate or retire package`
   - **Purpose:** Merge, rename, move, bundle, replace, or retire existing
     skills, plugins, or their coupled maintenance projects.
   - **Scope:** Old and new owners, callers, install prompts, manifests,
     marketplace entries, caches, and tests.
   - **Mutation:** Creator-first for substantial reshapes (`$skill-creator` or
     `$plugin-creator`), then integration and cleanup here. No aliases for
     retired identifiers.
   - **Playbook:** `package-lifecycle.md`. Explicit only.
4. `audit skill health`
   - **Purpose:** Read-only structural, discovery, instruction, reference-path,
     and validation health check.
   - **Scope:** Named packages or the full inventory above. Empty plugin sets
     are healthy when marketplace and docs agree.
   - **Mutation:** None. Findings are evidence, not edit authority.
   - **Playbook:** `skill-health.md`.
5. `review instruction density`
   - **Purpose:** Find behavior-preserving compaction: fewer or better-routed
     instructions for the same runtime guarantees.
   - **Scope:** Entrypoint, disclosed references, and metadata that duplicate
     runtime rules. Optional plugin manifests only when they create confusion.
   - **Mutation:** Proposal-first (`safe trim`, `move to reference`,
     `behavior-risk`, `leave as-is`). Edit only after explicit approval.
   - **Playbook:** `instruction-density-review.md`.
6. `review skill descriptions`
   - **Purpose:** Tighten discovery wording across `SKILL.md` frontmatter,
     `agents/openai.yaml`, and README one-liners.
   - **Scope:** Purpose and trigger family only; keep workflow contracts in the
     skill body or references.
   - **Mutation:** Propose first when invocation boundaries could change; apply
     safe metadata trims during approved maintenance.
   - **Playbooks:** `metadata-sync.md`; run `instruction-density-review.md`
     first when the wording change is behavior-sensitive.
7. `audit codex dependencies`
   - **Purpose:** Classify Codex-dependent versus portable skills and keep
     required runtime contracts named precisely.
   - **Scope:** Skills in inventory plus any inventory docs that claim
     dependency class.
   - **Mutation:** Audit is evidence-first; apply labeling fixes only under an
     accepted maintain route.
   - **Playbook:** `codex-dependency-audit.md`. Explicit only.
8. `refresh swift-docc references`
   - **Purpose:** Refresh bundled Swift-DocC assets and local fast-path
     references when the upstream DocC tree is stale.
   - **Scope:** `skills/swift-docc/` assets, manifest, and `references/*.md`.
   - **Mutation:** Explicit refresh only; never from bare `run`.
   - **Playbooks:** `swift-docc-refresh.md`, `swift-docc-runbook.md`.
9. `refresh swift-api-design references`
   - **Purpose:** Refresh bundled Swift API Design guideline source and local
     routing references when stale.
   - **Scope:** `skills/swift-api-design/` guideline asset, manifest, and
     `references/*.md`.
   - **Mutation:** Explicit refresh only; never from bare `run`.
   - **Playbooks:** `swift-api-design-refresh.md`, `swift-api-design-runbook.md`.
10. `refresh tanstack intent coverage`
   - **Purpose:** Update `$tanstack` routing and references when newly shipped
     first-party TanStack Intent coverage changes local guidance.
   - **Scope:** `skills/tanstack/` metadata and Intent-related references.
   - **Mutation:** Explicit refresh only; never from bare `run`.
   - **Playbook:** `tanstack-intent-refresh.md`.
11. `refresh tanstack skills coverage`
   - **Purpose:** Align local TanStack product references with upstream
     `tanstack-skills` coverage and TanStack-owned product docs.
   - **Scope:** `skills/tanstack/` product references. Ignore upstream bundle
     aliases (`tanstack-all`, `tanstack-core`, `tanstack-data`, `tanstack-ui`)
     unless local packaging intentionally changes.
   - **Mutation:** Explicit refresh only; never from bare `run`.
   - **Playbook:** `tanstack-skills-alignment.md`.
12. `refresh okf spec`
   - **Purpose:** Refresh the bundled Open Knowledge Format official spec copy
     and manifest when upstream `SPEC.md` is newer.
   - **Scope:** `skills/okf/assets/`, related references, CLI, and tests.
   - **Mutation:** Explicit refresh only; targeted `maintain okf` may stale-check
     but must not refresh without refresh authority.
   - **Playbooks:** `okf-spec-refresh.md`, `okf-spec-runbook.md`.
