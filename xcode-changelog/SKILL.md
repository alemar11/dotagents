---
name: xcode-changelog
description: Resolve the active Xcode version or a requested version and print the matching Apple Xcode Release Notes entry from the official release-notes site.
---

# Xcode Changelog

## Goal

Resolve the active Xcode version, or a user-requested version, and return the matching Apple Xcode Release Notes entry.

## Trigger rules

- Use when the user asks for Xcode changelog details, Xcode release notes, or what changed in their current Xcode.
- Use when the user wants release notes for a specific Xcode version such as `26.4`, `26.5 beta`, or `16.4`.
- Prefer this skill over ad-hoc browsing when the task is to match the active Xcode or a named version to Apple’s official release notes.

## Workflow

1. Run `python3 scripts/print_xcode_changelog.py`.
2. If the user requested a specific version, run `python3 scripts/print_xcode_changelog.py --version "<version label>"`.
3. Share the single `Xcode` section printed by the script.
4. Preserve the `Source:` URL in the final answer for traceability.
5. If the script reports a normalized or fallback match, keep that explanation in the user-facing summary.

## Runtime Notes

- This skill is portable, but it requires macOS with `python3`, `xcodebuild`, `xcode-select`, `plutil`, and network access to Apple’s documentation.

## Script

- `scripts/print_xcode_changelog.py`: Resolves the active Xcode via local tooling, optionally accepts `--version`, fetches Apple’s official Xcode Release Notes index from the markdown-backed documentation endpoint, matches the best release-notes entry by title/version, and prints one `Xcode` section with the cleaned note body plus source URL.
