# SE2 G Dependency Preflight

This reference owns the fail-closed availability gate for every SE2 handoff to
the G-owned GitHub workflows. It is a runtime prerequisite, not a plugin
installation or maintenance procedure.

## When to run

For Idea preview, do not load this gate and do not access GitHub. For Idea or
Feature publication, run it only after publish is explicitly resolved and
immediately before the first hosted read or write. For Implement, run it before
the first authoritative GitHub Feature, Task, PR, review, label, or relation
read. A passing gate authorizes only the next handoff to the applicable G-owned
workflow; it does not grant mutation authority.

## Required evidence

Establish all of the following from the current host:

- the Codex runtime can resolve the exact G plugin identity;
- the exact repo-local G plugin identity `g@alemar11` is the one being
  resolved;
- that plugin is installed and enabled;
- its declared source root is present and internally consistent;
- every bundled G workflow required by the invoking SE2 path is present and
  resolvable;
- the explicit handoff can be reached without using a compatibility alias.

Do not infer availability from a display name, an installed cache directory,
historical task output, or an unrelated GitHub connector. Do not require source
and installed versions to match as part of this gate.

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
