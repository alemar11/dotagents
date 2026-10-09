---
name: project-tools
description: "Install and update repository skills for the detected project stack, or configure project MCP entries when requested. Excludes global installation and host setup."
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
Apply the selected operation to every provider reference below; its examples
do not widen that operation's scope.
Reuse the current coding agent unless clients are explicitly selected; an
unspecified client does not block installing into the shared directory. Apply
the Claude link step when Claude is the current or requested client.

## Detect environments

Inspect project manifests, declared workspaces, build targets, and relevant
first-party source. Exclude installed skills, dependency trees, generated
artifacts, documentation examples, and fixtures from detection. Installed host
tools and stale lockfile entries alone do not establish a project environment.

| Project evidence | Default skill selection |
| --- | --- |
| Apple targets in Xcode projects/workspaces, Swift package platforms, or native build/source configuration | Official Apple skills exported by the selected Xcode, plus personal `swift-docc` and `swift-api-design`. |
| Android modules using Android Gradle plugins or equivalent native Android build/source configuration | Official Android collection. |
| React web frontend, evidenced by direct React dependencies plus a web renderer/framework or actual web entry points | Vercel `react-best-practices` and `composition-patterns`; add View Transitions only for evidenced compatible usage. |
| Application dependencies on `@tanstack/*` libraries | Official skills shipped with those installed dependencies, enabled through Intent. `@tanstack/intent` alone is tooling, not evidence of an application library. |

Select every matching environment in mixed repositories; do not stop at the
first match. A React web app with TanStack needs both routes. React Native's
`react` dependency alone does not justify React web skills; use evidenced Apple
and Android targets for those routes. Respect a user-selected subproject and
deduplicate shared skill installation at the repository root. Intent policy
still belongs to the relevant owning workspace package.

Inventory existing skills by identity and provider provenance before deciding
what is missing or updatable. In default mode, include already-installed skills
from the selected provider collections even when optional for a fresh setup.
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

For Claude Code, linking the shared directory is an additional step, not another
installation. If the requested skills are already installed and no update is
requested, only create or verify the link; do not re-download or export them.
The link exposes the whole shared collection to Claude Code. Client selection
is not an isolation boundary.

### Claude Code link

Inspect `.agents`, `.agents/skills`, `.claude`, and `.claude/skills` before
writing. Resolve their paths and reject links outside the repository. If the
destination is absent (neither a file nor a symlink), run from the repository root:

```sh
mkdir -p .agents/skills .claude
ln -s ../.agents/skills .claude/skills
```

If the existing link already resolves to the canonical directory, keep it.
Never use force-link replacement over an existing path. For an existing real
`.claude/skills` directory, reconcile its entries into `.agents/skills`:
move non-conflicting entries, preserve their full contents, and consolidate
identical duplicates only after comparison. For differing same-name entries or
an unexpected link, preserve both and resolve ownership before replacing
anything. Remove only the emptied old directory, then create the link. Report
unresolved collisions while completing unaffected requested work.

Verify that `.claude/skills` is a symlink resolving to this repository's
`.agents/skills`, with the same readable skill trees. Re-running setup must
reuse that link and the installed skills. MCP configuration remains in each
client's own configuration files. Dependency-loaded skills such as TanStack
Intent stay with their packages; do not copy them into a second catalog merely
to create the link.

## Android

For Android skill installation or updates, read
[references/android.md](references/android.md) and use its repository-local
`npx skills` workflow. Android CLI is not required to install the skills.

## Apple

For official Apple skill installation or updates, read
[references/apple-skills.md](references/apple-skills.md); Xcode provides the
embedded skill export. For the personal `swift-docc` and `swift-api-design`
skills from `alemar11/dotagents`, read
[references/apple-custom-skills.md](references/apple-custom-skills.md).
For project-local native Xcode MCP configuration, read
[references/xcode-mcp.md](references/xcode-mcp.md).
Run only the requested workflows; a failure in one does not
prevent independent work in the other.

## React

For Vercel's React skills, read [references/react.md](references/react.md).
Use `gh skill` to install only the relevant skills into the shared directory.

## TanStack

For official TanStack skills, read [references/tanstack.md](references/tanstack.md).
Use project-local TanStack Intent to discover and load skills shipped with the
installed library versions.

## Discourse MCP

For explicitly requested Discourse MCP setup, read
[references/discourse.md](references/discourse.md). Require one or more explicitly
selected forum URLs, verify each site, and configure one fixed-site entry per
distinct verified forum in the requested clients' project files.
Do not infer this MCP from environment detection or install it globally.

Other language, framework, and tooling installation workflows are not yet
implemented. State that limitation when requested rather than claiming setup
has completed.
