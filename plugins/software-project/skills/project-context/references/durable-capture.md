# Durable Capture

Use this reference for `memory_slice=durable-capture` when the user states a
correction, preference, policy, accepted decision, localization convention, or
other knowledge intended to survive the current task.

## Durability Filter

Capture only guidance likely to remain useful across future work. Exclude:

- one-off instructions tied only to the current files or task;
- tentative, rejected, or unresolved ideas;
- raw transcript text, session paths, credentials, secrets, or private payloads;
- generic architecture advice not grounded in this repository or an accepted
  decision.

Strong signals include `always`, `never`, `default`, `from now on`, `remember`,
`hard rule`, or an explicit request to preserve a correction. The signal is
not authority to write.

## Scope Resolution

Determine the narrowest suitable scope before drafting:

1. repository root or affected subpath when the guidance concerns this project;
2. a global `AGENTS.md` only when the rule is genuinely cross-project and the
   user explicitly approves that target;
3. never fall back to global because a project target is missing.

For a subpath, prefer the closest existing `AGENTS.md`. If it does not exist,
propose creating that exact target rather than silently widening scope.

## Destination Classification

| Knowledge | Destination |
| --- | --- |
| Rule that must apply on every task in scope | Closest applicable `AGENTS.md` |
| Conditional detail, example, rationale, or operational note | `project-context/<topic>.md` |
| Accepted load-bearing architectural decision | `project-context/adr/ADR-*.md` and `adr/index.md` |
| Localization or translation convention | `TRANSLATION.md` beside the owning context |
| Shared overview, vocabulary, routing, or explicit unknown | `CONTEXT.md` |

Keep the normative minimum in `AGENTS.md`. A topic file or ADR may be linked
from it, but it must not become a hidden replacement for an always-active rule.
Do not create a topic, ADR directory, or translation sidecar merely because a
candidate was mentioned; create it only after the durable target is authorized.

## Proposal And Confirmation

Before writing, show:

- the absolute target path and scope;
- the existing section or a proposed new section;
- exact wording and a concise rationale;
- meaningful before/after content;
- companion pointer, index, or link changes;
- duplicate or conflict handling;
- evidence supporting durability and destination choice.

For direct capture, wait for an affirmative approval of both target and wording.
Silence, an unrelated follow-up, or a target-selection reply is not approval.
A composed caller may authorize inline capture only when it supplies accepted
knowledge, named targets, repository scope, and capture authority.

## Apply And Verify

After authorization:

1. reread every target and stop on drift or conflict;
2. update only the selected surface and preserve unrelated custom text;
3. update `CONTEXT.md` indexes, `adr/index.md`, or short AGENTS pointers when
   required; when the destination is `AGENTS.md`, ensure each inserted learning
   bullet ends with ` (Codex learning)` and do not add that marker to unrelated
   prose;
4. read the result back and verify relative links and target existence;
5. scan for duplicate normative wording and run `git diff --check`;
6. report `captured`, `deferred`, or `no-durable-change` with destinations and
   reasons separated from the knowledge data.
