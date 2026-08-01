---
name: project-context
description: Maintain durable project context, ADRs, optional localization memory, Code Review Rules, confirmed corrections, and explicit AGENTS.md compaction proposals in Git repositories.
---

# Project Context

## Purpose

Use `$software-project:project-context` as the single public entry point for durable repository
context:

- always-active operating rules, ownership boundaries, and the exact
  `## Code Review Rules` section in the closest applicable `AGENTS.md`;
- root-first context routing through `CONTEXT.md`;
- conditional topic files and accepted ADRs under one repository-level
  `project-context/` directory;
- optional `TRANSLATION.md` sidecars when localization rules are evidenced;
- confirmed durable corrections and preferences, classified to the right
  surface;
- explicit, proposal-first compaction of an applicable `AGENTS.md` chain.

The skill owns context only. Tracker routing, issue metadata, publication,
delivery policy, branches, pull requests, and runtime worker configuration
belong to their workflows and are never stored in `project-context/`.

Use the smallest requested `memory_slice`. Load
`references/options.md` before resolving a branch and reject noncanonical
structured fields or values.

## Surfaces And Ownership

| Surface | Owns | Always active? |
| --- | --- | --- |
| `AGENTS.md` | Operating invariants, safety, ownership, essential verification, short pointers, and the minimal Code Review Rules contract. | Yes |
| `CONTEXT.md` | Shared overview, vocabulary, known state, explicit unknowns, scope routing, and the index of conditional context files. | No; entry point when context is needed |
| `project-context/<topic>.md` | Conditional details, examples, rationale, domain contracts, and operational notes. | No; each file declares `Read when` |
| `project-context/adr/index.md` | Canonical index of accepted ADRs. Created with the first ADR. | No |
| `project-context/adr/ADR-*.md` | Accepted load-bearing decisions and consequences. | No |
| `TRANSLATION.md` | Evidence-backed localization and language conventions beside its owning context. | No |

Keep topic files flat and lowercase. `project-context/adr/` is the only
initial subdirectory. Scoped `CONTEXT.md` files and their optional
`TRANSLATION.md` sidecars may exist in monorepos, but they never create nested
`project-context/` directories.

`AGENTS.md` is the source of always-active normative rules. A topic file may
contain a conditional contract, but it must not silently replace a rule that
must apply on every task. Do not duplicate the same normative wording across
surfaces.

## Operations

| `memory_slice` | Owns |
| --- | --- |
| `domain-memory` | Root/scoped context routing, topic setup, ADR setup, inline update, implementation closeout, or periodic review. |
| `durable-capture` | Manual capture of a confirmed correction, preference, rule, localization convention, or accepted decision. |
| `translation-memory` | Localization memory only. |
| `agents-pointers` | Missing or stale context pointers in `AGENTS.md`. |
| `agents-compaction` | Measurement, classification, proposal, and authorized compaction of an applicable `AGENTS.md` chain. |
| `code-review-rules` | Evidence-backed rules in the exact `## Code Review Rules` section of the closest applicable `AGENTS.md`. |
| `full-setup` | All applicable context slices, only when explicitly requested. |

For `memory_slice=domain-memory`, resolve `domain_operation` from
`references/domain-modeling.md`: `setup-bootstrap`, `inline-update`,
`implementation-closeout`, or `periodic-review`.

## Write Authority

There is no durable configuration file and no persisted write preference.
Resolve authority from the current request and caller data:

- inspection, review, proposal, dry-run, or indirect suggestion: read-only;
- explicit setup, initialize, update, or refresh: write only the selected
  surfaces in the requested repository scope;
- direct `durable-capture`: propose the exact target, section, wording, and
  before/after block, then wait for an affirmative confirmation before writing;
- a composed `domain-memory` handoff: write only when the caller supplies
  accepted durable knowledge, named targets, and explicit capture authority;
- `agents-compaction`: always show the measurement and before/after proposal;
  apply only after an explicit target and confirmation.

Never infer a durable capture from ordinary conversation, a tentative idea,
raw session text, a secret, or generic architecture advice. Preserve unrelated
custom prose, comments, overrides, context files, ADRs, and localization data.

## Non-Negotiable Rules

- Resolve the current Git repository as the default scope. For cross-repository
  work, use only explicitly authorized repository identities and candidate local
  roots verified one-to-one by the caller.
- Never fabricate paths from issue or Spec references, saved-project lists,
  common parents, or path proximity. Reject extra or unmatched roots.
- During authorized setup/bootstrap, create or update root `CONTEXT.md` at each
  selected Git root, even when the only supported content is a minimal entry
  point with explicit unknowns.
- Create `TRANSLATION.md` only when localization support or durable translation
  rules are evidenced or explicitly confirmed. Do not create empty ADR trees.
- Put accepted load-bearing decisions in ADRs, not in a growing `AGENTS.md`.
- For Code Review Rules, write only invariant, consequence, and safe path under
  the exact `## Code Review Rules` heading in the closest applicable
  `AGENTS.md`. Keep evidence, matrices, provenance, confidence, and history
  outside that section.
