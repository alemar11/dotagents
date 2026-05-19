---
name: code-wiki
description: Explore and study a local repository or git URL source code, then generate an evidence-backed linked HTML code wiki from that analysis. Use when the user asks to study, understand, document, explain, map, or onboard onto a repo in depth, including architecture, dependencies, code patterns, basic and advanced flows, diagrams, selected generated images, and a browsable wiki artifact produced through parallel repo-study subagents when available.
---

# Code Wiki

## Goal

Create a linked static HTML wiki that explains a repository from source
evidence. Cover what the repo does, how it is structured, which dependencies
matter, what patterns it uses, how the important flows work, and where a future
maintainer should look first.

This skill is Codex-dependent. It relies on:

- Codex subagents for parallel read-only repo study when the current runtime
  allows delegation.
- `$imagegen` for selected raster overview or conceptual images.
- `~/.cache/dotagents/skills/code-wiki/` for disposable git clones and
  temporary analysis artifacts only.

Never put the final wiki in the cache. The durable wiki belongs in the
user-chosen output folder.

## Workflow

### 1. Resolve Target and Output

- Accept either a local repository path or a git URL.
- For a local path, analyze the repo in place without moving it.
- For a git URL, create or refresh a shallow clone under
  `~/.cache/dotagents/skills/code-wiki/repos/<repo-slug>-<hash>/`.
- If the user did not provide an output path, ask where to write the wiki before
  creating files.
- Treat the output as a static HTML folder. Do not default to Markdown.

### 2. Build Inventory

Run the bundled helper from the skill root or with an absolute path:

```bash
scripts/code-wiki inventory --repo <repo-path> --out <wiki-out>/data/inventory.json
```

Use the inventory to identify manifests, source roots, test roots, docs,
entrypoint candidates, and language/file counts. Then inspect the real files
that matter; the inventory is a routing aid, not the final explanation.

### 3. Study the Repo

Open `references/repo-study-playbook.md` before a non-trivial wiki run.

When delegation is available and allowed for the request, use read-only
parallel explorer subagents for:

- architecture and module boundaries
- dependencies, build, runtime, and tooling
- APIs, data flow, and user/business flows
- code patterns, conventions, risks, and extension points

If subagents are unavailable, perform the same slices sequentially. In all
cases, require file-backed evidence and keep synthesis in the main agent.

### 4. Scaffold and Fill the Wiki

Run:

```bash
scripts/code-wiki scaffold --out <wiki-out> --title <repo-name>
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
content. Keep links local so the wiki opens from `index.html` without a server.

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

Fix broken local links, missing pages, missing assets, or invalid
`data/inventory.json`. Warnings about empty diagrams or images are acceptable
only if the user explicitly asked for a minimal wiki; otherwise add the
expected assets.

## Output

Return the final wiki path, the analyzed repo path or git URL, validation
status, and any important caveats such as skipped image generation or missing
subagent support.

Do not claim the wiki is complete unless each major page has evidence-backed
content and validation passes.
