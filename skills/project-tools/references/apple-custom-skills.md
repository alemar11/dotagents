# Personal Swift skills

Install or update these reusable skills from `alemar11/dotagents` when requested:

| Skill | Purpose |
| --- | --- |
| `swift-docc` | Author, review, preview, or publish Swift-DocC documentation, articles, and tutorials. |
| `swift-api-design` | Design, rename, or review Swift APIs using the bundled official API Design Guidelines. |

These are personal skills maintained in that repository, separate from Apple's
Xcode exports. Install their complete directories, including bundled references
and assets. Installation does not run their workflows or refresh their sources.

## Install

Use the authenticated `gh` CLI. Check `gh skill install --help` and
`gh skill update --help`; if the installed CLI lacks these commands, report the
prerequisite and suggest a CLI update without changing host tooling here.
Run from the target Git repository root and resolve the destination before
writing, preserving existing skills and rejecting links outside the repository.

To discover published skills without installing them, omit the skill name and
`--all` and disable interactive input:

```sh
gh skill install alemar11/dotagents </dev/null
```

Install only the requested names into the canonical directory, for any client:

```sh
gh skill install alemar11/dotagents skills/swift-docc --dir .agents/skills
gh skill install alemar11/dotagents skills/swift-api-design --dir .agents/skills
```

`--dir` overrides agent and scope selection; resolve it inside the target
repository. For Claude Code, apply the shared
[client link workflow](../SKILL.md#claude-code-link). If the skills are already
installed and no update is requested, only create or verify the link.
Never use `--all` on install:
the source repository contains unrelated reusable and maintenance skills.

Without a pin, `gh` selects the repository's latest release, falling back to
default-branch HEAD. Inspect its resolved ref; local unpushed changes are not
available remotely. Use `--pin <tag-or-commit>` only for a requested fixed
revision. Do not use `--upstream`: the intended source is the personal skill,
even where it bundles official documentation.

If the destination already contains a skill, inspect its provenance and local
changes. Use the update workflow for matching GitHub-managed installations.
In default mode, install missing selected names and update existing ones.
For `setup`, keep existing content; for `update`, do not install missing names.
Do not overwrite custom or manually installed copies, or replace symlinks, with
`--force`; reconcile them within the user's authorized scope first.

## Update

`gh skill update` normally scans both project and user installations. Always
provide the actual repository-local directory and only the requested installed
names. Verify their source is `alemar11/dotagents` before updating. For the shared
directory, preview and then apply:

```sh
gh skill update swift-docc swift-api-design --dir .agents/skills --dry-run
gh skill update swift-docc swift-api-design --dir .agents/skills --all
```

Use the same directory for every client. If only one skill is requested or
installed, pass only that name. Here `--all` applies the selected updates without
another prompt; keep both the name filter and directory restriction. Preserve
local edits and pins; do not add `--force` or `--unpin` implicitly. Skills without
GitHub tracking metadata require a deliberate migration before this updater can
manage them. Install missing skills only when the request includes installation.

## Verify

Inspect the scoped diff and the installed skill trees, including their bundled
assets and references. Verify source, version, scope, and resolved path:

```sh
gh skill list --dir .agents/skills --json skillName,sourceURL,version,pinned,path
```

Verify the shared Claude link when requested. Retain `gh`'s source-tracking frontmatter
so future updates work. Report installed, updated, unchanged, or skipped names;
file installation alone does not prove a running client has reloaded discovery.

## Sources

- [Personal skill repository](https://github.com/alemar11/dotagents)
- [GitHub CLI install](https://cli.github.com/manual/gh_skill_install)
- [GitHub CLI update](https://cli.github.com/manual/gh_skill_update)
