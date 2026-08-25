import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AlertSeverity, IntegrationProvider, IntegrationStatus, OrderStatus, VehicleStatus


class VehiclePosition(BaseModel):
    lat: float
    lon: float
    speed_kmh: float = 0
    heading: float | None = None
    ignition: bool = False
    updated_at: str | None = None
    source: str | None = None


class VehicleResponse(BaseModel):
    id: uuid.UUID
    plate: str
    brand: str | None
    model: str | None
    capacity_kg: float | None
    status: VehicleStatus
    external_ids: dict
    position: VehiclePosition | None = None
    motion: str = "offline"

    model_config = {"from_attributes": True}


class VehicleListResponse(BaseModel):
    items: list[VehicleResponse]
    total: int


class VehicleCreate(BaseModel):
    plate: str = Field(min_length=3, max_length=16)
    brand: str | None = None
    model: str | None = None
    capacity_kg: float | None = None
    status: VehicleStatus = VehicleStatus.ACTIVE


class FuelAlertResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID | None
    plate: str | None = None
    severity: AlertSeverity
    title: str
    detected_at: datetime
    acknowledged: bool

    model_config = {"from_attributes": True}


class FuelAlertListResponse(BaseModel):
    items: list[FuelAlertResponse]
    total: int
    unacknowledged: int


class IntegrationResponse(BaseModel):
    id: uuid.UUID
    provider: IntegrationProvider
    status: IntegrationStatus
    last_sync_at: datetime | None
    last_error: str | None
    demo: bool = False
    label: str

    model_config = {"from_attributes": True}


class IntegrationListResponse(BaseModel):
    items: list[IntegrationResponse]


class IntegrationConnectRequest(BaseModel):
    token: str = Field(min_length=1, max_length=512, description="Provider API token")
    host: str | None = Field(default=None, description="Wialon Local host / URL")
    demo: bool = Field(default=False, description="Mark connection as DEMO (allows demo-token)")


class SyncResponse(BaseModel):
    provider: str
    synced: int
    status: str
    message: str


class OrderResponse(BaseModel):
    id: uuid.UUID
    external_ref: str | None
    status: OrderStatus
    details: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int


class OrderCreate(BaseModel):
    external_ref: str | None = None
    origin_name: str = "Москва"
    destination_name: str = "Санкт-Петербург"
    mass_kg: float = 15000
    length_m: float = 13.6
    width_m: float = 2.45
    height_m: float = 3.5
    notes: str | None = None


class OrderAssignRequest(BaseModel):
    vehicle_id: uuid.UUID
