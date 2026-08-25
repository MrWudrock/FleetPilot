from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.crypto import seal_credentials
from app.models import FuelAlert, Integration, Order, Vehicle
from app.models.enums import IntegrationProvider, IntegrationStatus, OrderStatus, VehicleStatus
from app.schemas.fleet import (
    FuelAlertResponse,
    IntegrationConnectRequest,
    IntegrationResponse,
    OrderCreate,
    OrderResponse,
    VehicleCreate,
    VehiclePosition,
    VehicleResponse,
)
from app.services.demo_telematics import demo_order_details, demo_position_for_index, motion_status

PROVIDER_LABELS = {
    IntegrationProvider.WIALON: "Wialon Local (DEMO)",
    IntegrationProvider.TRANSMANAGER: "ТрансМенеджер (DEMO)",
    IntegrationProvider.OMNICOMM: "Omnicomm",
    IntegrationProvider.ROSDOR_MONITORING: "Росдормониторинг",
    IntegrationProvider.MASTER_TMS: "Master TMS",
    IntegrationProvider.STAVTRACK: "СтавТРЭК",
    IntegrationProvider.MSS_GLONASS: "MSS GLONASS",
}


def _vehicle_response(vehicle: Vehicle, index: int = 0) -> VehicleResponse:
    raw = (vehicle.external_ids or {}).get("last_position")
    position = VehiclePosition.model_validate(raw) if raw else None
    if position is None and vehicle.status == VehicleStatus.ACTIVE:
        # Lazy demo position if seed had none
        position = VehiclePosition.model_validate(
            demo_position_for_index(index, moving=True)
        )
    return VehicleResponse(
        id=vehicle.id,
        plate=vehicle.plate,
        brand=vehicle.brand,
        model=vehicle.model,
        capacity_kg=vehicle.capacity_kg,
        status=vehicle.status,
        external_ids=vehicle.external_ids or {},
        position=position,
        motion=motion_status(position.model_dump() if position else None, vehicle.status.value),
    )


async def list_vehicles(db: AsyncSession, org_id: uuid.UUID) -> list[VehicleResponse]:
    rows = (
        await db.scalars(
            select(Vehicle)
            .where(Vehicle.organization_id == org_id)
            .order_by(Vehicle.plate)
        )
    ).all()
    return [_vehicle_response(v, i) for i, v in enumerate(rows)]


async def create_vehicle(db: AsyncSession, org_id: uuid.UUID, payload: VehicleCreate) -> VehicleResponse:
    vehicle = Vehicle(
        organization_id=org_id,
        plate=payload.plate.upper(),
        brand=payload.brand,
        model=payload.model,
        capacity_kg=payload.capacity_kg,
        status=payload.status,
        external_ids={"wialon": f"unit_manual_{payload.plate}", "last_position": demo_position_for_index(0)},
    )
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return _vehicle_response(vehicle)


async def list_fuel_alerts(db: AsyncSession, org_id: uuid.UUID) -> tuple[list[FuelAlertResponse], int]:
    alerts = (
        await db.scalars(
            select(FuelAlert)
            .where(FuelAlert.organization_id == org_id)
            .order_by(FuelAlert.detected_at.desc())
        )
    ).all()
    vehicle_ids = {a.vehicle_id for a in alerts if a.vehicle_id}
    plates: dict[uuid.UUID, str] = {}
    if vehicle_ids:
        for v in await db.scalars(select(Vehicle).where(Vehicle.id.in_(vehicle_ids))):
            plates[v.id] = v.plate

    items = [
        FuelAlertResponse(
            id=a.id,
            vehicle_id=a.vehicle_id,
            plate=plates.get(a.vehicle_id) if a.vehicle_id else None,
            severity=a.severity,
            title=a.title,
            detected_at=a.detected_at,
            acknowledged=a.acknowledged,
        )
        for a in alerts
    ]
    unack = sum(1 for a in alerts if not a.acknowledged)
    return items, unack


