from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(
    *,
    user_id: UUID,
    organization_id: UUID,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    payload = {
        "sub": str(user_id),
        "org_id": str(organization_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


def try_decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return decode_access_token(token)
    except JWTError:
        return None
