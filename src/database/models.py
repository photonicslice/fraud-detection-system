from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ARRAY
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

    # Add relationship to Card
    cards = relationship("Card", back_populates="user")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True)
    card_id = Column(String(50), nullable=False)
    merchant_id = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    location_id = Column(Integer, ForeignKey('locations.id'))
    device_id = Column(String(50))
    ip_address = Column(String(50))
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

    # New columns for risk scores
    merchant_risk_score = Column(Float, nullable=True, default=0.0)
    location_risk_score = Column(Float, nullable=True, default=0.0)
    amount_risk_score = Column(Float, nullable=True, default=0.0)

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

    # Add relationship to User
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
    avg_transaction_amount = Column(Float)
    avg_daily_transactions = Column(Integer)
    common_merchants = Column(ARRAY(String))
    common_locations = Column(ARRAY(Integer))
    last_updated = Column(DateTime, default=datetime.utcnow)
