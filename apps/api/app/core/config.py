from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_DEFAULT_SECRET = "dev-secret-change-in-production"
INSECURE_DEFAULT_CREDENTIALS_KEY = "dev-credentials-key-change-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FleetPilot API"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = "postgresql://fleetpilot:fleetpilot@localhost:5432/fleetpilot"
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = INSECURE_DEFAULT_SECRET
    credentials_encryption_key: str | None = None
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    jwt_algorithm: str = "HS256"
    # Short-lived access tokens — reduce blast radius if stolen from localStorage.
    jwt_expire_minutes: int = 60 * 8
    invite_expire_hours: int = 168

    # False by default — enable only for local/demo (ALLOW_PUBLIC_SIGNUP=true).
    allow_public_signup: bool = False

    # Auth abuse protection (Redis-backed; falls back to in-memory).
    auth_rate_limit_login: int = 20
    auth_rate_limit_signup: int = 10
    auth_rate_limit_window_seconds: int = 60

    rosdor_parser_api_key: str | None = None
    rosdor_parser_base_url: str = "https://api.parser-api.com"
    rosdor_lk_enabled: bool = False

    permit_max_width_m: float = 2.55
    permit_max_height_m: float = 4.0
    permit_max_length_m: float = 12.0

    @field_validator("secret_key")
    @classmethod
    def secret_key_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("SECRET_KEY must not be empty")
        return value.strip()

    @model_validator(mode="after")
    def validate_security_defaults(self) -> "Settings":
        if self.secret_key == INSECURE_DEFAULT_SECRET and not self.debug:
            raise ValueError(
                "SECRET_KEY is the insecure default. Set a strong SECRET_KEY "
                "or enable DEBUG=true only for local development."
            )

        creds_key = self.resolved_credentials_encryption_key

        if not self.debug:
            if self.credentials_encryption_key is None:
                raise ValueError(
                    "CREDENTIALS_ENCRYPTION_KEY is required when DEBUG=false "
                    "(must differ from SECRET_KEY)."
                )
            if creds_key == self.secret_key:
                raise ValueError("CREDENTIALS_ENCRYPTION_KEY must differ from SECRET_KEY")
            if self.allow_public_signup:
                raise ValueError(
                    "ALLOW_PUBLIC_SIGNUP must be false when DEBUG=false. "
                    "Use admin invite flow instead."
                )

        if self.debug and self.credentials_encryption_key is None:
            # Local dev: fall back to insecure default only in DEBUG mode.
            pass

        return self

    @property
    def resolved_credentials_encryption_key(self) -> str:
        if self.credentials_encryption_key:
            return self.credentials_encryption_key.strip()
        if self.debug:
            return INSECURE_DEFAULT_CREDENTIALS_KEY
        return self.secret_key

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url

    @property
    def sync_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return url

    @property
    def docs_enabled(self) -> bool:
        return self.debug


@lru_cache
def get_settings() -> Settings:
    return Settings()
