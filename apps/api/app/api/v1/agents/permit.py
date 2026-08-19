import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, PermitStaffUser
from app.db.session import get_db
from app.integrations.rosdor_adapter import get_rosdor_adapter
from app.schemas.permit import (
    AnalyzeRouteRequest,
    AnalyzeRouteResponse,
    PermitApproveRequest,
    PermitRequestCreate,
    PermitRequestListResponse,
    PermitRequestResponse,
    RosdorHealthResponse,
    RosdorPermitCheckRequest,
    RosdorPermitCheckResponse,
)
from app.services import permit_service

router = APIRouter(prefix="/agents/permit", tags=["permit-agent"])


@router.post("/analyze-route", response_model=AnalyzeRouteResponse)
async def analyze_route(
    payload: AnalyzeRouteRequest,
    user: PermitStaffUser,
    db: AsyncSession = Depends(get_db),
) -> AnalyzeRouteResponse:
    return await permit_service.analyze_route(db, user, payload)


@router.get("/requests", response_model=PermitRequestListResponse)
async def list_permit_requests(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PermitRequestListResponse:
    return await permit_service.list_requests(db, user, limit=limit, offset=offset)


@router.post("/requests", response_model=PermitRequestResponse, status_code=201)
async def create_permit_request(
    payload: PermitRequestCreate,
    user: PermitStaffUser,
    db: AsyncSession = Depends(get_db),
) -> PermitRequestResponse:
    return await permit_service.create_request(db, user, payload)


@router.get("/requests/{request_id}", response_model=PermitRequestResponse)
async def get_permit_request(
    request_id: uuid.UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> PermitRequestResponse:
    return await permit_service.get_request(db, user, request_id)


@router.post("/requests/{request_id}/approve", response_model=PermitRequestResponse)
async def approve_permit_request(
    request_id: uuid.UUID,
    payload: PermitApproveRequest,
    user: PermitStaffUser,
    db: AsyncSession = Depends(get_db),
) -> PermitRequestResponse:
    return await permit_service.approve_request(db, user, request_id, payload)
