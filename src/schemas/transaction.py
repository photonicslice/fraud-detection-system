# src/schemas/transaction.py

from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

class TransactionCreate(BaseModel):
    card_id: str = Field(..., description="Unique identifier of the card")
    merchant_id: str = Field(..., description="Unique identifier of the merchant")
    amount: float = Field(..., gt=0, description="Transaction amount")
    location_id: Optional[int] = Field(None, description="Location identifier")
    device_id: Optional[str] = Field(None, description="Device identifier")
    ip_address: Optional[str] = Field(None, description="IP address of the transaction")

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return float(Decimal(str(v)).quantize(Decimal('0.01')))  # Round to 2 decimal places

    @validator('card_id')
    def validate_card_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Card ID cannot be empty')
        return v.strip()

    @validator('merchant_id')
    def validate_merchant_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Merchant ID cannot be empty')
        return v.strip()

class TransactionResponse(BaseModel):
    transaction_id: int = Field(..., description="Unique identifier of the transaction")
    card_id: str = Field(..., description="Card identifier")
    merchant_id: str = Field(..., description="Merchant identifier")
    amount: float = Field(..., description="Transaction amount")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    status: str = Field(..., description="Transaction status (fraud/legit)")
    fraud_probability: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Probability of transaction being fraudulent"
    )
    merchant_risk_score: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Risk score for the merchant"
    )
    location_risk_score: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Risk score for the location"
    )
    amount_risk_score: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Risk score based on amount"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "transaction_id": 1,
                "card_id": "card_123",
                "merchant_id": "merch_456",
                "amount": 100.00,
                "timestamp": "2024-01-01T12:00:00",
                "status": "legit",
                "fraud_probability": 0.1,
                "merchant_risk_score": 0.2,
                "location_risk_score": 0.1,
                "amount_risk_score": 0.3
            }
        }