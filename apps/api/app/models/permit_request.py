import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import pg_str_enum
from app.models.enums import PermitRequestStatus

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.permit_audit_log import PermitAuditLog
    from app.models.user import User
    from app.models.vehicle import Vehicle


class PermitRequest(Base):
    __tablename__ = "permit_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    origin: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    destination: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    waypoints: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    cargo: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")

    status: Mapped[PermitRequestStatus] = mapped_column(
        pg_str_enum(PermitRequestStatus, name="permit_request_status"),
        nullable=False,
        default=PermitRequestStatus.DRAFT,
    )
    analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    external_permit_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dispatcher_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization: Mapped["Organization"] = relationship(back_populates="permit_requests")
    vehicle: Mapped["Vehicle | None"] = relationship()
    created_by: Mapped["User | None"] = relationship(foreign_keys=[created_by_id])
    approved_by: Mapped["User | None"] = relationship(foreign_keys=[approved_by_id])
    audit_logs: Mapped[list["PermitAuditLog"]] = relationship(
        back_populates="permit_request", cascade="all, delete-orphan"
    )
