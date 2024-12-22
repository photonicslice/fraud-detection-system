# src/schemas/user.py

from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List
from .card import CardResponse

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip().title()

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User's password")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "securepassword123"
            }
        }

class UserResponse(UserBase):
    id: int = Field(..., description="User's unique identifier")
    created_at: datetime = Field(..., description="Account creation timestamp")
    cards: Optional[List[CardResponse]] = Field(None, description="List of user's cards")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "created_at": "2024-01-01T12:00:00",
                "cards": []
            }
        }
