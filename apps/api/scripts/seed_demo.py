"""Seed demo fleet: 32 vehicles + KPI data for ROI dashboard."""

from __future__ import annotations

import argparse
import asyncio
import random
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import async_session_factory
from app.models import (
    FuelAlert,
    Integration,
    MaintenanceTask,
    Order,
    Organization,
    SavingsEntry,
    User,
    Vehicle,
)
from app.models.enums import (
    AlertSeverity,
    IntegrationProvider,
    IntegrationStatus,
    OrderStatus,
    SavingsCategory,
    UserRole,
    VehicleStatus,
)
from app.services.demo_telematics import demo_order_details, demo_position_for_index
from app.services.ops_service import demo_maintenance_specs
from app.schemas.ops import OrgSettings

DEMO_SLUG = "demo-fleet"
DEMO_EMAIL = "demo@fleetpilot.ru"
DEMO_PASSWORD = "Demo12345!"
DEMO_ORG_NAME = "Демо Автопарк"

PLATES = [
    "А123ВС77",
    "В456КМ99",
    "Е789НО50",
    "К012РС77",
    "М345ТУ99",
    "Н678УХ50",
    "О901АВ77",
    "Р234СД99",
    "С567ЕЖ50",
    "Т890ЗИ77",
    "У123КЛ99",
    "Х456МН50",
    "А789ОП77",
    "В012РС99",
    "Е345ТУ50",
    "К678ФХ77",
    "М901ЦЧ99",
    "Н234ШЩ50",
    "О567ЫЬ77",
    "Р890ЭЮ99",
    "С123ЯА50",
    "Т456ВГ77",
    "У789ДЕ99",
    "Х012ЖЗ50",
    "А345ИК77",
    "В678ЛМ99",
    "Е901НО50",
    "К234ПР77",
    "М567СТ99",
    "Н890УФ50",
    "О123ХЦ77",
    "Р456ЧШ99",
]

FLEET = [
    ("КАМАЗ", "54901", 20000),
    ("МАЗ", "6501", 18000),
    ("Volvo", "FH16", 22000),
    ("MAN", "TGX", 21000),
    ("Scania", "R450", 23000),
    ("Mercedes-Benz", "Actros", 20000),
    ("DAF", "XF", 19000),
    ("IVECO", "S-Way", 18500),
]


def _month_start() -> datetime.date:
    now = datetime.now(UTC).date()
    return now.replace(day=1)


async def _clear_demo_data(db, org_id: uuid.UUID) -> None:
    await db.execute(delete(SavingsEntry).where(SavingsEntry.organization_id == org_id))
    await db.execute(delete(FuelAlert).where(FuelAlert.organization_id == org_id))
    await db.execute(delete(MaintenanceTask).where(MaintenanceTask.organization_id == org_id))
    await db.execute(delete(Order).where(Order.organization_id == org_id))
    await db.execute(delete(Vehicle).where(Vehicle.organization_id == org_id))
    await db.execute(delete(Integration).where(Integration.organization_id == org_id))


