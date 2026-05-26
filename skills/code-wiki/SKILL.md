---
name: code-wiki
description: Explore and study a local repository or git URL source code, then generate an evidence-backed linked HTML code wiki that gives a developer a comprehensive mental model of the codebase. Use when the user asks to study, understand, document, explain, map, or onboard onto a repo in depth, including repository scope, ownership boundaries, major modules, class/type/function interactions, call paths, dependencies, code patterns, basic and advanced flows, testing/ops, deterministic diagrams, optional conceptual images, and a browsable wiki artifact.
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

When delegation is explicitly authorized and allowed by the current runtime, use
read-only parallel explorer subagents for:

- architecture and module boundaries
- repository scope and ownership boundaries
- class/type/function collaboration and call paths
- dependencies, build, runtime, and tooling
- APIs, data flow, and user/business flows
- code patterns, conventions, risks, and extension points

If subagents are unavailable or not explicitly authorized, perform the same
slices sequentially. In all cases, require file-backed evidence and keep
synthesis in the main agent.

For multi-repo runs, strict runs, or repositories with `data/inventory.json`
`counts.files >= 500`, use reader subagents by default after generation unless
the user explicitly declines. Reader subagents must inspect only the generated
HTML/SVG wiki and report whether it is sufficient for expert developer
onboarding. Treat a reader FAIL as a real failure and iterate.

### 4. Scaffold and Fill the Wiki

Run:

```bash
scripts/code-wiki scaffold --out <wiki-out> --title <repo-name>
```

If the user asked to store cloned source locally beside the wiki, add:

```bash
scripts/code-wiki scaffold --out <wiki-out> --title <repo-name> --local-source-cache
```

Then replace placeholders using `references/wiki-html-contract.md`. Use the
template's documentation UI patterns: `lead` for page summaries, `meta-bar` for
compact repo/run facts, `doc-section` for substantive sections,
`diagram-frame` or `hybrid-diagram` for diagrams, and collapsible
`details.evidence` blocks when a section carries many source links.

Required output:

- `index.html`
- `pages/project-context.html`
- `pages/overview.html`
- `pages/public-interfaces.html`
- `pages/architecture.html`
- `pages/runtime-state.html`
- `pages/dependencies.html`
- `pages/code-patterns.html`
- `pages/flows-basic.html`
- `pages/flows-advanced.html`
- `pages/testing-and-ops.html`
- `pages/change-guide.html`
- `pages/source-map.html`
- `pages/deep-dives/index.html`
- `assets/style.css`
- `assets/app.js`
- `assets/diagrams/`
- `assets/images/`
- `data/inventory.json`

For large or multi-surface repositories, create two to five adaptive deep-dive
pages under `pages/deep-dives/`. Choose these pages from source evidence, not a
fixed taxonomy. Good deep dives usually follow the repo's natural subsystems:
public API families, protocol/runtime layers, plugin systems, storage models,
build matrices, language bindings, worker/event loops, or failure-prone
integration paths. Link every deep dive from `pages/deep-dives/index.html`.

Every non-trivial wiki must include structured, source-backed decision aids:

- a project context/use-case table with adoption constraints, governance,
  support, license, and official docs signals when present
- a public surface matrix that helps readers choose the right API, command,
  package export, route, plugin hook, schema, binding, or module surface
- a runtime state/lifecycle table naming state carriers, creators, mutators,
  observers, and cleanup owners
- an advanced failure table with triggers, detection branches, owner,
  caller/user effect, recovery, retry, fallback, abort, or rollback behavior
- exact validation command tables for testing and operations
- a change safety matrix with compatibility risk, validation, and rollback
  notes for common changes

Use deterministic local SVG or HTML diagrams for factual architecture, type or
module collaboration, and flow content. Every non-trivial wiki should include at
least:

- one component/module boundary diagram
- one interaction or call-path diagram showing how important types/modules
  collaborate
- one flow or lifecycle diagram for the primary runtime path

Diagrams must show relationships, not just labels. Use arrows with short
relationship verbs and readable labels. If a diagram truncates important text or
only repeats section headings, fix the diagram before reporting the wiki
complete.

For polished architecture or flow visuals, use a hybrid diagram path:

1. Build the source-backed diagram as deterministic SVG/HTML first.
2. Validate the exact nodes, arrows, labels, and layout.
3. Use `$imagegen` only as a visual polish pass from that SVG/spec.
4. Save the raster under `<wiki-out>/assets/images/`.
5. Keep or link the deterministic SVG adjacent to the raster, and add
   `data-source-diagram="../assets/diagrams/<name>.svg"` to the raster image.

Never let a generated bitmap replace the deterministic diagram for exact
topology, labels, or relationship evidence. If exact labels matter in the
polished visual, overlay them with deterministic SVG/HTML or keep the exact SVG
directly below the raster.

Keep page and asset links local so the wiki opens from `index.html` without a
server. For evidence references, prefer online commit-pinned source links when
the analyzed repo has a supported hosted remote.

For GitHub repos, generate source links with:

```bash
scripts/code-wiki evidence-link --repo <repo-path> --evidence <path:start-end> --html
```

Use the emitted evidence chip in wiki evidence blocks. For multiple refs, use:

```bash
scripts/code-wiki evidence-link --batch --repo <repo-path> --in <refs.txt|json|-> --html
```

Use the claim matrix as the page outline: every major section should map back to
ready claims, and every ready claim should be rendered as repo-specific prose,
tables, diagrams, or change guidance in its target page.

### 5. Use Images Selectively

Open `references/image-guidance.md` before generating images.

Use `$imagegen` for conceptual overview visuals, illustrative flow art, or the
hybrid diagram polish pass described above. Do not use generated images as the
only source for exact architecture, class names, API paths, dependency names, or
other factual claims.

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

Fix broken local links, missing pages, missing required assets, invalid
`data/inventory.json`, missing or incomplete `data/claim-matrix.json` in strict
runs, scaffold placeholders, thin or non-comprehensive page content, missing
clickable evidence links, invalid evidence paths, broad-only claim evidence,
reused broad evidence, duplicated claim text, and repeated boilerplate prose.
Warnings about empty diagrams are acceptable only if the user explicitly asked
for a minimal wiki; otherwise add deterministic diagram assets. Do not add
filler raster images only to satisfy validation.
If strict validation reports a polished diagram image without a deterministic
source diagram, add or link the SVG/spec instead of treating the raster as
authoritative.
If validation reports UI-pattern warnings, adjust the HTML structure rather
than hiding evidence or removing diagrams.

Validation prints `PASS` only for clean runs, `PASS_WITH_WARNINGS` when warnings
remain, and `FAIL` when errors remain. Report the exact status instead of
describing a warning-only run as a clean pass.

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
