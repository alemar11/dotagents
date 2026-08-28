# SE G Dependency Preflight

This reference owns the fail-closed availability gate for every SE handoff to
the G-owned GitHub workflows. It is a runtime prerequisite, not a plugin
installation or maintenance procedure.

## When to run

For Learn, do not load this gate: Learn is local-repository-only and has no
hosted dependency. For Idea, `publish` is the default; run the gate before its
first hosted read or write, while an explicitly requested `preview` remains
local and does not access GitHub. For Feature Plans, `publish` is the default
and the `plan-publication` node reaches this gate before its first hosted read
or write; an explicitly requested `preview` does not load this gate for a new
local source. Feature maintenance or an existing-source route must still run
the gate before the first hosted plan rehydration read, regardless of the
eventual terminal mode. Implement and Implement Next have no local-only or
preview mode: run the gate before their mandatory first authoritative GitHub
Feature Plan, PR, review, label, or relation read. A passing gate authorizes
only the next handoff to the applicable G-owned workflow; it does not broaden
the mutation scope. For an explicit SE request, the exact hosted writes
required by that selected workflow are already implicitly authorized; the gate
only verifies that the owner is available.

## Required evidence

Establish all of the following from the current host:

- the Codex runtime can resolve the exact G plugin identity;
- the exact repo-local G plugin identity `g@alemar11` is the one being
  resolved;
- that plugin is installed and enabled;
- its declared source root is present and internally consistent;
- every bundled G workflow required by the invoking SE path is present and
  resolvable;
- the explicit handoff can be reached without using a compatibility alias.

Do not infer availability from a display name, an installed cache directory,
historical task output, or an unrelated GitHub connector. Do not require source
and installed versions to match as part of this gate.

For Idea, the required workflow set contains `$g:github-issues`. For every
Feature publication, including a maintenance publication, it contains both
`$g:github-issues` for exact issue lifecycle operations and `$g:github-tagger`
for repository-owned label and native type classification. A maintenance or
existing-source route that only rehydrates hosted state requires
`$g:github-issues` until publication is selected. The Feature preview route for
a new local source requires neither workflow because it performs no hosted
access.

For Implement and Implement Next, the required workflow set includes the G
owners needed by the selected publication, review, CI, issue, local Git, and
stack paths. The delivery-status workflow plus branch-protection, ruleset,
mergeability-policy, merge-queue, auto-merge, and provider-policy inspection
are not required and must not be added to the dependency gate. A generic
GitHub read or raw provider call is not a substitute for the focused typed
workflow that owns the evidence being collected.

## Blocking outcomes

Fail closed before hosted access and report the observed evidence using one of
these lower-kebab outcomes:

- `codex-runtime-error`: the host capability inspection cannot be trusted;
- `plugin-missing`: the exact G plugin is not installed;
- `plugin-disabled`: the exact plugin exists but is disabled;
- `skill-unresolvable`: the plugin root or a required G workflow is missing or
  malformed;
- `codex-dependency-unresolved`: the explicit G handoff fails after local
  availability checks pass.

Never install, enable, refresh, remove, or substitute the dependency. A manual
remediation suggestion may be reported, but it is outside this workflow's
authority. Never fall back to direct provider calls.
