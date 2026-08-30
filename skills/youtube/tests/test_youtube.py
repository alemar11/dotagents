from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "youtube"
loader = importlib.machinery.SourceFileLoader("youtube_script", str(SCRIPT_PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec is not None
cli = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = cli
loader.exec_module(cli)


class YoutubeCliTests(unittest.TestCase):
    def test_probe_reports_runnable_ytdlp(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["/fake/yt-dlp", "--version"],
            returncode=0,
            stdout="2026.08.30\n",
            stderr="",
        )
        with (
            mock.patch.object(cli.shutil, "which", return_value="/fake/yt-dlp"),
            mock.patch.object(cli.Path, "resolve", return_value=Path("/fake/yt-dlp")),
            mock.patch.object(cli.subprocess, "run", return_value=completed),
        ):
            result = cli.probe_ytdlp()
        self.assertEqual(result["preflight_state"], "ready")
        self.assertEqual(result["version"], "2026.08.30")

    def test_every_read_fails_preflight_when_ytdlp_is_missing(self) -> None:
        missing = {
            "preflight_state": "missing",
            "path": None,
            "version": None,
            "message": "yt-dlp is required but was not found.",
            "hint": "install it",
        }
        commands = (
            (["videos", "search", "swift"], "videos.search"),
            (["playlists", "list", "playlist-url"], "playlists.list"),
            (
                ["playlists", "search-transcripts", "playlist-url", "memory"],
                "playlists.search-transcripts",
            ),
            (["transcripts", "languages", "abcdefghijk"], "transcripts.languages"),
            (["transcripts", "get", "abcdefghijk"], "transcripts.get"),
        )
        for arguments, command in commands:
            with self.subTest(command=command):
                stdout = io.StringIO()
                with (
                    mock.patch.object(cli, "probe_ytdlp", return_value=missing),
                    contextlib.redirect_stdout(stdout),
                ):
                    code = cli.main(["--json", *arguments])
                self.assertEqual(code, cli.EXIT_DEPENDENCY)
                payload = json.loads(stdout.getvalue())
                self.assertFalse(payload["ok"])
                self.assertEqual(payload["command"], command)
                self.assertEqual(payload["error"]["code"], "yt-dlp-missing")

    def test_doctor_does_not_create_cache_when_dependency_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cache_root = Path(directory) / "not-created"
            missing = {
                "preflight_state": "missing",
                "path": None,
                "version": None,
                "message": "missing",
                "hint": "install it",
            }
            with (
                mock.patch.object(cli, "CACHE_ROOT", cache_root),
                mock.patch.object(cli, "probe_ytdlp", return_value=missing),
            ):
                result = cli.doctor_result(mock.Mock(yt_dlp=None)).payload
            self.assertFalse(result["ok"])
            self.assertFalse(result["cache"]["exists"])
            self.assertFalse(cache_root.exists())

    def test_ytdlp_runs_without_user_config(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="{}",
            stderr="",
        )
        with mock.patch.object(cli.subprocess, "run", return_value=completed) as run:
            cli.run_ytdlp("/fake/yt-dlp", ["--dump-single-json", "--", "target"])
        command = run.call_args.args[0]
        self.assertEqual(
            command[:3], ["/fake/yt-dlp", "--ignore-config", "--no-warnings"]
        )
        self.assertEqual(command[-2:], ["--", "target"])

    def test_srv1_parser_decodes_and_deduplicates_rolling_text(self) -> None:
        fixture = """<transcript>
<text start="0" dur="1.5">Hello &amp;amp; welcome</text>
<text start="1" dur="1.5">Hello &amp;amp; welcome back</text>
<text start="4" dur="2">Next topic</text>
</transcript>"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "captions.srv1"
            path.write_text(fixture, encoding="utf-8")
            segments = cli.parse_srv1(path)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0]["text"], "Hello & welcome back")
        self.assertEqual(segments[1]["start_seconds"], 4.0)

    def test_json3_parser_preserves_timestamped_segments(self) -> None:
        fixture = {
            "events": [
                {
                    "tStartMs": 1250,
                    "dDurationMs": 2000,
                    "segs": [{"utf8": "One "}, {"utf8": "idea"}],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "captions.json3"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            segments = cli.parse_json3(path)
        self.assertEqual(
            segments,
            [{"start_seconds": 1.25, "duration_seconds": 2.0, "text": "One idea"}],
        )

    def test_caption_selection_prefers_manual_then_original_automatic(self) -> None:
        tracks = [
            {
                "language": "en",
                "caption_source": "automatic",
                "is_original": False,
            },
            {
                "language": "en",
                "caption_source": "manual",
                "is_original": False,
            },
            {
                "language": "it",
                "caption_source": "automatic",
                "is_original": True,
            },
        ]
        self.assertEqual(
            cli.select_caption_track(tracks, ["en"])["caption_source"],
            "manual",
        )
        automatic_only = [
            track for track in tracks if track["caption_source"] == "automatic"
        ]
        self.assertEqual(
            cli.select_caption_track(automatic_only, ["auto"])["language"],
            "it",
        )

    def test_caption_metadata_marks_named_original_track(self) -> None:
        metadata = {
            "language": "en",
            "automatic_captions": {
                "en-orig": [
                    {
                        "ext": "srv1",
                        "name": "English (Original)",
                        "url": "https://example.test/caption?tlang=en",
                    }
                ],
                "en": [
                    {
                        "ext": "srv1",
                        "name": "English",
                        "url": "https://example.test/caption?tlang=en",
                    }
                ],
            },
        }
        tracks = cli.available_caption_tracks(metadata)
        selected = cli.select_caption_track(tracks, ["auto"])
        self.assertEqual(selected["language"], "en-orig")
        self.assertTrue(selected["is_original"])

    def test_playlist_transcript_search_matches_across_segment_boundaries(self) -> None:
        segments = [
            {"start_seconds": 0.0, "duration_seconds": 2.0, "text": "Agent"},
            {"start_seconds": 2.0, "duration_seconds": 2.0, "text": "memory matters"},
            {"start_seconds": 50.0, "duration_seconds": 2.0, "text": "Unrelated"},
        ]
        matches = cli.search_segments(
            segments,
            "agent memory",
            match_mode="all",
            max_matches=3,
            video_id="abcdefghijk",
        )
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["start_seconds"], 0.0)
        self.assertEqual(matches[0]["url"], "https://youtu.be/abcdefghijk?t=0")

    def test_cache_round_trip_is_rebuildable_and_language_aware(self) -> None:
        payload = {
            "schema_version": cli.CACHE_SCHEMA_VERSION,
            "fetched_at": "2026-08-30T00:00:00+00:00",
            "video": {"video_id": "abcdefghijk"},
            "transcript": {
                "language": "it",
                "caption_source": "automatic",
                "segments": [],
            },
        }
        with (
            tempfile.TemporaryDirectory() as directory,
            mock.patch.object(cli, "CACHE_ROOT", Path(directory)),
        ):
            path = cli.write_cache(payload)
            loaded = cli.compatible_cached_transcript("abcdefghijk", ["it", "en"])
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded[0]["transcript"]["language"], "it")
        self.assertEqual(path.name, "automatic-it.json")

    def test_default_cache_selection_prefers_manual_captions(self) -> None:
        automatic = {
            "schema_version": cli.CACHE_SCHEMA_VERSION,
            "fetched_at": "2026-08-30T00:00:00+00:00",
            "video": {"video_id": "abcdefghijk"},
            "transcript": {
                "language": "en-orig",
                "caption_source": "automatic",
                "is_original": True,
                "segments": [],
            },
        }
        manual = {
            "schema_version": cli.CACHE_SCHEMA_VERSION,
            "fetched_at": "2026-08-30T00:00:00+00:00",
            "video": {"video_id": "abcdefghijk"},
            "transcript": {
                "language": "it",
                "caption_source": "manual",
                "is_original": False,
                "segments": [],
            },
        }
        with (
            tempfile.TemporaryDirectory() as directory,
            mock.patch.object(cli, "CACHE_ROOT", Path(directory)),
        ):
            cli.write_cache(automatic)
            cli.write_cache(manual)
            loaded = cli.compatible_cached_transcript("abcdefghijk", ["auto"])
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded[0]["transcript"]["caption_source"], "manual")


if __name__ == "__main__":
    unittest.main()
