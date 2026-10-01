# TanStack Intent

Use this reference for `@tanstack/intent`, dependency-packaged Agent Skills,
workspace skill discovery, consumer guidance setup, allowlists, or agent hooks.
Intent is optional tooling, not a runtime dependency of `$tanstack` or the app.

## Ownership Boundaries

- Intent discovers and loads guidance from installed npm or workspace packages;
  the library release owns its packaged skill content.
- The project owns source permissions in `package.json`, guidance placement,
  dependency updates, and hook installation. Discovery does not grant trust.
- Loading content or observing a load command does not prove that an agent
  selected the right skill or applied it correctly.

## Workflow

1. Inspect the installed CLI version, package manager, workspace root, and
   existing Intent policy. Prefer the lockfile-pinned binary when reproducibility
   matters; documentation examples using `@latest` can run a different CLI.
2. Run `intent list` (or `intent list --json`) from the workspace root and load
   only the most specific relevant `<package>#<skill>` with `intent load`.
   Use discovered identifiers rather than guessing package or skill names.
   A missing registry listing does not prove an installed package lacks skills.
3. For requested consumer setup, preview `intent install --dry-run` and review
   the proposed policy and guidance destination before writing. First-run
   permission selection requires an interactive terminal; report that limitation
   rather than broadening permissions to bypass it.
4. Preserve existing permissions. Use `intent install --review` for requested
   changes; plain `install` updates guidance without changing an effective policy.
   Keep hook installation separately authorized and scoped to the intended agent.
5. Verify the saved policy, managed guidance block, and a permitted skill load.
   If guidance fails after confirmed permissions are saved, inspect both files
   before retrying: permission writes are not rolled back automatically.

## Trust And Configuration

- `intent.skills` uses the nearest non-null declaration; a nearer declaration
  replaces inherited permissions. `intent.exclude` accumulates and wins afterward.
- Exact `<package>#<skill>` entries narrow access; package and scope patterns
  include future matching skills. Bare npm selectors and `workspace:` sources
  are distinct. `"*"` permits both kinds and is not a safe default.
- An absent allowlist currently exposes discovered skills with a deprecation
  notice; `[]` exposes none. Enabling a source does not freeze its instructions.
- Keep global discovery opt-in. Do not add dependencies, guidance, hooks, or
  library-maintainer setup merely to answer an application API question.

## Verification

Use official [consumer setup](https://tanstack.com/intent/latest/docs/getting-started/quick-start-consumers),
[configuration](https://tanstack.com/intent/latest/docs/concepts/configuration),
[trust](https://tanstack.com/intent/latest/docs/concepts/trust-model), and
[install](https://tanstack.com/intent/latest/docs/cli/intent-install) docs matched
to the CLI version. For an explicitly requested library skill-authoring or
publishing task, use the official maintainer docs instead of consumer setup.
