# Codex Runtime Surface

This reference is the SE-wide owner of read-only Codex surface classification.
Surface-aware SE skills must use this result instead of defining their own
detection heuristics.

## Classification

Derive one transient `codex_runtime_surface` fact from the runtime's explicit
description of the current invocation:

| Value | Required evidence |
| --- | --- |
| `codex-app` | Authoritative runtime context identifies the current interaction as a task in the Codex desktop application. |
| `codex-cli` | Authoritative runtime context identifies the current interaction as a Codex CLI session rather than an App task. |
| `unresolved` | The runtime supplies no trustworthy surface identity, or available evidence conflicts. |

The classification is an execution fact, not user preference or durable
configuration. Do not ask the user to choose when authoritative runtime
context already identifies the surface.

## Evidence boundary

Do not infer the surface from any of these signals alone:

- current working directory, shell, terminal, or operating system;
- availability or absence of a particular task, delegation, or UI capability;
- environment variables, process names, executable paths, or cached settings;
- repository files, prompt wording, previous runs, or user recollection.

Capability checks happen only after classification and remain owned by the
invoking skill's selected surface branch. A missing capability never changes
`codex-app` into `codex-cli` or the reverse.

When the result is `unresolved`, the invoking skill decides whether its work
can proceed without a known surface. It must not guess, silently choose a
branch, or claim that a surface-specific effect occurred.