async def acknowledge_alert(db: AsyncSession, org_id: uuid.UUID, alert_id: uuid.UUID) -> FuelAlertResponse:
    alert = await db.scalar(
        select(FuelAlert).where(FuelAlert.id == alert_id, FuelAlert.organization_id == org_id)
    )
    if not alert:
        raise LookupError("Alert not found")
    alert.acknowledged = True
    await db.commit()
    await db.refresh(alert)
    plate = None
    if alert.vehicle_id:
        v = await db.get(Vehicle, alert.vehicle_id)
        plate = v.plate if v else None
    return FuelAlertResponse(
        id=alert.id,
        vehicle_id=alert.vehicle_id,
        plate=plate,
        severity=alert.severity,
        title=alert.title,
        detected_at=alert.detected_at,
        acknowledged=alert.acknowledged,
    )


def _integration_response(row: Integration) -> IntegrationResponse:
    creds = row.credentials_enc or {}
    return IntegrationResponse(
        id=row.id,
        provider=row.provider,
        status=row.status,
        last_sync_at=row.last_sync_at,
        last_error=row.last_error,
        demo=bool(creds.get("demo", True)),
        label=PROVIDER_LABELS.get(row.provider, row.provider.value),
    )


async def list_integrations(db: AsyncSession, org_id: uuid.UUID) -> list[IntegrationResponse]:
    rows = (
        await db.scalars(select(Integration).where(Integration.organization_id == org_id))
    ).all()
    return [_integration_response(r) for r in rows]


async def connect_integration(
    db: AsyncSession,
    org_id: uuid.UUID,
    provider: IntegrationProvider,
    payload: IntegrationConnectRequest,
) -> IntegrationResponse:
    from fastapi import HTTPException, status

    from app.core.config import get_settings

    token = payload.token.strip()
    is_demo_token = token == "demo-token"
    demo = payload.demo or is_demo_token
    if is_demo_token and not get_settings().debug and not payload.demo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="demo-token is only allowed in DEBUG/demo mode",
        )

    row = await db.scalar(
        select(Integration).where(
            Integration.organization_id == org_id,
            Integration.provider == provider,
        )
    )
    creds = seal_credentials(token=token, host=payload.host, demo=demo)
    if row:
        row.credentials_enc = creds
        row.status = IntegrationStatus.ACTIVE
        row.last_error = None
        row.last_sync_at = datetime.now(UTC)
    else:
        row = Integration(
            organization_id=org_id,
            provider=provider,
            credentials_enc=creds,
            status=IntegrationStatus.ACTIVE,
            last_sync_at=datetime.now(UTC),
        )
        db.add(row)
    await db.commit()
    await db.refresh(row)
    return _integration_response(row)


async def sync_wialon(db: AsyncSession, org_id: uuid.UUID) -> tuple[int, IntegrationResponse | None]:
    integration = await db.scalar(
        select(Integration).where(
            Integration.organization_id == org_id,
            Integration.provider == IntegrationProvider.WIALON,
        )
    )
    vehicles = (
        await db.scalars(select(Vehicle).where(Vehicle.organization_id == org_id).order_by(Vehicle.plate))
    ).all()
    synced = 0
    for index, vehicle in enumerate(vehicles):
        moving = vehicle.status == VehicleStatus.ACTIVE
        pos = demo_position_for_index(index, moving=moving)
        ext = dict(vehicle.external_ids or {})
        ext["wialon"] = ext.get("wialon") or f"unit_{1000 + index}"
        ext["last_position"] = pos
        vehicle.external_ids = ext
        flag_modified(vehicle, "external_ids")
        synced += 1

    if integration:
        integration.last_sync_at = datetime.now(UTC)
        integration.status = IntegrationStatus.ACTIVE
        integration.last_error = None
    else:
        integration = Integration(
            organization_id=org_id,
            provider=IntegrationProvider.WIALON,
            credentials_enc=seal_credentials(token="demo-token", host=None, demo=True),
            status=IntegrationStatus.ACTIVE,
            last_sync_at=datetime.now(UTC),
        )
        db.add(integration)

    await db.commit()
    await db.refresh(integration)
    return synced, _integration_response(integration)


