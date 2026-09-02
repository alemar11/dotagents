from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib import error, parse, request

from .common import GError, REPO_PATTERN

UPLOAD_ENDPOINT = "https://uploads.github.com/user-attachments/assets"
STABLE_URL_PATTERN = re.compile(
    r"^https://github\.com/user-attachments/assets/[A-Za-z0-9-]+$"
)
CONTENT_TYPE_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*/[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*$"
)
MAX_RESPONSE_BYTES = 65_536
UPLOAD_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class AttachmentFile:
    path: Path
    data: bytes
    name: str
    content_type: str

    def proof(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "content_type": self.content_type,
            "bytes": len(self.data),
            "sha256": hashlib.sha256(self.data).hexdigest(),
        }


UrlOpener = Callable[..., Any]


def _validate_repo(value: str) -> str:
    repo = value.strip()
    if not REPO_PATTERN.fullmatch(repo):
        raise GError(
            "Invalid repository. Use owner/repo.",
            code="invalid_arguments",
            exit_code=64,
        )
    return repo


def _validate_name(value: str) -> str:
    name = value.strip()
    if (
        not name
        or name in {".", ".."}
        or len(name) > 255
        or any(character in name for character in ("/", "\\", "\r", "\n", "\0"))
    ):
        raise GError(
            "Attachment name must be a plain filename of at most 255 characters.",
            code="invalid_arguments",
            exit_code=64,
        )
    return name


def _validate_content_type(value: str) -> str:
    content_type = value.strip()
    if not CONTENT_TYPE_PATTERN.fullmatch(content_type):
        raise GError(
            "Attachment content type must be a plain MIME type such as image/png.",
            code="invalid_arguments",
            exit_code=64,
        )
    return content_type.lower()


def _read_attachment(
    raw_path: str,
    *,
    name: str | None,
    content_type: str | None,
) -> AttachmentFile:
    path = Path(raw_path)
    if not path.is_absolute():
        raise GError(
            "Attachment path must be absolute.",
            code="invalid_arguments",
            exit_code=64,
        )
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise GError(
            "Attachment file does not exist.",
            code="attachment_file_invalid",
            exit_code=66,
        ) from exc
    except OSError as exc:
        raise GError(
            "Attachment file metadata could not be read.",
            code="attachment_file_invalid",
            exit_code=66,
        ) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise GError(
            "Attachment path must identify a regular, non-symlink file.",
            code="attachment_file_invalid",
            exit_code=66,
        )
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise GError(
            "Attachment file could not be read.",
            code="attachment_file_invalid",
            exit_code=66,
        ) from exc
    if not data:
        raise GError(
            "Attachment file must not be empty.",
            code="attachment_file_invalid",
            exit_code=66,
        )

    resolved_name = _validate_name(name if name is not None else path.name)
    guessed_type = mimetypes.guess_type(resolved_name, strict=False)[0]
    if content_type is None and guessed_type is None:
        raise GError(
            "Could not infer the attachment content type; pass --content-type.",
            code="invalid_arguments",
            exit_code=64,
        )
    resolved_type = _validate_content_type(content_type or guessed_type or "")
    return AttachmentFile(path=path, data=data, name=resolved_name, content_type=resolved_type)


