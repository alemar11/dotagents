#!/usr/bin/env sh

set -eu

usage() {
  cat <<EOF
Usage: $(basename "$0") [--agent codex|claude|all]

Link reusable skills from skills/ into an agent's user skills directory.

  --agent codex   Link into ~/.agents/skills (Codex)
  --agent claude  Link into ~/.claude/skills (Claude Code)
  --agent all     Link into both (default)
EOF
}

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This script is intended for macOS only." >&2
  exit 1
fi

agent="all"
while [ $# -gt 0 ]; do
  case "$1" in
    --agent)
      [ $# -ge 2 ] || { usage >&2; exit 1; }
      agent="$2"
      shift 2
      ;;
    --agent=*)
      agent="${1#--agent=}"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

case "$agent" in
  codex) dest_dirs="$HOME/.agents/skills" ;;
  claude) dest_dirs="$HOME/.claude/skills" ;;
  all) dest_dirs="$HOME/.agents/skills $HOME/.claude/skills" ;;
  *)
    echo "Unknown agent: $agent" >&2
    usage >&2
    exit 1
    ;;
esac

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SOURCE_DIR="$ROOT_DIR/skills"

is_global_skill() {
  case "$1" in
    swift-api-design|swift-docc) return 1 ;;
    *) return 0 ;;
  esac
}

link_path() {
  source_path="$1"
  target_path="$2"
  label="$3"

  if [ -L "$target_path" ]; then
    rm -f "$target_path"
  elif [ -e "$target_path" ]; then
    echo "SKIP $label -> $target_path already exists (not a symlink)"
    return 1
  fi

  ln -s "$source_path" "$target_path"
  echo "LINK $label -> $target_path"
}

prune_stale_repo_skill_links() {
  dest_dir="$1"

  for target_path in "$dest_dir"/*; do
    [ -L "$target_path" ] || continue

    resolved_path="$(readlink "$target_path" || true)"
    case "$resolved_path" in
      "$SKILLS_SOURCE_DIR"/*)
        if ! is_global_skill "$(basename "$resolved_path")"; then
          rm -f "$target_path"
          echo "REMOVE project-only repo skill link -> $target_path"
        elif [ ! -d "$resolved_path" ] || [ ! -f "$resolved_path/SKILL.md" ]; then
          rm -f "$target_path"
          echo "REMOVE stale repo skill link -> $target_path"
        fi
        ;;
    esac
  done
}

link_skills_into() {
  dest_dir="$1"

  mkdir -p "$dest_dir"

  echo "Skills target directory: $dest_dir"
  echo

  prune_stale_repo_skill_links "$dest_dir"

  skill_count=0
  skill_linked_count=0
  skill_skip_count=0

  for skill_dir in "$SKILLS_SOURCE_DIR"/*; do
    [ -d "$skill_dir" ] || continue
    [ -f "$skill_dir/SKILL.md" ] || continue

    skill_name="$(basename "$skill_dir")"
    target_path="$dest_dir/$skill_name"
    skill_count=$((skill_count + 1))

    if ! is_global_skill "$skill_name"; then
      echo "SKIP $skill_name -> project-only skill"
      skill_skip_count=$((skill_skip_count + 1))
      continue
    fi

    if link_path "$skill_dir" "$target_path" "$skill_name"; then
      skill_linked_count=$((skill_linked_count + 1))
    else
      skill_skip_count=$((skill_skip_count + 1))
    fi
  done

  echo
  echo "Skills processed: $skill_count, linked: $skill_linked_count, skipped: $skill_skip_count"
  echo
}

echo "Linking local skills from: $ROOT_DIR"
echo "Skills source directory: $SKILLS_SOURCE_DIR"
echo

for dest_dir in $dest_dirs; do
  link_skills_into "$dest_dir"
done

echo "Completed."
