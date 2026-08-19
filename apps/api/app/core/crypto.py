"""Encrypt integration credentials at rest (Fernet, key derived from SECRET_KEY)."""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings

_TOKEN_FIELD = "token"
_CIPHER_FIELD = "token_enc"
_DEMO_FIELD = "demo"


def _fernet() -> Fernet:
    # Separate from JWT secret — rotating SECRET_KEY must not break stored integration tokens.
    material = get_settings().resolved_credentials_encryption_key.encode("utf-8")
    digest = hashlib.sha256(material).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def seal_credentials(*, token: str | None, host: str | None, demo: bool) -> dict[str, Any]:
    """Store token encrypted; never persist plaintext tokens."""
    payload: dict[str, Any] = {_DEMO_FIELD: demo}
    if host:
        payload["host"] = host
    if token:
        payload[_CIPHER_FIELD] = _fernet().encrypt(token.encode("utf-8")).decode("ascii")
    return payload


def open_credentials(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Decrypt credentials for internal use. Legacy plaintext `token` still readable."""
    data = dict(raw or {})
    cipher = data.get(_CIPHER_FIELD)
    if isinstance(cipher, str) and cipher:
        try:
            data[_TOKEN_FIELD] = _fernet().decrypt(cipher.encode("ascii")).decode("utf-8")
        except InvalidToken:
            data[_TOKEN_FIELD] = None
    return data


def credentials_public_view(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Safe subset for API responses / logging — no secrets."""
    data = raw or {}
    return {
        _DEMO_FIELD: bool(data.get(_DEMO_FIELD, True)),
        "host": data.get("host"),
        "has_token": bool(data.get(_CIPHER_FIELD) or data.get(_TOKEN_FIELD)),
    }


def dump_json_safe(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)