def _run_gh(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(command, capture_output=True, shell=False)
    except FileNotFoundError as exc:
        raise GError(
            "GitHub CLI is not installed or not on PATH.",
            code="attachment_provider_unavailable",
            exit_code=127,
        ) from exc
    except OSError as exc:
        raise GError(
            "GitHub CLI could not be executed.",
            code="attachment_provider_unavailable",
            exit_code=126,
        ) from exc


def _resolve_repository_id(repo: str) -> int:
    completed = _run_gh(["gh", "api", f"repos/{repo}"])
    if completed.returncode:
        raise GError(
            "Could not resolve the repository through GitHub.",
            code="attachment_repository_unavailable",
            exit_code=69,
            details={"repository": repo, "upstream_exit_code": completed.returncode},
        )
    try:
        payload = json.loads(completed.stdout)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise GError(
            "GitHub returned an invalid repository response.",
            code="attachment_repository_invalid",
            exit_code=65,
            details={"repository": repo},
        ) from exc
    repository_id = payload.get("id") if isinstance(payload, dict) else None
    full_name = payload.get("full_name") if isinstance(payload, dict) else None
    if (
        not isinstance(repository_id, int)
        or repository_id <= 0
        or not isinstance(full_name, str)
        or full_name.casefold() != repo.casefold()
    ):
        raise GError(
            "GitHub repository identity did not match the requested repository.",
            code="attachment_repository_invalid",
            exit_code=65,
            details={"repository": repo},
        )
    return repository_id


def _read_token() -> str:
    completed = _run_gh(["gh", "auth", "token"])
    if completed.returncode:
        raise GError(
            "GitHub CLI authentication is unavailable.",
            code="attachment_auth_unavailable",
            exit_code=4,
            details={"upstream_exit_code": completed.returncode},
        )
    try:
        token = completed.stdout.strip().decode("ascii")
    except UnicodeDecodeError as exc:
        raise GError(
            "GitHub CLI returned an invalid authentication token.",
            code="attachment_auth_unavailable",
            exit_code=4,
        ) from exc
    if not token or any(character.isspace() for character in token):
        raise GError(
            "GitHub CLI returned an invalid authentication token.",
            code="attachment_auth_unavailable",
            exit_code=4,
        )
    return token


def _parse_stable_url(raw_response: bytes) -> str:
    if len(raw_response) > MAX_RESPONSE_BYTES:
        raise GError(
            "GitHub returned an oversized attachment response.",
            code="attachment_upload_unknown",
            exit_code=65,
        )
    try:
        payload = json.loads(raw_response)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise GError(
            "GitHub returned an invalid attachment response; do not retry blindly.",
            code="attachment_upload_unknown",
            exit_code=65,
        ) from exc
    stable_url = payload.get("url") if isinstance(payload, dict) else None
    if not isinstance(stable_url, str) or not STABLE_URL_PATTERN.fullmatch(stable_url):
        raise GError(
            "GitHub did not confirm a stable attachment URL; do not retry blindly.",
            code="attachment_upload_unknown",
            exit_code=65,
        )
    return stable_url


def upload(
    *,
    repo: str,
    file: str,
    name: str | None = None,
    content_type: str | None = None,
    dry_run: bool = False,
    opener: UrlOpener | None = None,
) -> dict[str, Any]:
    repository = _validate_repo(repo)
    attachment = _read_attachment(file, name=name, content_type=content_type)
    result: dict[str, Any] = {
        "dry_run": dry_run,
        "repository": repository,
        "file": attachment.proof(),
    }
    if dry_run:
        result["url"] = None
        return result

    repository_id = _resolve_repository_id(repository)
    token = _read_token()
    query = parse.urlencode(
        {
            "name": attachment.name,
            "content_type": attachment.content_type,
            "repository_id": repository_id,
        }
    )
    upload_request = request.Request(
        f"{UPLOAD_ENDPOINT}?{query}",
        data=attachment.data,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        },
        method="POST",
    )
    open_url = opener or request.urlopen
    try:
        with open_url(upload_request, timeout=UPLOAD_TIMEOUT_SECONDS) as response:
            raw_response = response.read(MAX_RESPONSE_BYTES + 1)
    except error.HTTPError as exc:
        http_status = exc.code
        exc.close()
        raise GError(
            "GitHub rejected the attachment upload.",
            code="attachment_upload_rejected",
            exit_code=69,
            details={
                "repository": repository,
                "repository_id": repository_id,
                "file": attachment.proof(),
                "http_status": http_status,
            },
        ) from exc
    except (error.URLError, TimeoutError, OSError) as exc:
        raise GError(
            "The attachment upload outcome is unknown; inspect the issue before retrying.",
            code="attachment_upload_unknown",
            exit_code=69,
            details={
                "repository": repository,
                "repository_id": repository_id,
                "file": attachment.proof(),
            },
        ) from exc

    result["repository_id"] = repository_id
    result["url"] = _parse_stable_url(raw_response)
    return result
