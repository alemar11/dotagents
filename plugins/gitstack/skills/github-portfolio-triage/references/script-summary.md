# GitHub portfolio triage command summary

Use this as the command map for broad or multi-repo maintainer queue scans.

## Shared `ghflow` helper

Resolve the artifact with `../../github/references/core/ghflow-resolution.md`
before running helper commands from a consuming repository.

```bash
<resolved-ghflow> portfolio scan --repo owner/repo --repo owner/other
<resolved-ghflow> portfolio scan --repo-file repos.txt --limit 20
<resolved-ghflow> --json portfolio scan --repo owner/repo
```

The command is read-only and uses `gh` to gather:

- open issue samples;
- open pull request samples;
- recent GitHub Actions run state;
- latest GitHub Release metadata;
- conservative per-repo next actions.

## JSON Shape

`ghflow --json portfolio scan ...` returns the normal GitStack envelope:

```json
{
  "ok": true,
  "version": "3.4.0",
  "command": ["portfolio", "scan"],
  "data": {
    "summary": {"requested": 1, "successful": 1, "failed": 0, "limit": 20},
    "repos": [
      {
        "repo": "owner/repo",
        "ok": true,
        "repo_url": "https://github.com/owner/repo",
        "open_issues": 0,
        "open_prs": 0,
        "issues": [],
        "pull_requests": [],
        "ci": {"state": "green", "text": "1 recent successful/neutral run(s)"},
        "latest_release": {"status": "found", "tag": "v1.2.3"},
        "top_queue_signals": [],
        "next_action": "queue empty; check freshness/release need"
      }
    ]
  }
}
```

Partial per-repo failures remain in `data.repos` with `ok: false`. The command
exits nonzero only when no repository scans successfully or arguments are
invalid.
