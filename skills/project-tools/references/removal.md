# Removal

Use this reference for removal advice and removal requests covering repository
skills, project MCP entries, or both. Read the provider reference of each
affected skill or MCP provider for its specifics. This procedure does not
remove client plugins, global installations, or global configuration.

## Authorization

| Request | Action |
| --- | --- |
| Advice, such as "what can I remove" | Report candidates and their evidence without writing. |
| Named skills or MCP entries | Remove only those. |
| Unneeded or stale items, without names | Remove conclusive candidates; report the rest as recommendations. |

A request that names skills or MCP entries is limited to that kind; a generic
cleanup covers both.

Removal must stay recoverable: Git restores committed content, providers
reinstall unmodified skills, and provider references reproduce standard MCP
entries. Ask before deleting local modifications, custom content, or
customized entries that none of these can restore, even when named.

## Candidates

A candidate is conclusive when repository evidence supports it:

- **Environment gone:** an environment route installed the skill, and the
  project no longer has that route's detection evidence under the installation
  rules. For an MCP entry, the project no longer has the provider's
  [recommendation evidence](../SKILL.md#mcp-entries). Ambiguous evidence, such
  as a stale lockfile entry or a subproject outside the selected scope, is not
  conclusive.
- **Retired upstream:** the provider no longer publishes the skill's source.
  Check its current listing or export; an up-to-date update check does not
  prove that the source still exists.

A skill or MCP server that also reaches a client through another source, such
as a client plugin bundling it or a second entry for the same server, is a
duplicate. Report which copy to keep, and remove the other only when asked.

Items installed only by explicit selection record a user choice: Sketch skills,
optional upstream additions, Hopper entries, and Discourse entries for forums
outside the known destinations. Recommend removing them only when their source
is retired. Custom skills, entries for unsupported servers, and items of
unknown provenance are never candidates.

Remove a collection whose skills reference each other by name, such as
LiveKit Agents, as a set when its environment is gone. After a partial
removal, report remaining skills that still name a removed one.

## Skills

Before writing, inventory each target's provider provenance, Git tracking, and
local modifications. Resolve paths inside `.agents/skills/`; for a symlinked
entry, remove the link, never its target. Use the route that owns the
provenance:

| Provenance | Procedure |
| --- | --- |
| `gh skill` metadata in `SKILL.md` | [GitHub-managed skills](github-skills.md#remove) |
| `android/skills` in `skills-lock.json` | [Android](android.md#remove) |
| Xcode export | [Official Apple skills](apple-skills.md#remove) |
| TanStack Intent | [TanStack Intent](tanstack.md#remove) |

Every client reads the shared `.agents/skills/` collection, so removal applies
to all of them. Keep the `.claude/skills` link unless its removal is
requested. Report project instructions that still name a removed skill; edit
only provider-managed blocks.

A later default or setup run reinstalls a removed skill whose route still
matches the project. State this when removing such a skill.

## MCP entries

Inventory the entries in every client's project file and identify each by its
effective server, as its provider reference describes, not by its name. Remove
an entry from every project file holding it unless clients are named. Delete
only that entry: the `[mcp_servers.<name>]` table and its subtables in
`.codex/config.toml`, or the `mcpServers` key in `.cursor/mcp.json`,
`.pi/mcp.json`, and `.mcp.json`. Keep other entries, other settings, and a file
that the removal leaves empty.

Client commands may perform the same removal only with project scope:
`claude mcp remove --scope project <name>` or `pi mcp remove <name> --local`.
Without a scope, Claude removes the name from whichever scope holds it and Pi
edits its global file; `codex mcp remove` edits only global configuration.
Leave client approvals, credentials, and profiles referenced by a removed entry
unchanged, and report them.

## Verify

Confirm that each removed skill directory and its provider tracking entry are
gone, and parse each changed MCP file. Check that unrelated skills and entries
remain intact and that the scoped diff contains only the removal. Report
removed, kept, and blocked items separately, with the evidence for each
removal.
