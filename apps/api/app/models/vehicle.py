import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import pg_str_enum
from app.models.enums import VehicleStatus

if TYPE_CHECKING:
    from app.models.fuel_alert import FuelAlert
    from app.models.maintenance_task import MaintenanceTask
    from app.models.organization import Organization


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (UniqueConstraint("organization_id", "plate", name="uq_vehicles_org_plate"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plate: Mapped[str] = mapped_column(String(16), nullable=False)
    external_ids: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    capacity_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[VehicleStatus] = mapped_column(
        pg_str_enum(VehicleStatus, name="vehicle_status"),
        nullable=False,
        default=VehicleStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization: Mapped["Organization"] = relationship(back_populates="vehicles")
    fuel_alerts: Mapped[list["FuelAlert"]] = relationship(back_populates="vehicle")
    maintenance_tasks: Mapped[list["MaintenanceTask"]] = relationship(back_populates="vehicle")
