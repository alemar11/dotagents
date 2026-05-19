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
  data/
    inventory.json
```

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

- Use semantic HTML with local links only.
- Link pages through relative paths.
- Link assets under `assets/`.
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

Each major section should include an evidence block with links or textual
references to the files that support the claim. Use compact phrasing:

```html
<aside class="evidence">
  Evidence: <code>src/server.ts:18</code>, <code>package.json:6</code>
</aside>
```

If exact line numbers are unavailable, cite the narrowest path and explain why.

## Validation Expectations

Run:

```bash
scripts/code-wiki validate --wiki <wiki-out>
```

Validation must pass before the wiki is reported complete. Fix missing pages,
broken local links, missing assets, and invalid `data/inventory.json`.
