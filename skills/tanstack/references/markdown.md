# TanStack Markdown

Use this reference when a task involves `@tanstack/markdown`, deterministic
Markdown parsing, serializable Markdown ASTs, HTML rendering, React or Octane
rendering, documentation extensions, AI-stream rendering, or syntax-highlighter
integration.

TanStack Markdown now ships a 1.x release with a focused TanStack documentation
syntax profile rather than full CommonMark, GFM, or MDX compatibility. Inspect
the installed version and confirm that the input corpus fits the supported
profile before adopting or migrating; a 0.x dependency range will not select 1.x.

## Ownership Boundaries

- Markdown owns parsing, its serializable AST, safe-default HTML output, and
  matching HTML, React, and Octane rendering semantics.
- The application owns content trust, storage, URL policy, component mapping,
  cache invalidation, styling, and the decision to enable raw HTML.
- Syntax highlighting stays an explicit callback boundary; use TanStack
  Highlight or another selected highlighter rather than coupling it implicitly.

## Workflow

1. Choose the narrowest entry point.
   Use `parseMarkdown` from `@tanstack/markdown/parser`, `renderHtml` from
   `@tanstack/markdown/html`, or `Markdown` from `/react` or `/octane`.
   The ESM parser and HTML renderer need no framework peers; install only the
   selected adapter's peers (React 18+ or Octane 0.1.12+ for 1.0).
2. Establish the content trust model.
   Keep raw HTML disabled unless trusted content and product requirements make
   it necessary; review link, image, and executable-URL handling.
3. Parse once when content is reused.
   Cache or serialize the deterministic document for build-time or repeated
   rendering instead of reparsing unchanged source across boundaries.
4. Add extensions deliberately.
   Keep docs presets, component mappings, heading anchors, AI-stream behavior,
   and highlighting explicit at the parser and renderer boundary. Pass the same
   extensions when parsing and rendering a reused document.
   For AI responses, use `streamingMarkdownExtension` from
   `@tanstack/markdown/extensions/streaming`, disable `frontmatter` and
   `headingIds`, and render the complete accumulated text in batched UI updates.
5. Verify output parity.
   Test server and client rendering, duplicate headings, malformed input,
   code fences, links, raw HTML, and the actual documentation corpus.

## Default Rules

- Prefer safe defaults and narrow package subpaths.
- Preserve one parsed document across renderers when the same source is reused.
- Keep React or Octane as peer dependencies of their matching adapters.
- Treat custom extensions as a compatibility surface with focused tests.
- Treat AI responses as untrusted content; keep `allowHtml` disabled.
- Use `createTanStackMarkdownHighlighter` from `@tanstack/highlight/markdown`
  for escaped inner token markup, not Highlight's complete code-block output.
- Parsing screens URLs, but `urlTransform` results, extension output,
  highlighter HTML, and supplied document ASTs are trusted boundaries. Validate
  external ASTs and enforce input-size, link, and image policies in the app;
  the renderer is not a general HTML sanitizer.

## Avoid

- Assuming full CommonMark, GFM, MDX, or plugin-ecosystem compatibility.
- Enabling raw HTML for untrusted content.
- Passing a highlighter that emits a second code-block wrapper.
- Reparsing unchanged static or cached content without a measured need.
- Reusing stale parser output for streamed content; reparse the complete
  accumulated Markdown string on every stream update because the parser does
  not retain incremental state.

## Verification

Use the official [installation](https://tanstack.com/markdown/latest/docs/installation),
[syntax profile](https://tanstack.com/markdown/latest/docs/core-concepts/syntax-profile),
[security](https://tanstack.com/markdown/latest/docs/core-concepts/security),
[AI streaming](https://tanstack.com/markdown/latest/docs/guides/ai-streaming), and
[highlighting](https://tanstack.com/markdown/latest/docs/guides/syntax-highlighting)
docs. The 1.0 package ships first-party Intent skills for rendering, React,
Octane, docs features, extensions, and production pipelines; prefer the matching
installed skill for version-aligned detail via [Intent](intent.md).
