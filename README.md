# dotagents

Reusable agent skills and project maintainer skills.

This repository is organized around reusable installable skills:

- **Reusable skills** under `skills/`, which can be linked locally or installed into Codex.

Project-only maintainer workflows live under `.agents/skills/`. The retained
`.agents/plugins/marketplace.json` registry is empty; the current catalog ships
as skills.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `skills/` | Reusable skills, each with a `SKILL.md` entrypoint and `agents/openai.yaml` metadata. |
| `.agents/skills/` | Project-local maintainer skills for working on this repository. |
| `.agents/plugins/marketplace.json` | Local plugin discovery surface for this checkout. |
| `skills-link.sh` | Local development helper that links reusable skills into `~/.agents/skills` (Codex) and `~/.claude/skills` (Claude Code). |

## Reusable Skills

| Skill | Purpose |
| --- | --- |
| `ms-roberts` | Use when medium or long user-authored English prompts contain grammar errors; append corrections and learning tips after the main answer. |
| `okf` | Write, scaffold, inspect, and validate Open Knowledge Format Markdown bundles with the shipped CLI. |
| `skill-cli-creator` | Create, refactor, or check skill CLIs against one shared standard, with a template and a checker. |
| `postgres` | Inspect Postgres databases, design or run SQL, and diagnose PostgreSQL through the shipped CLI. |
| `swift-api-design` | Design, rename, or review Swift API surfaces using the bundled official API Design Guidelines. |
| `swift-docc` | Author, review, preview, or publish Swift-DocC symbol documentation, articles, and tutorials. |
| `youtube` | Search YouTube videos and playlists or answer from timestamped transcripts. Use for YouTube links and spoken-content research. |
| `ghostty` | Inspect or arrange Ghostty terminals and edit configuration or keybindings when explicitly requested. |
| `xcode-whats-new` | Explicitly read official release notes for the active, latest, or requested stable or beta Xcode. |

## Skill Dependencies

- `maintainer` uses its local health and validation workflows for diagnosis; it requires `$skill-creator` or `$plugin-creator` for substantial public reshapes and native `codex review` for non-trivial implementation closeout.

## Project-Local Skills

| Skill | Path | Purpose |
| --- | --- | --- |
| maintainer | `.agents/skills/maintainer/` | Explicitly invoke to run all routine maintenance, including managed source updates. Arguments narrow scope; audit is read-only. |

Project-local skills are repository-specific and are not included in reusable install commands.

## Installation

### Link Reusable Skills For Local Development

Run this from the repository root to link `skills/` into `~/.agents/skills`
(Codex) and `~/.claude/skills` (Claude Code):

```sh
./skills-link.sh
```

Pass `--agent codex` or `--agent claude` to link only one target; the default is
`--agent all`.

This helper only links reusable skills. It does not install, mirror, or rewrite plugin marketplace entries.
It excludes `swift-api-design` and `swift-docc` and removes existing links to
those skills owned by this checkout. Install them per project.

### Install Reusable Skills With `skill-installer` (Codex-only)

Inside Codex, install all reusable skills with:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/ms-roberts skills/okf skills/skill-cli-creator skills/postgres skills/swift-api-design skills/swift-docc skills/youtube skills/xcode-whats-new skills/ghostty
```

Install one reusable skill by passing only its path:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/okf
```

Replace `skills/okf` with any path listed in the reusable skills table.

### Install Reusable Skills With `npx skills`

These commands use the [`vercel-labs/skills`](https://github.com/vercel-labs/skills) CLI and target Codex directly.

List the skills available in this repository:

```sh
npx skills add alemar11/dotagents --list
```

Install all reusable skills globally for Codex:

```sh
npx skills add alemar11/dotagents -a codex -g -y \
  --skill ms-roberts \
  --skill okf \
  --skill skill-cli-creator \
  --skill postgres \
  --skill swift-api-design \
  --skill swift-docc \
  --skill youtube \
  --skill xcode-whats-new \
  --skill ghostty \
```

Install one reusable skill globally for Codex:

```sh
npx skills add alemar11/dotagents -a codex -g -y --skill okf
```

Replace `okf` with any skill name from the reusable skills table. Omit `-g` to install into the current project's `.agents/skills/` instead of your global `~/.codex/skills/`.

Restart Codex after installing or updating skills.
