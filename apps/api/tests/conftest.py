"""Pytest configuration for FleetPilot API."""

from __future__ import annotations

import os

import pytest

# Local/dev defaults so importing app.main succeeds during unit tests.
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("SECRET_KEY", "dev-secret-change-in-production")
os.environ.setdefault("CREDENTIALS_ENCRYPTION_KEY", "dev-credentials-key-change-in-production")
os.environ.setdefault("ALLOW_PUBLIC_SIGNUP", "true")


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    yield
    try:
        from app.core.config import get_settings

        get_settings.cache_clear()
    except Exception:
        pass


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def _integration_enabled() -> bool:
    return os.getenv("FP_INTEGRATION_TESTS") == "1"


@pytest.fixture
def integration_db(client):
    """Requires Postgres + Redis (FP_INTEGRATION_TESTS=1)."""
    if not _integration_enabled():
        pytest.skip("Set FP_INTEGRATION_TESTS=1 with Postgres/Redis for integration tests")
    yield client
