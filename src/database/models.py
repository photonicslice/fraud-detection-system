#src/database/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ARRAY, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    cards = relationship("Card", back_populates="user")

class FraudCase(Base):
    __tablename__ = 'fraud_cases'
    
    case_id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.transaction_id'), unique=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='open')  # open, closed, under_review
    fraud_type = Column(String(50))
    confidence_score = Column(Float)
    resolved_at = Column(DateTime)
    resolution = Column(String(100))
    transaction = relationship("Transaction", back_populates="fraud_case")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True)
    card_id = Column(String(50), nullable=False)
    merchant_id = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)  # Changed to Numeric for precise currency handling
    timestamp = Column(DateTime, default=datetime.utcnow)
    location_id = Column(Integer, ForeignKey('locations.id'))
    device_id = Column(String(50))
    ip_address = Column(String(50))
    status = Column(String(20), default='pending')  # pending, completed, failed, fraud
    created_at = Column(DateTime, default=datetime.utcnow)

    # Risk probabilities
    fraud_probability = Column(Float, nullable=True, default=0.0)
    risk_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH

    # Risk scores
    merchant_risk_score = Column(Float, nullable=True, default=0.0)
    location_risk_score = Column(Float, nullable=True, default=0.0)
    amount_risk_score = Column(Float, nullable=True, default=0.0)
    pattern_risk_score = Column(Float, nullable=True, default=0.0)
    user_behavior_risk_score = Column(Float, nullable=True, default=0.0)

    # Metadata
    analysis_version = Column(String(50), nullable=True)  # To track which model version made the prediction
    analyzed_at = Column(DateTime, nullable=True)  # When the risk analysis was performed

    # Relationships
    location = relationship("Location", back_populates="transactions")
    fraud_case = relationship("FraudCase", back_populates="transaction", uselist=False)

class Card(Base):
    __tablename__ = 'cards'
    
    card_id = Column(String(50), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    card_type = Column(String(20))
    issuing_bank = Column(String(50))
    country_code = Column(String(2))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="cards")

class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    merchant_id = Column(String(50), nullable=False)
    address = Column(String(255))
    city = Column(String(100))
    country = Column(String(2))
    postal_code = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    transactions = relationship("Transaction", back_populates="location")

class TransactionPattern(Base):
    __tablename__ = 'transaction_patterns'
    
    pattern_id = Column(Integer, primary_key=True)
    card_id = Column(String(50), ForeignKey('cards.card_id'))
    avg_transaction_amount = Column(Numeric(10, 2))  # Changed to Numeric
    avg_daily_transactions = Column(Integer)
    common_merchants = Column(ARRAY(String))
    common_locations = Column(ARRAY(Integer))
    last_updated = Column(DateTime, default=datetime.utcnow)