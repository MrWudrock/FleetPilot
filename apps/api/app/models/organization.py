import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.fuel_alert import FuelAlert
    from app.models.integration import Integration
    from app.models.maintenance_task import MaintenanceTask
    from app.models.order import Order
    from app.models.permit_audit_log import PermitAuditLog
    from app.models.permit_request import PermitRequest
    from app.models.savings_entry import SavingsEntry
    from app.models.user import User
    from app.models.vehicle import Vehicle


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    users: Mapped[list["User"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    integrations: Mapped[list["Integration"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    fuel_alerts: Mapped[list["FuelAlert"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    savings_entries: Mapped[list["SavingsEntry"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    permit_requests: Mapped[list["PermitRequest"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    permit_audit_logs: Mapped[list["PermitAuditLog"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    maintenance_tasks: Mapped[list["MaintenanceTask"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