- Never create tracker, publication, delivery, provider, branch, or worker
  configuration under `project-context/`.
- Verify links, target existence, duplicate normative content, preserved custom
  text, and the documentation diff after every authorized write.

## Reference Loading Matrix

Load only the selected branch:

| Work | Required references |
| --- | --- |
| Domain setup/bootstrap | `domain.md`, `domain-modeling.md`, `context-seed.md`, and `setup-workflow.md`; add `session-history.md` only for accepted existing-project evidence. |
| Domain inline update / closeout / review | `domain-modeling.md`; add `domain.md` for layout or ownership ambiguity and `documentation-shapes.md` when no stronger local shape exists. |
| Durable capture | `durable-capture.md`; add `domain-modeling.md`, `documentation-shapes.md`, or `translation.md` for the selected destination. |
| Translation | `translation.md` and `setup-workflow.md`. |
| Pointers | `setup-workflow.md`. |
| AGENTS compaction | `agents-compaction.md`, `documentation-shapes.md`, and `domain.md` when the context index needs updating. |
| Code Review Rules | `code-review-rules.md`; add evidence-mining, rule-evaluation, or official-doc references only when routed by that file. |

Do not load domain, localization, or session-history evidence for a
Code-Review-only request unless the selected reference explicitly routes to it.
Load `setup-questions.md` only when repository evidence and documented defaults
leave a material ambiguity.

## Workflow

### 1. Resolve scope and operation

Select the smallest `memory_slice`, resolve `domain_operation` when required,
and derive `execution_context` from repository evidence. Keep repository facts,
knowledge deltas, target paths, and confirmation state as data rather than
options.

### 2. Inspect focused evidence

Read the applicable `AGENTS.md` chain, root `CONTEXT.md`, matched scoped
contexts, indexed topic files, relevant ADRs, and only the source, tests, docs,
or accepted decisions needed for the selected operation.

### 3. Draft the intended change

Show exact files, target sections, meaningful before/after text, evidence,
unknowns, and any new links. Keep `AGENTS.md` pointer-first and do not copy
conditional detail into it.

### 4. Apply only authorized writes

Update only named surfaces. Use the domain-modeling workflow for context and
ADR content, the durable-capture workflow for confirmed corrections, and the
compaction workflow for section moves. Do not turn a proposal into an apply
operation because the user did not object.

### 5. Verify and report

Read targets back, verify relative links and indexes, scan for duplicate
normative wording, check the diff, and report `memory_slice`, operation,
execution context, targets, evidence, capture result, and any deferred items.

For implementation closeout, reconcile every accepted item against behavior
that actually landed. A nonempty accepted delta is `captured` only when every
named target is reconciled and verified; otherwise report `deferred`.

## Durable Capture

Use `references/durable-capture.md` for the former correction/preference
workflow. Determine the narrowest repository scope, classify the destination,
propose exact wording, wait for affirmative confirmation, handle duplicates or
conflicts, update required indexes or pointers, and verify the final diff.

The optional shipped helper
`scripts/extract_recent_transcript.py` resolves an explicit Codex session or
rollout path when current conversation evidence is insufficient. It is an
accelerator, not a source of authority, and must never persist raw transcript
content.

## AGENTS Compaction

Use `references/agents-compaction.md` only for an explicit compaction request
or a requested context-size review. Measure the actual applicable instruction
chain deterministically, classify sections, preserve always-active invariants
and the minimal Code Review Rules block, and propose conditional material as
flat topic files with `Read when` pointers. Never compact automatically merely
because a threshold is crossed.

## CLI Maintenance

The shipped helper lives at
`plugins/software-project/skills/project-context/scripts/extract_recent_transcript.py`. Run it through
that artifact, not from a temporary copy. It uses only the Python standard
library and does not create config or caches. Validate `--help`, `--version`,
`--json doctor`, explicit `--session-id`/`--rollout-path` resolution, stdout
JSON, stderr diagnostics, and missing-path exit behavior.

## Reference Responsibilities

- `options.md`: canonical fields and values.
- `domain.md`: repository-root and scoped-context discovery, layout, and ADR
  ownership.
- `domain-modeling.md`: context, topic, ADR, inline-update, closeout, and review
  semantics.
- `durable-capture.md`: correction, preference, rule, localization, and decision
  classification plus confirmation.
- `agents-compaction.md`: chain measurement, threshold proposal, section split,
  and link/duplicate verification.
- `setup-workflow.md`: settings, pointers, write checklist, and report.
- `code-review-rules.md`: evidence, evaluation, rendering, and exact AGENTS
  update semantics.
- `documentation-shapes.md`: fallback shapes for context, topics, ADR indexes,
  and ADRs.
- `context-seed.md`, `session-history.md`: initial and session-backed evidence.
- `translation.md`: optional localization memory.
