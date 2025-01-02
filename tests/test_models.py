# tests/test_models.py

from src.database.models import Transaction, Location
from datetime import datetime

def test_create_transaction(db_session):
    # Create test location
    location = Location(
        id=1,
        merchant_id="test_merchant",
        address="Test Address",
        city="Test City",
        country="US"
    )
    db_session.add(location)
    db_session.commit()
    
    # Create transaction
    transaction = Transaction(
        card_id="test_card",
        merchant_id="test_merchant",
        amount=100.00,
        location_id=1,
        status="pending"
    )
    
    db_session.add(transaction)
    db_session.commit()
    
    # Query and verify
    saved_transaction = db_session.query(Transaction).first()
    assert saved_transaction.card_id == "test_card"
    assert saved_transaction.amount == 100.00
