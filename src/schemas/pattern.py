# src/schemas/pattern.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any

class TransactionPattern(BaseModel):
    pattern_id: int = Field(..., description="Unique pattern identifier")
    card_id: str = Field(..., description="Card identifier")
    avg_transaction_amount: float = Field(..., ge=0, description="Average transaction amount")
    avg_daily_transactions: int = Field(..., ge=0, description="Average daily transaction count")
    common_merchants: List[str] = Field(default=[], description="Frequently visited merchants")
    common_locations: List[int] = Field(default=[], description="Frequently visited locations")
    last_updated: datetime = Field(..., description="Last pattern update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "pattern_id": 1,
                "card_id": "card_123",
                "avg_transaction_amount": 150.75,
                "avg_daily_transactions": 3,
                "common_merchants": ["merchant_1", "merchant_2"],
                "common_locations": [1, 2, 3],
                "last_updated": "2024-01-01T12:00:00"
            }
        }

class RiskAnalysis(BaseModel):
    risk_level: str = Field(..., description="Overall risk level")
    risk_factors: List[Dict[str, Any]] = Field(
        ..., 
        description="List of identified risk factors"
    )
    historical_pattern: Dict[str, Any] = Field(
        ..., 
        description="Historical transaction patterns"
    )
    recommendations: List[str] = Field(
        ..., 
        description="Risk mitigation recommendations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "risk_level": "MEDIUM",
                "risk_factors": [
                    {
                        "type": "amount",
                        "description": "Transaction amount significantly higher than user average",
                        "severity": "high"
                    },
                    {
                        "type": "location",
                        "description": "Transaction from unusual location",
                        "severity": "medium"
                    }
                ],
                "historical_pattern": {
                    "avg_transaction_amount": 150.75,
                    "typical_merchants": ["merchant_1", "merchant_2"],
                    "typical_locations": [1, 2, 3],
                    "common_transaction_times": ["morning", "evening"]
                },
                "recommendations": [
                    "Verify user identity through two-factor authentication",
                    "Contact card holder for transaction confirmation"
                ]
            }
        }