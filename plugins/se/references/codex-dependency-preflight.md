# SE to G Codex Runtime Preflight

This reference owns the fail-closed runtime availability gate for the SE to G
handoff. It is not a plugin manifest dependency declaration and it must not
install, enable, refresh, or remove a plugin.

## Load condition

Load this reference immediately before the first `$g:github-issues` handoff in
`idea`, `feature`, or `implement`. `learn` and
`improve-codebase-architecture` do not load it for their local-only paths.

The preflight runs for both read-only and write-capable flows. It must finish
before any G operation, GitHub mutation, run-state mutation, claim, task, or
worker creation that depends on G.

## Read-only checks

Run:

```sh
codex plugin list --json
```

Treat a non-zero exit, malformed JSON, or missing required fields as a
blocking runtime error. In the `installed` array, require one exact entry with
all of these properties:

- `pluginId` is exactly `g@alemar11`;
- `installed` is `true`;
- `enabled` is `true`;
- `source.path` is present and identifies the installed plugin root.

Do not match the display name `G` or infer availability from a cache directory.
Using the reported `source.path`, verify that the plugin root contains the
declared manifest and the exact bundled skill:

```text
<source.path>/.codex-plugin/plugin.json
<source.path>/skills/github-issues/SKILL.md
```

The manifest must identify plugin `g`, and the skill front matter must identify
`github-issues`. Record the reported plugin version and source path as
diagnostic evidence, but do not turn source-versus-installed version equality
into this availability gate. Freshness and reinstall remain separate,
explicit maintenance operations.

## Pass and handoff

A passing preflight authorizes only the next G handoff; it does not authorize a
GitHub mutation. Continue with the exact `$g:github-issues` invocation and
preserve G's transport, mutation, verification, and recovery contract.

`$g:github-issues` is an invocation handoff, not an availability predicate.
There is no supported alias or conditional form that can probe `$g`. If the
explicit handoff cannot be resolved after the local checks pass, stop with a
runtime dependency blocker and do not substitute direct `gh`, a connector
call, or another skill.

## Block and report

Block before the dependent workflow continues when any check fails. Report the
exact dependency, the failing signal, and the observed evidence. At minimum,
distinguish:

- `plugin-missing`: no exact installed `g@alemar11` entry;
- `plugin-disabled`: the exact entry exists but `enabled` is not `true`;
- `skill-unresolvable`: the reported bundle root or `github-issues` skill is
  missing or malformed;
- `codex-runtime-error`: the list command or JSON response cannot be trusted;
- `codex-dependency-unresolved`: the explicit G handoff fails after the local
  checks pass.

Do not continue with GitHub reads or writes, and do not silently fall back.

For `plugin-missing`, show this manual remediation command without executing
it:

```sh
codex plugin add "g@alemar11" --json
```

The command requires a configured `alemar11` marketplace. Marketplace
registration, enabling a disabled plugin, and opening a fresh task after
installation are separate user-authorized actions. The preflight never runs
them automatically.
