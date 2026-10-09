# React skills from Vercel

Use the official Vercel collection at `vercel-labs/agent-skills` for requested
React skill installation or updates. These skills are maintained by Vercel,
not the React team. Select only the relevant skills:

| Install directory / `gh` name | Skill frontmatter name | Coverage |
| --- | --- | --- |
| `react-best-practices` | `vercel-react-best-practices` | React and Next.js performance, rendering, data fetching, and bundle size. |
| `composition-patterns` | `vercel-composition-patterns` | Component composition and reusable APIs, including React 19 patterns. |
| `react-view-transitions` | `vercel-react-view-transitions` | Optional: React View Transition APIs and related Next.js integration. |

For a general React setup, use the first two. Include View Transitions only
when requested or relevant to the project's work and supported React version.
Installation does not authorize adopting Next.js, SWR, experimental APIs, or
changing the project's existing libraries to match examples in the skills.

## Install

Use authenticated `gh` and check that `gh skill install`, `update`, and `list`
are available. A missing or outdated CLI is a host prerequisite; report it
without installing host tools. From the target repository root, discover the
published collection without installing anything:

```sh
gh skill install vercel-labs/agent-skills </dev/null
```

Inspect existing skill directories and source tracking before writing. Preserve
custom skills, local modifications, and pins; do not force-overwrite collisions.
In default mode, install missing selected skills and update existing ones.
For `setup`, keep existing content; for `update`, skip missing skills.
Install the selected skills into the canonical shared directory:

```sh
gh skill install vercel-labs/agent-skills skills/react-best-practices --dir .agents/skills
gh skill install vercel-labs/agent-skills skills/composition-patterns --dir .agents/skills
```

For the optional View Transitions skill:

```sh
gh skill install vercel-labs/agent-skills skills/react-view-transitions --dir .agents/skills
```

`--dir` overrides agent/scope defaults; resolve it inside the repository.
Without an explicit pin, `gh` selects the latest repository release, falling
back to default-branch HEAD. Record the resolved ref; use `--pin <tag-or-commit>`
only when a fixed revision is requested. Never use install `--all`: the
collection also contains non-React and vendor-specific workflows.

Apply the shared [Claude link workflow](../SKILL.md#claude-code-link) when Claude
Code support is requested. If the selected skills are already installed and no
update is requested, reuse them and only create or verify that link.

## Update and verify

Use the installed names reported by `gh skill list`, which can differ from the
`vercel-` names in frontmatter. Confirm their source is
`https://github.com/vercel-labs/agent-skills`. Preview and apply only the requested
installed names, always restricting the scan to the repository directory:

```sh
gh skill update react-best-practices composition-patterns --dir .agents/skills --dry-run
gh skill update react-best-practices composition-patterns --dir .agents/skills --all
gh skill list --dir .agents/skills --json skillName,sourceURL,version,pinned,path
```

Adjust the name list to the requested scope; include `react-view-transitions`
only if installed and selected. Update `--all` confirms the selected updates;
never omit the name filter or `--dir`. Preserve local changes and version pins
instead of adding `--force` or `--unpin` implicitly. Manually installed copies
without GitHub metadata need provenance reconciliation before using this updater.

Check complete skill trees, including supporting files and `gh` source metadata,
the scoped Git diff, and the Claude link when applicable. Distinguish installed
files and successful update checks from discovery in a running client.

## Sources

- [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills)
- [Vercel React best practices](https://vercel.com/blog/introducing-react-best-practices)
- [GitHub CLI install](https://cli.github.com/manual/gh_skill_install)
- [GitHub CLI update](https://cli.github.com/manual/gh_skill_update)
