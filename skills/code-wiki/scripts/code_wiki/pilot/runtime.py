"""Nested Codex execution and fixture injection for pilot agent nodes."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


class ExecutionError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        exit_code: int | None = None,
        model_call_started: bool = False,
    ) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.model_call_started = model_call_started


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    reasoning_output_tokens: int

    @property
    def uncached_input_tokens(self) -> int:
        return self.input_tokens - self.cached_input_tokens

    @property
    def total_model_tokens(self) -> int:
        # Codex reports reasoning as a detail of output, not an additional token class.
        return self.input_tokens + self.output_tokens

    def as_dict(self) -> dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "uncached_input_tokens": self.uncached_input_tokens,
            "output_tokens": self.output_tokens,
            "reasoning_output_tokens": self.reasoning_output_tokens,
            "total_model_tokens": self.total_model_tokens,
        }

    @classmethod
    def zero(cls) -> TokenUsage:
        return cls(0, 0, 0, 0)

    def __add__(self, other: TokenUsage) -> TokenUsage:
        return TokenUsage(
            self.input_tokens + other.input_tokens,
            self.cached_input_tokens + other.cached_input_tokens,
            self.output_tokens + other.output_tokens,
            self.reasoning_output_tokens + other.reasoning_output_tokens,
        )


@dataclass(frozen=True)
class InvocationResult:
    usage: TokenUsage
    exit_code: int
    duration_ms: int
    stdout_path: Path
    stderr_path: Path


def parse_terminal_usage(stdout_text: str) -> TokenUsage:
    terminal_usage: list[dict[str, Any]] = []
    for line_number, line in enumerate(stdout_text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ExecutionError(f"malformed Codex JSONL at line {line_number}: {exc}") from exc
        if not isinstance(event, dict):
            raise ExecutionError(f"Codex JSONL event at line {line_number} is not an object")
        if event.get("type") == "turn.completed":
            usage = event.get("usage")
            if not isinstance(usage, dict):
                raise ExecutionError("turn.completed event is missing an object usage field")
            terminal_usage.append(usage)
    if len(terminal_usage) != 1:
        raise ExecutionError(f"expected exactly one terminal usage event, found {len(terminal_usage)}")

    raw = terminal_usage[0]
    values: dict[str, int] = {}
    for field in TOKEN_FIELDS:
        value = raw.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ExecutionError(f"terminal usage field {field} must be a nonnegative integer")
        values[field] = value
    if values["cached_input_tokens"] > values["input_tokens"]:
        raise ExecutionError("cached_input_tokens cannot exceed input_tokens")
    return TokenUsage(**values)


def _safe_environment() -> dict[str, str]:
    allowed = {
        "CODEX_HOME",
        "HOME",
        "PATH",
        "TMPDIR",
        "XDG_CONFIG_HOME",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
        "HTTPS_PROXY",
        "HTTP_PROXY",
        "NO_PROXY",
        "OPENAI_API_KEY",
    }
    return {key: value for key, value in os.environ.items() if key in allowed}


def _toml_string(value: str) -> str:
    return json.dumps(value)


def _write_source_free_config(
    codex_home: Path,
    *,
    input_root: Path,
    output_root: Path,
    working_directory: Path,
) -> None:
    profile = "code_wiki_source_free"
    entries = {
        ":minimal": "read",
        str(input_root.resolve()): "read",
        str(output_root.resolve()): "write",
        str(working_directory.resolve()): "write",
    }
    lines = [
        f"default_permissions = {_toml_string(profile)}",
        "",
        f"[permissions.{profile}.filesystem]",
    ]
    lines.extend(
        f"{_toml_string(path)} = {_toml_string(access)}"
        for path, access in entries.items()
    )
    lines.extend(
        [
            "",
            f"[permissions.{profile}.network]",
            "enabled = false",
            "",
        ]
    )
    (codex_home / "config.toml").write_text("\n".join(lines), encoding="utf-8")


def _copy_auth_for_ephemeral_home(environment: dict[str, str], codex_home: Path) -> None:
    if environment.get("OPENAI_API_KEY"):
        return
    current_home = Path(
        environment.get("CODEX_HOME", str(Path(environment.get("HOME", "~")).expanduser() / ".codex"))
    ).expanduser()
    auth_source = current_home / "auth.json"
    if not auth_source.is_file():
        raise ExecutionError(
            "source-free Codex execution requires OPENAI_API_KEY or readable CODEX_HOME/auth.json"
        )
    auth_target = codex_home / "auth.json"
    shutil.copy2(auth_source, auth_target)
    auth_target.chmod(0o600)


class CodexExecutor:
    def __init__(self, model: str, reasoning_effort: str) -> None:
        self.model = model
        self.reasoning_effort = reasoning_effort

    def invoke(
        self,
        *,
        node_id: str,
        attempt: int,
        prompt: str,
        snapshot: Path,
        input_root: Path,
        output_root: Path,
        raw_root: Path,
        source_allowed: bool,
    ) -> InvocationResult:
        stdout_path = raw_root / f"{node_id}-attempt-{attempt}.jsonl"
        stderr_path = raw_root / f"{node_id}-attempt-{attempt}.stderr.txt"
        raw_root.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        try:
            with (
                tempfile.TemporaryDirectory(prefix=f"code-wiki-{node_id}-") as working_value,
                tempfile.TemporaryDirectory(prefix=f"code-wiki-{node_id}-codex-home-") as home_value,
            ):
                working_directory = Path(working_value)
                codex_home = Path(home_value)
                environment = _safe_environment()
                command = [
                    "codex",
                    "exec",
                    "--ephemeral",
                    "--json",
                    "--strict-config",
                    "--model",
                    self.model,
                    "--config",
                    f'model_reasoning_effort="{self.reasoning_effort}"',
                    "--config",
                    'shell_environment_policy.exclude=["^OPENAI_API_KEY$"]',
                    "--cd",
                    str(working_directory),
                    "--skip-git-repo-check",
                    "--color",
                    "never",
                    "-",
                ]
                if source_allowed:
                    command[4:4] = ["--ignore-user-config", "--sandbox", "workspace-write"]
                    command[command.index("--color"):command.index("--color")] = [
                        "--add-dir",
                        str(output_root),
                    ]
                else:
                    _write_source_free_config(
                        codex_home,
                        input_root=input_root,
                        output_root=output_root,
                        working_directory=working_directory,
                    )
                    _copy_auth_for_ephemeral_home(environment, codex_home)
                    environment["CODEX_HOME"] = str(codex_home)
                completed = subprocess.run(
                    command,
                    input=prompt,
                    text=True,
                    capture_output=True,
                    check=False,
                    env=environment,
                )
        except OSError as exc:
            raise ExecutionError(f"cannot launch Codex CLI: {exc}") from exc
        duration_ms = max(1, round((time.monotonic() - started) * 1000))
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        if completed.returncode != 0:
            raise ExecutionError(
                f"Codex node {node_id} exited {completed.returncode}; see {stderr_path}",
                exit_code=completed.returncode,
                model_call_started=True,
            )
        try:
            usage = parse_terminal_usage(completed.stdout)
        except ExecutionError as exc:
            raise ExecutionError(
                str(exc),
                exit_code=completed.returncode,
                model_call_started=True,
            ) from exc
        return InvocationResult(usage, completed.returncode, duration_ms, stdout_path, stderr_path)


class FixtureExecutor:
    """Explicit test-only subprocess-boundary replay."""

    def __init__(self, fixture_path: Path) -> None:
        try:
            value = json.loads(fixture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExecutionError(f"cannot load executor fixture {fixture_path}: {exc}") from exc
        if not isinstance(value, dict) or not isinstance(value.get("invocations"), dict):
            raise ExecutionError("executor fixture must contain an invocations object")
        self.fixture = value

    @staticmethod
    def _safe_target(root: Path, relative: str) -> Path:
        target = (root / relative).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise ExecutionError(f"fixture path escapes output root: {relative}") from exc
        return target

    def invoke(
        self,
        *,
        node_id: str,
        attempt: int,
        prompt: str,
        snapshot: Path,
        input_root: Path,
        output_root: Path,
        raw_root: Path,
        source_allowed: bool,
    ) -> InvocationResult:
        del prompt
        del input_root
        del source_allowed
        invocations = self.fixture["invocations"]
        entries = invocations.get(node_id)
        if not isinstance(entries, list) or attempt < 1 or attempt > len(entries):
            raise ExecutionError(f"executor fixture has no {node_id} attempt {attempt}")
        entry = entries[attempt - 1]
        if not isinstance(entry, dict):
            raise ExecutionError(f"executor fixture entry {node_id} attempt {attempt} is not an object")
        allowed_fields = {
            "delay_ms",
            "duration_ms",
            "events",
            "exit_code",
            "mutate_source",
            "stderr",
            "stdout",
            "writes",
        }
        unknown_fields = sorted(set(entry) - allowed_fields)
        if unknown_fields:
            raise ExecutionError(
                "executor fixture contains unsupported fields: " + ", ".join(unknown_fields)
            )
        delay_ms = entry.get("delay_ms", 0)
        if not isinstance(delay_ms, int) or delay_ms < 0:
            raise ExecutionError("fixture delay_ms must be a nonnegative integer")
        if delay_ms:
            time.sleep(delay_ms / 1000)

        writes = entry.get("writes", {})
        if not isinstance(writes, dict):
            raise ExecutionError("fixture writes must be an object")
        for relative, content in writes.items():
            if not isinstance(relative, str) or not isinstance(content, str):
                raise ExecutionError("fixture writes must map paths to strings")
            target = self._safe_target(output_root, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        mutation = entry.get("mutate_source")
        if mutation is not None:
            if not isinstance(mutation, dict) or not isinstance(mutation.get("path"), str):
                raise ExecutionError("fixture mutate_source must contain path and optional content")
            target = self._safe_target(snapshot, mutation["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(str(mutation.get("content", "mutated\n")), encoding="utf-8")

        events = entry.get("events")
        stdout_text = entry.get("stdout")
        if stdout_text is None:
            if not isinstance(events, list):
                raise ExecutionError("fixture invocation must contain events or stdout")
            stdout_text = "\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n"
        if not isinstance(stdout_text, str):
            raise ExecutionError("fixture stdout must be a string")
        stderr_text = entry.get("stderr", "")
        exit_code = entry.get("exit_code", 0)
        duration_ms = entry.get("duration_ms", max(1, delay_ms))
        if not isinstance(stderr_text, str) or not isinstance(exit_code, int) or not isinstance(duration_ms, int):
            raise ExecutionError("fixture stderr, exit_code, and duration_ms have invalid types")

        raw_root.mkdir(parents=True, exist_ok=True)
        stdout_path = raw_root / f"{node_id}-attempt-{attempt}.jsonl"
        stderr_path = raw_root / f"{node_id}-attempt-{attempt}.stderr.txt"
        stdout_path.write_text(stdout_text, encoding="utf-8")
        stderr_path.write_text(stderr_text, encoding="utf-8")
        if exit_code != 0:
            raise ExecutionError(
                f"fixture node {node_id} exited {exit_code}; see {stderr_path}",
                exit_code=exit_code,
                model_call_started=True,
            )
        try:
            usage = parse_terminal_usage(stdout_text)
        except ExecutionError as exc:
            raise ExecutionError(
                str(exc),
                exit_code=exit_code,
                model_call_started=True,
            ) from exc
        return InvocationResult(usage, exit_code, duration_ms, stdout_path, stderr_path)
