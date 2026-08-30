# TanStack Markdown

Use this reference when a task involves `@tanstack/markdown`, deterministic
Markdown parsing, serializable Markdown ASTs, HTML rendering, React or Octane
rendering, documentation extensions, AI-stream rendering, or syntax-highlighter
integration.

TanStack Markdown is a pre-1.0 product with a focused TanStack documentation
syntax profile rather than full CommonMark, GFM, or MDX compatibility. Inspect
the installed version and confirm that the input corpus fits the supported
profile before adopting or migrating.

## Ownership Boundaries

- Markdown owns parsing, its serializable AST, safe-default HTML output, and
  matching HTML, React, and Octane rendering semantics.
- The application owns content trust, storage, URL policy, component mapping,
  cache invalidation, styling, and the decision to enable raw HTML.
- Syntax highlighting stays an explicit callback boundary; use TanStack
  Highlight or another selected highlighter rather than coupling it implicitly.

## Workflow

1. Choose the narrowest entry point.
   Use the parser, HTML renderer, or one framework adapter without importing
   unrelated renderers.
2. Establish the content trust model.
   Keep raw HTML disabled unless trusted content and product requirements make
   it necessary; review link, image, and executable-URL handling.
3. Parse once when content is reused.
   Cache or serialize the deterministic document for build-time or repeated
   rendering instead of reparsing unchanged source across boundaries.
4. Add extensions deliberately.
   Keep docs presets, component mappings, heading anchors, AI-stream behavior,
   and highlighting explicit at the parser and renderer boundary.
5. Verify output parity.
   Test server and client rendering, duplicate headings, malformed input,
   code fences, links, raw HTML, and the actual documentation corpus.

## Default Rules

- Prefer safe defaults and narrow package subpaths.
- Preserve one parsed document across renderers when the same source is reused.
- Keep React or Octane as peer dependencies of their matching adapters.
- Treat custom extensions as a compatibility surface with focused tests.
- Review the documented security boundary before enabling HTML or trusted
  highlighted markup.

## Avoid

- Assuming full CommonMark, GFM, MDX, or plugin-ecosystem compatibility.
- Enabling raw HTML for untrusted content.
- Passing a highlighter that emits a second code-block wrapper.
- Reparsing unchanged static or cached content without a measured need.
- Reusing stale parser output for streamed content; reparse the complete
  accumulated Markdown string on every stream update because the parser does
  not retain incremental state.

## Verification

Use current TanStack Markdown overview, installation, quick-start, syntax
profile, security, extension, AI streaming, and highlighting docs. If the
installed package ships first-party Intent skills, use the matching rendering
or production-pipeline skill for version-aligned detail.
