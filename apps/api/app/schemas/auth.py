import re
import uuid

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    organization_name: str = Field(min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class InviteRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    role: str = Field(default="viewer", pattern="^(admin|dispatcher|fleet_manager|driver|viewer)$")


class AcceptInviteRequest(BaseModel):
    token: str = Field(min_length=16, max_length=256)
    password: str = Field(min_length=8, max_length=128)


class OrganizationOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    organization_id: uuid.UUID

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    organization: OrganizationOut


class MeResponse(BaseModel):
    user: UserOut
    organization: OrganizationOut


class InviteResponse(BaseModel):
    invite_token: str
    expires_in_hours: int
    message: str
