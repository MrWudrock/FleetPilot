import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import pg_str_enum
from app.models.enums import AlertSeverity

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.vehicle import Vehicle


class FuelAlert(Base):
    __tablename__ = "fuel_alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        pg_str_enum(AlertSeverity, name="alert_severity"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    organization: Mapped["Organization"] = relationship(back_populates="fuel_alerts")
    vehicle: Mapped["Vehicle | None"] = relationship(back_populates="fuel_alerts")
