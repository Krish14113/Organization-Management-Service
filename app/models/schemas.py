from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class OrgCreate(BaseModel):
    organization_name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)

class OrgResponse(BaseModel):
    id: str
    organization_name: str
    collection_name: str
    admin_email: EmailStr

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class OrgUpdate(BaseModel):
    organization_name: Optional[str] = None
    admin_email: Optional[EmailStr] = None
