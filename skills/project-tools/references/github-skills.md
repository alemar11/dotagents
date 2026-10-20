# GitHub-managed skills

Use this reference for selected Swift, Vercel React, shadcn/ui, React Doctor,
Playwright CLI, LiveKit Agents, or Sketch skills. Install their instruction
files with authenticated `gh skill`; do not run the providers' native setup
installers.

## Catalog and selection

This table owns the supported source paths and identities. `gh` uses the
installed directory name, which can differ from the skill's frontmatter name.

| Provider | Repository | Source path | Installed / `gh` name | Frontmatter name |
| --- | --- | --- | --- | --- |
| Personal Swift | `alemar11/dotagents` | `skills/swift-docc` | `swift-docc` | `swift-docc` |
| Personal Swift | `alemar11/dotagents` | `skills/swift-api-design` | `swift-api-design` | `swift-api-design` |
| Vercel React | `vercel-labs/agent-skills` | `skills/react-best-practices` | `react-best-practices` | `vercel-react-best-practices` |
| Vercel React | `vercel-labs/agent-skills` | `skills/composition-patterns` | `composition-patterns` | `vercel-composition-patterns` |
| Vercel React | `vercel-labs/agent-skills` | `skills/react-view-transitions` | `react-view-transitions` | `vercel-react-view-transitions` |
| shadcn/ui | `shadcn-ui/ui` | `skills/shadcn` | `shadcn` | `shadcn` |
| React Doctor | `millionco/react-doctor` | `skills/react-doctor` | `react-doctor` | `react-doctor` |
| Playwright CLI | `microsoft/playwright-cli` | `skills/playwright-cli` | `playwright-cli` | `playwright-cli` |
| LiveKit Agents | `livekit/agent-skills` | `skills/reading-livekit-docs` | `reading-livekit-docs` | `reading-livekit-docs` |
| LiveKit Agents | `livekit/agent-skills` | `skills/building-livekit-agents` | `building-livekit-agents` | `building-livekit-agents` |
| LiveKit Agents | `livekit/agent-skills` | `skills/debugging-livekit-agents` | `debugging-livekit-agents` | `debugging-livekit-agents` |
| LiveKit Agents | `livekit/agent-skills` | `skills/testing-livekit-agents` | `testing-livekit-agents` | `testing-livekit-agents` |
| LiveKit Agents | `livekit/agent-skills` | `skills/writing-livekit-scenarios` | `writing-livekit-scenarios` | `writing-livekit-scenarios` |
| LiveKit Agents | `livekit/agent-skills` | `skills/running-livekit-simulations` | `running-livekit-simulations` | `running-livekit-simulations` |
| LiveKit Agents | `livekit/agent-skills` | `skills/operating-livekit-agents` | `operating-livekit-agents` | `operating-livekit-agents` |
| Sketch | `sketch-hq/agents` | `skills/sketch-design-to-code` | `sketch-design-to-code` | `sketch-design-to-code` |
| Sketch | `sketch-hq/agents` | `skills/sketch-design-from-reference` | `sketch-design-from-reference` | `sketch-design-from-reference` |

- **Personal Swift:** select both for an Apple environment. These personal
  skills cover Swift-DocC and Swift API design; they are separate from official
  Xcode exports. Do not use `--upstream` to replace their intended source, or
  run their workflows or reference-refresh procedures during installation.
- **Vercel React:** select `react-best-practices` and `composition-patterns`
  for a React web environment. These are Vercel-maintained, not React-team
  skills. Add `react-view-transitions` only when explicitly requested or when
  usage and the project's React version establish relevance and compatibility.
  Installation does not authorize adopting Next.js, SWR, or experimental APIs
  to match upstream examples.
- **shadcn/ui:** select `shadcn` for fresh setup. Other skills, such as
  `migrate-radix-to-base`, require explicit selection to install. Skill setup
  does not run component commands or authorize migrations.
- **React Doctor and Playwright CLI:** select the corresponding catalog name.
  Additional upstream skills require explicit selection to install. Installing
  files does not require or install their runtime packages, download browsers,
  add hooks or CI, configure MCP, or run diagnostics and tests. Report existing
  runtime availability separately; preserve project version pins and runners
  even when upstream examples use `@latest`.
