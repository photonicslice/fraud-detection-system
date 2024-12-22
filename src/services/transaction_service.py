# src/services/transaction_service.py

from sqlalchemy.orm import Session
from src.database.models import Transaction, Card, TransactionPattern
from src.schemas.transaction import TransactionCreate, TransactionResponse
from datetime import datetime
from src.utils.logging_config import setup_logging

# Setup logger
logger = setup_logging(__name__)

class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        logger.info("TransactionService initialized with database session")

    def enrich_transaction(self, transaction_data: TransactionCreate):
        """
        Enrich transaction data with additional features for fraud detection.
        """
        logger.info(f"Starting transaction enrichment for card_id: {transaction_data.card_id}")
        try:
            enriched_data = {
                "card_id": transaction_data.card_id,
                "amount": transaction_data.amount,
                "merchant_id": transaction_data.merchant_id,
                "timestamp": datetime.utcnow(),
                "location_id": transaction_data.location_id,
                "device_id": transaction_data.device_id,
                "ip_address": transaction_data.ip_address
            }

            # Adding calculated risks
            card_type = self.get_card_type(transaction_data.card_id)
            enriched_data["card_type"] = card_type
            logger.debug(f"Retrieved card type: {card_type}")

            merchant_risk = self.calculate_merchant_risk(transaction_data.merchant_id)
            enriched_data["merchant_risk_score"] = merchant_risk
            logger.debug(f"Calculated merchant risk: {merchant_risk}")

            location_risk = self.calculate_location_risk(transaction_data.location_id)
            enriched_data["location_risk_score"] = location_risk
            logger.debug(f"Calculated location risk: {location_risk}")

            amount_risk = self.calculate_amount_risk(transaction_data.amount)
            enriched_data["amount_risk_score"] = amount_risk
            logger.debug(f"Calculated amount risk: {amount_risk}")

            logger.info("Successfully enriched transaction data")
            return enriched_data

        except Exception as e:
            logger.error(f"Error enriching transaction: {str(e)}")
            raise

    def get_card_type(self, card_id: str):
        """
        Fetch card type based on card_id.
        """
        logger.debug(f"Fetching card type for card_id: {card_id}")
        try:
            card = self.db.query(Card).filter(Card.card_id == card_id).first()
            if card:
                logger.debug(f"Found card type: {card.card_type}")
                return card.card_type
            else:
                logger.warning(f"No card found for card_id: {card_id}")
                return "unknown"
        except Exception as e:
            logger.error(f"Error fetching card type: {str(e)}")
            raise

    def calculate_merchant_risk(self, merchant_id: str):
        """
        Calculate risk score for a merchant based on known fraud patterns.
        """
        logger.debug(f"Calculating risk score for merchant_id: {merchant_id}")
        try:
            high_risk_merchants = {"suspicious_merchant_1", "suspicious_merchant_2"}
            risk_score = 0.8 if merchant_id in high_risk_merchants else 0.2
            logger.debug(f"Merchant risk score calculated: {risk_score}")
            return risk_score
        except Exception as e:
            logger.error(f"Error calculating merchant risk: {str(e)}")
            raise

    def calculate_location_risk(self, location_id: int):
        """
        Calculate risk score for a location.
        """
        logger.debug(f"Calculating risk score for location_id: {location_id}")
        try:
            high_risk_locations = {101, 102, 103}
            risk_score = 0.7 if location_id in high_risk_locations else 0.1
            logger.debug(f"Location risk score calculated: {risk_score}")
            return risk_score
        except Exception as e:
            logger.error(f"Error calculating location risk: {str(e)}")
            raise

    def calculate_amount_risk(self, amount: float):
        """
        Calculate risk based on transaction amount.
        """
        logger.debug(f"Calculating risk score for amount: {amount}")
        try:
            if amount > 1000:
                risk_score = 0.9
            elif amount < 10:
                risk_score = 0.5
            else:
                risk_score = 0.3
            logger.debug(f"Amount risk score calculated: {risk_score}")
            return risk_score
        except Exception as e:
            logger.error(f"Error calculating amount risk: {str(e)}")
            raise

    def store_transaction(self, transaction_data: TransactionCreate, fraud_probability: float):
        """
        Store a transaction in the database and mark its fraud probability.
        """
        logger.info(f"Storing transaction for card_id: {transaction_data.card_id}")
        try:
            transaction = Transaction(
                card_id=transaction_data.card_id,
                merchant_id=transaction_data.merchant_id,
                amount=transaction_data.amount,
                timestamp=datetime.utcnow(),
                location_id=transaction_data.location_id,
                device_id=transaction_data.device_id,
                ip_address=transaction_data.ip_address,
                status="fraud" if fraud_probability > 0.5 else "legit",
                created_at=datetime.utcnow()
            )

            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"Successfully stored transaction with id: {transaction.transaction_id}")
            
            response = TransactionResponse(
                transaction_id=transaction.transaction_id,
                card_id=transaction.card_id,
                amount=transaction.amount,
                merchant_id=transaction.merchant_id,
                timestamp=transaction.timestamp,
                status=transaction.status
            )
            return response

        except Exception as e:
            logger.error(f"Error storing transaction: {str(e)}")
            self.db.rollback()
            raise

    def get_transaction_history(self, card_id: str):
        """
        Fetch the transaction history for a specific card.
        """
        logger.info(f"Fetching transaction history for card_id: {card_id}")
        try:
            transactions = self.db.query(Transaction).filter(
                Transaction.card_id == card_id
            ).all()
            logger.info(f"Found {len(transactions)} transactions for card_id: {card_id}")
            return transactions
        except Exception as e:
            logger.error(f"Error fetching transaction history: {str(e)}")
            raise

    def update_transaction_patterns(self, transaction_data: TransactionCreate):
        """
        Update transaction patterns for a card.
        """
        logger.info(f"Updating transaction patterns for card_id: {transaction_data.card_id}")
        try:
            pattern = self.db.query(TransactionPattern).filter(
                TransactionPattern.card_id == transaction_data.card_id
            ).first()
            
            if not pattern:
                # Create new pattern
                pattern = TransactionPattern(
                    card_id=transaction_data.card_id,
                    avg_transaction_amount=transaction_data.amount,
                    avg_daily_transactions=1
                )
                self.db.add(pattern)
            else:
                # Update existing pattern
                pattern.avg_transaction_amount = (
                    pattern.avg_transaction_amount * 0.7 + transaction_data.amount * 0.3
                )
            
            self.db.commit()
            logger.info(f"Updated transaction patterns for card {transaction_data.card_id}")
        except Exception as e:
            logger.error(f"Error updating transaction patterns: {str(e)}")
            self.db.rollback()
            raise