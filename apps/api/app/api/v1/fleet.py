import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, FleetStaffUser
from app.db.session import get_db
from app.models.enums import IntegrationProvider
from app.schemas.fleet import (
    FuelAlertListResponse,
    FuelAlertResponse,
    IntegrationConnectRequest,
    IntegrationListResponse,
    IntegrationResponse,
    OrderAssignRequest,
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    SyncResponse,
    VehicleCreate,
    VehicleListResponse,
    VehicleResponse,
)
from app.services import fleet_service

router = APIRouter(tags=["fleet"])


@router.get("/vehicles", response_model=VehicleListResponse)
async def get_vehicles(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> VehicleListResponse:
    items = await fleet_service.list_vehicles(db, user.organization_id)
    return VehicleListResponse(items=items, total=len(items))


@router.post("/vehicles", response_model=VehicleResponse, status_code=201)
async def post_vehicle(
    payload: VehicleCreate, user: FleetStaffUser, db: AsyncSession = Depends(get_db)
) -> VehicleResponse:
    return await fleet_service.create_vehicle(db, user.organization_id, payload)


@router.get("/fuel/alerts", response_model=FuelAlertListResponse)
async def get_fuel_alerts(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> FuelAlertListResponse:
    items, unack = await fleet_service.list_fuel_alerts(db, user.organization_id)
    return FuelAlertListResponse(items=items, total=len(items), unacknowledged=unack)


@router.post("/fuel/alerts/{alert_id}/acknowledge", response_model=FuelAlertResponse)
async def post_ack_alert(
    alert_id: uuid.UUID, user: FleetStaffUser, db: AsyncSession = Depends(get_db)
) -> FuelAlertResponse:
    try:
        return await fleet_service.acknowledge_alert(db, user.organization_id, alert_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/integrations", response_model=IntegrationListResponse)
async def get_integrations(
    user: CurrentUser, db: AsyncSession = Depends(get_db)
) -> IntegrationListResponse:
    items = await fleet_service.list_integrations(db, user.organization_id)
    return IntegrationListResponse(items=items)


@router.post("/integrations/wialon/connect", response_model=IntegrationResponse)
async def connect_wialon(
    payload: IntegrationConnectRequest,
    user: FleetStaffUser,
    db: AsyncSession = Depends(get_db),
) -> IntegrationResponse:
    return await fleet_service.connect_integration(
        db, user.organization_id, IntegrationProvider.WIALON, payload
    )


@router.post("/integrations/wialon/sync", response_model=SyncResponse)
async def sync_wialon(user: FleetStaffUser, db: AsyncSession = Depends(get_db)) -> SyncResponse:
    synced, _ = await fleet_service.sync_wialon(db, user.organization_id)
    return SyncResponse(
        provider="wialon",
        synced=synced,
        status="active",
        message=f"DEMO sync: обновлены позиции {synced} ТС",
    )


@router.post("/integrations/transmanager/connect", response_model=IntegrationResponse)
async def connect_transmanager(
    payload: IntegrationConnectRequest,
    user: FleetStaffUser,
    db: AsyncSession = Depends(get_db),
) -> IntegrationResponse:
    return await fleet_service.connect_integration(
        db, user.organization_id, IntegrationProvider.TRANSMANAGER, payload
    )


@router.post("/integrations/transmanager/sync", response_model=SyncResponse)
async def sync_transmanager(user: FleetStaffUser, db: AsyncSession = Depends(get_db)) -> SyncResponse:
    total, _ = await fleet_service.sync_transmanager(db, user.organization_id)
    return SyncResponse(
        provider="transmanager",
        synced=total,
        status="active",
        message=f"DEMO sync: заявок в системе {total}",
    )


@router.get("/orders", response_model=OrderListResponse)
async def get_orders(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> OrderListResponse:
    items = await fleet_service.list_orders(db, user.organization_id)
    return OrderListResponse(items=items, total=len(items))


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def post_order(
    payload: OrderCreate, user: FleetStaffUser, db: AsyncSession = Depends(get_db)
) -> OrderResponse:
    return await fleet_service.create_order(db, user.organization_id, payload)


@router.post("/orders/{order_id}/assign", response_model=OrderResponse)
async def post_assign_order(
    order_id: uuid.UUID,
    payload: OrderAssignRequest,
    user: FleetStaffUser,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    try:
        return await fleet_service.assign_order(db, user.organization_id, order_id, payload.vehicle_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
