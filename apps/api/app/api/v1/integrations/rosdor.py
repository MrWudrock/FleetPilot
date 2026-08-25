from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PermitStaffUser
from app.db.session import get_db
from app.integrations.rosdor_adapter import get_rosdor_adapter
from app.models import Integration
from app.models.enums import IntegrationProvider
from app.schemas.permit import RosdorHealthResponse, RosdorPermitCheckRequest, RosdorPermitCheckResponse

router = APIRouter(prefix="/integrations/rosdor", tags=["rosdor-integration"])


@router.get("/health", response_model=RosdorHealthResponse)
async def rosdor_health() -> RosdorHealthResponse:
    return get_rosdor_adapter().health()


@router.post("/permits/check", response_model=RosdorPermitCheckResponse)
async def check_permit(
    payload: RosdorPermitCheckRequest,
    user: PermitStaffUser,
    db: AsyncSession = Depends(get_db),
) -> RosdorPermitCheckResponse:
    adapter = get_rosdor_adapter()
    result = await adapter.check_permit(payload.permit_number, payload.plate)

    from app.models import PermitAuditLog

    db.add(
        PermitAuditLog(
            organization_id=user.organization_id,
            action="registry_check",
            provider="rosdor_monitoring",
            request_payload={
                "permit_number": payload.permit_number,
                "plate": payload.plate[:4] + "***",
            },
            response_summary={"found": result.found, "source": result.source},
        )
    )
    await db.commit()
    return result


@router.post("/sync")
async def force_sync(
    user: PermitStaffUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    integration = await db.scalar(
        select(Integration).where(
            Integration.organization_id == user.organization_id,
            Integration.provider == IntegrationProvider.ROSDOR_MONITORING,
        )
    )
    if not integration:
        return {"status": "skipped", "message": "Rosdor integration not configured for organization"}
    return {"status": "queued", "message": "Registry sync scheduled (Sprint 7.1)"}
