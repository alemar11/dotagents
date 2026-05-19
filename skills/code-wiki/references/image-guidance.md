# Image Guidance

Use `$imagegen` only when a raster image improves the wiki beyond what local
HTML/SVG diagrams can do.

## When to Generate Images

Good uses:

- a conceptual repo overview image for `index.html`
- an illustrative lifecycle visual for a broad workflow
- an onboarding-style mental model image that avoids exact file/API names

Avoid raster images for:

- exact architecture topology
- dependency names and versions
- class/function/module names
- API paths or database schemas
- details that must be mechanically accurate

Use local SVG or HTML diagrams for factual content instead.

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

If a visual needs exact labels, build it as local HTML/SVG instead of
generating a bitmap.

## Multiple Images

For multiple conceptual images, issue one `$imagegen` call per distinct visual.
Do not batch unrelated prompts through one image request unless the current
imagegen skill explicitly supports that path.

## Final Checks

Before referencing an image from HTML:

- confirm it is saved under `<wiki-out>/assets/images/`
- verify the file path used by HTML exists
- make sure the page text carries the factual explanation, not the bitmap alone
- note in the final response if images were skipped or intentionally limited
