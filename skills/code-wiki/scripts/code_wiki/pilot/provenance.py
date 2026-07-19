"""Externally anchored execution-provenance signing for live pilot runs."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import stat
from pathlib import Path
from typing import Any


KEY_BYTES = 32


def provenance_key_path(cache_root: Path | None = None) -> Path:
    root = cache_root or Path("~/.cache/dotagents/skills/code-wiki/pilot").expanduser().resolve()
    return root / "provenance.key"


def load_or_create_provenance_key(cache_root: Path | None = None) -> bytes:
    key_path = provenance_key_path(cache_root)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        return load_provenance_key(key_path)
    key_text = secrets.token_bytes(KEY_BYTES).hex() + "\n"
    descriptor = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, key_text.encode("ascii"))
    finally:
        os.close(descriptor)
    return load_provenance_key(key_path)


def load_provenance_key(path: Path | None = None) -> bytes:
    key_path = path or provenance_key_path()
    try:
        metadata = key_path.stat()
    except OSError as exc:
        raise RuntimeError(
            "live pilot provenance key is unavailable; run one live `scripts/code-wiki pilot run` first"
        ) from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError(f"pilot provenance key is not a regular file: {key_path}")
    if stat.S_IMODE(metadata.st_mode) & 0o077:
        raise RuntimeError(f"pilot provenance key permissions must be 0600: {key_path}")
    try:
        key = bytes.fromhex(key_path.read_text(encoding="ascii").strip())
    except (OSError, UnicodeError, ValueError) as exc:
        raise RuntimeError(f"pilot provenance key is invalid: {key_path}") from exc
    if len(key) != KEY_BYTES:
        raise RuntimeError(f"pilot provenance key must contain {KEY_BYTES} bytes: {key_path}")
    return key


def provenance_key_status(path: Path | None = None) -> dict[str, Any]:
    key_path = path or provenance_key_path()
    try:
        load_provenance_key(key_path)
    except RuntimeError as exc:
        return {"ok": False, "path": str(key_path), "error": str(exc)}
    return {"ok": True, "path": str(key_path), "error": None}


def manifest_evidence_sha256(manifest: dict[str, Any]) -> str:
    """Hash the complete durable run evidence without its circular receipt hash."""
    evidence = {
        key: value
        for key, value in manifest.items()
        if not key.startswith("_")
    }
    normalized = json.loads(json.dumps(evidence))
    output = normalized.get("output")
    if isinstance(output, dict):
        output["provenance_sha256"] = None
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _canonical_payload(receipt: dict[str, Any]) -> bytes:
    unsigned = {key: value for key, value in receipt.items() if key != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_receipt(receipt: dict[str, Any], key: bytes) -> str:
    return hmac.new(key, _canonical_payload(receipt), hashlib.sha256).hexdigest()


def verify_receipt(receipt: dict[str, Any], key: bytes) -> bool:
    signature = receipt.get("signature")
    return isinstance(signature, str) and hmac.compare_digest(signature, sign_receipt(receipt, key))
