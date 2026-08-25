from pydantic import BaseModel, Field


class SavingsBreakdown(BaseModel):
    fuel: float = 0
    route: float = 0
    dispatch: float = 0
    maintenance: float = 0
    permit: float = 0


class KpiDataSource(BaseModel):
    vehicles: str = "database"
    monthly_savings: str = "database"
    fuel_alerts: str = "database"
    active_routes: str = "database"
    orders_today: str = "database"
    roi: str = "calculated"


class RoiKpiResponse(BaseModel):
    monthly_savings_rub: float
    monthly_savings_delta_pct: float | None = None
    vehicle_count: int
    active_vehicle_count: int
    active_routes_count: int
    orders_today: int
    fuel_alerts_count: int
    fuel_alerts_critical: int
    roi_percent_annual: float | None = None
    payback_months: float | None = None
    annual_savings_rub: float
    subscription_cost_monthly_rub: float = Field(default=49_000)
    breakdown: SavingsBreakdown
    data_sources: KpiDataSource
