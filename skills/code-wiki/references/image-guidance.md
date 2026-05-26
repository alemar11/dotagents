# Image Guidance

Use `$imagegen` only when a raster image improves the wiki beyond what local
HTML/SVG diagrams can do. It is optional; do not generate filler images only
because the wiki has an `assets/images/` folder.

## When to Generate Images

Good uses:

- a conceptual repo overview image for `index.html`
- an illustrative lifecycle visual for a broad workflow
- an onboarding-style mental model image that avoids exact file/API names

Avoid raster images as the only source of truth for:

- exact architecture topology
- dependency names and versions
- class/function/module names
- API paths or database schemas
- details that must be mechanically accurate

Use local SVG or HTML diagrams for factual content first. Exact architecture,
dependency graphs, and source-level flows should remain deterministic and
reviewable.

## Hybrid Diagram Polish

For architecture or flow diagrams that would benefit from stronger visual
presentation, use this hybrid path:

1. Create a canonical diagram spec from source-backed claims: nodes, edges,
   relationship labels, evidence refs, and intended layout.
2. Render the deterministic SVG under `<wiki-out>/assets/diagrams/`.
3. Validate the SVG for exact nodes, arrows, labels, and readable layout.
4. Use `$imagegen` only as a polish pass, with the SVG/spec as the reference.
5. Save the raster image under `<wiki-out>/assets/images/`.
6. Keep the SVG in the page or link it adjacent to the raster.

The generated raster must not be the only factual diagram. In HTML, add a
`data-source-diagram` attribute on the raster image that points to the
deterministic SVG or canonical JSON spec, for example:

```html
<figure class="hybrid-diagram">
  <img src="../assets/images/architecture-overview.png"
       alt="Polished architecture overview"
       data-source-diagram="../assets/diagrams/architecture.svg">
  <figcaption>Polished overview generated from the deterministic architecture diagram.</figcaption>
</figure>
```

Do not let `$imagegen` own exact text. If exact labels must be shown, either
overlay deterministic SVG/HTML labels on top of a raster background or keep the
exact SVG directly below the polished visual.

## Built-In Imagegen Path

Use the default built-in `$imagegen` path for normal image generation. Do not
ask for `OPENAI_API_KEY` unless the user explicitly requests the imagegen CLI
fallback or true native transparency.

After generation, move or copy the selected project-referenced image from
`$CODEX_HOME/generated_images/...` into:

```text
<wiki-out>/assets/images/
```

Never leave a referenced wiki image only under `$CODEX_HOME/*`.

## Prompt Pattern

Use this compact prompt shape for conceptual visuals:

```text
Use case: infographic-diagram
Asset type: static HTML code wiki overview image
Primary request: conceptual visual explaining the repository as a maintainable software system
Style/medium: clean editorial technical illustration, no tiny text
Composition/framing: wide image with clear sections and generous whitespace
Constraints: do not include exact class names, API paths, dependency versions, secrets, logos, or watermarks
Avoid: dense unreadable labels, invented product branding, misleading topology
```

If a visual needs exact labels, build and validate the local HTML/SVG first,
then optionally use the hybrid polish path above.

## Multiple Images

For multiple conceptual images, issue one `$imagegen` call per distinct visual.
Do not batch unrelated prompts through one image request unless the current
imagegen skill explicitly supports that path.

## Final Checks

Before referencing an image from HTML:

- confirm it is saved under `<wiki-out>/assets/images/`
- verify the file path used by HTML exists
- verify factual diagram images point to their deterministic source with
  `data-source-diagram`
- make sure the page text carries the factual explanation, not the bitmap alone
- note in the final response if images were skipped or intentionally limited
- state whether `$imagegen` was used