async def sync_transmanager(db: AsyncSession, org_id: uuid.UUID) -> tuple[int, IntegrationResponse | None]:
    integration = await db.scalar(
        select(Integration).where(
            Integration.organization_id == org_id,
            Integration.provider == IntegrationProvider.TRANSMANAGER,
        )
    )
    count = await db.scalar(
        select(func.count()).select_from(Order).where(Order.organization_id == org_id)
    )
    # Ensure at least a handful of demo orders exist
    created = 0
    if (count or 0) < 5:
        vehicles = (
            await db.scalars(select(Vehicle).where(Vehicle.organization_id == org_id).limit(5))
        ).all()
        for i in range(5):
            vid = vehicles[i].id if i < len(vehicles) else None
            db.add(
                Order(
                    organization_id=org_id,
                    external_ref=f"TM-DEMO-{100 + i}",
                    status=OrderStatus.NEW if i > 1 else OrderStatus.ASSIGNED,
                    details=demo_order_details(i, vid),
                )
            )
            created += 1

    if integration:
        integration.last_sync_at = datetime.now(UTC)
        integration.status = IntegrationStatus.ACTIVE
        integration.last_error = None
    else:
        integration = Integration(
            organization_id=org_id,
            provider=IntegrationProvider.TRANSMANAGER,
            credentials_enc=seal_credentials(token=None, host=None, demo=True),
            status=IntegrationStatus.ACTIVE,
            last_sync_at=datetime.now(UTC),
        )
        db.add(integration)

    await db.commit()
    await db.refresh(integration)
    total = await db.scalar(
        select(func.count()).select_from(Order).where(Order.organization_id == org_id)
    )
    return int(total or 0) + created, _integration_response(integration)


async def list_orders(db: AsyncSession, org_id: uuid.UUID) -> list[OrderResponse]:
    rows = (
        await db.scalars(
            select(Order)
            .where(Order.organization_id == org_id)
            .order_by(Order.created_at.desc())
        )
    ).all()
    return [OrderResponse.model_validate(r) for r in rows]


async def create_order(db: AsyncSession, org_id: uuid.UUID, payload: OrderCreate) -> OrderResponse:
    details = {
        "origin": {"name": payload.origin_name},
        "destination": {"name": payload.destination_name},
        "cargo": {
            "mass_kg": payload.mass_kg,
            "length_m": payload.length_m,
            "width_m": payload.width_m,
            "height_m": payload.height_m,
            "description": "Заявка пилота",
        },
        "vehicle_id": None,
        "source": "transmanager_demo",
        "notes": payload.notes or "Создано вручную в FleetPilot",
    }
    order = Order(
        organization_id=org_id,
        external_ref=payload.external_ref or f"TM-{uuid.uuid4().hex[:8].upper()}",
        status=OrderStatus.NEW,
        details=details,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


async def assign_order(
    db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID, vehicle_id: uuid.UUID
) -> OrderResponse:
    order = await db.scalar(
        select(Order).where(Order.id == order_id, Order.organization_id == org_id)
    )
    if not order:
        raise LookupError("Order not found")
    vehicle = await db.scalar(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.organization_id == org_id)
    )
    if not vehicle:
        raise LookupError("Vehicle not found")
    details = dict(order.details or {})
    details["vehicle_id"] = str(vehicle.id)
    details["plate"] = vehicle.plate
    order.details = details
    flag_modified(order, "details")
    order.status = OrderStatus.ASSIGNED
    await db.commit()
    await db.refresh(order)
    return OrderResponse.model_validate(order)
