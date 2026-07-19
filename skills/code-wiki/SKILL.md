---
name: code-wiki
description: Generate an evidence-backed linked HTML wiki for a local repository or git URL.
---

# Code Wiki

## Goal

Create a linked static HTML wiki that explains a repository from source
evidence. Cover what the repo does, how it is structured, which dependencies
matter, what patterns it uses, how the important flows work, and where a future
maintainer should look first.

The wiki must be useful to a developer who has never seen the codebase. It is
not enough to describe directories or list files. Build a mental model of:

- repository scope: what this repo owns, what it delegates to dependencies or
  external systems, and what is intentionally out of scope
- architecture: runtime components, ownership boundaries, public API surfaces,
  storage/network/process boundaries, and deployment/runtime shape
- interaction model: which classes, structs, protocols, traits, interfaces,
  modules, or key functions collaborate, who calls whom, and where state moves
- lifecycle and flows: startup, request/command/API/call paths, state
  transitions, failure paths, retries, async/background work, and cleanup
- developer change map: where to start for common changes, which tests protect
  those areas, and which extension points are intended versus incidental

Do not satisfy these sections with generic meta-prose about what a wiki should
do. Write repo-specific facts: concrete usage paths, public API contracts,
callers and callees, state carriers, branch conditions, cleanup owners, test
commands, and change recipes. If a sentence could apply to any repository,
replace it with a source-backed statement from this repository.

This skill is Codex-dependent. It can use:

- Codex subagents for parallel read-only repo study when the active runtime
  policy permits delegation.
- `$imagegen` for selected raster overview or conceptual images when a bitmap
  adds value beyond deterministic local diagrams.
- `~/.cache/dotagents/skills/code-wiki/` for default disposable git clones and
  temporary analysis artifacts.
- An explicit opt-in Markdown node-graph pilot that requires local `python3`,
  `git`, and the Codex CLI with `codex exec --ephemeral --json`, explicit model
  and reasoning-effort selection, and a non-bypass workspace sandbox.

Never put the final wiki in the cache. The durable wiki belongs in the
user-chosen output folder. If the user explicitly asks to store cloned source
locally beside the wiki, use the local wiki cache pattern instead of the global
cache.

## Optional Markdown Node-Graph Pilot

The normal workflow below remains the default. Select the pilot only when the
user explicitly asks to run or inspect the baseline/node-graph experiment; do
not infer it from an ordinary Code Wiki request.

Open `references/pilot.md` before a pilot run. It owns the shipped commands,
clean snapshot boundary, Markdown node contracts, typed manifests, actual
Codex token fields, identical reader evaluation, deterministic comparison
gates, and the `promote|revise|reject|inconclusive` result contract. A pilot
result is evidence only and never promotes or mutates the default workflow.

## Workflow

### 1. Resolve Target and Output

- Accept either a local repository path or a git URL.
- For a local path, analyze the repo in place without moving it.
- For a git URL, create or update a real Git clone under
  `~/.cache/dotagents/skills/code-wiki/repos/<repo-slug>-<hash>/`.
- Do not use archive downloads for git repos. Keep `.git/` metadata so the
  source can be fetched, pulled, and inspected with history.
- Do not use shallow clones by default because repo history may be useful for
  understanding architecture and evolution. If the repo is very large or the
  user asks for a fast snapshot, ask before using a shallow or partial clone.
- On repeat runs, update the clone with `git fetch --all --prune --tags` and
  fast-forward the checked-out branch when safe.
- If the user asks to store the cloned repo locally, clone under the
  selected wiki root at `code-wiki/.cache/sources/<repo-slug>/` and keep
  `code-wiki/.cache/.gitignore` as:
  ```gitignore
  *
  !.gitignore
  ```
  For multi-repo wiki output, keep one shared `code-wiki/.cache/sources/`
  folder with one source clone per repo slug.
- For every cloned git URL, record the exact clone path. This path must be
  included in the final response whether the clone lives in the global cache or
  in the wiki-local `.cache/sources/` folder.
- If the user did not provide an output path but clearly asks for the chat
  folder/current workspace, default to `<cwd>/code-wiki` and state that
  assumption. Otherwise ask where to write the wiki before creating files.
- Treat the output as a static HTML folder. Do not default to Markdown.

### 2. Build Inventory

Run the bundled helper from the skill root or with an absolute path:

```bash
scripts/code-wiki inventory --repo <repo-path> --out <wiki-out>/data/inventory.json
```

`scripts/code-wiki` is the only public helper artifact. The Python package
under `scripts/code_wiki/` is shipped internal runtime code; do not run those
module files directly in normal skill usage.

Use the inventory to identify manifests, source roots, test roots, docs,
entrypoint candidates, git metadata, and language/file counts. Then inspect the
real files that matter; the inventory is a routing aid, not the final
explanation.

Then create the claim matrix scaffold:

```bash
scripts/code-wiki synthesize --repo <repo-path> --inventory <wiki-out>/data/inventory.json --out <wiki-out>/data/claim-matrix.json
```

