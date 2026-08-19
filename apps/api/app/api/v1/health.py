import asyncio
from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AdminUser
from app.core.config import get_settings
from app.db.session import get_db
from app.models import FuelAlert, Integration, Order, Organization, SavingsEntry, User, Vehicle

router = APIRouter(tags=["health"])


async def _check_redis(redis_url: str) -> dict[str, Any]:
    client = aioredis.from_url(redis_url, decode_responses=True)
    try:
        pong = await asyncio.wait_for(client.ping(), timeout=3.0)
        return {"status": "ok" if pong else "error", "detail": "PONG" if pong else "no response"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
    finally:
        await client.aclose()


async def _check_postgres(db: AsyncSession) -> dict[str, Any]:
    try:
        result = await asyncio.wait_for(db.execute(text("SELECT version()")), timeout=3.0)
        version = result.scalar_one()
        return {"status": "ok", "detail": version.split(",")[0]}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "fleetpilot-api",
        "version": settings.app_version,
    }


@router.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    settings = get_settings()
    postgres, redis_check = await asyncio.gather(
        _check_postgres(db),
        _check_redis(settings.redis_url),
    )

    checks = {"postgres": postgres, "redis": redis_check}
    all_ok = all(check["status"] == "ok" for check in checks.values())

    return {
        "status": "ok" if all_ok else "degraded",
        "service": "fleetpilot-api",
        "version": settings.app_version,
        "checks": checks,
    }


@router.get("/meta/db")
async def database_meta(user: AdminUser, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Schema verification for FP-2 — admin only (not public)."""
    _ = user
    try:
        revision = await db.scalar(text("SELECT version_num FROM alembic_version LIMIT 1"))
        counts = {
            "organizations": await db.scalar(select(func.count()).select_from(Organization)),
            "users": await db.scalar(select(func.count()).select_from(User)),
            "vehicles": await db.scalar(select(func.count()).select_from(Vehicle)),
            "integrations": await db.scalar(select(func.count()).select_from(Integration)),
            "fuel_alerts": await db.scalar(select(func.count()).select_from(FuelAlert)),
            "orders": await db.scalar(select(func.count()).select_from(Order)),
            "savings_entries": await db.scalar(select(func.count()).select_from(SavingsEntry)),
        }
        return {"migration": revision or "unknown", "tables": counts}
    except Exception as exc:
        return {"migration": "not_applied", "tables": {}, "error": str(exc)}
