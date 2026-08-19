import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import PermitRequestStatus, PermitRiskLevel


class RoutePoint(BaseModel):
    name: str | None = None
    address: str | None = None
    lat: float | None = None
    lon: float | None = None


class CargoSpec(BaseModel):
    length_m: float = Field(gt=0, description="Длина груза, м")
    width_m: float = Field(gt=0, description="Ширина груза, м")
    height_m: float = Field(gt=0, description="Высота груза, м")
    mass_kg: float = Field(gt=0, description="Масса груза, кг")
    axle_loads_kg: list[float] = Field(default_factory=list, description="Нагрузка на оси, кг")


class PermitAnalysisResult(BaseModel):
    permit_required: bool
    podd_required: bool
    risk_level: PermitRiskLevel
    risk_score: float = Field(ge=0, le=1)
    route_summary: str
    restrictions: list[str] = Field(default_factory=list)
    special_conditions: list[str] = Field(default_factory=list)
    alternative_routes: list[str] = Field(default_factory=list)
    legal_references: list[str] = Field(default_factory=list)
    dispatcher_actions: list[str] = Field(default_factory=list)
    exceeds_limits: dict[str, bool] = Field(default_factory=dict)
    confidence: float = Field(ge=0, le=1, default=0.9)


class PermitRequestCreate(BaseModel):
    origin: RoutePoint
    destination: RoutePoint
    waypoints: list[RoutePoint] = Field(default_factory=list)
    cargo: CargoSpec
    vehicle_id: uuid.UUID | None = None
    order_id: uuid.UUID | None = None
    dispatcher_notes: str | None = None


class AnalyzeRouteRequest(BaseModel):
    origin: RoutePoint
    destination: RoutePoint
    waypoints: list[RoutePoint] = Field(default_factory=list)
    cargo: CargoSpec
    vehicle_id: uuid.UUID | None = None
    permit_request_id: uuid.UUID | None = None
    persist: bool = False


class AnalyzeRouteResponse(BaseModel):
    analysis: PermitAnalysisResult
    permit_request_id: uuid.UUID | None = None


class PermitApproveRequest(BaseModel):
    notes: str | None = None
    external_permit_number: str | None = None


class PermitRequestResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    order_id: uuid.UUID | None
    vehicle_id: uuid.UUID | None
    origin: RoutePoint
    destination: RoutePoint
    waypoints: list[RoutePoint]
    cargo: CargoSpec
    status: PermitRequestStatus
    analysis: PermitAnalysisResult | None
    risk_score: float | None
    external_permit_number: str | None
    dispatcher_notes: str | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PermitRequestListResponse(BaseModel):
    items: list[PermitRequestResponse]
    total: int


class RosdorHealthResponse(BaseModel):
    provider: str = "rosdor_monitoring"
    configured: bool
    parser_api_enabled: bool
    lk_enabled: bool
    status: str
    message: str


class RosdorPermitCheckRequest(BaseModel):
    permit_number: str = Field(min_length=3, max_length=64)
    plate: str = Field(min_length=3, max_length=16)


class RosdorPermitCheckResponse(BaseModel):
    found: bool
    permit_number: str
    plate: str
    status: str | None = None
    valid_until: str | None = None
    route_summary: str | None = None
    special_conditions: list[str] = Field(default_factory=list)
    source: str
