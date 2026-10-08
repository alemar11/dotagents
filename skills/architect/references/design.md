# Design from usage

Read when a change introduces or alters state, responsibilities, interfaces, or
module boundaries. The specification contract owns what is binding and how the
result is recorded; this reference guides the design reasoning.

## Ground the change

Trace the relevant user or caller action through the existing system to its
observable result. Identify the owners and contracts the change must preserve.
When replacing an unusual boundary or behavior, inspect its rationale in
available history or documentation before treating it as accidental complexity.
Distinguish recorded reasons from inference and unknowns; do not require a
repository-wide investigation for a local decision.

Write representative usage before designing internal shapes. For an app, use
the user interaction and visible state, including recovery when it matters. For
an API or library, show the consumer's inputs, calls, outputs, and errors. Derive
interfaces from that usage and check them against actual existing callers.

## Settle the load-bearing decisions

Describe only what constrains correctness, integration, or significant cost:

- Which component owns each important piece of state, who may change it, and
  whether it survives restarts or is derived from another source.
- The domain data and invariants. Show a compact type, schema, or transition
  example when prose would hide an illegal state or ambiguous contract.
- How data and control cross boundaries, where external input is validated,
  and what failures, cancellation, retries, or concurrent actors mean for the
  requested behavior. Include only the cases the feature actually encounters.
- Compatibility and migration obligations, including coexistence with old
  callers or data when needed. Reuse suitable existing boundaries before
  introducing new ones.

Give shared state an explicit owner. Consider isolated state before introducing
coordination. Prefer an interface that hides domain policy and lets callers
complete an operation without knowing internal sequencing. Leave incidental
helpers, class layouts, and signatures open unless they are part of an accepted
contract. A sketch explains the design; it is not a requirement to create code
scaffolding or commit temporarily broken implementations.

## Compare when the choice matters

Compare concrete, structurally distinct alternatives when uncertainty affects
correctness, ownership, compatibility, user experience, or substantial cost.
Use the same usage and constraints for each; consider extending the current
design when viable. Explain the chosen tradeoff and why the credible alternative
was rejected. When evidence or an accepted decision already settles the shape,
record that reason without inventing a second candidate.

Use optional research helpers for independent unknowns or genuinely useful
alternative designs. No fixed candidate count, model panel, or mandatory
prototype is required. Product preferences go through clarification; facts go
through research. If observation is necessary, name the experiment and required
evidence without running it under planning authority.

## Challenge the design

Check for duplicated writers or sources of truth, public interfaces that expose
internal representations, thin layers without a distinct responsibility, and
invariants that callers must remember rather than the owner enforcing them.
These are reasons to investigate, not universal bans: preserve justified
adapters, compatibility boundaries, and existing contracts.

Walk the representative usage and relevant failure paths through the proposed
shape. Connect material assumptions to credible verification boundaries and
identify what remains unproven. Then derive tasks that deliver observable
slices of that design. If later evidence invalidates an accepted decision,
revise the decision, criteria, and affected tasks together under the existing
revision rules; an implementation difficulty alone does not authorize changing
the requested behavior.
