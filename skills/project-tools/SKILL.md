---
name: project-tools
description: "Install or update skills and configure MCP entries only at repository scope. Supports official Android and Xcode skills and Apple's native Xcode MCP; excludes global installation and host setup."
---

# Project Tools

## Scope

This skill MUST stay focused on two repository-level operations: installing or
updating skill files, and configuring MCP entries for the requested clients.
Infer the target repository, coding agent, and requested action from the
conversation and current project; ask only when these remain ambiguous. Resolve
destination paths before writing and reject links that escape the repository.
Temporary staging for inspecting installation payloads is allowed.

Do not install or update global skills, clients, SDKs, CLIs, or IDEs; change
global configuration or host permissions; manage MCP server lifecycles; or run
application development workflows. Missing tools, access grants, and host
enablement are prerequisites to report, not setup branches to execute here.

An explanation or preview request does not authorize installation. Keep skill
installation and MCP configuration separate unless both are requested.
Verification covers the repository artifacts and, when available, client
discovery; it must not expand into host setup or permission repair.

## Clients

Support Codex, Cursor, Pi, and Claude Code. Configure only the requested
clients. Use these project-local skill destinations for exported or copied
skills; provider installers may use another documented discovery directory.

| Client | Skill directory relative to the repository root |
| --- | --- |
| Codex | `.agents/skills/` |
| Cursor | `.agents/skills/` |
| Pi | `.agents/skills/` |
| Claude Code | `.claude/skills/` |

Clients sharing a destination need only one copy. Do not create duplicate
same-name skills across a client's discovery directories. Shared directories
can also be discovered by other compatible clients; they are not an isolation
boundary. Preserve existing custom skills and project-local layouts.

## Android

For Android skill installation or updates, read
[references/android.md](references/android.md) and use its repository-local
`npx skills` workflow. Android CLI is not required to install the skills.

## Xcode

For Xcode's embedded skill export or project-local native MCP configuration, read
[references/xcode.md](references/xcode.md) and select the requested workflow.

Other language, framework, and tooling installation workflows are not yet
implemented. State that limitation when requested rather than claiming setup
has completed.