The claim matrix is the synthesis contract. Fill it with concrete, repo-specific
claims before or while writing HTML. Mark a claim `ready` only after it has a
target page, source evidence, and a maintainer-focused `why_it_matters`. Do not
use `synthesize` as a substitute for repo study; it only creates deterministic
structure from inventory.

### 3. Study the Repo and Fill the Claim Matrix

Open `references/repo-study-playbook.md` before a non-trivial wiki run.

When the active runtime policy permits delegation, use read-only parallel
explorer subagents when they materially improve coverage or speed for:

- architecture and module boundaries
- repository scope and ownership boundaries
- class/type/function collaboration and call paths
- dependencies, build, runtime, and tooling
- APIs, data flow, and user/business flows
- code patterns, conventions, risks, and extension points

Ask before delegation only when runtime policy requires it or when creating
visible user-owned Codex App threads. If internal subagents are unavailable or
disallowed, perform the same slices sequentially. In all cases, require
file-backed evidence and keep synthesis in the main agent.

For multi-repo runs, strict runs, or repositories with `data/inventory.json`
`counts.files >= 500`, run a generated-wiki review after generation. When the
active runtime policy permits delegation, use read-only reader subagents for
that review when useful; otherwise inspect the generated HTML/SVG sequentially.
Treat a reader FAIL as a real failure and iterate.

### 4. Scaffold and Fill the Wiki

Run the scaffold helper:

```bash
scripts/code-wiki scaffold --out <wiki-out> --title <repo-name>
```

If the user asked to store cloned source locally beside the wiki, add:

```bash
scripts/code-wiki scaffold --out <wiki-out> --title <repo-name> --local-source-cache
```

Then replace placeholders using `references/wiki-html-contract.md`. That
reference owns required pages and assets, page responsibilities, source-backed
decision aids, deterministic diagrams, evidence-chip commands, HTML rules,
deep-dive expectations, and validation semantics.

Use the claim matrix as the page outline: every major section should map back
to ready claims, and every ready claim should be rendered as repo-specific
prose, tables, diagrams, or change guidance in its target page.

### 5. Use Images Selectively

Open `references/image-guidance.md` before generating images.

Use `$imagegen` for conceptual overview visuals, illustrative flow art, or the
hybrid diagram polish pass described in `references/image-guidance.md`. Do not
use generated images as the only source for exact architecture, class names, API
paths, dependency names, or other factual claims.

Any project-referenced image must be copied into `<wiki-out>/assets/images/`.
Never leave a referenced image only under `$CODEX_HOME/generated_images/`.
For factual polished diagram images, verify the HTML includes
`data-source-diagram` pointing to the deterministic SVG/spec.

### 6. Validate

Before finishing, run:

```bash
scripts/code-wiki validate --wiki <wiki-out>
```

For multi-repo runs, strict runs, or repositories with `data/inventory.json`
`counts.files >= 500`, run:

```bash
scripts/code-wiki validate --wiki <wiki-out> --strict
```

Use `references/wiki-html-contract.md` to interpret validation failures and
warnings. Fix structural errors, weak evidence, thin pages, broken links,
missing deterministic diagrams, unsupported polished-image claims, and generic
filler before reporting the wiki complete. Load `references/options.md` and
report the exact canonical `validation_status` emitted by the validator. The
uppercase validation line is display text only.

## Output

Return the final wiki path, the analyzed repo path or git URL, validation
status, whether subagents were used, whether `$imagegen` was used, and any
important caveats.

For every git URL that was cloned, include a `Cloned source path:
<absolute-clone-path>` line. Do this for both default global-cache clones and
user-requested wiki-local clones. If the source was a local path and nothing was
cloned, say `Source was not cloned; analyzed local path:
<absolute-repo-path>`.

Do not claim the wiki is complete unless each major page has evidence-backed
developer-grade content, the wiki explains scope and interactions rather than
only file layout, and validation passes.

## References

- Canonical validation result option: `references/options.md`
- `references/repo-study-playbook.md`: source-study slices and claim quality.
- `references/wiki-html-contract.md`: required HTML output, page contract,
  diagrams, evidence links, and validation expectations.
- `references/image-guidance.md`: optional raster image and hybrid diagram
  rules.
- `references/pilot.md`: explicit opt-in baseline/node-graph execution,
  manifests, reader evaluation, and deterministic comparison.

## CLI Maintenance

- Normal runtime execution stays on `scripts/code-wiki`; the Python package
  under `scripts/code_wiki/` is internal to the shipped artifact.
- `scripts/code_wiki/version.py` is the single semver source of truth.
- CLI changes must preserve the standard-library-only package, update the
  shipped help and owner docs, and rerun `--help`, `--version`, `--json doctor`,
  the full unit suite, and a safe fixture-backed end-to-end check.
- Reads and `doctor` must not create config or signing keys. Live pilot runs may
  create and reuse the mode-0600 provenance key under
  `~/.cache/dotagents/skills/code-wiki/pilot/`. Pilot snapshots there are
  disposable; final wikis, manifests, raw evidence, and comparisons stay under
  user-selected outputs.