async def seed_demo(*, force: bool = False) -> None:
    settings = get_settings()
    month_start = _month_start()
    prev_month = (month_start.replace(day=1) - timedelta(days=1)).replace(day=1)

    async with async_session_factory() as db:
        org = await db.scalar(select(Organization).where(Organization.slug == DEMO_SLUG))

        if org and not force:
            existing = await db.scalar(
                select(Vehicle.id).where(Vehicle.organization_id == org.id).limit(1)
            )
            if existing:
                print(f"Demo fleet already exists ({DEMO_SLUG}). Use --force to reseed.")
                return

        if org and force:
            await _clear_demo_data(db, org.id)
            org.settings = OrgSettings().model_dump()
        elif not org:
            org = Organization(name=DEMO_ORG_NAME, slug=DEMO_SLUG, settings=OrgSettings().model_dump())
            db.add(org)
            await db.flush()
        else:
            if not org.settings:
                org.settings = OrgSettings().model_dump()

        user = await db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if not user:
            user = User(
                organization_id=org.id,
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
                full_name="Демо Администратор",
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(user)

        statuses = [VehicleStatus.ACTIVE] * 28 + [VehicleStatus.MAINTENANCE] * 2 + [VehicleStatus.INACTIVE] * 2
        random.shuffle(statuses)

        vehicles: list[Vehicle] = []
        for index, plate in enumerate(PLATES):
            brand, model, capacity = FLEET[index % len(FLEET)]
            vehicle = Vehicle(
                organization_id=org.id,
                plate=plate,
                brand=brand,
                model=model,
                capacity_kg=capacity,
                status=statuses[index],
                external_ids={
                    "omnicomm": f"unit_{1000 + index}",
                    "wialon": f"unit_{1000 + index}",
                    "last_position": demo_position_for_index(
                        index, moving=statuses[index] == VehicleStatus.ACTIVE
                    ),
                },
            )
            vehicles.append(vehicle)
            db.add(vehicle)

        await db.flush()

        for provider in (
            IntegrationProvider.OMNICOMM,
            IntegrationProvider.WIALON,
            IntegrationProvider.TRANSMANAGER,
        ):
            existing = await db.scalar(
                select(Integration).where(
                    Integration.organization_id == org.id,
                    Integration.provider == provider,
                )
            )
            if not existing:
                db.add(
                    Integration(
                        organization_id=org.id,
                        provider=provider,
                        credentials_enc={"demo": True},
                        status=IntegrationStatus.ACTIVE,
                        last_sync_at=datetime.now(UTC),
                    )
                )

        savings_plan = [
            (SavingsCategory.FUEL, 142_000),
            (SavingsCategory.ROUTE, 85_000),
            (SavingsCategory.DISPATCH, 25_000),
            (SavingsCategory.MAINTENANCE, 15_000),
        ]
        for category, amount in savings_plan:
            db.add(
                SavingsEntry(
                    organization_id=org.id,
                    category=category,
                    amount_rub=amount,
                    period_month=month_start,
                    note="Demo seed",
                )
            )

        prev_total = 267_000 / 1.22
        for category, amount in savings_plan:
            db.add(
                SavingsEntry(
                    organization_id=org.id,
                    category=category,
                    amount_rub=round(amount / 267_000 * prev_total, 2),
                    period_month=prev_month,
                    note="Demo seed previous month",
                )
            )

        alert_specs = [
            (AlertSeverity.CRITICAL, "Подозрительный слив 180 л · А123ВС77"),
            (AlertSeverity.WARNING, "Расход +18% vs baseline · В456КМ99"),
            (AlertSeverity.INFO, "Заправка вне маршрута · Е789НО50"),
        ]
        for idx, (severity, title) in enumerate(alert_specs):
            db.add(
                FuelAlert(
                    organization_id=org.id,
                    vehicle_id=vehicles[idx].id,
                    severity=severity,
                    title=title,
                    detected_at=datetime.now(UTC) - timedelta(hours=2),
                )
            )

        now = datetime.now(UTC)
        day_start = now.replace(hour=8, minute=0, second=0, microsecond=0)

        for index in range(18):
            status = OrderStatus.NEW
            if index < 5:
                status = OrderStatus.ASSIGNED if index % 2 == 0 else OrderStatus.IN_TRANSIT
            elif index < 12:
                status = OrderStatus.COMPLETED

            assigned_vehicle = vehicles[index % len(vehicles)].id if status != OrderStatus.NEW else None
            db.add(
                Order(
                    organization_id=org.id,
                    external_ref=f"ORD-{202600 + index}",
                    status=status,
                    details=demo_order_details(index, assigned_vehicle),
                    created_at=day_start + timedelta(minutes=index * 17),
                )
            )

        for spec in demo_maintenance_specs(vehicles):
            db.add(
                MaintenanceTask(
                    organization_id=org.id,
                    vehicle_id=spec["vehicle_id"],
                    title=spec["title"],
                    kind=spec["kind"],
                    status=spec["status"],
                    due_at=spec["due_at"],
                    mileage_km=spec["mileage_km"],
                    estimated_cost_rub=spec["estimated_cost_rub"],
                    notes=spec["notes"],
                )
            )

        await db.commit()

        print("Demo fleet seeded successfully.")
        print(f"  Organization : {DEMO_ORG_NAME} ({DEMO_SLUG})")
        print(f"  Login        : {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print(f"  Vehicles     : 32 (28 active)")
        print(f"  Maintenance  : {len(demo_maintenance_specs(vehicles))} tasks")
        print(f"  Monthly KPI  : ₽267,000 savings")
        print(f"  Database URL : {settings.database_url}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed FleetPilot demo data")
    parser.add_argument("--force", action="store_true", help="Replace existing demo fleet data")
    args = parser.parse_args()
    asyncio.run(seed_demo(force=args.force))


if __name__ == "__main__":
    main()
