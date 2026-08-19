from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from pydantic import ValidationError

from app.models import MaintenanceTask, Order, Organization, Vehicle
from app.models.enums import MaintenanceKind, MaintenanceStatus, OrderStatus
from app.schemas.ops import (
    MaintenanceTaskCreate,
    MaintenanceTaskResponse,
    OrgSettings,
    RoutePlanResponse,
    RouteVariant,
    SettingsResponse,
    SettingsUpdate,
)

_BASE_DISTANCE = {
    ("Москва", "Санкт-Петербург"): 710,
    ("Казань", "Нижний Новгород"): 340,
    ("Екатеринбург", "Челябинск"): 210,
    ("Самара", "Уфа"): 430,
    ("Тверь", "Москва"): 180,
    ("Вологда", "Ярославль"): 200,
    ("Москва", "Казань"): 820,
}


def _pair_distance(origin: str, destination: str) -> float:
    key = (origin, destination)
    rev = (destination, origin)
    if key in _BASE_DISTANCE:
        return float(_BASE_DISTANCE[key])
    if rev in _BASE_DISTANCE:
        return float(_BASE_DISTANCE[rev])
    digest = hashlib.md5(f"{origin}|{destination}".encode()).hexdigest()
    return 250.0 + (int(digest[:4], 16) % 600)


def _build_variants(origin: str, destination: str) -> list[RouteVariant]:
    base = _pair_distance(origin, destination)
    mid = "объезд МКАД" if "Москва" in (origin, destination) else "федеральная трасса"
    return [
        RouteVariant(
            id="fast",
            label="Быстрый",
            distance_km=round(base * 1.02, 1),
            duration_h=round(base / 72, 1),
            fuel_cost_rub=round(base * 1.02 * 48, 0),
            savings_rub=round(base * 4.5, 0),
            via=[mid, "платные участки"],
        ),
        RouteVariant(
            id="eco",
            label="Экономичный",
            distance_km=round(base * 1.12, 1),
            duration_h=round(base / 58, 1),
            fuel_cost_rub=round(base * 0.95 * 48, 0),
            savings_rub=round(base * 9.2, 0),
            via=["второстепенные дороги", mid],
        ),
        RouteVariant(
            id="balanced",
            label="Баланс",
            distance_km=round(base * 1.05, 1),
            duration_h=round(base / 65, 1),
            fuel_cost_rub=round(base * 48, 0),
            savings_rub=round(base * 6.8, 0),
            via=[mid],
        ),
    ]


def _route_from_order(order: Order) -> RoutePlanResponse:
    details = order.details or {}
    origin = (details.get("origin") or {}).get("name") or "—"
    destination = (details.get("destination") or {}).get("name") or "—"
    route = details.get("route") or {}
    variants_raw = route.get("variants") or []
    variants = [RouteVariant.model_validate(v) for v in variants_raw]
    return RoutePlanResponse(
        order_id=order.id,
        external_ref=order.external_ref,
        status=order.status.value if hasattr(order.status, "value") else str(order.status),
        origin=origin,
        destination=destination,
        plate=details.get("plate"),
        recommended=route.get("recommended"),
        accepted_variant_id=route.get("accepted_variant_id"),
        variants=variants,
    )


async def list_routes(db: AsyncSession, org_id: uuid.UUID) -> list[RoutePlanResponse]:
    rows = (
        await db.scalars(
            select(Order)
            .where(
                Order.organization_id == org_id,
                Order.status.in_(
                    [OrderStatus.NEW, OrderStatus.ASSIGNED, OrderStatus.IN_TRANSIT]
                ),
            )
            .order_by(Order.created_at.desc())
        )
    ).all()
    return [_route_from_order(o) for o in rows]


async def optimize_route(db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID) -> RoutePlanResponse:
    order = await db.scalar(
        select(Order).where(Order.id == order_id, Order.organization_id == org_id)
    )
    if not order:
        raise LookupError("Order not found")
    details = dict(order.details or {})
    origin = (details.get("origin") or {}).get("name") or "Москва"
    destination = (details.get("destination") or {}).get("name") or "Санкт-Петербург"
    variants = _build_variants(origin, destination)
    details["route"] = {
        "recommended": "balanced",
        "accepted_variant_id": None,
        "optimized_at": datetime.now(UTC).isoformat(),
        "variants": [v.model_dump() for v in variants],
        "source": "route_agent_demo",
    }
    order.details = details
    flag_modified(order, "details")
    await db.commit()
    await db.refresh(order)
    return _route_from_order(order)


