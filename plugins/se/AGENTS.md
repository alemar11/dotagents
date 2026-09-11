# SE Plugin Maintenance

SE owns the graph-based planning and delivery workflows. Consult `CONTEXT.md`
for package context when relevant; keep shared repository rules at the root.
Do not restore retired compatibility surfaces.

## Shared ownership

A shared reference belongs in `references/` when at least two skills consume its
contract, or when it defines a reusable role under `references/subagents/`. Each consumer routes to it at the relevant read condition.
Keep skill-specific states, topology, templates, and branch detail with the skill.
When ownership changes, update affected consumers and remove obsolete routes.

| Shared owner | Contract |
| --- | --- |
| `references/states.md` | Shared spec-delivery readiness states, GitHub label colors, authorization and verified human handoff. |
| `references/workflow-graph.md` | Graph vocabulary, registry structure, terminal meanings, authority, and validation. |
| `references/g-dependency-preflight.md` | Host-specific setup and availability of required G workflows before hosted access. |
| `references/codex-runtime-surface.md` | Read-only App/CLI classification; capability checks are not surface evidence. |
| `references/execution-scope.md` | Uniform standalone/composed responsibilities and delegation policies across SE skills. |
| `references/subagents.md` and `references/subagents/` | Role index, common constraints and reusable role definitions with default profiles; callers own transport, orchestration and disposition. |
| `references/hosted-content-safety.md` | Portable hosted content, title normalization, and bounded same-artifact repair. |
| `scripts/validate-hosted-content-safety` | Static ownership, routing, and hosted-template checks. |

## Skill ownership

- Chief of Staff owns App-only cross-repository coordination, the global standalone
  project gate, Deliver task reuse and combined acceptance. Deliver owns all
  repository execution; project configuration remains App-owned.

- Deliver owns the single-repository worker-to-PR workflow and its local worker role,
  integration, single-pass candidate review and recovery references. It has no
  graph, claim registry or repair ledger.

- Learn owns local durable context, localization, review rules, and managed
  AGENTS pointers. It does not own tracker, task, or delivery state.
- Grilling Session owns read-only interview refinement from supplied context.
- Explore owns read-only investigation in the invoking task or session, Grilling
  Session composition, Learn context preparation, bounded native workers, and synthesis.
- Spec owns coherent specs, stable spec/task identities, actionable
  task contracts, recommended order, real prerequisites, accepted decisions,
  review, and optional GitHub issue representation. Its specification
  reference owns content and templates project it; Spec does not own delivery
  authorization or labels. Shared readiness states remain owned by the delivery
  workflow.
- Adversarial Review owns independent read-only critique and generic findings;
  composed callers own target identity, lifecycle, and disposition mapping.
- Review PR requests or resumes one hosted Codex review, waits, and returns the
  provider result to the calling task. It owns no subagents, repairs, CI or
  acceptance. G owns provider operations, lineage and bounded waiting.
- Implement owns bounded local implementation/repairs, optional read-only UI
  design delegation, and candidate handoff;
  composed callers own independent review, orchestration, claims and publication.

## Maintenance invariants

Preserve these boundaries when changing their runtime owners; do not copy their
full protocols into this file:

- Feature specs preserve observable outcomes, accepted technical decisions,
  relevant baseline evidence, paired task verification checks, and full coverage. Task
  order is independent of identity and hard prerequisites. Planning never
  overwrites executor progress or prescribes workers and PR topology.
- Each Spec invocation and all its specs/tasks belong to one repository. Spec
  authors only same-repository issue references; cross-repository coordination
  belongs to its caller. Delivery verifies prerequisite availability and assembled
  outcomes, and owns PR grouping, stack/integration choices, and closing refs.
- GitHub issues own the saved spec/task contract. Spec owns body-backed prerequisites
  and ordinary links; G owns explicitly requested native blocker changes. Spec
  preserves existing provider relationships.
- Material spec questions compose Grilling Session in the planner. Safe assumptions
  and explicitly delegated decisions do not require extra interviews. Every
  complete draft passes Review, with progress-bounded correction.
- Spec runs in the invoking session and updates its title when supported.
  Title availability does not gate planning. Model profiles remain in runtime
  owners and the repository model index.
- Hosted writes pass the shared content-safety owner, including worker output.
  G owns transport/readback; SE owns semantic projection and correction.
- Graph node IDs and transitions stay synchronized across registries, step
  frontmatter, state glossaries, and Mermaid projections. Terminal nodes have
  no outgoing edges. Acceptance criteria are plain behavioral bullets;
  verification belongs in task checks, and progress remains separate.

## Validation

Validate affected metadata, links, state ownership, registry row arity,
registered transitions, terminal reachability, and graph projections. Do not
assert Markdown wording or section placement. Use bounded forward-model checks
when changed semantics cannot be established statically.

For hosted-content changes, run `scripts/validate-hosted-content-safety` and
inspect affected write owners. For manifest alignment,
run `python3 -m unittest discover -s plugins/se -v` from the repository root;
`test_all.py` discovers the alignment suite.

Check manifest/marketplace paths and scan for retired identifiers after routing
changes. Keep both plugin manifest versions aligned.
