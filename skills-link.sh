#!/usr/bin/env sh

set -eu

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This script is intended for macOS only." >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SOURCE_DIR="$ROOT_DIR/skills"
SKILLS_DEST_DIR="$HOME/.agents/skills"

mkdir -p "$SKILLS_DEST_DIR"

DEPRECATED_BUNDLED_SKILLS="git-commit github github-ci github-releases github-reviews github-triage yeet"

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

prune_deprecated_skill_link() {
  skill_name="$1"
  target_path="$SKILLS_DEST_DIR/$skill_name"

  [ -L "$target_path" ] || return 0

  resolved_path="$(readlink "$target_path" || true)"
  case "$resolved_path" in
    "$ROOT_DIR"/*)
      rm -f "$target_path"
      echo "REMOVE deprecated bundled skill link -> $target_path"
      ;;
  esac
}

echo "Linking local skills from: $ROOT_DIR"
echo "Skills source directory: $SKILLS_SOURCE_DIR"
echo "Skills target directory: $SKILLS_DEST_DIR"
echo

for skill_name in $DEPRECATED_BUNDLED_SKILLS; do
  prune_deprecated_skill_link "$skill_name"
done

skill_count=0
skill_linked_count=0
skill_skip_count=0

for skill_dir in "$SKILLS_SOURCE_DIR"/*; do
  [ -d "$skill_dir" ] || continue
  [ -f "$skill_dir/SKILL.md" ] || continue

  skill_name="$(basename "$skill_dir")"
  target_path="$SKILLS_DEST_DIR/$skill_name"
  skill_count=$((skill_count + 1))

  if link_path "$skill_dir" "$target_path" "$skill_name"; then
    skill_linked_count=$((skill_linked_count + 1))
  else
    skill_skip_count=$((skill_skip_count + 1))
  fi
done

echo
echo "Completed."
echo "Skills processed: $skill_count, linked: $skill_linked_count, skipped: $skill_skip_count"
