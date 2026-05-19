# HTML Wiki Contract

The `code-wiki` output is a static, linked HTML folder. It should open from
`index.html` without a local server and without external CDN dependencies.

## Required Structure

```text
<wiki-out>/
  index.html
  pages/
    overview.html
    architecture.html
    dependencies.html
    code-patterns.html
    flows-basic.html
    flows-advanced.html
    testing-and-ops.html
    file-map.html
  assets/
    style.css
    app.js
    diagrams/
    images/
  .cache/              # optional local source cache when explicitly requested
    .gitignore
    sources/
  data/
    inventory.json
```

The `.cache/` folder is optional. Create it only when the user asks to keep
cloned source repos locally beside the wiki. It must contain a `.gitignore`
that ignores everything except itself.

## Page Responsibilities

- `index.html`: navigation hub, repo name, generation context, and page cards.
- `overview.html`: repository scope, what the repo owns, what it delegates or
  leaves out of scope, audience, runtime shape, core concepts, and the shortest
  mental model for a new developer. Include how the project is used by a
  consumer, caller, CLI user, library user, application, or downstream package.
- `architecture.html`: modules, boundaries, data stores, external systems, and
  deterministic diagrams. Must include a component/module map and a
  class/type/function interaction map that explains important collaborators,
  not only directories. The text must name who creates, calls, owns, mutates,
  registers, or observes whom.
- `dependencies.html`: dependency manifests, frameworks, build/runtime tools,
  package managers, noteworthy version constraints, and how dependencies shape
  runtime behavior or repo boundaries.
- `code-patterns.html`: conventions, naming, layering, configuration, error
  handling, testing style, extension patterns, state ownership, and the
  difference between public extension points and incidental internals.
- `flows-basic.html`: main happy-path flows a maintainer must understand first.
  Trace at least one path from public entrypoint through the key collaborators.
  Include the caller, callee, state carrier, return/callback/output, and the
  source-backed function/module handoffs.
- `flows-advanced.html`: edge cases, retries, async/background work,
  integrations, failure modes, state transitions, cleanup, and operational
  hazards. Identify branch conditions, failure triggers, cancellation/abort
  ownership, timeout/retry/fallback behavior, overload handling, and shutdown or
  resource cleanup where present.
- `testing-and-ops.html`: local run, tests, CI, deployment, observability,
  environment variables, and operator caveats. Map common change types to the
  exact validation commands, test files, CI matrix entries, release checks, or
  package checks that protect them.
- `file-map.html`: directory/file responsibilities and where to start for
  common changes. Include a developer change guide that maps likely change
  requests to files, collaborators, and tests. For large repos, include several
  task-specific recipes instead of broad "start here" advice.

## Comprehension Bar

Validation passing should mean the wiki is substantively useful for onboarding.
Each major page should contain multiple evidence-backed sections and explain
relationships between code units. A complete wiki should answer:

- What is in scope for this repo, and what is out of scope?
- Which modules/classes/types/functions collaborate on the primary runtime path?
- What are the public APIs or extension points?
- Where is state created, mutated, persisted, or handed across boundaries?
- What happens on startup, the main happy path, failure paths, and shutdown?
- Where should a developer start for common changes, and how should they test?

Do not fill pages with generic prose, dependency lists, or directory summaries
alone. Every architectural claim should be backed by evidence that proves the
relationship, such as constructor calls, registration tables, imports,
inheritance/conformance, route wiring, command dispatch, build target links, or
callback assignments.

Avoid meta-prose about what a good wiki should do. Phrases like "a useful wiki
must", "this page should", "a good onboarding wiki", or "language-neutral
terms" are signs of filler. Replace them with repo-specific facts, examples,
call paths, failure branches, and change recipes.

For non-trivial repositories, include a compact usage example or usage-shaped
walkthrough. This does not need to be executable code, but it must answer how a
developer or downstream consumer enters the system and which public APIs,
commands, routes, structs, classes, modules, or functions they touch first.

## HTML Rules

- Use semantic HTML.
- Link pages through relative paths.
- Link assets under `assets/`.
- Use online commit-pinned links for source evidence when the analyzed source
  has a supported hosted remote.