- **LiveKit Agents:** select all seven catalog skills for a LiveKit Agents
  environment or a LiveKit-wide request; they hand off to each other by name
  and load `reading-livekit-docs` first. A request naming specific skills
  selects only those; report referenced siblings that remain missing. If the
  LiveKit Claude Code plugin is enabled for a selected Claude client, project
  copies would duplicate its skills and compete for routing; report this and
  ask before installing them. Upstream replaced `livekit-agents` and
  `livekit-simulations` with this set; report installed copies as stale and
  remove them only on request. Installing files does not install or
  authenticate the `lk` CLI, create a LiveKit Cloud project, or configure the
  LiveKit Docs MCP; report their availability separately.
- **Sketch:** select both catalog skills when Sketch skills are requested;
  a request naming one skill selects only that skill. Follow the selected
  setup/update operation. These cover Sketch-to-code and design creation from
  references. Installing them does not install a client plugin, configure MCP,
  start Sketch, or execute their design workflows. Their runtime requires
  Sketch MCP; report its availability separately and use the
  [Sketch MCP procedure](sketch-mcp.md) only when configuration is also requested.

Apply the entrypoint's operation and selection rules. For explicitly selected
additional skills from these providers, discover their actual source paths and
identities before installation rather than guessing them.

## Install

Check that `gh skill install`, `update`, and `list` are available. Missing or
outdated `gh` is a host prerequisite to report, not install here. Run from the
target repository root. Inspect existing destinations, local changes, pins,
and source tracking before writing; reconcile collisions or untracked copies
without force-overwriting them.

When collection discovery is needed, omit the skill path and disable
interactive input; this lists published skills without installing them:

```sh
gh skill install vercel-labs/agent-skills </dev/null
```

Install each selected missing skill using its exact repository and source path
from the catalog. For example, a named React Doctor installation is:

```sh
gh skill install millionco/react-doctor skills/react-doctor --dir .agents/skills
```

Keep `--dir .agents/skills` for every client; it overrides agent and scope
defaults. Never use install `--all`: these collections contain unrelated or
optional skills. Resolve destination paths inside the target repository.

Without a pin, `gh` chooses the repository's latest release, falling back to
default-branch HEAD. Record the resolved ref; add `--pin <tag-or-commit>` only
for a requested fixed revision. That ref identifies skill content, not
necessarily a runtime package version; unpushed source changes are unavailable.

## Update

Inventory installed names and verify that each source matches its selected
provider repository:

```sh
gh skill list --dir .agents/skills --json skillName,sourceURL,version,pinned,path
```

Copies from other installers or manual copying without `gh` source metadata
need provenance reconciliation before this updater can manage them. Preview
and apply only the selected installed names. For a request selecting both
React Doctor and Playwright CLI:

```sh
gh skill update react-doctor playwright-cli --dir .agents/skills --dry-run
gh skill update react-doctor playwright-cli --dir .agents/skills --all
```

Replace the name list with the actual selection. Update `--all` confirms the
selected updates; never omit the name filter or `--dir`, since the default scan
can include user installations. A dry run compares upstream versions rather
than detecting local edits. Preserve local modifications and pins; do not add
`--force` or `--unpin` implicitly.

## Verify

Verify complete skill trees, including linked references, rules, assets, and
installer-managed source metadata. Keep that metadata for future updates.
Inspect the scoped repository diff and the shared Claude link when applicable.
Report installed, updated, unchanged, or blocked names separately from discovery
in a running client.

## Sources

- [Personal Swift skills](https://github.com/alemar11/dotagents)
- [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills)
- [shadcn/ui skill](https://github.com/shadcn-ui/ui/tree/main/skills/shadcn)
- [React Doctor skill](https://github.com/millionco/react-doctor/tree/main/skills/react-doctor)
- [Playwright CLI skill](https://github.com/microsoft/playwright-cli/tree/main/skills/playwright-cli)
- [LiveKit Agent Skills](https://github.com/livekit/agent-skills)
- [Official Sketch skills](https://github.com/sketch-hq/agents)
- [GitHub CLI install](https://cli.github.com/manual/gh_skill_install)
- [GitHub CLI update](https://cli.github.com/manual/gh_skill_update)
