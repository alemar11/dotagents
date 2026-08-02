# Translation Memory

Use this reference when `project-context` creates or updates optional
`TRANSLATION.md` localization memory.

## When to create it

Create `TRANSLATION.md` only when localization support is clear from durable
evidence or explicit user confirmation.

Strong signals include:

- committed locale folders or translation catalogs,
- i18n/l10n dependencies and active framework locale configuration,
- product docs naming supported markets, languages, or target audiences,
- existing copy, tone, translation, or brand-language guidelines,
- app-store, release, marketing, or support docs that define language support.

If signals are ambiguous, load [setup-questions.md](setup-questions.md) and use
its localization conventions prompt before drafting. If no localization
support is visible, do not create `TRANSLATION.md` and do not add an
`AGENTS.md` localization pointer.

## Location

Place `TRANSLATION.md` beside the relevant `CONTEXT.md`:

- repository root: root `TRANSLATION.md` for shared localization rules;
- scoped monorepo context: scoped `TRANSLATION.md` beside the selected scoped
  `CONTEXT.md` when that scope has independent localization rules.

Use product vocabulary from the neighboring `CONTEXT.md`; do not duplicate the
project glossary here. `CONTEXT.md` may include a one-line pointer to this file
when localization affects domain terms, audience, product naming, or
user-facing copy, but the pointer is not required.

## File shape

Use only sections with evidence:

```markdown
# Translation

## Audience And Markets

## Source Language

## Supported Locales

## Tone And Register

## Terminology Rules

## UI Copy Rules

## Formatting Rules

## Review And Ownership

## Open Questions
```

## What to capture

- Target audience or market constraints that affect translation.
- Source language and supported target locales.
- Tone/register rules, including formality and inclusive-language expectations.
- Product terms that must be translated consistently or intentionally left
  untranslated.
- UI copy rules for buttons, errors, notifications, legal text, and support
  surfaces when they are project-specific.
- Locale-sensitive formatting rules for dates, numbers, currency, units,
  pluralization, names, and addresses.
- Review ownership, approval expectations, or external translation handoff
  rules.
- Open localization questions only when evidence shows uncertainty or conflict.

## What to avoid

- Generic translation best practices not grounded in the project.
- Full translation catalogs or copied locale files.
- Product glossary material that belongs in `CONTEXT.md`.
- Agent operating instructions that belong in `AGENTS.md`.
- Tentative audience or market guesses.
