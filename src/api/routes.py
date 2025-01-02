# src/api/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.ml.prediction.predictor import FraudPredictor
from src.schemas.transaction import TransactionCreate, TransactionResponse
from src.services.transaction_service import TransactionService
import logging

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()
predictor = FraudPredictor()

@router.post("/transactions/verify", response_model=TransactionResponse)
async def verify_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Verify a transaction for potential fraud.
    Returns enriched transaction data with fraud probability and risk scores.
    """
    logger.info(f"Processing transaction for card: {transaction.card_id}")
    transaction_service = TransactionService(db)
    
    try:
        # Enrich transaction data
        enriched_data = transaction_service.enrich_transaction(transaction)
        logger.info("Transaction data enriched successfully")
        
        # Get fraud prediction with risk components
        prediction_result = predictor.predict(enriched_data)
        logger.info(f"Fraud probability: {prediction_result['fraud_probability']:.4f}")
        
        # Store result with all risk components
        result = transaction_service.store_transaction(
            transaction_data=transaction,
            fraud_probability=prediction_result['fraud_probability'],
            risk_components=prediction_result['risk_components']
        )
        
        # Add prediction details to response
        response_data = {
            **result.dict(),
            'risk_breakdown': prediction_result['risk_components'],
            'risk_level': prediction_result['risk_level']
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing transaction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing transaction: {str(e)}"
        )



@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running
    """
    try:
        # Basic model health check
        predictor.health_check()
        return {"status": "healthy", "model_loaded": True}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Service unhealthy: {str(e)}"
        )