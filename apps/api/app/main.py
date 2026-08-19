from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()


docs_url = "/docs" if settings.docs_enabled else None
redoc_url = "/redoc" if settings.docs_enabled else None
openapi_url = "/openapi.json" if settings.docs_enabled else None

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
    lifespan=lifespan,
)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

# Electron serves UI from http://127.0.0.1:<random-port> — allow any localhost origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    payload = {
        "service": "fleetpilot-api",
        "version": settings.app_version,
    }
    if settings.docs_enabled:
        payload["docs"] = "/docs"
    return payload
