# src/schemas/card.py

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class CardBase(BaseModel):
    card_type: str = Field(..., description="Type of card (credit/debit)")
    issuing_bank: str = Field(..., description="Name of issuing bank")
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO country code")

    @validator('country_code')
    def validate_country_code(cls, v):
        return v.upper()

    @validator('card_type')
    def validate_card_type(cls, v):
        valid_types = {'credit', 'debit', 'prepaid'}
        if v.lower() not in valid_types:
            raise ValueError(f'Card type must be one of: {", ".join(valid_types)}')
        return v.lower()

class CardCreate(CardBase):
    user_id: int = Field(..., gt=0, description="ID of card owner")

    class Config:
        json_schema_extra = {
            "example": {
                "card_type": "credit",
                "issuing_bank": "Example Bank",
                "country_code": "US",
                "user_id": 1
            }
        }

class CardResponse(CardBase):
    card_id: str = Field(..., description="Unique card identifier")
    user_id: int = Field(..., description="ID of card owner")
    created_at: datetime = Field(..., description="Card creation timestamp")
    is_active: bool = Field(True, description="Card active status")
    last_used: Optional[datetime] = Field(None, description="Last transaction timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "card_id": "card_123",
                "card_type": "credit",
                "issuing_bank": "Example Bank",
                "country_code": "US",
                "user_id": 1,
                "created_at": "2024-01-01T12:00:00",
                "is_active": True,
                "last_used": "2024-01-02T15:30:00"
            }
        }
