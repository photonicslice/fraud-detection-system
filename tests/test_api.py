# tests/test_api.py

from fastapi.testclient import TestClient
import pytest
from datetime import datetime

def test_verify_transaction(test_client, db_session):
    # Test data
    transaction_data = {
        "card_id": "card_123",
        "merchant_id": "merch_456",
        "amount": 100.00,
        "location_id": 1,
        "device_id": "device_789",
        "ip_address": "192.168.1.1"
    }
    
    # Make request
    response = test_client.post("/api/v1/transactions/verify", json=transaction_data)
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert "transaction_id" in data
    assert data["card_id"] == transaction_data["card_id"]
    assert data["merchant_id"] == transaction_data["merchant_id"]
    assert data["amount"] == transaction_data["amount"]
    assert "fraud_probability" in data

def test_verify_transaction_invalid_amount(test_client):
    # Test data with invalid amount
    transaction_data = {
        "card_id": "card_123",
        "merchant_id": "merch_456",
        "amount": -100.00,
        "location_id": 1
    }
    
    # Make request
    response = test_client.post("/api/v1/transactions/verify", json=transaction_data)
    
    # Assert response
    assert response.status_code == 422
