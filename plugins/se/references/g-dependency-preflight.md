# G Dependency Preflight

This reference owns the fail-closed availability gate for every SE handoff to
the G-owned GitHub workflows. It applies to both Cursor and Codex. It is a
runtime prerequisite, not a plugin installation or maintenance procedure.

This gate is host-agnostic. It must not classify Cursor versus Codex or infer a
surface from any dependency result. A consumer that separately needs Codex App
versus CLI classification must use the
[Codex runtime surface contract](codex-runtime-surface.md); passing or failing
this gate never changes that authoritative result.

## Host setup

SE never installs, enables, refreshes or substitutes G. The user or workspace
administrator must expose the exact portable G plugin before a hosted SE path
can run.

| Host | Setup | After setup |
| --- | --- | --- |
| Cursor | Install the `g` Agent Plugin from Cursor's Customize/Plugins surface at project or user scope. For local development, expose the plugin root under `~/.cursor/plugins/local/g`. | Reload Cursor and start or reload the agent session. Confirm the required `g:*` skills are visible to the agent. |
| Codex desktop/App | Add the repository or personal marketplace containing `g` (this repository exposes it through `.agents/plugins/marketplace.json`) and install it from the Plugins surface. | Start a new chat/session so the bundled skills are loaded. |
| Codex CLI | Add the repository or configured marketplace containing `g`, then install it from the CLI plugin browser. | Start a new CLI session so the bundled skills are loaded. |

The Codex marketplace-qualified identity is `g@alemar11`; Cursor resolves the
same plugin by its portable `g` identity and publisher/repository. The host
must expose the exact workflow named by the invoking SE path, not merely show a
plugin directory or a marketplace entry.

## When to run

For Learn, do not load this gate: Learn has no hosted dependency. Spec runs it
before any hosted source read or GitHub save. A local source preview needs no G
workflow. A preview does not waive the gate for an explicitly admitted hosted
source read.

Review PR runs this gate before hosted access. Its default invocation authorizes
requesting and waiting for a missing explicit review; audit-only scope remains
read-only. It does not authorize or own any other hosted action. Explicit SE
invocation authorizes only the writes required by its selected workflow and
consistent with caller constraints.

Deliver runs this gate before hosted access in the orchestrator and each worker.
Require only G workflows used by the selected source reads, local Git,
publication/readiness, required CI, and optional stacks or requested reviews.
A missing optional review workflow does not block ordinary Deliver. Explicit
no-push constraints remove publication authority, not permission for admitted
read-only source/CI inspection. Deliver's ready transition is explicitly owned by its entrypoint and uses G's
network/gh preflight with the supported GitHub CLI operation, because Send
excludes readiness. This admitted operation is not a fallback for missing G
publication or CI workflows.

## Required evidence

Establish all of the following from the current host:

- the active host can resolve the exact G plugin identity;
- the G source is the repository-owned plugin from `alemar11/dotagents` (Codex
  qualifies it as `g@alemar11`);
- that plugin is installed and enabled;
- its declared source root is present and internally consistent;
- every bundled G workflow required by the invoking SE path is present and
  resolvable;
- the explicit handoff is exposed to and reachable from the current session
  without using a compatibility alias.

Installed and enabled state plus source resolvability are necessary local
evidence, not proof of current-session reachability. Do not infer full
availability from those facts alone, a display name, an installed cache
directory, historical task output, or an unrelated GitHub connector. Do not
require source and installed versions to match as part of this gate. When local
checks pass but the current session cannot reach the explicit handoff, report
`g-dependency-unresolved`.

Spec hosted operations require `$g:github-issues` for issue
lifecycle and relationships. Optional classification uses that skill's
classification branch; classification failure never blocks semantic save.
Spec's approved delivery-marker creation, application or revocation uses the
same issue lifecycle owner. A required marker failure leaves that authorization
change incomplete even when semantic save succeeded.

Review PR requires only the hosted review owner's inspection, request, wait and
reconciliation operations. It does not use publication, local Git, issue, stack,
CI, finding-repair, reply/resolution, or merge-policy workflows.

## Blocking outcomes

Fail closed before hosted access and report the observed evidence using one of
these lower-kebab outcomes:

- `runtime-error`: the host capability inspection cannot be trusted;
- `plugin-missing`: the exact G plugin is not installed;
- `plugin-disabled`: the exact plugin exists but is disabled;
- `skill-unresolvable`: the plugin root or a required G workflow is missing or
  malformed;
- `g-dependency-unresolved`: the explicit G handoff fails after local
  availability checks pass.

Never install, enable, refresh, remove, or substitute the dependency. A manual
remediation suggestion may be reported, but it is outside this workflow's
authority. Never fall back to direct provider calls.
