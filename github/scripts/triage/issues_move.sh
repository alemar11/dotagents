#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: issues_move.sh --issue <number> --source-repo <owner/repo> --target-repo <owner/repo> [--dry-run]

Move an issue across repositories using the standard transfer sequence:
1) create a new issue in the target repository
2) prefix the target body with "Moved from <source_repo>#<issue> (<source_url>)."
3) add a backlink comment on the source issue
4) close the source issue if it is still OPEN
EOF
}

ISSUE=""
SOURCE_REPO=""
TARGET_REPO=""
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
    --source-repo)
      SOURCE_REPO="${2:-}"
      if [[ -z "$SOURCE_REPO" ]]; then
        echo "Missing value for --source-repo" >&2
        usage >&2
        exit 64
      fi
      shift 2
      ;;
    --target-repo)
      TARGET_REPO="${2:-}"
      if [[ -z "$TARGET_REPO" ]]; then
        echo "Missing value for --target-repo" >&2
        usage >&2
        exit 64
      fi
      shift 2
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

if [[ -z "$ISSUE" || -z "$SOURCE_REPO" || -z "$TARGET_REPO" ]]; then
  echo "Missing required arguments." >&2
  usage >&2
  exit 64
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../core/github_lib.sh"

github_require_issue_number "$ISSUE"
github_require_repo_reference "$SOURCE_REPO"
github_require_repo_reference "$TARGET_REPO"

if [[ "$SOURCE_REPO" == "$TARGET_REPO" ]]; then
  echo "--source-repo and --target-repo must be different for issue moves." >&2
  exit 64
fi

"$SCRIPT_DIR/../core/preflight_gh.sh" --allow-non-project >&2

TITLE="$(gh issue view "$ISSUE" --repo "$SOURCE_REPO" --json title -q .title)"
STATE="$(gh issue view "$ISSUE" --repo "$SOURCE_REPO" --json state -q .state)"
SOURCE_URL="$(gh issue view "$ISSUE" --repo "$SOURCE_REPO" --json url -q .url)"

SOURCE_BODY_FILE="$(mktemp)"
TARGET_BODY_FILE="$(mktemp)"
trap 'rm -f "$SOURCE_BODY_FILE" "$TARGET_BODY_FILE"' EXIT

gh issue view "$ISSUE" --repo "$SOURCE_REPO" --json body -q .body >"$SOURCE_BODY_FILE"

TRANSFER_NOTE="Moved from $SOURCE_REPO#$ISSUE ($SOURCE_URL)."
{
  printf '%s\n' "$TRANSFER_NOTE"
  if [[ -s "$SOURCE_BODY_FILE" ]]; then
    printf '\n'
    cat "$SOURCE_BODY_FILE"
  fi
} >"$TARGET_BODY_FILE"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry run: would move issue #$ISSUE from $SOURCE_REPO to $TARGET_REPO."
  echo "Dry run: source state: $STATE"
  echo "Dry run: target title: $TITLE"
  echo "Dry run: target body note: $TRANSFER_NOTE"
  exit 0
fi

NEW_URL="$(gh issue create --repo "$TARGET_REPO" --title "$TITLE" --body-file "$TARGET_BODY_FILE")"
NEW_NUMBER="${NEW_URL##*/}"
SOURCE_NOTE="Moved to $TARGET_REPO#$NEW_NUMBER ($NEW_URL). Continuing work there."

gh issue comment "$ISSUE" --repo "$SOURCE_REPO" --body "$SOURCE_NOTE" >/dev/null
if [[ "$STATE" == "OPEN" ]]; then
  gh issue close "$ISSUE" --repo "$SOURCE_REPO" >/dev/null
fi

echo "$NEW_URL"
