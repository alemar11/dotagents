# Repo Study Playbook

Use this reference for non-trivial `code-wiki` runs. Keep the work read-only
against the target repo until the output wiki path is resolved.

## Discovery Order

1. Confirm target type.
   - Local path: resolve to an absolute path.
   - Git URL by default: clone or update a real Git checkout under
     `~/.cache/dotagents/skills/code-wiki/repos/<repo-slug>-<hash>/`.
   - Git URL when the user asks to store cloned source locally beside the wiki:
     clone into `code-wiki/.cache/sources/<repo-slug>/` under the
     selected wiki root.
   - For local wiki source storage, create `code-wiki/.cache/.gitignore` with:
     ```gitignore
     *
     !.gitignore
     ```
   - Record the exact resolved source path immediately. For git URLs, this is
     the clone path and must be reported at the end of the flow.
2. Check repository state without changing it:
   - `git status --short` when `.git/` exists.
   - Do not revert, format, or modify the target repo.
3. Generate inventory:
   - `scripts/code-wiki inventory --repo <repo-path> --out <wiki-out>/data/inventory.json`
   - Treat `source_roots` as primary study hints. Use `root_candidates`
     to separate source, test, docs, examples, fixtures, and vendored roots
     before assigning study work.
   - Treat `interface_roots` as public API hints for C-family and similar
     repos. They are usually headers or interface definitions, not secondary
     documentation.
   - Treat `generated-docs` roots as secondary evidence. They can help explain
     public API surfaces, but they should not outweigh source, manifests, or
     authored docs.
   - Include `ops` roots in testing-and-ops study slices so CI workflows and
     release automation are not lost behind source-only scans.
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
- C/C++ and native builds: `CMakeLists.txt`, `configure`, `configure.ac`,
  `Makefile*`, `meson.build`, `BUILD.bazel`, Visual Studio solutions/projects.
- JVM/Android: `build.gradle*`, `settings.gradle*`, `gradle.properties`.
- Docker/runtime: `Dockerfile*`, `docker-compose*`, deployment manifests.

For each dependency family, explain why it matters to runtime behavior. Avoid
listing every transitive package unless it shapes architecture or operations.

## Language-Specific Root Checks

Before synthesis, sanity-check the inventory against language conventions:

- Go libraries may keep primary `.go` files and `*_test.go` tests at repo
  root; do not require `src/` or `tests/`.
- Rust workspaces may define binaries outside `src/main.rs`, especially in
  `crates/<name>/main.rs` or manifest-declared paths.
- JavaScript and TypeScript monorepos often contain `packages/*/src`,
  `playground/*`, templates, and generated `dist`; classify these before
  treating every `src` as product source.
- C and C++ projects frequently split implementation under `src/` or `lib/`
  from public API under `include/`. They may also vendor large `deps/`,
  `third_party/`, or `vendor/` trees; inspect build files to decide which
  bundled dependencies shape runtime behavior without promoting vendored source
  roots to primary architecture.
- Ruby projects may use `exe/`, `lib/`, gemspecs, Rake tasks, Cucumber
  features, and dynamic registration through `autoload` or DSLs.
- Swift packages may include `Sources/`, `Tests/`, `Examples/`, plugins, tools,
  DocC bundles, and path names with spaces.
- Swift libraries may also use singular `Source/` and generated Jazzy docs
  under `docs/`; prefer source and authored documentation for architecture.

## Parallel Study Slices

Use independent read-only explorer prompts only when the user explicitly asks for
subagents/delegation/parallel agent work and the current runtime allows it. Do
not treat ordinary `$code-wiki` invocation as implicit delegation permission. Do
not ask subagents to write files. Ask for concise findings with evidence paths
and line numbers.

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

If delegation is unavailable or not explicitly authorized, run these slices
sequentially in the main agent.

## Evidence Rules

- Tie factual claims to source files, manifests, docs, or observed commands.
- Prefer exact local file paths and line numbers while studying.
- In generated pages, render source evidence as clickable chips. For GitHub
  repos, use commit-pinned online blob links from the analyzed commit.
- Use `scripts/code-wiki evidence-link --repo <repo-path> --evidence
  <path:start-end> --html` to create GitHub evidence chips when supported.
- Distinguish inference from confirmed behavior.
- Do not claim production behavior from comments alone unless no better source
  exists and the page labels it as a comment-derived inference.
- Do not expose secrets from `.env`, config, or credentials. Mention only key
  names when environment shape matters.

## Completion Notes

The final response must state:

- whether subagents were used
- whether `$imagegen` was used
- the analyzed commit or dirty working-tree caveat when available
- the cloned source path for every cloned git URL

## Dirty Worktrees

If the target repo has uncommitted changes:

- Treat them as user-owned.
- Do not revert or format them.
- Note in the generated wiki metadata or final response that the analysis used
  the current working tree state.
- If changes directly affect the explained behavior, describe that the evidence
  came from the working tree, not necessarily the committed branch.

## Source Clone Storage

Default remote-source clones live under
`~/.cache/dotagents/skills/code-wiki/repos/` because they are disposable and
recoverable from the git URL.

Use project-local source storage only when the user asks for wording such as
"store the repo locally", "keep the source beside the wiki", "self-contained
wiki", or "put the cloned repos in code-wiki". In that mode:

- Use `<wiki-root>/.cache/sources/<repo-slug>/` for cloned source.
- Keep `<wiki-root>/.cache/.gitignore` committed or present with:
  ```gitignore
  *
  !.gitignore
  ```
- Do not put final HTML pages, diagrams, images, or `data/inventory.json` under
  `.cache/`.
- Exclude `code-wiki/` and `.cache/` from future source inventories to avoid
  recursively studying generated wiki output or cached clone copies.

## Git Clone Policy

For git URLs, use a real Git clone instead of archive downloads so future wiki
refinement can fetch updates, pull branch changes, and inspect commit history.

Default first clone:

```bash
git clone <git-url> <clone-path>
```

Default refresh for an existing clone:

```bash
git -C <clone-path> fetch --all --prune --tags
git -C <clone-path> pull --ff-only
```

If `pull --ff-only` fails because the clone is detached, on a different branch,
or has local changes, do not force-reset. Report the current branch/HEAD and use
the fetched checkout as-is unless the user asks to change refs.

Do not use `git archive`, source ZIP downloads, or shallow clones by default.
Use `--depth`, `--filter`, or another reduced-history clone only when the repo is
too large or the user explicitly asks for a fast snapshot; label the wiki as
based on limited history in that case.

At completion, always report the cloned source path for every git URL. Expand
`~` to the actual absolute home path in the final response:

- Default mode: `Cloned source path: <absolute-home>/.cache/dotagents/skills/code-wiki/repos/<repo-slug>-<hash>/`
- Local mode: `Cloned source path: <wiki-root>/.cache/sources/<repo-slug>/`

If the target was a local path and no clone happened, report the analyzed local
source path instead of pretending there is a cloned source.
