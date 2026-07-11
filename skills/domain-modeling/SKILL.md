---
name: domain-modeling
description: Build and maintain project domain language, context docs, and ADRs from repo evidence and accepted decisions.
---

# Domain Modeling

## Goal

Keep a project's shared language and durable decisions current while work is
being discussed. Turn clarified terminology, boundaries, rules, and decisions
into lightweight project documentation that future agents and maintainers can
reuse.

This is the semantic engine for domain documentation, not a standalone
brainstorming session. `$project-memory domain-memory` is the normal public
entry point when the goal is to create or update durable memory surfaces; it
loads this skill to shape `CONTEXT.md`, relevant domain docs, and ADR changes.
Direct callers that already own a domain workflow, such as
`$grill-me-with-context`, may compose this skill without routing through
`$project-memory`. Update docs only when the conversation or repo evidence
resolves something durable.

## Trigger Rules

- Use when the user asks to model a domain, define terms, sharpen vocabulary,
  record architectural or product decisions, or update project context docs.
- Use when another skill is clarifying a codebase-backed plan and domain terms,
  business concepts, workflows, or durable decisions become clear.
- Use when `$project-memory` delegates a `domain-memory` setup, refresh, or
  implementation-closeout slice. Stay within the caller's authorized targets
  and return the semantic capture result to `$project-memory` for closeout.
- Use for a periodic project context review when the caller provides recent
  project conversations, session notes, or equivalent work history to mine for
  durable terminology, rules, open questions, or accepted decisions.
- Do not invent a domain model before there is evidence from the user, repo, or
  existing docs.
- Do not update docs for transient preferences, tentative ideas, or decisions
  the user has not accepted.

## Workflow

### 1. Inspect existing context

- Look for `CONTEXT.md`, `CONTEXT-MAP.md`,
  `project-memory/agents/domain.md`, `project-memory/adr/`, `README.md`,
  project docs, product specs, issue templates, and nearby code or tests that
  define the vocabulary already in use.
- If `CONTEXT-MAP.md` exists, use it to choose the relevant context-specific
  `CONTEXT.md` before editing domain language.
- Prefer updating an existing relevant file over creating a new one.
- If no domain context file exists and a durable term or rule needs a home,
  create `CONTEXT.md` at the project root.
- If no suitable durable destination exists and the current caller is not
  setting up project memory or otherwise creating new context surfaces, do not
  invent a shadow home in chat. Mark the capture as deferred, name the missing
  destination explicitly, and say which file would have been updated.

### 2. Sharpen the model

Track these items while the conversation progresses:

- **Terms**: project-specific words, aliases, and phrases.
- **Boundaries**: where one concept, workflow, actor, or module stops and
  another starts.
- **Rules**: invariants, permissions, lifecycle transitions, validations, and
  failure states.
- **Decisions**: accepted choices that future work should not relitigate.
- **Open questions**: unresolved points that should remain visibly uncertain.

When a term is fuzzy, challenge it with a concrete edge case before writing it
down. When two names appear to mean the same thing, ask whether they are aliases
or distinct concepts.

### 3. Update docs inline

Write the smallest durable update that preserves the resolved meaning:

- Add or revise glossary entries in `CONTEXT.md`.
- Add short workflow or rule notes to the most relevant project doc.
- Add an ADR under `project-memory/adr/` only for load-bearing decisions that
  future agents or maintainers would otherwise reopen.
- Leave open questions clearly marked instead of smoothing over uncertainty.

When invoked by `$project-memory`, treat its selected context, authorized target
surfaces, evidence boundary, and operation (`fresh-setup`,
`existing-project-bootstrap`, or `implementation-closeout`) as the write
boundary. Do not expand into tracker, localization, pointer, or unrelated domain
surfaces.

Keep docs practical:

- Use project vocabulary from the repo and user.
- Cite durable repo sources such as source files, tests, project docs, or ADRs
  when they are available.
- Treat issues, PRs, tracker discussions, and session history as discovery
  evidence or optional provenance, not as the sole authority for a durable
  `CONTEXT.md` term, rule, boundary, or decision. First restate the accepted
  meaning in a repo-owned source; keep tracker links in that source's
  background or provenance when useful.
- Avoid generic domain-driven-design exposition.
- Do not rewrite broad docs just to add one clarified term.
- If the right destination is missing, return the smallest explicit deferral:
  the durable item, the missing file or doc surface, and why capture stopped.

### 4. Periodic context review

When invoked by an automation, scheduled review, or other batch workflow:

- Treat recent conversations, session logs, issue activity, and commit history
  as candidate evidence, not as authority by themselves.
- Re-read the current repo context files and relevant source or tracker evidence
  before deciding that a candidate belongs in durable docs.
- Default to a review report or proposed patch when acceptance is unclear.
- Edit docs only when the durable term, rule, boundary, open question, or
  accepted decision is explicit enough that an inline run of this skill would
  have recorded it.
- Do not create ADRs from batch review alone unless the decision is clearly
  accepted and load-bearing.
- When the right destination doc does not exist, keep the candidate in
  `Deferred Candidates` and name the missing destination instead of implying the
  knowledge was captured somewhere durable.

Use a compact closeout shape so repeated reviews stay comparable:

```markdown
## Accepted Updates

- Durable term, rule, boundary, open question, or accepted decision captured
  now, with destination doc.

## Deferred Candidates

- Plausible durable knowledge that still needs acceptance, stronger repo
  evidence, or tracker/source confirmation before capture.

## ADR-worthy Decisions

- Accepted, load-bearing decisions that may deserve an ADR if they are not yet
  recorded.

## No Durable Change

- Explicitly state this when the review found nothing worth capturing.
```

Omit empty sections unless `No Durable Change` is the only correct result.

### 5. Report what changed

When returning to the user or calling skill, summarize:

- docs created or updated,
- terms, rules, or decisions captured,
- any capture deferred because the destination surface was missing, including
  the file that should exist,
- deferred candidates left out of durable docs and why,
- unresolved domain questions,
- any decision that may deserve a future ADR.

## References

- `references/documentation-shapes.md`: default `CONTEXT.md` and ADR Markdown
  shapes when the project does not already have stronger local formats.

## Guardrails

- Do not make runtime skills depend on repo-maintenance docs.
- Do not create ADRs for every small preference; reserve them for durable,
  load-bearing decisions.
- Do not remove existing domain notes unless the user explicitly invalidates
  them or repo evidence proves they are stale.
- Do not ask documentation questions that can be answered by reading the repo.
