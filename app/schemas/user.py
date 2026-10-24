from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    username: str
    name: str
    phone: Optional[str] = None


# What client sends when creating a user
class UserCreate(UserBase):
    password: str


# What API returns (never return password!)
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
