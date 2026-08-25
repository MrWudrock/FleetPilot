import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PermitAuditLog, PermitRequest, User, Vehicle
from app.models.enums import PermitRequestStatus
from app.schemas.permit import (
    AnalyzeRouteRequest,
    AnalyzeRouteResponse,
    CargoSpec,
    PermitApproveRequest,
    PermitRequestCreate,
    PermitRequestListResponse,
    PermitRequestResponse,
    RoutePoint,
)
from app.services.permit_rules import analyze_route_rules


def _to_route_point(data: dict) -> RoutePoint:
    return RoutePoint.model_validate(data)


def _to_cargo(data: dict) -> CargoSpec:
    return CargoSpec.model_validate(data)


def _to_response(req: PermitRequest) -> PermitRequestResponse:
    analysis = None
    if req.analysis:
        from app.schemas.permit import PermitAnalysisResult

        analysis = PermitAnalysisResult.model_validate(req.analysis)

    return PermitRequestResponse(
        id=req.id,
        organization_id=req.organization_id,
        order_id=req.order_id,
        vehicle_id=req.vehicle_id,
        origin=_to_route_point(req.origin),
        destination=_to_route_point(req.destination),
        waypoints=[_to_route_point(wp) for wp in req.waypoints],
        cargo=_to_cargo(req.cargo),
        status=req.status,
        analysis=analysis,
        risk_score=req.risk_score,
        external_permit_number=req.external_permit_number,
        dispatcher_notes=req.dispatcher_notes,
        approved_at=req.approved_at,
        created_at=req.created_at,
        updated_at=req.updated_at,
    )


async def _ensure_vehicle(db: AsyncSession, org_id: uuid.UUID, vehicle_id: uuid.UUID | None) -> None:
    if vehicle_id is None:
        return
    vehicle = await db.scalar(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.organization_id == org_id)
    )
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")


async def _get_request_or_404(db: AsyncSession, org_id: uuid.UUID, request_id: uuid.UUID) -> PermitRequest:
    req = await db.scalar(
        select(PermitRequest).where(
            PermitRequest.id == request_id,
            PermitRequest.organization_id == org_id,
        )
    )
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permit request not found")
    return req


async def _log_audit(
    db: AsyncSession,
    *,
    org_id: uuid.UUID,
    action: str,
    provider: str,
    request_payload: dict,
    response_summary: dict,
    permit_request_id: uuid.UUID | None = None,
) -> None:
    db.add(
        PermitAuditLog(
            organization_id=org_id,
            permit_request_id=permit_request_id,
            action=action,
            provider=provider,
            request_payload=request_payload,
            response_summary=response_summary,
        )
    )


async def create_request(db: AsyncSession, user: User, payload: PermitRequestCreate) -> PermitRequestResponse:
    await _ensure_vehicle(db, user.organization_id, payload.vehicle_id)

    req = PermitRequest(
        organization_id=user.organization_id,
        order_id=payload.order_id,
        vehicle_id=payload.vehicle_id,
        created_by_id=user.id,
        origin=payload.origin.model_dump(),
        destination=payload.destination.model_dump(),
        waypoints=[wp.model_dump() for wp in payload.waypoints],
        cargo=payload.cargo.model_dump(),
        dispatcher_notes=payload.dispatcher_notes,
        status=PermitRequestStatus.DRAFT,
    )
    db.add(req)
    await db.flush()
    await _log_audit(
        db,
        org_id=user.organization_id,
        permit_request_id=req.id,
        action="create_request",
        provider="fleetpilot",
        request_payload={"cargo": payload.cargo.model_dump()},
        response_summary={"status": PermitRequestStatus.DRAFT.value},
    )
    await db.commit()
    await db.refresh(req)
    return _to_response(req)


async def list_requests(
    db: AsyncSession,
    user: User,
    *,
    limit: int = 50,
    offset: int = 0,
) -> PermitRequestListResponse:
    org_id = user.organization_id
    total = await db.scalar(
        select(func.count()).select_from(PermitRequest).where(PermitRequest.organization_id == org_id)
    ) or 0
    rows = await db.scalars(
        select(PermitRequest)
        .where(PermitRequest.organization_id == org_id)
        .order_by(PermitRequest.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = [_to_response(row) for row in rows.all()]
    return PermitRequestListResponse(items=items, total=total)


async def get_request(db: AsyncSession, user: User, request_id: uuid.UUID) -> PermitRequestResponse:
    req = await _get_request_or_404(db, user.organization_id, request_id)
    return _to_response(req)


async def analyze_route(db: AsyncSession, user: User, payload: AnalyzeRouteRequest) -> AnalyzeRouteResponse:
    await _ensure_vehicle(db, user.organization_id, payload.vehicle_id)

    analysis = analyze_route_rules(
        payload.origin,
        payload.destination,
        payload.cargo,
        waypoints=payload.waypoints,
    )

    permit_request_id: uuid.UUID | None = None
    req: PermitRequest | None = None

    if payload.permit_request_id:
        req = await _get_request_or_404(db, user.organization_id, payload.permit_request_id)
        permit_request_id = req.id
    elif payload.persist:
        req = PermitRequest(
            organization_id=user.organization_id,
            vehicle_id=payload.vehicle_id,
            created_by_id=user.id,
            origin=payload.origin.model_dump(),
            destination=payload.destination.model_dump(),
            waypoints=[wp.model_dump() for wp in payload.waypoints],
            cargo=payload.cargo.model_dump(),
            status=PermitRequestStatus.ANALYZING,
        )
        db.add(req)
        await db.flush()
        permit_request_id = req.id

    if req is not None:
        req.status = PermitRequestStatus.READY
        req.analysis = analysis.model_dump()
        req.risk_score = analysis.risk_score

    await _log_audit(
        db,
        org_id=user.organization_id,
        permit_request_id=permit_request_id,
        action="analyze_route",
        provider="permit_agent",
        request_payload={
            "origin": payload.origin.model_dump(),
            "destination": payload.destination.model_dump(),
            "cargo": payload.cargo.model_dump(),
        },
        response_summary={
            "permit_required": analysis.permit_required,
            "risk_level": analysis.risk_level.value,
            "risk_score": analysis.risk_score,
        },
    )

    await db.commit()
    if req is not None:
        await db.refresh(req)

    return AnalyzeRouteResponse(analysis=analysis, permit_request_id=permit_request_id)


async def approve_request(
    db: AsyncSession,
    user: User,
    request_id: uuid.UUID,
    payload: PermitApproveRequest,
) -> PermitRequestResponse:
    req = await _get_request_or_404(db, user.organization_id, request_id)

    if req.status not in {PermitRequestStatus.READY, PermitRequestStatus.DRAFT}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot approve request in status '{req.status.value}'",
        )
    if not req.analysis:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Run analyze-route before approval",
        )

    req.status = PermitRequestStatus.APPROVED
    req.approved_by_id = user.id
    req.approved_at = datetime.now(UTC)
    if payload.notes:
        req.dispatcher_notes = payload.notes
    if payload.external_permit_number:
        req.external_permit_number = payload.external_permit_number

    await _log_audit(
        db,
        org_id=user.organization_id,
        permit_request_id=req.id,
        action="approve",
        provider="fleetpilot",
        request_payload={"notes": payload.notes},
        response_summary={"status": PermitRequestStatus.APPROVED.value},
    )
    await db.commit()
    await db.refresh(req)
    return _to_response(req)
