# SE G Dependency Preflight

This reference owns the fail-closed availability gate for every SE handoff to
the G-owned GitHub workflows. It is a runtime prerequisite, not an installation
or maintenance procedure.

## When to run

For Learn, do not load this gate: Learn is local-repository-only and has no
hosted dependency. For Idea, `publish` is the default; run the gate before its
first hosted read or write, while an explicitly requested `preview` remains
local and does not access GitHub. For Feature Plans, `publish` is the default
and Intake reaches this gate before any hosted source read, while Publish
reaches it before the first hosted publication operation. An explicitly
requested `preview` from a new local source does not load this gate. A preview
whose source is hosted, including a hosted Idea or issue, still runs the gate
for that read. Implement has no local-only or preview mode:
run the gate before its mandatory first authoritative GitHub Feature Plan,
PR, review, label, or relation read. A passing gate authorizes only the next
handoff to the applicable G-owned workflow; it does not broaden the mutation
scope. For an explicit SE request, the exact hosted writes required by that
selected workflow are already implicitly authorized; the gate only verifies
that the owner is available.

## Required evidence

Establish all of the following from the current host:

- the reusable skill with canonical identity `g` is installed and resolvable;
- its `SKILL.md`, routed workflow references, and shipped CLI are present and
  internally consistent;
- the G workflow required by the invoking SE path is reachable through `$g`;
- the explicit handoff can be reached without using a compatibility alias.

Do not infer availability from a display name, an installed cache directory,
historical task output, a retired plugin installation, or an unrelated GitHub
integration. Do not require source and installed versions to match as part of
this gate.

For Idea, `$g` must route to its GitHub Issues workflow. Every Feature hosted
source read or publication, including maintenance, requires that same workflow
for exact issue lifecycle operations. Require G's GitHub Tagger workflow only
when optional repository-owned classification is actually attempted; its
absence or failure never blocks semantic publication. The Feature preview
route for a new local source requires neither workflow because it performs no
hosted access.

For Implement, the required workflow set includes the G
owners needed by the selected publication, review, CI, issue, local Git, and
stack paths. The delivery-status workflow plus branch-protection, ruleset,
mergeability-policy, merge-queue, auto-merge, and provider-policy inspection
are not required and must not be added to the dependency gate. A generic
GitHub read or raw provider call is not a substitute for the focused typed
workflow that owns the evidence being collected.

## Blocking outcomes

Fail closed before hosted access when the runtime capability inspection cannot
be trusted, the reusable G skill is unavailable or malformed, a required
workflow is not reachable, or the explicit handoff fails after local
availability checks pass. Report the observed cause in prose and use the
invoking SE workflow's canonical `blocked` terminal state.

Never install, refresh, remove, or substitute the dependency. A manual
remediation suggestion may be reported, but it is outside this workflow's
authority. Never fall back to direct provider calls.
