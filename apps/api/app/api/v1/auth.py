from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AdminUser, CurrentUser
from app.core.config import get_settings
from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_db
from app.schemas.auth import (
    AcceptInviteRequest,
    AuthResponse,
    InviteRequest,
    InviteResponse,
    LoginRequest,
    MeResponse,
    SignupRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(
    payload: SignupRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    settings = get_settings()
    await enforce_rate_limit(
        request,
        bucket="signup",
        limit=settings.auth_rate_limit_signup,
        window_seconds=settings.auth_rate_limit_window_seconds,
    )
    return await auth_service.signup(db, payload)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    settings = get_settings()
    await enforce_rate_limit(
        request,
        bucket="login",
        limit=settings.auth_rate_limit_login,
        window_seconds=settings.auth_rate_limit_window_seconds,
    )
    return await auth_service.login(db, payload)


@router.get("/me", response_model=MeResponse)
async def me(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> MeResponse:
    return await auth_service.get_me(db, user)


@router.post("/invite", response_model=InviteResponse, status_code=201)
async def invite(
    payload: InviteRequest,
    user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> InviteResponse:
    return await auth_service.create_invite(db, user, payload)


@router.post("/accept-invite", response_model=AuthResponse)
async def accept_invite(
    payload: AcceptInviteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    settings = get_settings()
    await enforce_rate_limit(
        request,
        bucket="accept-invite",
        limit=settings.auth_rate_limit_signup,
        window_seconds=settings.auth_rate_limit_window_seconds,
    )
    return await auth_service.accept_invite(db, payload)
