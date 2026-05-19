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
- `overview.html`: what the repo does, audience, runtime shape, core concepts.
- `architecture.html`: modules, boundaries, data stores, external systems, and
  deterministic diagrams.
- `dependencies.html`: dependency manifests, frameworks, build/runtime tools,
  package managers, and noteworthy version constraints.
- `code-patterns.html`: conventions, naming, layering, configuration, error
  handling, testing style, and extension patterns.
- `flows-basic.html`: main happy-path flows a maintainer must understand first.
- `flows-advanced.html`: edge cases, retries, async/background work,
  integrations, failure modes, and operational hazards.
- `testing-and-ops.html`: local run, tests, CI, deployment, observability,
  environment variables, and operator caveats.
- `file-map.html`: directory/file responsibilities and where to start for
  common changes.

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

## Diagrams

Use deterministic diagrams for facts:

- Local SVG files under `assets/diagrams/` are preferred for architecture and
  request/data flows.
- `.mmd` files may be kept beside rendered SVG as editable source, but pages
  should embed or link a rendered local asset.
- Do not rely on generated raster images for exact topology.

Recommended diagram set:

- `assets/diagrams/architecture.svg`
- `assets/diagrams/basic-flow.svg`
- `assets/diagrams/advanced-flow.svg`
- `assets/diagrams/dependency-map.svg`

## Evidence Callouts

Each major section should include an evidence block with clickable links to the
files that support the claim. For GitHub-hosted repos, use commit-pinned blob
URLs generated from the analyzed commit:

```html
<aside class="evidence">
  Evidence:
  <span class="evidence-list">
    <a class="evidence-chip" href="https://github.com/org/repo/blob/<commit>/src/server.ts#L18" target="_blank" rel="noopener noreferrer"><code>src/server.ts:18</code></a>
    <a class="evidence-chip" href="https://github.com/org/repo/blob/<commit>/package.json#L6" target="_blank" rel="noopener noreferrer"><code>package.json:6</code></a>
  </span>
</aside>
```

For GitHub sources, generate chips with:

```bash
scripts/code-wiki evidence-link --repo <repo-path> --evidence <path:start-end> --html
```

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
