# SE2 G Dependency Preflight

This reference owns the fail-closed availability gate for the SE2 Idea
workflow's hosted issue handoff. It is a runtime prerequisite, not a plugin
installation or maintenance procedure.

## When to run

Run this read-only gate only after `run_mode=publish` is explicitly resolved,
immediately before the first hosted issue or label read or write. Preview does
not load this gate and must not access GitHub. A passing gate authorizes only
the next handoff to the G-owned issue workflow; it does not grant publication
authority.

## Required evidence

Establish all of the following from the current host:

- the Codex runtime can resolve the exact G plugin identity;
- the exact repo-local G plugin identity `g@alemar11` is the one being
  resolved;
- that plugin is installed and enabled;
- its declared source root is present and internally consistent;
- the bundled GitHub issue workflow is present and resolvable;
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
- `skill-unresolvable`: the plugin root or issue workflow is missing or
  malformed;
- `codex-dependency-unresolved`: the explicit G handoff fails after local
  availability checks pass.

Never install, enable, refresh, remove, or substitute the dependency. A manual
remediation suggestion may be reported, but it is outside this workflow's
authority. Never fall back to direct provider calls.
