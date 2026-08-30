---
name: whats-new
description: Resolve active, latest stable and beta, or requested Xcode release notes from Apple official release-notes pages.
---

# Xcode What's New

## Goal

Resolve the active Xcode version, a user-requested stable or beta version, or
list the available Apple Xcode Release Notes entries. For active local Xcode
reports, include the installed version's release notes plus the latest stable
and latest beta notes when they are distinct from the installed entry.

## Runtime surface

- The supported runtime entrypoint is the shipped
  `scripts/print_xcode_changelog.py` helper inside this skill package.
- If your current working directory is the skill root, run it as
  `python3 scripts/print_xcode_changelog.py`.
- If you are invoking the skill from another repo, resolve the installed skill
  root first and run
  `python3 <xcode-whats-new-skill-root>/scripts/print_xcode_changelog.py`.

## Trigger rules

- Use when the user asks for Xcode changelog details, Xcode release notes, or what changed in their current Xcode.
- Use when the user wants to compare their installed Xcode changelog against the latest available Apple release notes.
- Use when the user wants release notes for a specific Xcode version such as `26.4`, `26.5 beta`, or `16.4`.
- Use when the user asks which Xcode versions have release notes or wants the available Xcode release-note versions listed.
- Prefer this skill over ad-hoc browsing when the task is to match the active Xcode or a named version to Apple’s official release notes.

Before selecting a lookup path, read
[references/states.md](references/states.md) for the canonical selection mode,
release channel, and numbered-beta matching behavior.

## Workflow

1. Run the shipped helper for the active local Xcode:
   `python3 <xcode-whats-new-skill-root>/scripts/print_xcode_changelog.py`.
   The default report prints the installed Xcode release notes and appends the
   latest stable and latest beta notes when those entries are different.
2. If the user requested a specific version, run
   `python3 <xcode-whats-new-skill-root>/scripts/print_xcode_changelog.py --version "<version label>"`.
   Use labels such as `26.6`, `27 beta`, or `27 beta 6`. A numbered beta must
   match exactly; do not substitute stable notes for a missing beta.
3. If the user asked which versions are available, run
   `python3 <xcode-whats-new-skill-root>/scripts/print_xcode_changelog.py --list`.
4. Share the single `Xcode` section printed by the script.
5. Preserve the `Source:` URL lines in the final answer for traceability.
6. If the script reports a normalized or fallback match, keep that explanation in the user-facing summary.

## Runtime Notes

- This skill is portable, but it requires macOS with `python3`, `xcodebuild`, `xcode-select`, `plutil`, and network access to Apple’s documentation.

## Script

- `scripts/print_xcode_changelog.py`: the shipped skill helper that resolves
  the active Xcode via local tooling, supports `--version` for explicit
  lookups and `--list` for index listings, fetches Apple’s official Xcode
  Release Notes index from the markdown-backed documentation endpoint, matches
  stable and numbered-beta titles by channel and version, and prints one
  `Xcode` section with the requested notes, the installed notes plus distinct
  latest stable and beta notes, or the available version list plus source URLs.
