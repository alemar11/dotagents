#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: issues_close_with_evidence.sh --issue <number> --commit-sha <sha> [--commit-url <url>] [--pr-url <url>] [--repo <owner/repo>] [--allow-non-project] [--dry-run]

Close an issue using the standard evidence sequence:
1) verify issue state is OPEN
2) post closure note with implementation evidence
3) close the issue
EOF
}

ISSUE=""
COMMIT_SHA=""
COMMIT_URL=""
PR_URL=""
REPO=""
ALLOW_NON_PROJECT=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --issue)
      ISSUE="${2:-}"
      if [[ -z "$ISSUE" ]]; then
        echo "Missing value for --issue" >&2
        usage >&2
        exit 64
      fi
      shift 2
      ;;
    --commit-sha)
      COMMIT_SHA="${2:-}"
      if [[ -z "$COMMIT_SHA" ]]; then
        echo "Missing value for --commit-sha" >&2
        usage >&2
        exit 64
      fi
      shift 2
      ;;
    --commit-url)
      COMMIT_URL="${2:-}"
      if [[ -z "$COMMIT_URL" ]]; then
        echo "Missing value for --commit-url" >&2
        usage >&2
        exit 64
      fi
      shift 2
      ;;
    --pr-url)
      PR_URL="${2:-}"
      if [[ -z "$PR_URL" ]]; then
        echo "Missing value for --pr-url" >&2
        usage >&2
        exit 64
      fi
      shift 2
      ;;
    --repo)
      REPO="${2:-}"
      if [[ -z "$REPO" ]]; then
        echo "Missing value for --repo" >&2
        usage >&2
        exit 64
      fi
      shift 2
      ;;
    --allow-non-project)
      ALLOW_NON_PROJECT=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 64
      ;;
  esac
done

if [[ -z "$ISSUE" ]]; then
  echo "Missing required --issue" >&2
  usage >&2
  exit 64
fi

if [[ -z "$COMMIT_SHA" ]]; then
  echo "Missing required --commit-sha" >&2
  usage >&2
  exit 64
fi

if ! [[ "$COMMIT_SHA" =~ ^[0-9A-Fa-f]{7,40}$ ]]; then
  echo "Invalid --commit-sha value '$COMMIT_SHA'. Use a 7-40 character hex commit SHA." >&2
  exit 64
fi

if [[ -n "$REPO" && "$ALLOW_NON_PROJECT" -eq 0 ]]; then
  ALLOW_NON_PROJECT=1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/github_lib.sh"

if [[ -n "$REPO" ]]; then
  github_require_repo_reference "$REPO"
fi
github_require_issue_number "$ISSUE"

TARGET_REPO="$(github_resolve_repo "$SCRIPT_DIR" "$REPO" "$ALLOW_NON_PROJECT")"

if [[ -z "$COMMIT_URL" ]]; then
  COMMIT_URL="https://github.com/$TARGET_REPO/commit/$COMMIT_SHA"
fi

SHORT_SHA="${COMMIT_SHA:0:7}"
BODY="Implemented in commit $SHORT_SHA ($COMMIT_URL)."
if [[ -n "$PR_URL" ]]; then
  BODY="$BODY Implemented via PR $PR_URL."
fi

STATE="$(gh issue view "$ISSUE" --repo "$TARGET_REPO" --json state -q .state)"
if [[ "$STATE" != "OPEN" ]]; then
  echo "Issue #$ISSUE is already $STATE; no changes made."
  exit 0
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry run: issue #$ISSUE in $TARGET_REPO is OPEN."
  echo "Dry run: would post comment body:"
  echo "$BODY"
  echo "Dry run: would close issue #$ISSUE."
  exit 0
fi

gh issue comment "$ISSUE" --repo "$TARGET_REPO" --body "$BODY"
gh issue close "$ISSUE" --repo "$TARGET_REPO"

echo "Closed issue #$ISSUE in $TARGET_REPO with implementation evidence."
