# Package Lifecycle

Use this playbook to merge, rename, move, bundle, replace, or retire existing
skills and plugins.

## Creator-First Boundary

Use `$skill-creator` first for substantial skill reshapes and `$plugin-creator`
first for substantial plugin reshapes. This includes public invocation changes,
package merges/removals, standalone-to-plugin moves, breaking handoff changes,
and major responsibility redistribution. Return here for repository integration,
lifecycle cleanup, validation, and release checks.

## Lifecycle Map

Before mutation, record:

- old and new package owners, paths, names, and public invocations;
- replacement behavior and any intentionally removed capability;
- callers, composed-skill dependencies, repo docs, install commands, manifests,
  marketplace entries, scripts, tests, caches, and generated artifacts;
- hard-cut boundary and any intentionally independent surfaces;
- plugin and embedded CLI version impact under repository semantic-versioning
  rules.

Do not keep aliases or duplicate compatibility surfaces for retired packages.

## Workflow

1. Confirm the creator-first design and lifecycle map.
2. Move or replace the package atomically with its metadata and directly coupled
   callers. Preserve unrelated dirty worktree state.
3. Remove stale discovery surfaces, dependencies, install prompts, and runtime
   references. Runtime skills must not gain maintainer-only routing.
4. For plugins, update the manifest version in the same rollout. Align embedded
   CLI versions unless an independent policy is documented, rebuild shipped
   artifacts deterministically, and update marketplace metadata when needed.
5. Select migration/removal plus package-specific lanes from
   `validation-matrix.md`.
6. Verify source discovery, installed/cache state when applicable, and absence
   of the retired surface. Compare before/after status and require that reinstall
   introduces no checkout changes while preserving pre-existing dirty state.
7. When the user explicitly authorizes commits, split them by package or
   migration intent when multiple skills/plugins are affected. Without commit
   authority, report the recommended split without staging or changing Git
   history. Then run the release checklist.

## Failure Handling

- Stop on unresolved callers, duplicate discovery, incompatible replacement
  behavior, missing version authority, non-reproducible artifacts, install/cache
  mismatch, or reinstall-induced checkout changes.
- Do not delete the old surface until replacement discovery and validation
  evidence are available in the same rollout.

## Output

Report the lifecycle map, hard-cut boundary, moved and retired surfaces,
version/artifact/install evidence, stale-reference scan, commit split, and final
result.