- Keep CSS and JavaScript local.
- Do not require Mermaid CDN or remote scripts at view time.
- Escape source-derived text before putting it into HTML.
- Keep long code excerpts short. Prefer paraphrase plus file links/evidence.
- Wrap tables in `.table-wrap`. The default template stacks table rows on
  narrow Codex split-pane widths; do not rely on body-level horizontal
  scrolling for important content.

## Diagrams

Use deterministic diagrams for facts:

- Local SVG files under `assets/diagrams/` are preferred for architecture and
  request/data flows.
- `.mmd` files may be kept beside rendered SVG as editable source, but pages
  should embed or link a rendered local asset.
- Do not rely on generated raster images for exact topology.

Recommended diagram set:

- `assets/diagrams/architecture.svg`
- `assets/diagrams/interaction-map.svg`
- `assets/diagrams/basic-flow.svg`
- `assets/diagrams/advanced-flow.svg`
- `assets/diagrams/dependency-map.svg`

`architecture.svg` should show component/module boundaries.
`interaction-map.svg` should show class/type/function/module collaboration.
Flow diagrams should show ordered calls, state changes, or message movement.

Diagrams must add information beyond a list of labels. Use directed edges with
short verb labels such as "creates", "dispatches", "mutates", "renders",
"polls", "calls", "wraps", "emits", or "cancels". Split long labels across
lines and test narrow viewport rendering; truncated diagram text is a content
defect, not only a styling issue.

Avoid generic edge-label sets like `owns/feeds/supports`,
`calls/returns/extends`, `starts/dispatches/emits`, or
`branches/recovers/cleans` unless the surrounding diagram also contains
repo-specific relationship labels. A generated diagram should let a reader
understand a real call path or ownership boundary without reading the adjacent
paragraph.

## Evidence Callouts

Each major section should include an evidence block with clickable links to the
files that support the claim. For GitHub-hosted repos, use commit-pinned blob
URLs generated from the analyzed commit:

```html
<aside class="evidence">
  Evidence:
  <span class="evidence-list">
    <a class="evidence-chip" href="https://github.com/org/repo/blob/<commit>/src/server.ts#L18" data-evidence="src/server.ts:18" title="src/server.ts:18" target="_blank" rel="noopener noreferrer"><span class="evidence-file">server.ts</span><span class="evidence-lines">L18</span></a>
    <a class="evidence-chip" href="https://github.com/org/repo/blob/<commit>/package.json#L6" data-evidence="package.json:6" title="package.json:6" target="_blank" rel="noopener noreferrer"><span class="evidence-file">package.json</span><span class="evidence-lines">L6</span></a>
  </span>
</aside>
```

For GitHub sources, generate chips with:

```bash
scripts/code-wiki evidence-link --repo <repo-path> --evidence <path:start-end> --html
```

Evidence chip text should stay compact. Put the full `path:start-end` in the
`data-evidence` and `title` attributes, render the visible file label as the
basename, and render the line range as a small secondary label. Do not show long
source paths as the primary visible chip text.

Unsupported remotes may fall back to local source references, but do not guess
host-specific URL formats.

If exact line numbers are unavailable, cite the narrowest path and explain why.

## Validation Expectations

Run:

```bash
scripts/code-wiki validate --wiki <wiki-out>
```

Validation must pass before the wiki is reported complete. Fix missing pages,
broken local links, missing assets, invalid `data/inventory.json`, scaffold
placeholders, missing clickable evidence links, invalid evidence paths, and
evidence links that are not pinned to the analyzed commit when a supported
remote exists.

The validator also rejects thin pages. A page can fail even when links are
valid if it lacks enough sections, evidence-backed claims, or required
developer-comprehension topics such as scope, ownership boundaries,
interactions, lifecycle, state/failure handling, and change-guide coverage.
It also rejects known generic wiki meta-prose because word count alone is not
evidence of developer-grade content.
Major pages are expected to carry multiple source links, not only one broad
evidence block. Advanced flow and file-map pages should cite the specific
functions, branches, tests, and owner files they discuss.
