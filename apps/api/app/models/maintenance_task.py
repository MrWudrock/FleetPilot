import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import pg_str_enum
from app.models.enums import MaintenanceKind, MaintenanceStatus

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.vehicle import Vehicle


class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[MaintenanceKind] = mapped_column(
        pg_str_enum(MaintenanceKind, name="maintenance_kind"), nullable=False
    )
    status: Mapped[MaintenanceStatus] = mapped_column(
        pg_str_enum(MaintenanceStatus, name="maintenance_status"),
        nullable=False,
        default=MaintenanceStatus.PLANNED,
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    mileage_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_cost_rub: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization: Mapped["Organization"] = relationship(back_populates="maintenance_tasks")
    vehicle: Mapped["Vehicle | None"] = relationship(back_populates="maintenance_tasks")
