from fastapi import APIRouter

from app.api.v1 import analytics, auth, fleet, health, ops
from app.api.v1.agents import permit as permit_agent
from app.api.v1.integrations import rosdor

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(analytics.router)
api_router.include_router(fleet.router)
api_router.include_router(ops.router)
api_router.include_router(permit_agent.router)
api_router.include_router(rosdor.router)
