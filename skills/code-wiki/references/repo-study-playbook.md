# Repo Study Playbook

Use this reference for non-trivial `code-wiki` runs. Keep the work read-only
against the target repo until the output wiki path is resolved.

## Discovery Order

1. Confirm target type.
   - Local path: resolve to an absolute path.
   - Git URL: shallow-clone into
     `~/.cache/dotagents/skills/code-wiki/repos/<repo-slug>-<hash>/`.
2. Check repository state without changing it:
   - `git status --short` when `.git/` exists.
   - Do not revert, format, or modify the target repo.
3. Generate inventory:
   - `scripts/code-wiki inventory --repo <repo-path> --out <wiki-out>/data/inventory.json`
4. Read high-signal files first:
   - `README*`, `AGENTS.md`, `CONTRIBUTING*`, `docs/**`
   - dependency manifests and lockfiles
   - entrypoints found by inventory
   - config files that define routing, build, runtime, or deployment
5. Use fast search before deep reads:
   - `rg --files`
   - `rg -n "TODO|FIXME|route|router|controller|service|handler|main|server|config|env"`

## Dependency Manifests

Inspect these when present:

- JavaScript/TypeScript: `package.json`, lockfile, `tsconfig.json`, framework
  config, monorepo workspace config.
- Python: `pyproject.toml`, `requirements*.txt`, `setup.py`, `setup.cfg`,
  lockfile.
- Swift: `Package.swift`, `.xcodeproj`, `.xcworkspace`, `Podfile`.
- Go: `go.mod`, `go.sum`.
- Rust: `Cargo.toml`, `Cargo.lock`.
- JVM/Android: `build.gradle*`, `settings.gradle*`, `gradle.properties`.
- Docker/runtime: `Dockerfile*`, `docker-compose*`, deployment manifests.

For each dependency family, explain why it matters to runtime behavior. Avoid
listing every transitive package unless it shapes architecture or operations.

## Parallel Study Slices

When subagents are available and allowed, use independent read-only explorer
prompts. Do not ask subagents to write files. Ask for concise findings with
evidence paths and line numbers.

Architecture prompt:

```text
Study this repo read-only for architecture and module boundaries. Return the
main runtime components, ownership boundaries, important entrypoints, and the
best evidence paths/line numbers. Do not edit files.
```

Dependencies prompt:

```text
Study this repo read-only for dependencies, build tooling, runtime frameworks,
package managers, and deployment or local-run assumptions. Return only
high-signal findings with evidence paths/line numbers. Do not edit files.
```

Flows prompt:

```text
Study this repo read-only for user-facing, API, CLI, background, or data flows.
Identify basic happy paths and advanced/failure paths with evidence paths/line
numbers. Do not edit files.
```

Patterns prompt:

```text
Study this repo read-only for recurring code patterns, naming, layering, error
handling, configuration, tests, risks, and extension points. Return
evidence-backed findings with paths/line numbers. Do not edit files.
```

If delegation is unavailable, run these slices sequentially in the main agent.

## Evidence Rules

- Tie factual claims to source files, manifests, docs, or observed commands.
- Prefer exact local file paths and line numbers in page evidence callouts.
- Distinguish inference from confirmed behavior.
- Do not claim production behavior from comments alone unless no better source
  exists and the page labels it as a comment-derived inference.
- Do not expose secrets from `.env`, config, or credentials. Mention only key
  names when environment shape matters.

## Dirty Worktrees

If the target repo has uncommitted changes:

- Treat them as user-owned.
- Do not revert or format them.
- Note in the generated wiki metadata or final response that the analysis used
  the current working tree state.
- If changes directly affect the explained behavior, describe that the evidence
  came from the working tree, not necessarily the committed branch.