async def accept_route(
    db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID, variant_id: str
) -> RoutePlanResponse:
    order = await db.scalar(
        select(Order).where(Order.id == order_id, Order.organization_id == org_id)
    )
    if not order:
        raise LookupError("Order not found")
    details = dict(order.details or {})
    route = dict(details.get("route") or {})
    variants = route.get("variants") or []
    if not variants:
        raise LookupError("Сначала оптимизируйте маршрут")
    if not any(v.get("id") == variant_id for v in variants):
        raise LookupError("Вариант не найден")
    route["accepted_variant_id"] = variant_id
    route["accepted_at"] = datetime.now(UTC).isoformat()
    details["route"] = route
    order.details = details
    flag_modified(order, "details")
    if order.status == OrderStatus.NEW:
        order.status = OrderStatus.ASSIGNED
    await db.commit()
    await db.refresh(order)
    return _route_from_order(order)


def _task_response(task: MaintenanceTask, plate: str | None = None) -> MaintenanceTaskResponse:
    return MaintenanceTaskResponse(
        id=task.id,
        vehicle_id=task.vehicle_id,
        plate=plate,
        title=task.title,
        kind=task.kind,
        status=task.status,
        due_at=task.due_at,
        mileage_km=task.mileage_km,
        estimated_cost_rub=task.estimated_cost_rub,
        notes=task.notes,
        created_at=task.created_at,
    )


