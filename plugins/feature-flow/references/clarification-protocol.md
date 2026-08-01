# Clarification Protocol

Load this internal protocol only when Idea or Plan cannot proceed faithfully
from the evidence already available to that caller. It is not a public skill,
a selectable mode, or an independent workflow. The calling phase derives the
profile and remains responsible for every artifact, mutation, and handoff.

## Shared Loop

1. Ground the next question in the caller-authorized discussion, repository,
   and project-context evidence. Do not expand repository scope or ask for
   information already available in those sources.
2. Track resolved decisions, material unknowns, risks, and intentionally
   deferred questions internally.
3. Ask exactly one high-signal question per turn. Include a concise recommended
   answer so the requester can accept, reject, or adjust a concrete default.
   Use a structured question UI only when it preserves that one-question flow
   and its choices are genuinely meaningful.
4. Stop as soon as the caller can proceed safely, the requester asks to
   proceed, or the remaining unknowns no longer affect the caller's output.

Use this question shape:

```text
Question: [one concrete decision-shaping question]
Recommended answer: [the default and why, in one short sentence]
```

The protocol never edits tracker artifacts, Feature Specs, implementation
issues, Project Context, project documentation, or ADRs. It returns decisions
and blockers to the caller, which applies its own authority and output
contract.

## Idea Profile

Use the Idea profile only after candidate extraction, deduplication, and any
multi-candidate selection, and before publication preflight. Run it only when
the accepted proposal is not yet faithfully capturable because its problem or
opportunity, expected value, or proposal boundary is materially unclear.

- Ask at most one clarification question for the accepted set. Do not run a
  general interview merely to improve wording.
- Use the supplied discussion and the minimum repository facts already needed
  for ownership. Do not initiate a full repository, `CONTEXT.md`, or ADR scan.
- Do not make architecture decisions, invent acceptance criteria, define an
  implementation plan, or produce durable knowledge data.
- Preserve nonblocking uncertainty in the Idea's `Open Questions`. If no
  concrete proposal can be resolved, stop instead of inventing one.
- Candidate selection, tracker ownership, duplicate detection, and collision
  resolution remain Idea-owned interactions and do not consume the single
  content-clarification question.

Return only refined Idea capture facts and unresolved open questions. Idea
owns rendering, duplicate checks, publication, and reporting.

## Plan Profile

Use the Plan profile only on `source_route=new-source` when supplied intent plus
the repository and project-context evidence already loaded by Plan cannot
support a complete Feature Spec and safe implementation issue graph. The
`existing-source` and `scope_repair_request` branches keep their own immutable
source rules and do not enter this profile.

- Inspect relevant code, documentation, tests, root and matched scoped
  `CONTEXT.md` files, and ADRs before asking.
- Resolve one material decision at a time and continue only while another
  answer can change the Feature Spec, issue graph, validation policy, or safe
  execution boundary.
- Keep unresolved product-shaping questions in `planning_blockers`; do not hide
  them inside durable knowledge data.
- Identify as a durable knowledge candidate only an accepted project-specific
  term, rule, boundary, or decision that is new or changes an existing rule,
  has portable evidence, and has an intended repository-owned target surface.

Return resolved planning decisions, remaining `planning_blockers`, and any
durable knowledge candidates to Plan. Plan validates those candidates against
the accepted scope and current Project Context, then owns whether to construct
an optional `knowledge_delta` with `decisions`, `target_surfaces`, and
`evidence`. Omit the delta when clarification introduced no durable project
knowledge.

Plan never writes the delta into a Feature Spec or updates Project Context
during planning. Its issue phase owns placing each validated repository shard
only on the final integration closeout issue that Implement will reconcile
through `$project-context` with `domain_operation=implementation-closeout`
after integrated behavior is proven.
