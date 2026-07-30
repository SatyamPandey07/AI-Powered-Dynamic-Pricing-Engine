from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class OrgCreate(BaseModel):
    name: str

class UserResponse(BaseModel):
    id: str
    org_id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class UserInvite(BaseModel):
    email: EmailStr
    role: str

class UserUpdate(BaseModel):
    role: str

class OrgResponse(BaseModel):
    id: str
    name: str
    subscription_tier: Optional[str]
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class OrgUpdate(BaseModel):
    name: Optional[str]
    subscription_tier: Optional[str]

class ApiKeyCreate(BaseModel):
    name: str
    permissions: Optional[List[str]] = None

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    created_at: datetime

class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    changes_before: Optional[Dict[str, Any]]
    changes_after: Optional[Dict[str, Any]]
    ip_address: str
    created_at: datetime
    class Config:
        from_attributes = True
