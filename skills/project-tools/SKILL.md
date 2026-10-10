---
name: project-tools
description: "Only when explicitly invoked, install or update repository skills, or configure requested project MCP entries. Excludes global installation and host setup."
---

# Project Tools

## Scope

This skill MUST stay focused on two repository-level operations: installing or
updating skills (including dependency-packaged skill loading), and configuring
MCP entries for the requested clients. A provider's skill CLI may be added as a
repository development dependency when needed for the requested setup.
Infer the target repository, coding agent, and requested action from the
conversation and current project; ask only when these remain ambiguous. Resolve
destination paths before writing and reject links that escape the repository.
Temporary staging for inspecting installation payloads is allowed.

Do not install or update global skills, clients, SDKs, CLIs, or IDEs; change
global configuration or host permissions; manage MCP server lifecycles; or run
application development workflows. Missing host tools, access grants, and host
enablement are prerequisites to report, not setup branches to execute here.

An explanation or preview request does not authorize installation. Keep skill
installation and MCP configuration separate unless both are requested.
Verification covers the repository artifacts and, when available, client
discovery; it must not expand into host setup or permission repair.

## Invocation

Use only when the user explicitly invokes `$project-tools` or asks to use
Project Tools. Do not auto-select this skill from the detected stack, missing
skills, MCP availability, or an ordinary development request. Discussing or
editing this skill does not invoke its installation workflow.

A bare `$project-tools` MUST start work in the current repository, using any
scope already established in the conversation. Detect its environments, install
the relevant missing skills, and update matching installed skills through their
provider workflows. Do not ask the user to choose an operation or confirm this
default. Ask only if the repository cannot be identified or a material conflict
cannot be resolved from the request and project evidence.

Explicit instructions narrow or override that default:

| Request | Action |
| --- | --- |
| No additional instructions | Detect the stack; install missing relevant skills and update those already installed. |
| `setup` | Install missing relevant skills and verify existing ones; do not refresh existing content unless also requested. |
| `update` | Update relevant installed skills only; do not add missing skills or new provider collections. |
| Named environment, skill, client, or package | Restrict work to that selection; apply the requested operation, or install-and-update if none is specified. |
| MCP setup or update | Configure only the named MCP/client entries; do not infer skill installation. |
| Explain, inspect, preview, or dry run | Report findings and proposed actions without writing. |

For `setup` or `update` without a named environment, detect it from the current
repository. A skill-only invocation never implies MCP setup, even for Apple.
Apply the selected operation to each relevant reference below; its examples
do not widen that operation's scope.
Reuse the current coding agent unless clients are explicitly selected; an
unspecified client does not block installing into the shared directory. Apply
the Claude link step when Claude is the current or requested client.

## Detect environments

Inspect project manifests, declared workspaces, build targets, and relevant
first-party source. Exclude installed skills, dependency trees, generated
artifacts, documentation examples, and fixtures from detection. Installed host
tools and stale lockfile entries alone do not establish a project environment.

| Project evidence | Default selection and procedure |
| --- | --- |
| Apple targets in Xcode projects/workspaces, Swift package platforms, or native build/source configuration | [Official Xcode exports](references/apple-skills.md), plus [personal Swift skills through GitHub](references/github-skills.md). |
| Android modules using Android Gradle plugins or equivalent native Android build/source configuration | [Official Android collection](references/android.md) through repository-local `npx skills`. Android CLI is not required to install the skills. |
| React web frontend, evidenced by direct React dependencies plus a web renderer/framework or actual web entry points | [Vercel React skills and React Doctor through GitHub](references/github-skills.md). |
| First-party `components.json` or `registry.json` using a `ui.shadcn.com` schema, or confirmed first-party shadcn/ui component usage | [Official shadcn/ui skill through GitHub](references/github-skills.md). |
| Application dependencies on `@tanstack/*` libraries | [Official dependency-packaged skills through Intent](references/tanstack.md). `@tanstack/intent` alone is tooling, not evidence of an application library. |
| Direct `@playwright/test`, `playwright`, or `@playwright/cli` dependencies, or first-party Playwright tests/configuration | [Official Playwright CLI skill through GitHub](references/github-skills.md). |

Read only the procedures for selected routes. The GitHub reference owns their
source paths, skill identities, and provider-specific selection details.

Select every matching environment in mixed repositories; do not stop at the
first match. A React web app with TanStack needs both routes. React Native's
`react` dependency alone does not justify React web skills; use evidenced Apple
and Android targets for those routes. React, Tailwind, or Radix dependencies
alone do not establish shadcn/ui usage. Respect a user-selected subproject and
deduplicate shared skill installation at the repository root. Intent policy
still belongs to the relevant owning workspace package.

Inventory existing skills by identity and provider provenance before deciding
what is missing or updatable. For environment-based selection in default mode,
include already-installed skills from the selected provider collections even
when optional for a fresh setup. A named skill selection remains restricted to
those names.
Preserve local modifications, explicit exclusions, and pins; do not uninstall
unrelated or apparently obsolete skills. If no supported environment is found,
report the evidence and coverage gap instead of installing a generic bundle.
Continue independent routes when one lacks prerequisites, then report detected
environments and installed, updated, unchanged, or blocked results.

## Clients

Support Codex, Cursor, Pi, and Claude Code. Configure only the requested
clients. All repository-installed skill files MUST live in `.agents/skills/`,
regardless of the client or provider. Install and update each skill there once;
never create a separate copy in a client-specific directory. Configure provider
installers to use this canonical destination rather than their client defaults.

| Client | Discovery path relative to the repository root |
| --- | --- |
| Codex | `.agents/skills/` |
| Cursor | `.agents/skills/` |
| Pi | `.agents/skills/` |
| Claude Code | `.claude/skills` symlink to `../.agents/skills` |

When Claude Code is the current or requested client, read the
[shared directory link procedure](references/claude-code.md). Linking is an
additional step, not another installation. If the requested skills are already
installed and no update is requested, only create or verify the link; do not
re-download or export them. The link exposes the whole shared collection;
client selection is not an isolation boundary.

## Requested MCP configuration

MCP selection requires an explicit request; do not infer it from environment
detection or installed host tools. Read only the selected provider's reference
and configure the requested clients' project files.

| Requested provider | Procedure |
| --- | --- |
| Native Xcode MCP | [Xcode MCP](references/xcode-mcp.md). Skill export is a separate route. |
| Hopper Disassembler MCP setup, repair, or inspection | [Hopper MCP](references/hopper-mcp.md), using its bundled server. |
| Discourse MCP | [Discourse MCP](references/discourse.md). Require explicitly selected forum URLs, verify each site, and configure one fixed-site entry per distinct forum. |

Other language, framework, and tooling installation workflows are not yet
implemented. State that limitation when requested rather than claiming setup
has completed.
