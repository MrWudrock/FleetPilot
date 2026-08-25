from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.db.session import get_db
from app.schemas.analytics import RoiKpiResponse
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/roi", response_model=RoiKpiResponse)
async def roi_dashboard(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> RoiKpiResponse:
    return await analytics_service.get_roi_kpis(db, user)
