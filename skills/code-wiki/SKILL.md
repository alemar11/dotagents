---
name: code-wiki
description: Explore and study a local repository or git URL source code, then generate an evidence-backed linked HTML code wiki from that analysis. Use when the user asks to study, understand, document, explain, map, or onboard onto a repo in depth, including architecture, dependencies, code patterns, basic and advanced flows, diagrams, optional conceptual images, and a browsable wiki artifact.
---

# Code Wiki

## Goal

Create a linked static HTML wiki that explains a repository from source
evidence. Cover what the repo does, how it is structured, which dependencies
matter, what patterns it uses, how the important flows work, and where a future
maintainer should look first.

This skill is Codex-dependent. It can use:

- Codex subagents for parallel read-only repo study only when the user and
  current runtime explicitly allow delegation.
- `$imagegen` for selected raster overview or conceptual images when a bitmap
  adds value beyond deterministic local diagrams.
- `~/.cache/dotagents/skills/code-wiki/` for default disposable git clones and
  temporary analysis artifacts.

Never put the final wiki in the cache. The durable wiki belongs in the
user-chosen output folder. If the user explicitly asks to store cloned source
locally beside the wiki, use the local wiki cache pattern instead of the global
cache.

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

Use the inventory to identify manifests, source roots, test roots, docs,
entrypoint candidates, git metadata, and language/file counts. Then inspect the
real files that matter; the inventory is a routing aid, not the final
explanation.

### 3. Study the Repo

Open `references/repo-study-playbook.md` before a non-trivial wiki run.

When delegation is explicitly authorized and allowed by the current runtime, use
read-only parallel explorer subagents for:

- architecture and module boundaries
- dependencies, build, runtime, and tooling
- APIs, data flow, and user/business flows
- code patterns, conventions, risks, and extension points

If subagents are unavailable or not explicitly authorized, perform the same
slices sequentially. In all cases, require file-backed evidence and keep
synthesis in the main agent.

### 4. Scaffold and Fill the Wiki

Run:

```bash
scripts/code-wiki scaffold --out <wiki-out> --title <repo-name>
```

If the user asked to store cloned source locally beside the wiki, add:

```bash
scripts/code-wiki scaffold --out <wiki-out> --title <repo-name> --local-source-cache
```

Then replace placeholders using `references/wiki-html-contract.md`.

Required output:

- `index.html`
- `pages/overview.html`
- `pages/architecture.html`
- `pages/dependencies.html`
- `pages/code-patterns.html`
- `pages/flows-basic.html`
- `pages/flows-advanced.html`
- `pages/testing-and-ops.html`
- `pages/file-map.html`
- `assets/style.css`
- `assets/app.js`
- `assets/diagrams/`
- `assets/images/`
- `data/inventory.json`

Use deterministic local SVG or HTML diagrams for factual architecture and flow
content. Keep page and asset links local so the wiki opens from `index.html`
without a server. For evidence references, prefer online commit-pinned source
links when the analyzed repo has a supported hosted remote.

For GitHub repos, generate source links with:

```bash
scripts/code-wiki evidence-link --repo <repo-path> --evidence <path:start-end> --html
```

Use the emitted evidence chip in wiki evidence blocks.

### 5. Use Images Selectively

Open `references/image-guidance.md` before generating images.

Use `$imagegen` only for conceptual overview visuals or illustrative flow art
that benefits from a raster image. Do not use generated images as the only
source for exact architecture, class names, API paths, dependency names, or
other factual claims.

Any project-referenced image must be copied into `<wiki-out>/assets/images/`.
Never leave a referenced image only under `$CODEX_HOME/generated_images/`.

### 6. Validate

Before finishing, run:

```bash
scripts/code-wiki validate --wiki <wiki-out>
```

Fix broken local links, missing pages, missing required assets, invalid
`data/inventory.json`, scaffold placeholders, missing clickable evidence links,
and invalid evidence paths. Warnings about empty diagrams are acceptable only if
the user explicitly asked for a minimal wiki; otherwise add deterministic
diagram assets. Do not add filler raster images only to satisfy validation.

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
content and validation passes.
