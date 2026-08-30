---
name: youtube
description: Search YouTube videos and playlists, retrieve timestamped transcripts, and search spoken content across a playlist. Use when the user provides a YouTube URL or asks to find, summarize, compare, quote, or locate topics in YouTube videos. Not for uploading or changing YouTube content.
---

# YouTube

## Goal

Use the shipped `scripts/youtube` CLI to search YouTube, inspect playlists,
retrieve captions as normalized timestamped segments, and search spoken content
across playlist videos. The CLI uses `yt-dlp` for YouTube access and owns the
stable JSON, cache, transcript normalization, and error contracts.

## Required Preflight

From this skill's root, start with:

```bash
scripts/youtube --json doctor
scripts/youtube --json preflight
```

Every network command performs the same `yt-dlp` preflight before contacting
YouTube. If it reports `yt-dlp-missing` or `yt-dlp-broken`, stop and surface the
provided installation hint. Do not silently install a dependency, switch to a
paid provider, or claim that the requested search ran.

## Workflow

- For a topic, run `scripts/youtube --json videos search ...`, choose relevant
  candidates, then fetch only the transcripts needed for the answer.
- For one video URL or ID, use `transcripts languages` when language choice
  matters, then `transcripts get`.
- For a playlist, use `playlists list` to inspect its size and metadata. Use
  `playlists search-transcripts` for spoken-content search. Pass
  `--max-videos 0` only when the user wants the complete playlist rather than
  the bounded default.
- Use `--json` for agent consumption. Preserve video IDs, caption source,
  language, timestamps, scope, cache, and partial-result state in the answer.
- Read [references/cli.md](references/cli.md) when exact commands, options, or
  JSON shapes are needed.
- Read [references/states.md](references/states.md) before interpreting CLI
  modes or any `*_state`, `caption_source`, `cache_state`, or `match_mode`
  value.

## Evidence and Access Boundaries

- A transcript proves spoken caption content, not unspoken visuals, slides, or
  demonstrations. State that limitation when it affects the answer.
- Prefer manual captions; use automatic captions when manual captions are not
  available. Report which source was used.
- Keep direct quotations brief. Prefer paraphrase, include timestamps, and use
  the returned moment URL when a claim depends on a specific passage.
- Missing, disabled, private, blocked, or language-mismatched captions are
  explicit failures. Never fill gaps from the title or description.
- Public and accessible unlisted resources need no account. Use
  `--cookies-from-browser` only when the user explicitly places private,
  account-scoped, age-restricted, Watch Later, or Liked content in scope. Never
  export or persist browser cookies.
- Search and transcript reads do not write to the working repository. Successful
  transcript retrieval lazily writes a rebuildable cache under
  `~/.cache/dotagents/skills/youtube/`; use `--no-cache` when the user does not
  want that cache.

## CLI Maintenance

- Normal runtime execution stays on `scripts/youtube`; the implementation is a
  standard-library Python artifact with no maintenance project.
- `VERSION` in `scripts/youtube` is the CLI semver source of truth. Use major
  for breaking command or JSON changes, minor for compatible capabilities, and
  patch for compatible fixes.
- Validate shipped CLI changes with `python3 -m unittest discover -s tests`,
  `scripts/youtube --help`, `scripts/youtube --version`,
  `scripts/youtube --json doctor`, a missing-`yt-dlp` preflight fixture, and a
  safe read-only live check when YouTube is reachable.
