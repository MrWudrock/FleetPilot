import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AdminUser, CurrentUser, FleetStaffUser
from app.db.session import get_db
from app.schemas.ops import (
    MaintenanceTaskCreate,
    MaintenanceTaskListResponse,
    MaintenanceTaskResponse,
    RouteAcceptRequest,
    RouteListResponse,
    RouteOptimizeRequest,
    RoutePlanResponse,
    SettingsResponse,
    SettingsUpdate,
)
from app.services import ops_service

router = APIRouter(tags=["ops"])


@router.get("/routes", response_model=RouteListResponse)
async def get_routes(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> RouteListResponse:
    items = await ops_service.list_routes(db, user.organization_id)
    return RouteListResponse(items=items, total=len(items))


@router.post("/routes/optimize", response_model=RoutePlanResponse)
async def post_optimize_route(
    payload: RouteOptimizeRequest, user: FleetStaffUser, db: AsyncSession = Depends(get_db)
) -> RoutePlanResponse:
    try:
        return await ops_service.optimize_route(db, user.organization_id, payload.order_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/routes/{order_id}/accept", response_model=RoutePlanResponse)
async def post_accept_route(
    order_id: uuid.UUID,
    payload: RouteAcceptRequest,
    user: FleetStaffUser,
    db: AsyncSession = Depends(get_db),
) -> RoutePlanResponse:
    try:
        return await ops_service.accept_route(db, user.organization_id, order_id, payload.variant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/maintenance/tasks", response_model=MaintenanceTaskListResponse)
async def get_maintenance_tasks(
    user: CurrentUser, db: AsyncSession = Depends(get_db)
) -> MaintenanceTaskListResponse:
    items, overdue = await ops_service.list_maintenance(db, user.organization_id)
    return MaintenanceTaskListResponse(items=items, total=len(items), overdue=overdue)


@router.post("/maintenance/tasks", response_model=MaintenanceTaskResponse, status_code=201)
async def post_maintenance_task(
    payload: MaintenanceTaskCreate, user: FleetStaffUser, db: AsyncSession = Depends(get_db)
) -> MaintenanceTaskResponse:
    try:
        return await ops_service.create_maintenance(db, user.organization_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/maintenance/tasks/{task_id}/start", response_model=MaintenanceTaskResponse)
async def post_start_maintenance(
    task_id: uuid.UUID, user: FleetStaffUser, db: AsyncSession = Depends(get_db)
) -> MaintenanceTaskResponse:
    try:
        return await ops_service.start_maintenance(db, user.organization_id, task_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/maintenance/tasks/{task_id}/complete", response_model=MaintenanceTaskResponse)
async def post_complete_maintenance(
    task_id: uuid.UUID, user: FleetStaffUser, db: AsyncSession = Depends(get_db)
) -> MaintenanceTaskResponse:
    try:
        return await ops_service.complete_maintenance(db, user.organization_id, task_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/settings", response_model=SettingsResponse)
async def get_settings(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> SettingsResponse:
    try:
        return await ops_service.get_settings(db, user.organization_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/settings", response_model=SettingsResponse)
async def patch_settings(
    payload: SettingsUpdate, user: AdminUser, db: AsyncSession = Depends(get_db)
) -> SettingsResponse:
    try:
        return await ops_service.update_settings(db, user.organization_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
