import json
import re
import secrets
import uuid

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Organization, User
from app.models.enums import UserRole
from app.schemas.auth import (
    AcceptInviteRequest,
    AuthResponse,
    InviteRequest,
    InviteResponse,
    LoginRequest,
    MeResponse,
    OrganizationOut,
    SignupRequest,
    UserOut,
)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "org"


async def _unique_slug(db: AsyncSession, base: str) -> str:
    slug = slugify(base)
    candidate = slug
    suffix = 1

    while True:
        exists = await db.scalar(select(Organization.id).where(Organization.slug == candidate))
        if not exists:
            return candidate
        suffix += 1
        candidate = f"{slug}-{suffix}"


async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        organization_id=user.organization_id,
    )


def _auth_response(user: User, organization: Organization) -> AuthResponse:
    token = create_access_token(
        user_id=user.id,
        organization_id=user.organization_id,
        role=user.role.value,
    )
    return AuthResponse(
        access_token=token,
        user=_user_out(user),
        organization=OrganizationOut.model_validate(organization),
    )


async def signup(db: AsyncSession, payload: SignupRequest) -> AuthResponse:
    settings = get_settings()
    if not settings.allow_public_signup:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is disabled. Contact your organization admin for an invite.",
        )

    email = payload.email.lower()

    if await _get_user_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    organization = Organization(
        name=payload.organization_name.strip(),
        slug=await _unique_slug(db, payload.organization_name),
    )
    user = User(
        organization=organization,
        email=email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role=UserRole.ADMIN,
        is_active=True,
    )

    db.add(organization)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await db.refresh(organization)

    return _auth_response(user, organization)


async def login(db: AsyncSession, payload: LoginRequest) -> AuthResponse:
    user = await _get_user_by_email(db, payload.email.lower())

    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    organization = await db.get(Organization, user.organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return _auth_response(user, organization)


async def get_me(db: AsyncSession, user: User) -> MeResponse:
    organization = await db.get(Organization, user.organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return MeResponse(
        user=_user_out(user),
        organization=OrganizationOut.model_validate(organization),
    )


async def create_invite(db: AsyncSession, inviter: User, payload: InviteRequest) -> InviteResponse:
    settings = get_settings()
    email = payload.email.lower()

    if await _get_user_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    role = UserRole(payload.role)
    token = secrets.token_urlsafe(32)
    invite_data = {
        "organization_id": str(inviter.organization_id),
        "email": email,
        "full_name": payload.full_name.strip(),
        "role": role.value,
        "invited_by": str(inviter.id),
    }

    client = aioredis.from_url(settings.redis_url, decode_responses=True)
    try:
        ttl_seconds = settings.invite_expire_hours * 3600
        await client.setex(f"invite:{token}", ttl_seconds, json.dumps(invite_data))
    finally:
        await client.aclose()

    return InviteResponse(
        invite_token=token,
        expires_in_hours=settings.invite_expire_hours,
        message="Share invite token with the user to complete registration",
    )


async def accept_invite(db: AsyncSession, payload: AcceptInviteRequest) -> AuthResponse:
    settings = get_settings()

    client = aioredis.from_url(settings.redis_url, decode_responses=True)
    try:
        raw = await client.get(f"invite:{payload.token}")
        if not raw:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired invite")
        invite_data = json.loads(raw)
        await client.delete(f"invite:{payload.token}")
    finally:
        await client.aclose()

    email = invite_data["email"]
    if await _get_user_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    organization = await db.get(Organization, uuid.UUID(invite_data["organization_id"]))
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    user = User(
        organization_id=organization.id,
        email=email,
        password_hash=hash_password(payload.password),
        full_name=invite_data["full_name"],
        role=UserRole(invite_data["role"]),
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return _auth_response(user, organization)
