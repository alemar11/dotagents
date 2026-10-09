---
name: project-tools
description: "Install or update Android, Apple, TanStack, and personal Swift skills and configure MCP entries at repository scope. Excludes global installation and host setup."
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

## TanStack

For official TanStack skills, read [references/tanstack.md](references/tanstack.md).
Use project-local TanStack Intent to discover and load skills shipped with the
installed library versions.

Other language, framework, and tooling installation workflows are not yet
implemented. State that limitation when requested rather than claiming setup
has completed.
