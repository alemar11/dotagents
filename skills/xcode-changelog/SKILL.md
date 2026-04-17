---
name: xcode-changelog
description: Resolve the active Xcode version, a requested Xcode version, or list available Xcode release notes from the official Apple release-notes site.
---

# Xcode Changelog

## Goal

Resolve the active Xcode version, a user-requested version, or list the available Apple Xcode Release Notes entries.

## Trigger rules

- Use when the user asks for Xcode changelog details, Xcode release notes, or what changed in their current Xcode.
- Use when the user wants release notes for a specific Xcode version such as `26.4`, `26.5 beta`, or `16.4`.
- Use when the user asks which Xcode versions have release notes or wants the available Xcode release-note versions listed.
- Prefer this skill over ad-hoc browsing when the task is to match the active Xcode or a named version to Apple’s official release notes.

## Workflow

1. Run `python3 scripts/print_xcode_changelog.py` for the active local Xcode.
2. If the user requested a specific version, run `python3 scripts/print_xcode_changelog.py --version "<version label>"`.
3. If the user asked which versions are available, run `python3 scripts/print_xcode_changelog.py --list`.
4. Share the single `Xcode` section printed by the script.
5. Preserve the `Source:` URL lines in the final answer for traceability.
6. If the script reports a normalized or fallback match, keep that explanation in the user-facing summary.

## Runtime Notes

- This skill is portable, but it requires macOS with `python3`, `xcodebuild`, `xcode-select`, `plutil`, and network access to Apple’s documentation.

## Script

- `scripts/print_xcode_changelog.py`: Resolves the active Xcode via local tooling, supports `--version` for explicit lookups and `--list` for index listings, fetches Apple’s official Xcode Release Notes index from the markdown-backed documentation endpoint, matches the best release-notes entry by title/version, and prints one `Xcode` section with either the cleaned note body or the available version list plus source URLs.
