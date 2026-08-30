# TanStack Highlight

Use this reference when a task involves `@tanstack/highlight`, selective syntax
highlighting, explicit language registration, SSR-safe code rendering, theme
generation, line or range annotations, framework code blocks, or Markdown
pipelines.

TanStack Highlight is a pre-1.0, synchronous highlighter optimized for blogs
and documentation. Inspect the installed version and supported languages before
depending on exact package subpaths or output contracts.

## Ownership Boundaries

- Highlight owns registered language tokenization, escaped semantic HTML,
  stable class names, themes, and annotation metadata.
- The application owns which languages ship, code-source trust, CSS placement,
  container markup, copy controls, line numbers, and product presentation.
- Markdown owns its `<pre><code>` tree when the two products integrate;
  Highlight supplies trusted inner token markup through the documented adapter.

## Workflow

1. Inventory the real language set.
   Register only the languages the product renders and include embedded
   dependencies such as JavaScript or CSS when HTML examples need them.
2. Create one reusable highlighter.
   Keep it at module scope and use the same configured instance during SSR and
   client rendering; no asynchronous initialization is required.
3. Generate theme CSS once.
   Select light and dark themes, define the dark-mode selector, and install the
   returned CSS at the application boundary.
4. Keep the HTML boundary explicit.
   Insert only output returned directly by Highlight, and do not treat
   arbitrary pre-rendered HTML as equivalent trusted output.
5. Verify representative code.
   Test every registered language, embedded regions, unknown-language behavior,
   SSR and hydration parity, themes, annotations, and Markdown integration.

## Default Rules

- Prefer selective imports from `core`, `languages/*`, `theme`, and
  `themes/*` over broad convenience imports.
- Reuse the highlighter and theme CSS rather than rebuilding them per render.
- Keep source language explicit; do not assume automatic language detection.
- Preserve the stable semantic HTML tree and style its classes externally.

## Avoid

- Registering every available language by default.
- Re-highlighting solely because the color theme changed.
- Passing Highlight's complete wrapper into a Markdown callback that already
  owns `<pre><code>`.
- Assuming TextMate grammar compatibility or editor-grade semantic tokens.

## Verification

Use current TanStack Highlight overview, installation, quick-start, language,
theme, annotation, Markdown-pipeline, and comparison docs. When available, use
the installed first-party Intent skill matching the target integration.
