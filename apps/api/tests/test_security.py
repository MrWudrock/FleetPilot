"""Regression tests for security review findings (config, crypto, path helpers)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from pydantic import ValidationError


def test_insecure_secret_rejected_when_not_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SECRET_KEY", "dev-secret-change-in-production")
    monkeypatch.setenv("CREDENTIALS_ENCRYPTION_KEY", "prod-credentials-key-separate-value")
    monkeypatch.setenv("ALLOW_PUBLIC_SIGNUP", "false")
    from app.core.config import Settings, get_settings

    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        Settings()
    get_settings.cache_clear()


def test_insecure_secret_allowed_in_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("SECRET_KEY", "dev-secret-change-in-production")
    monkeypatch.setenv("CREDENTIALS_ENCRYPTION_KEY", "dev-credentials-key-change-in-production")
    monkeypatch.setenv("ALLOW_PUBLIC_SIGNUP", "true")
    from app.core.config import Settings, get_settings

    get_settings.cache_clear()
    settings = Settings()
    assert settings.debug is True
    assert settings.jwt_expire_minutes == 60 * 8
    assert settings.docs_enabled is True
    assert settings.allow_public_signup is True
    get_settings.cache_clear()


def test_credentials_key_required_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SECRET_KEY", "prod-secret-key-at-least-32-characters-long")
    monkeypatch.delenv("CREDENTIALS_ENCRYPTION_KEY", raising=False)
    monkeypatch.setenv("ALLOW_PUBLIC_SIGNUP", "false")
    from app.core.config import Settings, get_settings

    get_settings.cache_clear()
    with pytest.raises(ValidationError, match="CREDENTIALS_ENCRYPTION_KEY"):
        Settings()
    get_settings.cache_clear()


def test_credentials_key_must_differ_from_secret_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "prod-secret-key-at-least-32-characters-long"
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SECRET_KEY", secret)
    monkeypatch.setenv("CREDENTIALS_ENCRYPTION_KEY", secret)
    monkeypatch.setenv("ALLOW_PUBLIC_SIGNUP", "false")
    from app.core.config import Settings, get_settings

    get_settings.cache_clear()
    with pytest.raises(ValidationError, match="must differ"):
        Settings()
    get_settings.cache_clear()


def test_public_signup_rejected_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SECRET_KEY", "prod-secret-key-at-least-32-characters-long")
    monkeypatch.setenv("CREDENTIALS_ENCRYPTION_KEY", "prod-credentials-key-separate-value!!")
    monkeypatch.setenv("ALLOW_PUBLIC_SIGNUP", "true")
    from app.core.config import Settings, get_settings

    get_settings.cache_clear()
    with pytest.raises(ValidationError, match="ALLOW_PUBLIC_SIGNUP"):
        Settings()
    get_settings.cache_clear()


def test_docs_disabled_outside_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SECRET_KEY", "unit-test-secret-key-please-change")
    monkeypatch.setenv("CREDENTIALS_ENCRYPTION_KEY", "unit-test-credentials-key-separate!!")
    monkeypatch.setenv("ALLOW_PUBLIC_SIGNUP", "false")
    from app.core.config import Settings, get_settings

    get_settings.cache_clear()
    settings = Settings()
    assert settings.docs_enabled is False
    get_settings.cache_clear()


def test_credentials_sealed_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("SECRET_KEY", "unit-test-secret-key-please-change")
    monkeypatch.setenv("CREDENTIALS_ENCRYPTION_KEY", "unit-test-credentials-key-separate!!")
    from app.core.config import get_settings
    from app.core.crypto import open_credentials, seal_credentials

    get_settings.cache_clear()
    sealed = seal_credentials(token="super-secret-token", host="https://wialon.local", demo=False)
    assert "token" not in sealed
    assert "token_enc" in sealed
    opened = open_credentials(sealed)
    assert opened["token"] == "super-secret-token"
    assert opened["host"] == "https://wialon.local"
    get_settings.cache_clear()


def test_meta_db_requires_auth(client) -> None:
    """Unauthenticated /meta/db must not leak table counts."""
    response = client.get("/api/v1/meta/db")
    assert response.status_code in (401, 403)
    body = response.json()
    assert "tables" not in body


def test_electron_path_jail_logic() -> None:
    """Mirror Electron isPathInside semantics used in main.js."""
    root = Path("C:/fleet/ui").resolve() if os.name == "nt" else Path("/tmp/fleet/ui").resolve()

    def is_path_inside(root_dir: Path, candidate: Path) -> bool:
        try:
            candidate.resolve().relative_to(root_dir.resolve())
            return True
        except ValueError:
            return False

    assert is_path_inside(root, root / "index.html")
    assert not is_path_inside(root, root.parent / "secrets.txt")
    assert not is_path_inside(root, Path("/etc/passwd") if os.name != "nt" else Path("C:/Windows/System32/config"))
