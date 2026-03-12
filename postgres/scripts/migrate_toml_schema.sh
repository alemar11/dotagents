#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/runtime_env.sh"

if [[ -n "${PROJECT_ROOT+x}" ]]; then
  echo "Unsupported environment variable 'PROJECT_ROOT'. Use 'DB_PROJECT_ROOT' instead." >&2
  exit 1
fi

ROOT_OVERRIDE="${DB_PROJECT_ROOT:-}"
PROJECT_ROOT="$ROOT_OVERRIDE"
if [[ -z "$PROJECT_ROOT" && -x "$(command -v git)" ]]; then
  PROJECT_ROOT="$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null || true)"
fi
if [[ -z "$PROJECT_ROOT" ]]; then
  PROJECT_ROOT="$PWD"
fi
if [[ -z "$ROOT_OVERRIDE" ]]; then
  case "$PROJECT_ROOT" in
    "$SKILL_ROOT"|"$SKILL_ROOT"/*)
      echo "Project root resolved to the postgres skill directory: $SKILL_ROOT" >&2
      echo "Run this from the postgres skill directory with DB_PROJECT_ROOT set (or run from your project root)." >&2
      exit 1
      ;;
  esac
fi

TOML_PATH="$PROJECT_ROOT/.skills/postgres/postgres.toml"

if [[ ! -f "$TOML_PATH" ]]; then
  echo "postgres.toml not found at $TOML_PATH" >&2
  exit 1
fi

if [[ -x "$SCRIPT_DIR/check_toml_gitignored.sh" ]]; then
  "$SCRIPT_DIR/check_toml_gitignored.sh" "$PROJECT_ROOT" || true
fi

PYTHON_BIN="$(postgres_runtime_resolve_python "$TOML_PATH")" || exit 1

MIGRATE_RESOLVED_PYTHON_BIN="$PYTHON_BIN" "$PYTHON_BIN" - "$TOML_PATH" <<'PY'
import os
import shutil
import sys
import tomllib
from typing import Any

LATEST_SCHEMA = (1, 1, 0)
LEGACY_SCHEMA = (1, 0, 0)
RESOLVED_PYTHON_BIN = os.environ.get("MIGRATE_RESOLVED_PYTHON_BIN", sys.executable)


def die(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def format_schema(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def parse_schema_version(value: Any) -> tuple[int, int, int]:
    if value is None:
        return (0, 0, 0)
    if isinstance(value, bool):
        return (int(value), 0, 0)
    if isinstance(value, int):
        if value == 1:
            return LEGACY_SCHEMA
        die(f"Invalid schema_version: {value!r}")
    text = str(value).strip()
    if not text:
        return (0, 0, 0)
    if text == "1":
        return LEGACY_SCHEMA
    parts = text.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        die(f"Invalid schema_version: {value!r}")
    version = tuple(int(part) for part in parts)
    if version in {LEGACY_SCHEMA, LATEST_SCHEMA}:
        return version
    die(f"Unsupported schema_version: {text}")
    return (0, 0, 0)


def sslmode_to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value in (0, 1):
            return bool(value)
        die(f"Invalid sslmode integer: {value!r}")
    text = str(value).strip()
    if not text:
        return False
    lower = text.lower()
    if lower in {
        "true",
        "t",
        "1",
        "yes",
        "y",
        "on",
        "enable",
        "enabled",
        "require",
        "required",
        "verify-ca",
        "verify-full",
    }:
        return True
    if lower in {"false", "f", "0", "no", "n", "off", "disable", "disabled"}:
        return False
    die(
        "Unrecognized sslmode value while migrating postgres.toml: "
        f"{value!r}. sslmode must be boolean (true/false), or remove it and "
        "rely on a one-off DB_URL."
    )
    return False


def normalize_sslmode_fields(data: dict) -> bool:
    changed = False
    db = data.get("database")
    if not isinstance(db, dict):
        return False

    if "sslmode" in db and not isinstance(db.get("sslmode"), bool):
        db["sslmode"] = sslmode_to_bool(db.get("sslmode"))
        changed = True

    for _, value in list(db.items()):
        if not isinstance(value, dict):
            continue
        if "sslmode" in value and not isinstance(value.get("sslmode"), bool):
            value["sslmode"] = sslmode_to_bool(value.get("sslmode"))
            changed = True

    if "sslmode" not in db:
        db["sslmode"] = False
        changed = True

    return changed


def normalize_pg_bin_dir(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().rstrip("/\\")
    if not text:
        return ""
    base = os.path.basename(text)
    if base in {"psql", "psql.exe"}:
        return os.path.dirname(text)
    return text


def detect_pg_bin_dir() -> str:
    psql_path = shutil.which("psql")
    if not psql_path:
        return ""
    return os.path.dirname(psql_path)


def require_pg_bin_dir(config: dict) -> None:
    value = normalize_pg_bin_dir(config.get("pg_bin_dir") or config.get("pg_bin_path"))
    if not value:
        value = detect_pg_bin_dir()
    if not value:
        die(
            "pg_bin_dir is required but could not be determined. "
            "Install psql or set [configuration].pg_bin_dir, then re-run."
        )
    if not os.path.isdir(value):
        die(f"pg_bin_dir must point to a directory that exists. Got: {value}")
    psql_path = os.path.join(value, "psql")
    psql_exe_path = os.path.join(value, "psql.exe")
    if not (os.path.isfile(psql_path) or os.path.isfile(psql_exe_path)):
        die(
            "pg_bin_dir must contain a psql binary. "
            f"Expected: {psql_path} (or {psql_exe_path} on Windows)"
        )
    config["pg_bin_dir"] = value
    config.pop("pg_bin_path", None)


def normalize_python_bin(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    resolved = shutil.which(text) if os.sep not in text else text
    if not resolved or not os.path.isfile(resolved):
        return ""
    return os.path.realpath(resolved)


def ensure_python_bin(config: dict) -> None:
    value = normalize_python_bin(config.get("python_bin"))
    if not value:
        value = normalize_python_bin(RESOLVED_PYTHON_BIN) or os.path.realpath(sys.executable)
    config["python_bin"] = value


def migrate_0_to_1_0_0(data: dict) -> dict:
    config = data.setdefault("configuration", {})
    config["schema_version"] = format_schema(LEGACY_SCHEMA)
    legacy_bin = normalize_pg_bin_dir(config.get("pg_bin_dir") or config.get("pg_bin_path"))
    if legacy_bin:
        config["pg_bin_path"] = legacy_bin
    require_pg_bin_dir(config)
    config["pg_bin_path"] = config.pop("pg_bin_dir")
    normalize_sslmode_fields(data)
    return data


def migrate_1_0_0_to_1_1_0(data: dict) -> dict:
    config = data.setdefault("configuration", {})
    require_pg_bin_dir(config)
    ensure_python_bin(config)
    config["schema_version"] = format_schema(LATEST_SCHEMA)
    return data


MIGRATIONS = {
    (0, 0, 0): migrate_0_to_1_0_0,
    LEGACY_SCHEMA: migrate_1_0_0_to_1_1_0,
}


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_table(name: str, data: dict) -> list[str]:
    lines: list[str] = [f"[{name}]"]
    keys = list(data.keys())
    if name == "configuration":
        ordered = ["schema_version", "pg_bin_dir", "python_bin"]
        keys = [key for key in ordered if key in data] + [
            key for key in keys if key not in ordered
        ]
    for key in keys:
        lines.append(f"{key} = {format_value(data[key])}")
    return lines


def render_toml(data: dict) -> str:
    lines: list[str] = []

    config = data.get("configuration")
    if isinstance(config, dict):
        lines.extend(render_table("configuration", config))

    db = data.get("database")
    if isinstance(db, dict):
        if lines:
            lines.append("")
        defaults = [(k, v) for k, v in db.items() if not isinstance(v, dict)]
        profiles = [(k, v) for k, v in db.items() if isinstance(v, dict)]
        lines.append("[database]")
        for key, value in defaults:
            lines.append(f"{key} = {format_value(value)}")
        for profile, cfg in profiles:
            lines.append("")
            lines.append(f"[database.{profile}]")
            for key, value in cfg.items():
                lines.append(f"{key} = {format_value(value)}")

    for key, value in data.items():
        if key in {"configuration", "database"}:
            continue
        if isinstance(value, dict):
            if lines:
                lines.append("")
            lines.extend(render_table(key, value))
        else:
            if lines:
                lines.append("")
            lines.append(f"{key} = {format_value(value)}")

    return "\n".join(lines).rstrip() + "\n"


toml_path = sys.argv[1]
with open(toml_path, "rb") as fh:
    data = tomllib.load(fh)

config = data.get("configuration", {})
if not isinstance(config, dict):
    die("postgres.toml [configuration] must be a table if present.")

current = parse_schema_version(config.get("schema_version"))
if current > LATEST_SCHEMA:
    die(
        "postgres.toml schema_version "
        f"{format_schema(current)} is newer than supported {format_schema(LATEST_SCHEMA)}."
    )

before_render = render_toml(data)

if current == LATEST_SCHEMA:
    require_pg_bin_dir(config)
    ensure_python_bin(config)
    data["configuration"] = config
    normalize_sslmode_fields(data)
    if render_toml(data) == before_render:
        print(f"postgres.toml already at schema_version {format_schema(LATEST_SCHEMA)}.")
        sys.exit(0)
    with open(toml_path, "w", encoding="utf-8") as fh:
        fh.write(render_toml(data))
    print(f"Updated postgres.toml for schema_version {format_schema(LATEST_SCHEMA)}.")
    sys.exit(0)

version = current
while version < LATEST_SCHEMA:
    migrate = MIGRATIONS.get(version)
    if not migrate:
        die(
            "Missing migration for schema_version "
            f"{format_schema(version)} -> {format_schema(LATEST_SCHEMA)}."
        )
    data = migrate(data)
    config = data.setdefault("configuration", {})
    version = parse_schema_version(config.get("schema_version"))

config = data.setdefault("configuration", {})
config["schema_version"] = format_schema(LATEST_SCHEMA)
require_pg_bin_dir(config)
ensure_python_bin(config)
normalize_sslmode_fields(data)

with open(toml_path, "w", encoding="utf-8") as fh:
    fh.write(render_toml(data))

print(f"Migrated postgres.toml to schema_version {format_schema(LATEST_SCHEMA)}.")
PY
