import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import MaintenanceKind, MaintenanceStatus


class RouteVariant(BaseModel):
    id: str
    label: str
    distance_km: float
    duration_h: float
    fuel_cost_rub: float
    savings_rub: float
    via: list[str] = Field(default_factory=list)


class RoutePlanResponse(BaseModel):
    order_id: uuid.UUID
    external_ref: str | None
    status: str
    origin: str
    destination: str
    plate: str | None = None
    recommended: str | None = None
    accepted_variant_id: str | None = None
    variants: list[RouteVariant] = Field(default_factory=list)


class RouteListResponse(BaseModel):
    items: list[RoutePlanResponse]
    total: int


class RouteOptimizeRequest(BaseModel):
    order_id: uuid.UUID


class RouteAcceptRequest(BaseModel):
    variant_id: str


class MaintenanceTaskResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID | None
    plate: str | None = None
    title: str
    kind: MaintenanceKind
    status: MaintenanceStatus
    due_at: datetime | None
    mileage_km: float | None
    estimated_cost_rub: float | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MaintenanceTaskListResponse(BaseModel):
    items: list[MaintenanceTaskResponse]
    total: int
    overdue: int


class MaintenanceTaskCreate(BaseModel):
    vehicle_id: uuid.UUID | None = None
    title: str = Field(min_length=3, max_length=255)
    kind: MaintenanceKind = MaintenanceKind.TO
    due_at: datetime | None = None
    mileage_km: float | None = None
    estimated_cost_rub: float | None = None
    notes: str | None = None


class OrgSettings(BaseModel):
    timezone: str = "Europe/Moscow"
    currency: str = "RUB"
    notify_fuel_email: bool = True
    notify_maintenance_days: int = Field(default=7, ge=1, le=30)
    demo_mode: bool = True
    default_origin: str = "Москва"


class SettingsResponse(BaseModel):
    organization_id: uuid.UUID
    name: str
    slug: str
    settings: OrgSettings


class SettingsUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    settings: OrgSettings | None = None
