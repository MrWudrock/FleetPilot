"""RBAC and org-isolation regression tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models import FuelAlert, Organization, User
from app.models.enums import AlertSeverity, UserRole


def test_settings_patch_requires_admin(client: TestClient) -> None:
    org_id = uuid.uuid4()
    driver = User(
        id=uuid.uuid4(),
        organization_id=org_id,
        email="driver@example.com",
        full_name="Driver User",
        role=UserRole.DRIVER,
        is_active=True,
        password_hash="unused",
    )

    async def override_current_user() -> User:
        return driver

    app.dependency_overrides[get_current_user] = override_current_user
    try:
        response = client.patch("/api/v1/settings", json={"name": "Hacked Org"})
        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_public_signup_disabled_returns_403(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOW_PUBLIC_SIGNUP", "false")
    get_settings.cache_clear()

    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
            "organization_name": "New Org",
        },
    )
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()


def test_cross_org_fuel_alert_ack_returns_404(integration_db: TestClient) -> None:
    """Org A user cannot acknowledge org B fuel alert."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    settings = get_settings()
    engine = create_async_engine(settings.async_database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    org_a = uuid.uuid4()
    org_b = uuid.uuid4()
    user_a_id = uuid.uuid4()
    alert_b_id = uuid.uuid4()

    async def seed() -> None:
        async with session_factory() as db:
            db.add(Organization(id=org_a, name="Org A", slug=f"org-a-{org_a.hex[:8]}"))
            db.add(Organization(id=org_b, name="Org B", slug=f"org-b-{org_b.hex[:8]}"))
            db.add(
                User(
                    id=user_a_id,
                    organization_id=org_a,
                    email=f"admin-a-{org_a.hex[:8]}@test.local",
                    password_hash=hash_password("TestPass123!"),
                    full_name="Admin A",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
            )
            db.add(
                FuelAlert(
                    id=alert_b_id,
                    organization_id=org_b,
                    vehicle_id=None,
                    severity=AlertSeverity.WARNING,
                    title="Cross-org probe",
                    detected_at=datetime.now(UTC),
                    acknowledged=False,
                )
            )
            await db.commit()

    import asyncio

    asyncio.run(seed())

    login = integration_db.post(
        "/api/v1/auth/login",
        json={"email": f"admin-a-{org_a.hex[:8]}@test.local", "password": "TestPass123!"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    ack = integration_db.post(
        f"/api/v1/fuel/alerts/{alert_b_id}/acknowledge",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ack.status_code == 404

    asyncio.run(engine.dispose())
