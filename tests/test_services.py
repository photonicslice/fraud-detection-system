# tests/test_services.py

import pytest
from src.services.transaction_service import TransactionService
from src.schemas.transaction import TransactionCreate

def test_transaction_service_enrichment(db_session):
    # Create service instance
    service = TransactionService(db_session)
    
    # Test data
    transaction_data = TransactionCreate(
        card_id="card_123",
        merchant_id="merch_456",
        amount=100.00,
        location_id=1
    )
    
    # Test enrichment
    enriched_data = service.enrich_transaction(transaction_data)
    
    # Assertions
    assert enriched_data["card_id"] == transaction_data.card_id
    assert enriched_data["merchant_id"] == transaction_data.merchant_id
    assert enriched_data["amount"] == transaction_data.amount
    assert "merchant_risk_score" in enriched_data
    assert "location_risk_score" in enriched_data