async def _plates_map(db: AsyncSession, vehicle_ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    if not vehicle_ids:
        return {}
    rows = await db.scalars(select(Vehicle).where(Vehicle.id.in_(vehicle_ids)))
    return {v.id: v.plate for v in rows}


def _refresh_overdue(task: MaintenanceTask, now: datetime) -> None:
    if task.status in (MaintenanceStatus.DONE, MaintenanceStatus.IN_PROGRESS):
        return
    if task.due_at and task.due_at < now and task.status != MaintenanceStatus.OVERDUE:
        task.status = MaintenanceStatus.OVERDUE


async def list_maintenance(
    db: AsyncSession, org_id: uuid.UUID
) -> tuple[list[MaintenanceTaskResponse], int]:
    now = datetime.now(UTC)
    rows = (
        await db.scalars(
            select(MaintenanceTask)
            .where(MaintenanceTask.organization_id == org_id)
            .order_by(MaintenanceTask.due_at.asc().nulls_last(), MaintenanceTask.created_at.desc())
        )
    ).all()
    changed = False
    for task in rows:
        before = task.status
        _refresh_overdue(task, now)
        if task.status != before:
            changed = True
    if changed:
        await db.commit()

    plates = await _plates_map(db, {t.vehicle_id for t in rows if t.vehicle_id})
    items = [_task_response(t, plates.get(t.vehicle_id) if t.vehicle_id else None) for t in rows]
    overdue = sum(1 for t in rows if t.status == MaintenanceStatus.OVERDUE)
    return items, overdue


async def create_maintenance(
    db: AsyncSession, org_id: uuid.UUID, payload: MaintenanceTaskCreate
) -> MaintenanceTaskResponse:
    if payload.vehicle_id:
        vehicle = await db.scalar(
            select(Vehicle).where(Vehicle.id == payload.vehicle_id, Vehicle.organization_id == org_id)
        )
        if not vehicle:
            raise LookupError("Vehicle not found")
        plate = vehicle.plate
    else:
        plate = None

    status = MaintenanceStatus.PLANNED
    if payload.due_at and payload.due_at < datetime.now(UTC):
        status = MaintenanceStatus.OVERDUE

    task = MaintenanceTask(
        organization_id=org_id,
        vehicle_id=payload.vehicle_id,
        title=payload.title,
        kind=payload.kind,
        status=status,
        due_at=payload.due_at,
        mileage_km=payload.mileage_km,
        estimated_cost_rub=payload.estimated_cost_rub,
        notes=payload.notes,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return _task_response(task, plate)


async def complete_maintenance(
    db: AsyncSession, org_id: uuid.UUID, task_id: uuid.UUID
) -> MaintenanceTaskResponse:
    task = await db.scalar(
        select(MaintenanceTask).where(
            MaintenanceTask.id == task_id, MaintenanceTask.organization_id == org_id
        )
    )
    if not task:
        raise LookupError("Task not found")
    task.status = MaintenanceStatus.DONE
    await db.commit()
    await db.refresh(task)
    plate = None
    if task.vehicle_id:
        v = await db.get(Vehicle, task.vehicle_id)
        plate = v.plate if v else None
    return _task_response(task, plate)


async def start_maintenance(
    db: AsyncSession, org_id: uuid.UUID, task_id: uuid.UUID
) -> MaintenanceTaskResponse:
    task = await db.scalar(
        select(MaintenanceTask).where(
            MaintenanceTask.id == task_id, MaintenanceTask.organization_id == org_id
        )
    )
    if not task:
        raise LookupError("Task not found")
    task.status = MaintenanceStatus.IN_PROGRESS
    await db.commit()
    await db.refresh(task)
    plate = None
    if task.vehicle_id:
        v = await db.get(Vehicle, task.vehicle_id)
        plate = v.plate if v else None
    return _task_response(task, plate)


DEFAULT_SETTINGS = OrgSettings()


def _parse_settings(raw: dict | None) -> OrgSettings:
    try:
        return OrgSettings.model_validate(raw or {})
    except ValidationError as exc:
        import logging

        logging.getLogger(__name__).warning("Invalid org settings payload, using defaults: %s", exc)
        return DEFAULT_SETTINGS.model_copy()


async def get_settings(db: AsyncSession, org_id: uuid.UUID) -> SettingsResponse:
    org = await db.get(Organization, org_id)
    if not org:
        raise LookupError("Organization not found")
    return SettingsResponse(
        organization_id=org.id,
        name=org.name,
        slug=org.slug,
        settings=_parse_settings(org.settings),
    )


async def update_settings(
    db: AsyncSession, org_id: uuid.UUID, payload: SettingsUpdate
) -> SettingsResponse:
    org = await db.get(Organization, org_id)
    if not org:
        raise LookupError("Organization not found")
    if payload.name is not None:
        org.name = payload.name.strip()
    if payload.settings is not None:
        org.settings = payload.settings.model_dump()
        flag_modified(org, "settings")
    await db.commit()
    await db.refresh(org)
    return SettingsResponse(
        organization_id=org.id,
        name=org.name,
        slug=org.slug,
        settings=_parse_settings(org.settings),
    )


def demo_maintenance_specs(vehicles: list[Vehicle]) -> list[dict]:
    now = datetime.now(UTC)
    specs = [
        ("ТО-2 · масло и фильтры", MaintenanceKind.TO, 3, 45000, MaintenanceStatus.PLANNED),
        ("Замена тормозных колодок", MaintenanceKind.REPAIR, -2, 28000, MaintenanceStatus.OVERDUE),
        ("Диагностика ДВС / CAN", MaintenanceKind.INSPECTION, 1, 12000, MaintenanceStatus.IN_PROGRESS),
        ("ТО-1 · сезонный осмотр", MaintenanceKind.TO, 10, 18000, MaintenanceStatus.PLANNED),
        ("Ремонт пневмоподвески", MaintenanceKind.REPAIR, 5, 65000, MaintenanceStatus.PLANNED),
    ]
    out: list[dict] = []
    for i, (title, kind, days, cost, status) in enumerate(specs):
        vehicle = vehicles[i % len(vehicles)] if vehicles else None
        out.append(
            {
                "vehicle_id": vehicle.id if vehicle else None,
                "title": title,
                "kind": kind,
                "status": status,
                "due_at": now + timedelta(days=days),
                "mileage_km": 120000 + i * 8500,
                "estimated_cost_rub": cost,
                "notes": "Maintenance Agent (DEMO)",
            }
        )
    return out
