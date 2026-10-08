# TanStack Highlight

Use this reference when a task involves `@tanstack/highlight`, selective syntax
highlighting, explicit language registration, SSR-safe code rendering, theme
generation, line or range annotations, framework code blocks, or Markdown
pipelines.

TanStack Highlight now ships a 1.x synchronous highlighter optimized for blogs
and documentation. Existing 0.x ranges do not select 1.x; inspect the installed
version and supported languages before upgrading. The 1.0 release preserves
0.1 entry points and APIs, but parser fixes can change token spans and colors
without changing source text or the semantic HTML contract.

## Ownership Boundaries

- Highlight owns registered language tokenization, escaped semantic HTML,
  stable class names, themes, and annotation metadata.
- The application owns which languages ship, code-source trust, CSS placement,
  container markup, copy controls, line numbers, and product presentation.
- Markdown owns its `<pre><code>` tree when the two products integrate;
  `createTanStackMarkdownHighlighter` from `@tanstack/highlight/markdown`
  supplies escaped inner token markup. See [Markdown](markdown.md) for the
  parser and content-trust boundary.

## Workflow

1. Inventory the real language set.
   Register only the languages the product renders and include embedded
   dependencies such as JavaScript or CSS when HTML examples need them.
   Version 1.1 adds selective Swift, Java, Kotlin, Rust, Ruby, C#, Dart, Lua,
   and Perl definitions; check the [language inventory](https://tanstack.com/highlight/latest/docs/language-inventory)
   against the installed version rather than assuming every 1.x includes them.
2. Create one reusable highlighter.
   Keep it at module scope and use the same version, registrations, and options
   during SSR and client rendering; no asynchronous initialization is required.
   Do not re-highlight server-rendered blocks merely to hydrate them.
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
- Preserve the stable semantic HTML tree and style its classes externally;
  exact token boundaries and complete HTML snapshots are not frozen in 1.x.
- Treat language definitions and theme CSS as trusted application configuration.
  Bound untrusted code sizes or isolate expensive work off the UI thread.

## Avoid

- Registering every available language by default.
- Re-highlighting solely because the color theme changed.
- Passing Highlight's complete wrapper into a Markdown callback that already
  owns `<pre><code>`. Use `/remark` for mdast pipelines and `/rehype` for
  existing HAST code blocks; `languages/markdown` highlights Markdown source
  and does not replace those rendering adapters.
- Assuming TextMate grammar compatibility or editor-grade semantic tokens.

## Verification

Use current TanStack Highlight installation, language, theme, annotation,
Markdown-pipeline, and [v1 migration](https://tanstack.com/highlight/latest/docs/guides/migrating-to-v1)
docs. The runtime package is ESM-only, supports Node.js 18+, and needs no
framework peers. Prefer the installed first-party Intent skill matching the
target integration; [Intent](intent.md) owns discovery and trust guidance.
