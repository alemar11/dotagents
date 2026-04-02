#!/usr/bin/env bash
set -euo pipefail

github_require_repo_reference() {
  local repo="${1:-}"
  if [[ -z "$repo" || "$repo" != */* || "$repo" == */ || "$repo" == */*/* ]]; then
    echo "Invalid --repo value '$repo'. Use owner/repo." >&2
    exit 64
  fi
}

github_require_issue_number() {
  local issue="${1:-}"
  if ! [[ "$issue" =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid --issue value '$issue'. It must be a positive integer." >&2
    exit 64
  fi
}

github_require_pr_number() {
  local pr="${1:-}"
  if ! [[ "$pr" =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid --pr value '$pr'. It must be a positive integer." >&2
    exit 64
  fi
}

github_require_positive_int() {
  local field="${1:-}"
  local value="${2:-}"
  if ! [[ "$value" =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid --$field value '$value'. It must be a positive integer." >&2
    exit 64
  fi
}

github_require_allowed_value() {
  local field="${1:-}"
  local value="${2:-}"
  shift 2
  local allowed
  for allowed in "$@"; do
    if [[ "$value" == "$allowed" ]]; then
      return 0
    fi
  done
  local joined
  joined="$(printf '%s, ' "$@")"
  joined="${joined%, }"
  echo "Invalid --$field value '$value'. Use $joined." >&2
  exit 64
}

github_normalize_hex_color() {
  local color="${1:-}"
  if [[ -z "$color" ]]; then
    return 0
  fi

  local normalized="${color#\#}"
  if ! [[ "$normalized" =~ ^[A-Fa-f0-9]{6}$ ]]; then
    echo "Invalid --color value '$color'. Use six hex digits, e.g. 1F9D55." >&2
    exit 64
  fi

  echo "$normalized"
}

github_repo_from_remote_url() {
  local remote="${1:-}"
  if [[ -z "$remote" ]]; then
    return 1
  fi

  local repo
  repo="$(printf '%s\n' "$remote" \
    | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#^ssh://[^/]+/##; s#^git://[^/]+/##; s#\.git$##; s#/$##')"

  if [[ -z "$repo" || "$repo" != */* || "$repo" == */ || "$repo" == */*/* ]]; then
    return 1
  fi

  echo "$repo"
}

github_require_git_repo() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "No git repository detected." >&2
    exit 3
  fi
}

github_current_branch() {
  github_require_git_repo

  local branch
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  if [[ -z "$branch" || "$branch" == "HEAD" ]]; then
    echo "Detached HEAD detected. Check out a branch first." >&2
    exit 5
  fi

  echo "$branch"
}

github_branch_is_long_lived() {
  local branch="${1:-}"
  if [[ -z "$branch" ]]; then
    echo "github_branch_is_long_lived requires a branch name." >&2
    exit 64
  fi

  case "$branch" in
    main|master|stable|develop|development|trunk|next|integration|staging|release/*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

github_tracking_remote_name() {
  local branch="${1:-}"
  if [[ -z "$branch" ]]; then
    echo "github_tracking_remote_name requires a branch name." >&2
    exit 64
  fi

  git config --get "branch.$branch.remote" 2>/dev/null || true
}

github_tracking_branch_name() {
  local branch="${1:-}"
  if [[ -z "$branch" ]]; then
    echo "github_tracking_branch_name requires a branch name." >&2
    exit 64
  fi

  local merge_ref
  merge_ref="$(git config --get "branch.$branch.merge" 2>/dev/null || true)"
  if [[ -z "$merge_ref" ]]; then
    return 0
  fi

  echo "${merge_ref#refs/heads/}"
}

github_resolve_repo() {
  local script_dir="${1:-}"
  local repo_ref="${2:-}"
  local allow_non_project="${3:-0}"

  local core_dir="$script_dir"
  if [[ ! -f "$core_dir/preflight_gh.sh" || ! -f "$core_dir/issue_resolve_repo.sh" ]]; then
    core_dir="$(cd "$script_dir/../core" && pwd)"
  fi

  local -a preflight_cmd=("$core_dir/preflight_gh.sh")
  local -a resolve_cmd=("$core_dir/issue_resolve_repo.sh")

  if [[ "$allow_non_project" -eq 1 ]]; then
    preflight_cmd+=(--allow-non-project)
    resolve_cmd+=(--allow-non-project)
  fi

  if [[ -n "$repo_ref" ]]; then
    resolve_cmd+=(--repo "$repo_ref")
  fi

  "${preflight_cmd[@]}" >&2
  "${resolve_cmd[@]}"
}

github_core_dir() {
  cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
}

github_user_state_script_path() {
  printf '%s/github_user_state.py\n' "$(github_core_dir)"
}

github_preflight_user_scope() {
  local core_dir
  core_dir="$(github_core_dir)"
  "$core_dir/preflight_gh.sh" --allow-non-project >&2
}

github_require_readable_file() {
  local field="${1:-file}"
  local path="${2:-}"
  if [[ -z "$path" ]]; then
    echo "Missing value for --$field." >&2
    exit 64
  fi
  if [[ ! -f "$path" ]]; then
    echo "File for --$field was not found: $path" >&2
    exit 66
  fi
  if [[ ! -r "$path" ]]; then
    echo "File for --$field is not readable: $path" >&2
    exit 66
  fi
}

github_collect_repo_targets() {
  local repo_file="${1:-}"
  shift || true

  if [[ -n "$repo_file" ]]; then
    github_require_readable_file "repos-file" "$repo_file"
  fi

  GITHUB_REPO_FILE="$repo_file" python3 - "$@" <<'PY'
import os
import re
import sys

pattern = re.compile(r"^[^/\s]+/[^/\s]+$")
seen = set()
ordered = []

def add_repo(value: str) -> None:
    repo = value.strip()
    if not repo:
        return
    if not pattern.match(repo):
        print(f"Invalid repository reference '{repo}'. Use owner/repo.", file=sys.stderr)
        raise SystemExit(64)
    if repo not in seen:
        seen.add(repo)
        ordered.append(repo)

for repo in sys.argv[1:]:
    add_repo(repo)

repo_file = os.environ.get("GITHUB_REPO_FILE", "")
if repo_file:
    with open(repo_file, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            add_repo(line)

for repo in ordered:
    print(repo)
PY
}

github_repo_lookup_json() {
  local repo="${1:-}"
  github_require_repo_reference "$repo"
  gh repo view "$repo" --json id,nameWithOwner,viewerHasStarred,url --jq '.'
}

github_viewer_starred_repositories_json() {
  local limit="${1:-0}"
  python3 "$(github_user_state_script_path)" viewer-stars --limit "$limit"
}

github_viewer_lists_json() {
  local limit="${1:-0}"
  python3 "$(github_user_state_script_path)" viewer-lists --limit "$limit"
}

github_resolve_list_json() {
  local selector="${1:-}"
  local list_id="${2:-}"
  if [[ -n "$selector" && -n "$list_id" ]]; then
    echo "Pass either a list selector or a list id, not both." >&2
    exit 64
  fi
  if [[ -z "$selector" && -z "$list_id" ]]; then
    echo "A list selector is required." >&2
    exit 64
  fi
  if [[ -n "$list_id" ]]; then
    python3 "$(github_user_state_script_path)" resolve-list --list-id "$list_id"
  else
    python3 "$(github_user_state_script_path)" resolve-list --list "$selector"
  fi
}

github_list_items_json() {
  local list_id="${1:-}"
  local limit="${2:-0}"
  if [[ -z "$list_id" ]]; then
    echo "github_list_items_json requires a list id." >&2
    exit 64
  fi
  python3 "$(github_user_state_script_path)" list-items --list-id "$list_id" --limit "$limit"
}

github_repo_list_memberships_json() {
  local -a cmd=(python3 "$(github_user_state_script_path)" repo-memberships)
  local repo_id
  for repo_id in "$@"; do
    cmd+=(--repo-id "$repo_id")
  done
  "${cmd[@]}"
}
