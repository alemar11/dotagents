# YouTube CLI Reference

Run the shipped artifact from the skill root. Put the global `--json` option
before the command noun.

## Diagnostics

```bash
scripts/youtube --version
scripts/youtube --json doctor
scripts/youtube --json preflight
```

`doctor` always returns a diagnostic payload and does not create the runtime
cache. `preflight` exits nonzero unless `yt-dlp` is runnable. Every other
command performs that same preflight automatically.

## Search videos

```bash
scripts/youtube --json videos search "swift concurrency" --limit 10
scripts/youtube --json videos search "swift concurrency" --order date --limit 10
```

The success payload includes `query`, `order`, `result_state`, and normalized
`results` containing stable video IDs and canonical watch URLs.

## Inspect a playlist

```bash
scripts/youtube --json playlists list "PLAYLIST_URL"
scripts/youtube --json playlists list "PLAYLIST_URL" --query "memory" --match all
scripts/youtube --json playlists list "PLAYLIST_URL" --limit 25
```

`--limit 0` means all entries. A bounded response reports
`scope_state=limited` and must not be presented as a complete playlist scan.

## Retrieve one transcript

```bash
scripts/youtube --json transcripts languages "VIDEO_URL_OR_ID"
scripts/youtube --json transcripts get "VIDEO_URL_OR_ID"
scripts/youtube --json transcripts get "VIDEO_URL_OR_ID" --languages it,en
scripts/youtube transcripts get "VIDEO_URL_OR_ID" --timestamps
```

`--languages` is a descending preference list. The default `auto` prefers an
available manual track, then the original automatic track. JSON always retains
`start_seconds` and `duration_seconds`; `--timestamps` changes only human text
output. Use `--refresh` to bypass a compatible cache entry or `--no-cache` to
avoid cache reads and writes.

## Search spoken content across a playlist

```bash
scripts/youtube --json playlists search-transcripts \
  "PLAYLIST_URL" "agent memory" --max-videos 50

scripts/youtube --json playlists search-transcripts \
  "PLAYLIST_URL" "agent memory" --max-videos 0 --match all
```

The bounded default is 50 videos. Use `--max-videos 0` only for an intentional
complete-playlist scan. Retrieval is sequential to reduce upstream throttling.
The payload includes `scope_state`, `result_state`, `scanned_count`, matches
with moment URLs, and per-video failures. A partial result exits with code 6;
the JSON payload remains usable and must be inspected.

## Account-scoped access

Pass `--cookies-from-browser safari`, `chrome`, `firefox`, or another
`yt-dlp`-supported browser only when the user explicitly authorizes access to
their account-scoped YouTube content:

```bash
scripts/youtube --json playlists list "PRIVATE_PLAYLIST_URL" \
  --cookies-from-browser safari
```

The CLI passes the browser selector directly to `yt-dlp`. It never exports,
copies, prints, or caches cookies.

## JSON and exit contract

Success envelopes use `ok=true`, a canonical `command`, and command-specific
data. Errors use:

```json
{
  "ok": false,
  "command": "preflight",
  "error": {
    "code": "yt-dlp-missing",
    "message": "yt-dlp is required but was not found.",
    "hint": "Install it with brew install yt-dlp or uv tool install yt-dlp."
  }
}
```

| Exit | Meaning |
| --- | --- |
| `0` | Complete success, including an empty search. |
| `2` | Invalid CLI arguments. |
| `3` | `yt-dlp` preflight failure. |
| `4` | YouTube access, extraction, authentication, or parsing failure. |
| `5` | No compatible transcript is available. |
| `6` | Partial playlist transcript result. |
