# YouTube State Contract

This reference owns every behavior-affecting mode and state emitted by the
shipped `scripts/youtube` CLI. Assigned values are canonical lower-kebab
strings. YouTube-owned language codes, IDs, URLs, and metadata keep their native
syntax.

## Command modes

Command modes are transient execution choices and are never persisted.

| Mode | Meaning |
| --- | --- |
| `doctor` | Inspect local CLI and `yt-dlp` readiness without contacting YouTube or creating cache state. |
| `preflight` | Require a runnable `yt-dlp` binary and fail before any YouTube request when it is unavailable. |
| `videos.search` | Search YouTube for video candidates. |
| `playlists.list` | Enumerate and optionally filter playlist metadata. |
| `transcripts.languages` | List manual and automatic caption tracks for one video. |
| `transcripts.get` | Retrieve one normalized timestamped transcript. |
| `playlists.search-transcripts` | Retrieve and search transcript windows across a bounded or complete playlist scope. |

## Preflight state

`preflight_state` is an observed local runtime fact.

| Value | Meaning |
| --- | --- |
| `ready` | `yt-dlp` was found, executed, and reported a version. |
| `missing` | No `yt-dlp` executable was found. |
| `broken` | A candidate executable existed but could not run or report a version. |

## Result and scope state

These values are transient command results.

| Field | Value | Meaning |
| --- | --- | --- |
| `result_state` | `complete` | The requested scope completed and returned at least one result. |
| `result_state` | `empty` | The requested scope completed with no matching result. |
| `result_state` | `partial` | Some playlist transcripts failed while other results remain usable. |
| `scope_state` | `complete` | The complete requested collection was inspected. |
| `scope_state` | `limited` | The command stopped at the caller or default video bound; it must not be described as a complete-playlist result. |

## Caption, cache, and matching state

`caption_source` is external transcript provenance. Cache files persist only
normalized, rebuildable transcript data; cache and match state themselves are
transient.

| Field | Value | Meaning |
| --- | --- | --- |
| `caption_source` | `manual` | The channel or video owner supplied the selected caption track. |
| `caption_source` | `automatic` | YouTube generated the selected caption track. |
| `cache_state` | `hit` | A compatible normalized transcript was read from cache. |
| `cache_state` | `miss` | No compatible cache entry existed; the retrieved transcript was cached. |
| `cache_state` | `refreshed` | The caller bypassed existing cache data and replaced the normalized entry. |
| `cache_state` | `disabled` | The caller selected `--no-cache`; no cache was read or written. |
| `match_mode` | `all` | Every normalized query term must appear in a transcript window. |
| `match_mode` | `any` | At least one normalized query term must appear in a transcript window. |
| `match_mode` | `phrase` | The normalized query phrase must appear contiguously in a transcript window. |

## Persistence boundary

- Persisted: normalized transcript cache entries under
  `~/.cache/dotagents/skills/youtube/transcripts/`.
- Transient: command mode, preflight, result, scope, cache, and match state.
- External: YouTube availability, playlist visibility, caption availability,
  caption source, language, video metadata, authentication validity, and
  upstream throttling or blocking.
