# scripts/populate_initial_data.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.database.connection import SessionLocal
from src.database.models import Location, Card
from datetime import datetime

def populate_initial_data():
    db = SessionLocal()
    try:
        # Create sample locations
        locations = [
            Location(
                id=1,
                merchant_id="merch_456",
                address="123 Main St",
                city="New York",
                country="US",
                postal_code="10001",
                created_at=datetime.utcnow()
            ),
            Location(
                id=2,
                merchant_id="merch_456",
                address="456 Market St",
                city="San Francisco",
                country="US",
                postal_code="94103",
                created_at=datetime.utcnow()
            ),
            # Add high-risk locations
            Location(
                id=101,
                merchant_id="merch_456",
                address="High Risk Location 1",
                city="Risk City",
                country="XX",
                postal_code="99999",
                created_at=datetime.utcnow()
            )
        ]
        
        # Add locations to database
        for location in locations:
            existing_location = db.query(Location).filter(Location.id == location.id).first()
            if not existing_location:
                db.add(location)
        
        # Create sample cards
        cards = [
            Card(
                card_id="card_123",
                card_type="credit",
                issuing_bank="Example Bank",
                country_code="US",
                created_at=datetime.utcnow()
            )
        ]
        
        # Add cards to database
        for card in cards:
            existing_card = db.query(Card).filter(Card.card_id == card.card_id).first()
            if not existing_card:
                db.add(card)
        
        db.commit()
        print("Initial data populated successfully!")
        
    except Exception as e:
        print(f"Error populating data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_initial_data()
