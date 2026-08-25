from calendar import monthrange
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FuelAlert, Order, SavingsEntry, User, Vehicle
from app.models.enums import AlertSeverity, OrderStatus, SavingsCategory, VehicleStatus
from app.schemas.analytics import KpiDataSource, RoiKpiResponse, SavingsBreakdown

SUBSCRIPTION_MONTHLY_RUB = 49_000


def _month_bounds(target: date) -> tuple[date, date]:
    start = target.replace(day=1)
    last_day = monthrange(target.year, target.month)[1]
    end = target.replace(day=last_day)
    return start, end


def _previous_month(target: date) -> date:
    first = target.replace(day=1)
    return (first - timedelta(days=1)).replace(day=1)


async def get_roi_kpis(db: AsyncSession, user: User) -> RoiKpiResponse:
    org_id = user.organization_id
    today = datetime.now(UTC).date()
    month_start, _ = _month_bounds(today)
    prev_month_start = _previous_month(today)

    vehicle_count = await db.scalar(
        select(func.count()).select_from(Vehicle).where(Vehicle.organization_id == org_id)
    ) or 0
    active_vehicle_count = await db.scalar(
        select(func.count())
        .select_from(Vehicle)
        .where(Vehicle.organization_id == org_id, Vehicle.status == VehicleStatus.ACTIVE)
    ) or 0

    fuel_alerts_count = await db.scalar(
        select(func.count())
        .select_from(FuelAlert)
        .where(FuelAlert.organization_id == org_id, FuelAlert.acknowledged.is_(False))
    ) or 0
    fuel_alerts_critical = await db.scalar(
        select(func.count())
        .select_from(FuelAlert)
        .where(
            FuelAlert.organization_id == org_id,
            FuelAlert.acknowledged.is_(False),
            FuelAlert.severity == AlertSeverity.CRITICAL,
        )
    ) or 0

    active_routes_count = await db.scalar(
        select(func.count())
        .select_from(Order)
        .where(
            Order.organization_id == org_id,
            Order.status.in_([OrderStatus.ASSIGNED, OrderStatus.IN_TRANSIT]),
        )
    ) or 0

    day_start = datetime.combine(today, datetime.min.time(), tzinfo=UTC)
    day_end = day_start + timedelta(days=1)
    orders_today = await db.scalar(
        select(func.count())
        .select_from(Order)
        .where(
            Order.organization_id == org_id,
            Order.created_at >= day_start,
            Order.created_at < day_end,
        )
    ) or 0

    breakdown_rows = await db.execute(
        select(SavingsEntry.category, func.sum(SavingsEntry.amount_rub))
        .where(SavingsEntry.organization_id == org_id, SavingsEntry.period_month == month_start)
        .group_by(SavingsEntry.category)
    )

    breakdown = SavingsBreakdown()
    monthly_savings = 0.0
    for category, amount in breakdown_rows.all():
        value = float(amount or 0)
        monthly_savings += value
        setattr(breakdown, category.value, value)

    prev_month_savings = await db.scalar(
        select(func.coalesce(func.sum(SavingsEntry.amount_rub), 0.0)).where(
            SavingsEntry.organization_id == org_id,
            SavingsEntry.period_month == prev_month_start,
        )
    )
    prev_month_savings = float(prev_month_savings or 0)
    monthly_savings_delta_pct = None
    if prev_month_savings > 0:
        monthly_savings_delta_pct = round(
            ((monthly_savings - prev_month_savings) / prev_month_savings) * 100, 1
        )

    annual_savings = monthly_savings * 12
    annual_cost = SUBSCRIPTION_MONTHLY_RUB * 12
    roi_percent = None
    payback_months = None
    if annual_cost > 0 and annual_savings > 0:
        roi_percent = round((annual_savings / annual_cost) * 100, 1)
        payback_months = round(annual_cost / (monthly_savings or 1), 1)

    return RoiKpiResponse(
        monthly_savings_rub=monthly_savings,
        monthly_savings_delta_pct=monthly_savings_delta_pct,
        vehicle_count=vehicle_count,
        active_vehicle_count=active_vehicle_count,
        active_routes_count=active_routes_count,
        orders_today=orders_today,
        fuel_alerts_count=fuel_alerts_count,
        fuel_alerts_critical=fuel_alerts_critical,
        roi_percent_annual=roi_percent,
        payback_months=payback_months,
        annual_savings_rub=annual_savings,
        subscription_cost_monthly_rub=SUBSCRIPTION_MONTHLY_RUB,
        breakdown=breakdown,
        data_sources=KpiDataSource(),
    )
